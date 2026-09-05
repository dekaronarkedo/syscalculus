---
title: "Docker Run to Production Docker Compose Converter"
slug: "docker-compose-converter"
category: "Containers / Docker"
subtitle: "Convert messy multiline terminal docker run commands into hardened, production-grade docker-compose.yml files with security options and healthchecks."
meta_description: "Convert terminal docker run commands into production-grade, hardened docker-compose.yml files with securityOpts, healthchecks, and resource limits."
article_headline: "From Hacky Terminal Flags to Hardened Production Containers: The Docker Compose Reliability Standard"
date_published: "2026-09-04"
date_modified: "2026-09-05"
faqs:
  - question: "Why is running containers with raw 'docker run' bad practice in production?"
    answer: "Executing raw 'docker run' in a terminal leaves ephemeral state, lacks version control tracking, does not persist environment variables across server reboots, and frequently omits critical security boundaries such as memory limits and log rotation."
  - question: "What does 'security_opt: [no-new-privileges:true]' do in Docker Compose?"
    answer: "The 'no-new-privileges:true' flag prevents container processes from acquiring additional privileges via setuid or setgid binaries. If an attacker gains shell execution inside the container, this kernel flag stops them from escalating privileges to root on the host machine."
  - question: "Why must log rotation options always be configured in docker-compose.yml?"
    answer: "By default, Docker's json-file logging driver records container stdout/stderr indefinitely to the host disk without size limits. In production, an unchecked debug loop will fill the root partition (100% disk usage), causing the entire Docker daemon and host OS to freeze."
---

## Executive DevOps Analysis: The Ephemeral Terminal Trap

In engineering incident reviews, container crashes frequently trace back to undocumented `docker run` commands executed directly in SSH sessions.

A typical failure scenario:
An engineer logs into a production Ubuntu host to deploy a Redis caching instance. They execute:
```bash
docker run -d -p 6379:6379 -v /data/redis:/data redis:7
```

While the service initially runs, several critical failure modes are embedded in this raw execution:
1. **No Restart Policy:** When the underlying cloud VM reboots for a kernel security update 3 weeks later, the container remains stopped.
2. **Unbounded Memory Allocation:** Redis has no memory limits (`--memory`). Under an unexpected cache key explosion, Redis consumes 100% of host RAM, prompting the Linux kernel's OOM killer to terminate host networking daemons.
3. **No Log Rotation:** Container logging writes unbounded JSON logs to `/var/lib/docker/containers/`, silently exhausting the host's root disk inode table until all filesystem writes fail.

```
+-----------------------------------------------------------------------------------+
|                        RAW DOCKER RUN VS PRODUCTION COMPOSE                       |
+-----------------------------------------------------------------------------------+
| RAW DOCKER RUN:                                                                   |
|   X Ephemeral terminal history (Lost on SSH disconnect)                           |
|   X No memory or CPU throttling (Susceptible to noisy neighbor starvation)        |
|   X Unbounded log files (Fills host disk with GBs of logs)                        |
|   X Root execution without security restrictions                                  |
|                                                                                   |
| HARDENED DOCKER COMPOSE:                                                          |
|   ✓ Declarative YAML version-controlled in Git                                    |
|   ✓ Strict memory ceilings (mem_limit: 2g) & CPU quotas                           |
|   ✓ Automatic log rotation (max-size: 10m, max-file: 3)                           |
|   ✓ security_opt: [no-new-privileges:true] & read-only rootfs                     |
+-----------------------------------------------------------------------------------+
```

---

## The Hardened Docker Compose Standard

A production-grade `docker-compose.yml` file is not merely a translation of command flags; it is a declarative contract for reliability, observability, and container containment:

```yaml
version: "3.8"

services:
  production-api:
    image: node:20-alpine
    container_name: production-api
    restart: unless-stopped

    # 1. Security Boundaries
    security_opt:
      - no-new-privileges:true
    read_only: false
    user: "1001:1001" # Never run as root inside the container

    # 2. Resource Ceilings (Prevents host OOM crashes)
    deploy:
      resources:
        limits:
          cpus: "2.0"
          memory: 2048M
        reservations:
          cpus: "0.5"
          memory: 512M

    # 3. Network Isolation
    networks:
      - backend-net
    ports:
      - "127.0.0.1:8080:8080" # Bind strictly to localhost, reverse-proxy via Nginx

    # 4. Mandatory Log Rotation
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

    # 5. Integrated Healthcheck
    healthcheck:
      test: ["CMD-SHELL", "wget -qO- http://localhost:8080/health || exit 1"]
      interval: 15s
      timeout: 3s
      retries: 3
      start_period: 20s

networks:
  backend-net:
    driver: bridge
```

---

## Flag-by-Flag Translation Reference

| Docker Run CLI Flag | Docker Compose YAML Equivalent | Production Best Practice |
| :--- | :--- | :--- |
| `-d` / `--detach` | *Implicit* | Containers run detached by default when using `docker compose up -d`. |
| `-p 8080:8080` | `ports: ["127.0.0.1:8080:8080"]` | Bind to localhost (`127.0.0.1`) to prevent exposing ports directly to the public internet without an SSL reverse proxy. |
| `-v /data:/app/data` | `volumes: ["/data:/app/data:rw"]` | Append `:ro` (read-only) for configuration directories to prevent malicious container processes from modifying host files. |
| `-e ENV=prod` | `environment: [ENV=prod]` | Use `.env` file references (`${ENV}`) to avoid committing secrets into source control repositories. |
| `--restart always` | `restart: unless-stopped` | `unless-stopped` prevents Docker from forcibly restarting containers that were deliberately stopped by an engineer. |
| `--memory 1g` | `deploy.resources.limits.memory: 1024M` | Mandatory for all database, cache, and queue containers to eliminate cascading OOM host reboots. |

---

## Production Security Audit Checklist

Before deploying any containerized workload in production:
* **Never bind public ports directly:** Avoid `-p 0.0.0.0:5432:5432` for databases. Keep databases inside internal Docker bridge networks accessible only to the API services.
* **Enforce non-root execution:** Use alpine or distroless base images and set `USER 1000` in the Dockerfile or `user: "1000:1000"` in Compose.
* **Inspect Volume Mounts:** Never mount sensitive host paths such as `/var/run/docker.sock` unless deploying trusted monitoring agents (e.g. Datadog or Prometheus node-exporter), as mounting the Docker socket grants full root privileges over the host.
