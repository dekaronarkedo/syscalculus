"""
RuntimeZero - Autonomous Growth & Developer Community Syndication Agent
Generates value-first technical solutions for Reddit (r/devops, r/aws), 
technical teardown threads for Twitter/X, and canonical syndicated posts for Dev.to/Hashnode.
"""

import os
import json
from datetime import datetime

class GrowthAgent:
    def __init__(self, workspace_root):
        self.workspace_root = workspace_root
        self.queue_file = os.path.join(workspace_root, 'data', 'social_queue.json')

    def generate_reddit_post(self, tool):
        """Generates a value-first, non-spam technical response for r/devops or r/aws."""
        slug = tool.get('slug')
        if slug == 'db-deadlock-simulator':
            subreddit = "r/devops"
            title = "[Deep-Dive] Why your database connection pool is likely 5x too big (and how HikariCP sizing formula actually works)"
            body = f"""Most teams I talk to configure their connection pool to 100 or 200 connections thinking 'more connections = more throughput'. 

In reality, on an 8-core DB server, when 150 threads compete for disk I/O and shared buffers, the Linux kernel spends more time context-switching than executing queries, causing P99 latencies to skyrocket.

Here is the exact formula from the creators of HikariCP:
Connections = ((Core Count * 2) + Effective Spindle Count)

On an 8-core database instance, 18-20 connections will almost always deliver higher throughput than 100 connections.

We built an interactive, 100% client-side simulator where you can test pool starvation and leak thresholds live in your browser:
https://runtimezero.dev/tools/db-deadlock-simulator.html (Runs entirely in-browser, zero logs sent to any server)

Hope this helps anyone dealing with Black Friday / high-traffic connection exhaustion!"""

        elif slug == 'aws-egress-calculator':
            subreddit = "r/aws"
            title = "[Cost Optimization] How to eliminate AWS S3 internet egress gouging ($0.09/GB) using Cloudflare R2"
            body = f"""If you run media-heavy or public download workloads on AWS S3, you know that data transfer out ($0.09/GB) is frequently 3x the cost of actual S3 storage.

For an 80 TB/month workload, you're looking at ~$7,300/month just in egress.

Cloudflare R2 implements the exact same S3 REST API (SigV4) but charges $0.00 for data transfer out. By pointing your public download domain to R2 while keeping your AWS EC2/EKS backend intact, you can completely eliminate internet egress bills.

I wrote an open-source visual egress cost calculator and Terraform configuration template here:
https://runtimezero.dev/tools/aws-egress-calculator.html (Evaluates 100% client-side, zero data sent to external servers)

Terraform snippet is included for anyone looking to set up an active-active zero-egress mirror."""

        elif slug == 'airgapped-log-sanitizer':
            subreddit = "r/sysadmin"
            title = "[Security Tool] Air-gapped in-browser log sanitizer for redacting AWS keys, JWTs, and DB URIs"
            body = f"""Quick PSA for sysadmins and on-call engineers:

Pasting production error logs into random online web formatters is one of the easiest ways to leak database credentials and AWS access keys (these sites often store logs in unauthenticated /tmp directories or use third-party session recorders).

We created a zero-telemetry, 100% air-gapped log sanitizer:
https://runtimezero.dev/tools/airgapped-log-sanitizer.html

It scrubs:
- AWS Access Keys (AKIA / ASIA)
- JWT Bearer Tokens
- DB connection strings with embedded passwords (postgres://, mysql://)
- IPv4 addresses

You can disconnect your internet / turn on Airplane mode after loading the page and verify in DevTools Network tab that zero bytes leave your browser."""

        else:
            subreddit = "r/webdev"
            title = f"[Dev Tool] Interactive Simulator: {tool.get('title')}"
            body = f"""We built an air-gapped, zero-network simulator for {tool.get('title')}.
100% client-side, runs in your browser with zero telemetry.

Check it out: https://runtimezero.dev/tools/{tool.get('slug')}.html"""

        return {
            "platform": "reddit",
            "target": subreddit,
            "title": title,
            "content": body,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }

    def generate_twitter_thread(self, tool):
        """Generates a 5-tweet technical teardown thread with ASCII diagrams."""
        slug = tool.get('slug')
        tweets = [
            f"🧵 1/5 The hidden reason database connection pools cause production outages under traffic spikes (and the mathematical formula to fix them):",
            f"2/5 Many engineers configure pool sizes to 100+ thinking 'more connections = more throughput'.\n\nReality: A 16-core CPU can only execute 16 threads simultaneously. 100+ threads cause catastrophic OS context-switching penalties & buffer lock contention.",
            f"3/5 The battle-tested HikariCP formula:\n\nPool Size = (Core Count * 2) + Effective Spindle Count\n\nFor an 8-core NVMe server, 18-20 connections will outperform 200 connections every single time.",
            f"4/5 We built an interactive Canvas simulator where you can test pool starvation, leak thresholds, and P99 latency spikes live in your browser:\n\n👉 https://runtimezero.dev/tools/{slug}.html\n\n(100% client-side, zero logs or data sent to servers)",
            f"5/5 Bookmark the tool and check your pg_stat_activity for 'idle in transaction' states before your next high-traffic launch. #DevOps #PostgreSQL #SRE #CloudEngineering"
        ]
        return {
            "platform": "twitter",
            "handle": "@runtimezerodev",
            "thread": tweets,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }

    def generate_devto_article(self, tool):
        """Generates canonical Markdown syndication post for Dev.to / Hashnode."""
        return {
            "platform": "devto",
            "title": tool.get('article_headline', tool.get('title')),
            "canonical_url": f"https://runtimezero.dev/tools/{tool.get('slug')}.html",
            "tags": ["devops", "cloud", "architecture", "database"],
            "body_markdown": f"""Originally published on [RuntimeZero](https://runtimezero.dev/tools/{tool.get('slug')}.html).

{tool.get('raw_content', '')}

---
*Run the interactive simulator 100% in your browser with zero data exfiltration at [RuntimeZero](https://runtimezero.dev/tools/{tool.get('slug')}.html).*
""",
            "status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }

    def sync_all_social_queues(self, tools_data):
        """Builds and updates the full syndication queue in data/social_queue.json."""
        queue = []
        if os.path.exists(self.queue_file):
            try:
                with open(self.queue_file, 'r', encoding='utf-8') as f:
                    queue = json.load(f)
            except Exception:
                queue = []

        existing_keys = {f"{item['platform']}-{item.get('target', '')}-{item.get('title', '')[:30]}" for item in queue}

        new_items = []
        for tool in tools_data:
            reddit = self.generate_reddit_post(tool)
            rk = f"{reddit['platform']}-{reddit['target']}-{reddit['title'][:30]}"
            if rk not in existing_keys:
                queue.append(reddit)
                new_items.append(reddit)

            tweet = self.generate_twitter_thread(tool)
            tk = f"{tweet['platform']}-{tweet.get('handle', '')}-{tweet['thread'][0][:30]}"
            if tk not in existing_keys:
                queue.append(tweet)
                new_items.append(tweet)

            devto = self.generate_devto_article(tool)
            dk = f"{devto['platform']}--{devto['title'][:30]}"
            if dk not in existing_keys:
                queue.append(devto)
                new_items.append(devto)

        os.makedirs(os.path.dirname(self.queue_file), exist_ok=True)
        with open(self.queue_file, 'w', encoding='utf-8') as f:
            json.dump(queue, f, indent=2)

        return {
            "total_queued": len(queue),
            "newly_added": len(new_items)
        }

    def dispatch_pending_queue(self, max_items=2):
        """
        Autonomously dispatches pending syndicated articles and announcements.
        Supports Dev.to REST API and Webhook broadcasting.
        """
        import urllib.request
        import urllib.error

        if not os.path.exists(self.queue_file):
            return {"dispatched": 0, "errors": []}

        try:
            with open(self.queue_file, 'r', encoding='utf-8') as f:
                queue = json.load(f)
        except Exception:
            return {"dispatched": 0, "errors": ["Failed to load queue file"]}

        dispatched_count = 0
        errors = []
        devto_key = os.environ.get("DEVTO_API_KEY")
        discord_webhook = os.environ.get("DISCORD_WEBHOOK_URL")

        for item in queue:
            if item.get("status") != "pending":
                continue
            if dispatched_count >= max_items:
                break

            platform = item.get("platform")

            # 1. Dev.to Autonomous REST API Publishing
            if platform == "devto" and devto_key:
                try:
                    payload = json.dumps({
                        "article": {
                            "title": item["title"],
                            "published": True,
                            "body_markdown": item["body_markdown"],
                            "tags": item.get("tags", ["devops", "cloud", "architecture"]),
                            "canonical_url": item.get("canonical_url")
                        }
                    }).encode("utf-8")

                    req = urllib.request.Request(
                        "https://dev.to/api/articles",
                        data=payload,
                        headers={
                            "Content-Type": "application/json",
                            "api-key": devto_key,
                            "User-Agent": "RuntimeZeroGrowthAgent/1.0"
                        }
                    )
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        if resp.getcode() in [200, 201]:
                            res_data = json.loads(resp.read().decode("utf-8"))
                            item["status"] = "dispatched"
                            item["dispatched_at"] = datetime.utcnow().isoformat()
                            item["published_url"] = res_data.get("url")
                            dispatched_count += 1
                            print(f"[GROWTH DISPATCH] Published article on Dev.to: {res_data.get('url')}")
                except Exception as e:
                    errors.append(f"Dev.to dispatch error: {e}")

            # 2. Discord / Webhook Developer Community Broadcast
            elif discord_webhook and platform in ["reddit", "twitter"]:
                try:
                    content_str = item.get("content") or "\n".join(item.get("thread", []))
                    payload = json.dumps({
                        "username": "RuntimeZero Growth Sentinel",
                        "content": f"**[SYNDICATED TO {platform.upper()}]** {item.get('title', '')}\n\n{content_str[:1500]}"
                    }).encode("utf-8")

                    req = urllib.request.Request(
                        discord_webhook,
                        data=payload,
                        headers={"Content-Type": "application/json", "User-Agent": "RuntimeZeroWebhook/1.0"}
                    )
                    with urllib.request.urlopen(req, timeout=8) as resp:
                        if resp.getcode() in [200, 204]:
                            item["status"] = "dispatched"
                            item["dispatched_at"] = datetime.utcnow().isoformat()
                            dispatched_count += 1
                            print(f"[GROWTH DISPATCH] Broadcasted {platform} post to Webhook channel.")
                except Exception as e:
                    errors.append(f"Webhook dispatch error: {e}")

        # Save updated queue
        try:
            with open(self.queue_file, 'w', encoding='utf-8') as f:
                json.dump(queue, f, indent=2)
        except Exception as e:
            errors.append(f"Failed to save updated queue: {e}")

        return {
            "dispatched": dispatched_count,
            "errors": errors
        }
