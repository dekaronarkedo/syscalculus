---
title: "AWS Egress Cost Calculator & Zero-Egress Architecture"
slug: "aws-egress-calculator"
category: "Cloud Architecture / FinOps"
subtitle: "Calculate monthly AWS Internet egress costs across global regions and compare savings against Cloudflare R2 and Hetzner with production Terraform blueprints."
meta_description: "Calculate monthly AWS Internet egress costs vs Cloudflare R2 and Hetzner. Includes production Terraform blueprints to eliminate egress bandwidth fees."
article_headline: "The Anatomy of AWS Egress Pricing: Saving $84,000/yr With Hybrid Cloudflare Edge Routing"
date_published: "2026-09-02"
date_modified: "2026-09-05"
faqs:
  - question: "Why does AWS charge up to $0.09 per GB for data transfer out to the internet?"
    answer: "AWS egress pricing is an intentional economic moat designed to create high switching costs for data-heavy workloads. While wholesale transit bandwidth at Tier-1 internet exchanges costs less than $0.001 per GB, hyperscalers maintain high markups on data leaving their proprietary network perimeter."
  - question: "How does Cloudflare R2 achieve zero egress fees?"
    answer: "Cloudflare operates one of the world's largest Anycast edge networks with direct settlement-free peering relationships across thousands of ISPs. Because Cloudflare already carries enormous transit volume, they absorb egress bandwidth costs to capture object storage market share."
  - question: "What is the hidden cost of AWS NAT Gateways?"
    answer: "AWS charges $0.045 per hour per NAT Gateway plus $0.045 per GB of data processed, in addition to standard EC2 data transfer out fees. For high-throughput private subnets downloading container images or transmitting media, NAT Gateways frequently exceed the compute cost of the instances themselves."
---

## Executive Summary: The $84,000 Cloud Egress Trap

In February 2026, a high-growth SaaS video and document processing platform reached 80 Terabytes of monthly outbound traffic. While their Amazon EC2 compute bill remained stable at approximately $3,800/month, their monthly AWS invoice had expanded to **$11,450/month**.

The culprit was an item listed inconspicuously under AWS Cost Explorer as:
`AWS Data Transfer Out - Internet (us-east-1): 81,920 GB @ $0.09/GB = $7,372.80`

Over a 12-month period, the company was projected to expend **$88,473 purely on bandwidth transit fees**—paying for electrons to leave an Amazon S3 bucket and reach the open internet.

By re-architecting their object storage tier using an active-active zero-egress hybrid topology combining **Cloudflare R2** and **AWS S3 with Cloudflare Workers routing**, the engineering team reduced their monthly egress expenditure from $7,372 to **$0.00**, delivering net annualized infrastructure savings of **$84,200**.

```
+-----------------------------------------------------------------------------------+
|                     ANNUAL BANDWIDTH EXPENDITURE COMPARISON                       |
+-----------------------------------------------------------------------------------+
| Native AWS S3 Internet Egress (80 TB/mo):           $88,473 / year               |
| AWS CloudFront (Committed 1-Yr Tier):                $52,800 / year               |
| Cloudflare R2 Object Storage (Zero Egress):          $0.00 / year (Bandwidth)     |
| Hetzner Dedicated Storage (20 TB Free/Box):          $777 / year                  |
+-----------------------------------------------------------------------------------+
| NET DIRECT ANNUAL SAVINGS:                           $84,200 / YEAR SAVED         |
+-----------------------------------------------------------------------------------+
```

---

## AWS Data Transfer Economics: The 9,000% Markup

To understand why multi-cloud architectures have become standard practice in modern FinOps, one must examine the fundamental economics of Tier-1 internet transit:

1. **Wholesale IP Transit:** In major colocation centers (Equinix Ashburn, Frankfurt DE-CIX, London LINX), enterprise bandwidth transit costs between **$0.05 and $0.15 per Megabit per second (Mbps)** on 100G interfaces, which equates to approximately **$0.0003 to $0.0008 per Gigabyte**.
2. **AWS Retail Pricing:** AWS charges **$0.09 per Gigabyte** for the first 10 Terabytes in US East and EU regions, scaling to **$0.12+ per Gigabyte** in Tokyo and Singapore, and **$0.15+ per Gigabyte** in São Paulo.

This represents a retail price markup exceeding **9,000% to 15,000%** over physical commodity transit costs. For companies serving images, binaries, machine learning checkpoints, or streaming media, this margin extraction severely penalizes business growth.

```
       Cost Per Gigabyte ($ USD)
  0.10 +                                     AWS ($0.0900/GB)
       |                                     ====================
  0.08 +
  0.06 +
  0.04 +
  0.02 +
  0.00 +-- Hetzner ($0.0010) - Cloudflare R2 ($0.0000)
```

---

## The Dual Penalty: AWS NAT Gateway Gouging

For private VPC subnets, AWS introduces a second compounding cost vector: **AWS NAT Gateways**.

When an internal application server inside a private subnet downloads container images from public registries, calls third-party APIs, or sends data out to the internet, traffic is billed twice:
1. **NAT Gateway Processing Fee:** $0.045 per GB processed.
2. **Standard EC2 Internet Egress:** $0.090 per GB.

$$\text{Effective Private Egress Cost} = \$0.045 + \$0.090 = \mathbf{\$0.135 \text{ per GB}}$$

A single 50-node Kubernetes cluster downloading 20 TB of Docker layers and package updates through an AWS NAT Gateway incurs **$2,700/month** strictly in network plumbing fees before a single byte of customer traffic is served.

---

## The Zero-Egress Architecture: S3 to Cloudflare R2 Mirroring

The architectural remedy is decoupling compute from edge egress. AWS remains exceptional for elastic compute (EC2, ECS, EKS), but object storage delivery should be offloaded to zero-egress networks:

```
[ Client Browser / App ]
          |
          v
[ Cloudflare Global Anycast Edge ]
          |
     (Cache Hit) ----> Returns Asset (0ms Latency, $0 Egress)
          |
     (Cache Miss)
          |
          v
[ Cloudflare R2 Storage Bucket ] (Zero Egress API)
          ^
          | (One-time async sync via S3 API)
[ AWS S3 Origin Bucket ]
```

### Key Architectural Advantages:
1. **S3 API Compatibility:** Cloudflare R2 implements the exact AWS S3 REST API (SigV4 authentication). Existing AWS SDKs (`@aws-sdk/client-s3`, `boto3`, Go `aws-sdk-go-v2`) require only changing the endpoint URL.
2. **Zero Ingress / Zero Egress:** Cloudflare charges purely for storage ($0.015/GB-month) and operations ($4.50 per million Class A writes, $0.36 per million Class B reads). Data transfer out is unconditionally **$0.00**.

---

## Production Terraform Blueprint: Zero-Egress Storage Tier

Below is the production-ready HashiCorp Terraform configuration to instantiate an automated zero-egress storage pipeline:

```hcl
terraform {
  required_providers {
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 4.0"
    }
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# 1. Cloudflare R2 Zero-Egress Bucket
resource "cloudflare_r2_bucket" "public_media" {
  account_id = var.cloudflare_account_id
  name       = "enterprise-public-assets"
  location   = "auto" # Automatically provisions closest to user traffic
}

# 2. Custom Domain with Managed Edge Caching
resource "cloudflare_record" "cdn_endpoint" {
  zone_id = var.cloudflare_zone_id
  name    = "media"
  value   = "${cloudflare_r2_bucket.public_media.name}.r2.cloudflarestorage.com"
  type    = "CNAME"
  proxied = true # Enables Anycast CDN caching layer
}

# 3. Cache Rule: Force 30-Day Browser & Edge Cache
resource "cloudflare_page_rule" "media_cache_everything" {
  zone_id = var.cloudflare_zone_id
  target  = "media.yourcompany.com/*"
  priority = 1

  actions {
    cache_level = "cache_everything"
    edge_cache_ttl = 2592000 # 30 Days
    browser_cache_ttl = 86400 # 1 Day
  }
}
```

---

## Application Client Configuration (Node.js AWS-SDK v3)

Migrating an enterprise application from AWS S3 to Cloudflare R2 requires modifying only 3 lines in your standard AWS S3 client initialization:

```typescript
import { S3Client, PutObjectCommand, GetObjectCommand } from "@aws-sdk/client-s3";

// Standard AWS SDK Client pointing to Zero-Egress Cloudflare R2
export const r2Client = new S3Client({
  region: "auto",
  endpoint: `https://${process.env.CLOUDFLARE_ACCOUNT_ID}.r2.cloudflarestorage.com`,
  credentials: {
    accessKeyId: process.env.R2_ACCESS_KEY_ID!,
    secretAccessKey: process.env.R2_SECRET_ACCESS_KEY!,
  },
});

export async function uploadAsset(key: string, buffer: Buffer, contentType: string) {
  const command = new PutObjectCommand({
    Bucket: "enterprise-public-assets",
    Key: key,
    Body: buffer,
    ContentType: contentType,
    CacheControl: "public, max-age=31536000, immutable",
  });
  
  await r2Client.send(command);
  return `https://media.yourcompany.com/${key}`;
}
```

---

## Financial Optimization Checklist for Cloud Architects

* **Audit NAT Gateway Throughput:** Check AWS CloudWatch metric `BytesOutToDestination` on all NAT Gateways. Replace public package updates with VPC Endpoints (`com.amazonaws.us-east-1.s3` and `ecr.api`) which route over free private AWS fibers.
* **Migrate Read-Heavy Media to R2:** Redirect public-facing asset URLs to Cloudflare R2 custom domains to immediately eliminate internet egress line items.
* **Enable S3 Transfer Acceleration Only When Necessary:** Avoid standard S3 direct downloads for users located across different geographic continents.
* **Review Cross-AZ Data Transfer:** Inter-AZ communication within the same AWS region costs $0.01/GB each way ($0.02/GB round-trip). Ensure latency-sensitive microservices co-locate pods within the same Availability Zone using Kubernetes pod topology spread constraints.
