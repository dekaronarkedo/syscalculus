"""
SysCalculus - Autonomous Principal Engineer Agent
Manages creation, scaffolding, and verification of interactive client-side systems simulators.
"""

import os
import json
from datetime import datetime

class EngineerAgent:
    def __init__(self, workspace_root):
        self.workspace_root = workspace_root
        self.tools_dir = os.path.join(workspace_root, 'content', 'tools')

    def list_available_tools(self):
        """Lists all existing tools in content/tools."""
        tools = []
        if os.path.exists(self.tools_dir):
            for f in os.listdir(self.tools_dir):
                if f.endswith('.md'):
                    slug = f[:-3]
                    tools.append(slug)
        return tools

    def scaffold_new_tool(self, title, slug, category, subtitle, meta_description, article_headline):
        """Scaffolds a new client-side tool definition."""
        file_path = os.path.join(self.tools_dir, f"{slug}.md")
        if os.path.exists(file_path):
            return {"status": "exists", "file": file_path}

        now_str = datetime.utcnow().strftime("%Y-%m-%d")
        template = f"""---
title: "{title}"
slug: "{slug}"
category: "{category}"
subtitle: "{subtitle}"
meta_description: "{meta_description}"
article_headline: "{article_headline}"
date_published: "{now_str}"
date_modified: "{now_str}"
faqs:
  - question: "How does this tool operate in an air-gapped environment?"
    answer: "This tool runs 100% inside your browser's local JavaScript V8 engine with zero network dependencies."
---

## Architectural Deep-Dive: {title}

Production infrastructure requires deterministic modeling and low-latency analysis. This guide details the mathematics, failure modes, and mitigation strategies.
"""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(template)

        return {"status": "created", "file": file_path}

    def generate_next_autonomous_tool(self):
        """
        Autonomously discovers and deploys the next high-CPC engineering tool
        from the autonomous engineering pipeline.
        """
        existing = set(self.list_available_tools())
        
        # High-CPC Autonomous Pipeline Catalog
        catalog = [
            {
                "slug": "k8s-oom-killer-sizing",
                "title": "Kubernetes Cgroup v2 OOM-Killer Threshold Calculator",
                "category": "Containers",
                "subtitle": "Deterministic memory limit modeling to eliminate exit code 137 under peak burst traffic.",
                "meta_description": "Calculate Linux cgroups v2 memory.max thresholds, page cache reclaim rates, and RSS headroom to prevent Kubernetes OOMKilled 137 pod terminations.",
                "article_headline": "Root Cause Analysis: Why Kubernetes Pods Get OOMKilled (Exit Code 137) Before Hitting Memory Limits",
                "content": r"""
### The Anatomy of Linux cgroups v2 Memory Pressure

In Linux cgroups v2, memory limits are not a single hard boundary. The Linux kernel evaluates three distinct thresholds before invoking the Out-Of-Memory (OOM) killer:

1. **`memory.low`**: Best-effort memory protection. Below this threshold, page caches are rarely reclaimed unless system-wide starvation occurs.
2. **`memory.high`**: Throttle boundary. When a process exceeds `memory.high`, the kernel injects synthetic delays into memory-allocating threads to slow down allocation rate.
3. **`memory.max`**: Hard ceiling. Exceeding `memory.max` triggers synchronous reclaim. If insufficient pages can be freed, the kernel invokes `oom_kill_process()`, terminating the container with **SIGKILL (Exit Code 137)**.

```
Total Memory Usage = RSS (Anonymous Memory) + Page Cache (Buffer/File I/O) + Kernel Slab
```

### Why Default Kubernetes Sizing Fails in Production

Most development teams set `resources.limits.memory` equal to `resources.requests.memory * 1.5` without accounting for page cache eviction speeds on NVMe disks. Under high throughput, I/O intensive services (e.g. log ingestion, SQLite caching, Node.js buffer pools) fill the page cache faster than kernel reclaim loops can cycle, triggering instant OOM kills even when heap usage is well below 60%.

### Production Mitigation Formula

To size memory limits deterministically without OOM risk:

$$M_{limit} = (RSS_{p99} \times 1.25) + \max(I/O_{burst}, 64\text{MB}) + Slab_{overhead}$$

Where:
* $RSS_{p99}$ is your application's 99th percentile active anonymous memory.
* $1.25$ accounts for GC compaction latency in managed runtimes (Go, JVM, V8).
* $\max(I/O_{burst}, 64\text{MB})$ guarantees sufficient unevicted page cache for kernel socket buffers.
"""
            },
            {
                "slug": "kafka-consumer-lag-estimator",
                "title": "Apache Kafka Partition Lag & Rebalance Time Estimator",
                "category": "Linux",
                "subtitle": "Calculate consumer recovery velocity, message backlog drainage time, and rebalance storm windows.",
                "meta_description": "Calculate Kafka partition lag recovery time, consumer group rebalance windows, and partition assignment efficiency.",
                "article_headline": "Engineering Guide: Preventing Cascading Kafka Consumer Group Rebalance Storms Under High Lag",
                "content": r"""
### The Mathematical Mechanics of Kafka Consumer Lag Recovery

When a partition consumer fails or falls behind incoming producer rates, lag accumulates linearly:

$$L(t) = L_0 + \int_0^t (R_{produce}(s) - R_{consume}(s)) \, ds$$

Recovery is only possible if the sustained consumption rate strictly exceeds the production velocity:

$$R_{consume} > R_{produce} \implies T_{drain} = \frac{L_0}{R_{consume} - R_{produce}}$$

### The Dreaded Cooperative-Sticky Rebalance Storm

When a consumer's poll interval exceeds `max.poll.interval.ms` (typically due to slow downstream database writes), the group coordinator revokes all partitions and initiates an incremental rebalance. If recovery processing takes longer than `max.poll.interval.ms`, consumers are repeatedly evicted in an infinite cascade known as a **Rebalance Storm**.

### Battle-Tested Configuration Rules

1. Set `max.poll.records` such that `(max.poll.records * p99_process_time) < (0.5 * max.poll.interval.ms)`.
2. Migrate to `CooperativeStickyAssignor` to avoid stop-the-world partition revocations.
3. Scale partitions along powers of 2 matching consumer CPU cores.
"""
            }
        ]

        for item in catalog:
            if item["slug"] not in existing:
                now_str = datetime.utcnow().strftime("%Y-%m-%d")
                fpath = os.path.join(self.tools_dir, f"{item['slug']}.md")
                content_str = f"""---
title: "{item['title']}"
slug: "{item['slug']}"
category: "{item['category']}"
subtitle: "{item['subtitle']}"
meta_description: "{item['meta_description']}"
article_headline: "{item['article_headline']}"
date_published: "{now_str}"
date_modified: "{now_str}"
faqs:
  - question: "Why does this tool execute client-side?"
    answer: "Systems diagnostics must never leak infrastructure metrics or cluster topologies over the public internet. All math evaluates locally in browser memory."
  - question: "Which formula governs this calculation?"
    answer: "The deterministic kernel sizing formulas derived in the technical post-mortem below."
---

## Architectural Deep-Dive: {item['title']}

{item['content']}
"""
                with open(fpath, "w", encoding="utf-8") as fp:
                    fp.write(content_str)
                print(f"[ENGINEER AGENT] Autonomously generated new systems tool: {item['slug']}")
                return {"status": "generated", "slug": item["slug"]}

        return {"status": "catalog_full", "message": "All pipeline tools are active."}
