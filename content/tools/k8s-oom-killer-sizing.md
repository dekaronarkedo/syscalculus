---
title: "Kubernetes Cgroup v2 OOM-Killer Threshold Calculator"
slug: "k8s-oom-killer-sizing"
category: "Containers"
subtitle: "Deterministic memory limit modeling to eliminate exit code 137 under peak burst traffic."
meta_description: "Calculate Linux cgroups v2 memory.max thresholds, page cache reclaim rates, and RSS headroom to prevent Kubernetes OOMKilled 137 pod terminations."
article_headline: "Root Cause Analysis: Why Kubernetes Pods Get OOMKilled (Exit Code 137) Before Hitting Memory Limits"
date_published: "2026-09-05"
date_modified: "2026-09-05"
faqs:
  - question: "Why does this tool execute client-side?"
    answer: "Systems diagnostics must never leak infrastructure metrics or cluster topologies over the public internet. All math evaluates locally in browser memory."
  - question: "Which formula governs this calculation?"
    answer: "The deterministic kernel sizing formulas derived in the technical post-mortem below."
---

## Architectural Deep-Dive: Kubernetes Cgroup v2 OOM-Killer Threshold Calculator


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

$$M_{limit} = (RSS_{p99} 	imes 1.25) + \max(I/O_{burst}, 64	ext{MB}) + Slab_{overhead}$$

Where:
* $RSS_{p99}$ is your application's 99th percentile active anonymous memory.
* $1.25$ accounts for GC compaction latency in managed runtimes (Go, JVM, V8).
* $\max(I/O_{burst}, 64	ext{MB})$ guarantees sufficient unevicted page cache for kernel socket buffers.

