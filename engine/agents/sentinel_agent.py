"""
================================================================================
SysCalculus - Autonomous Self-Healing Sentinel & Quality Watchdog Agent
================================================================================
Core Mission:
Continuously patrol, detect anomalies, verify HTTP availability, check static
asset integrity, watch for content changes, and execute autonomous self-healing
repairs with ZERO human intervention.
================================================================================
"""

import os
import sys
import time
import json
import re
import urllib.request
import threading
from datetime import datetime

class SentinelAgent:
    def __init__(self, workspace_root, port=3000, check_interval=20, sre_agent=None, server_controller=None):
        self.workspace_root = workspace_root
        self.port = port
        self.check_interval = check_interval
        self.sre = sre_agent
        self.server_controller = server_controller
        self.dist_dir = os.path.join(workspace_root, "dist")
        self.content_dir = os.path.join(workspace_root, "content", "tools")
        self.templates_dir = os.path.join(workspace_root, "templates")
        self.static_dir = os.path.join(workspace_root, "static")
        self.ledger_file = os.path.join(workspace_root, "data", "autonomous_audit_ledger.json")

        self.running = True
        self.thread = None
        self.start_time = time.time()
        
        # State tracking
        self.file_mtimes = {}
        self.total_cycles = 0
        self.anomalies_detected = 0
        self.auto_heals_executed = 0
        self.last_status = "INITIALIZING"
        self.recent_incidents = []

        # Populate initial file modification times
        self.file_mtimes = self._scan_file_mtimes()

    def _scan_file_mtimes(self):
        """Records current modification timestamps for hot-reload watching."""
        mtimes = {}
        watch_dirs = [self.content_dir, self.templates_dir, self.static_dir]
        for wdir in watch_dirs:
            if not os.path.exists(wdir):
                continue
            for root, _, files in os.walk(wdir):
                for f in files:
                    fpath = os.path.join(root, f)
                    try:
                        mtimes[fpath] = os.path.getmtime(fpath)
                    except OSError:
                        pass
        return mtimes

    def log_incident(self, incident_type, reason, action_taken):
        """Records an autonomous self-healing incident."""
        incident = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "type": incident_type,
            "reason": reason,
            "action_taken": action_taken
        }
        self.recent_incidents.append(incident)
        if len(self.recent_incidents) > 100:
            self.recent_incidents = self.recent_incidents[-100:]

        print(f"\n[SENTINEL AUTO-HEAL] [ALERT] Incident: {incident_type} | Cause: {reason}")
        print(f"[SENTINEL AUTO-HEAL] [ACTION] Autonomous Action: {action_taken}\n")

        if self.sre:
            self.sre.log_event("SENTINEL_AUTO_HEAL", incident)

        self._save_ledger()

    def _save_ledger(self):
        """Persists the audit & healing metrics."""
        os.makedirs(os.path.dirname(self.ledger_file), exist_ok=True)
        data = {
            "sentinel_uptime_seconds": int(time.time() - self.start_time),
            "total_cycles": self.total_cycles,
            "anomalies_detected": self.anomalies_detected,
            "auto_heals_executed": self.auto_heals_executed,
            "last_status": self.last_status,
            "last_cycle_timestamp": datetime.utcnow().isoformat() + "Z",
            "recent_incidents": self.recent_incidents
        }
        try:
            with open(self.ledger_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[SENTINEL] Failed to write ledger: {e}")

    # =========================================================================
    # SELF-HEALING RECOVERY ACTIONS
    # =========================================================================

    def heal_build(self, reason):
        """Recompiles the static site and regenerates all assets."""
        self.anomalies_detected += 1
        self.auto_heals_executed += 1
        self.last_status = "HEALING_BUILD"
        
        try:
            import build
            build.build_site()
            self.file_mtimes = self._scan_file_mtimes()
            self.log_incident("CORRUPTED_OR_OUTDATED_BUILD", reason, "Executed build.build_site() cleanly.")
            self.last_status = "HEALTHY"
            return True
        except Exception as e:
            self.log_incident("BUILD_HEAL_FAILED", str(e), "Failed to recompile site.")
            self.last_status = "DEGRADED"
            return False

    def heal_server(self, reason):
        """Restarts the HTTP server controller."""
        self.anomalies_detected += 1
        self.auto_heals_executed += 1
        self.last_status = "HEALING_SERVER"

        if self.server_controller:
            try:
                self.server_controller.restart()
                self.log_incident("HTTP_SERVER_DOWN", reason, f"Restarted ServerController on port {self.port}")
                self.last_status = "HEALTHY"
                return True
            except Exception as e:
                self.log_incident("SERVER_RESTART_FAILED", str(e), "Failed to restart server.")
                self.last_status = "DEGRADED"
                return False
        else:
            self.log_incident("SERVER_CONTROLLER_MISSING", reason, "No server controller registered.")
            return False

    # =========================================================================
    # AUDIT PROBES
    # =========================================================================

    def probe_file_integrity(self):
        """Verifies critical static pages exist and are not empty."""
        critical_files = [
            os.path.join(self.dist_dir, "index.html"),
            os.path.join(self.dist_dir, "about.html"),
            os.path.join(self.dist_dir, "privacy.html"),
            os.path.join(self.dist_dir, "sitemap.xml"),
            os.path.join(self.dist_dir, "robots.txt"),
        ]

        # Also check all markdown tools have compiled html
        if os.path.exists(self.content_dir):
            for f in os.listdir(self.content_dir):
                if f.endswith(".md"):
                    tool_slug = f[:-3]
                    critical_files.append(os.path.join(self.dist_dir, "tools", f"{tool_slug}.html"))

        for fpath in critical_files:
            if not os.path.exists(fpath):
                return False, f"Missing critical file: {os.path.relpath(fpath, self.workspace_root)}"
            try:
                min_size = 15 if fpath.endswith((".txt", ".xml")) else 100
                if os.path.getsize(fpath) < min_size:
                    return False, f"Truncated file (<{min_size} bytes): {os.path.relpath(fpath, self.workspace_root)}"
            except OSError as e:
                return False, f"Cannot access file {fpath}: {e}"

        return True, "All critical files present and healthy."

    def probe_unrendered_jinja(self):
        """Scans compiled HTML files to ensure zero raw Jinja tags leak."""
        if not os.path.exists(self.dist_dir):
            return True, "dist/ does not exist yet"

        for root, _, files in os.walk(self.dist_dir):
            for f in files:
                if f.endswith(".html"):
                    fpath = os.path.join(root, f)
                    try:
                        with open(fpath, "r", encoding="utf-8", errors="ignore") as fp:
                            content = fp.read()
                        leaks = re.findall(r"\{\{.*?\}\}|\{%.*?%\}", content)
                        if leaks:
                            return False, f"Unrendered Jinja tag in {f}: {leaks[:2]}"
                    except Exception:
                        pass
        return True, "Zero Jinja leaks."

    def probe_source_mutations(self):
        """Detects if any tool markdown, template, or static asset changed on disk."""
        current_mtimes = self._scan_file_mtimes()
        mutated_file = None

        for fpath, mtime in current_mtimes.items():
            prev_mtime = self.file_mtimes.get(fpath)
            if prev_mtime is None or mtime > prev_mtime:
                mutated_file = fpath
                break

        # Check for deleted files
        if not mutated_file:
            for fpath in self.file_mtimes:
                if fpath not in current_mtimes:
                    mutated_file = fpath
                    break

        self.file_mtimes = current_mtimes
        if mutated_file:
            return True, f"File changed or added: {os.path.relpath(mutated_file, self.workspace_root)}"
        return False, "No file mutations."

    def probe_http_service(self):
        """Sends HTTP probes to the running server."""
        probe_urls = [
            f"http://localhost:{self.port}/",
            f"http://localhost:{self.port}/tools/db-deadlock-simulator.html"
        ]
        for url in probe_urls:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "SysCalculusSentinel/1.0"})
                with urllib.request.urlopen(req, timeout=3) as resp:
                    if resp.getcode() != 200:
                        return False, f"HTTP Probe {url} returned status {resp.getcode()}"
            except Exception as e:
                return False, f"HTTP Probe failed on {url}: {e}"
        return True, "HTTP endpoints responding 200 OK."

    def probe_adsense_compliance(self):
        """Verifies zero fake sponsors exist and DART policy is present."""
        privacy_file = os.path.join(self.dist_dir, "privacy.html")
        if os.path.exists(privacy_file):
            try:
                with open(privacy_file, "r", encoding="utf-8") as f:
                    text = f.read()
                if "DART" not in text:
                    return False, "Privacy policy missing Google DART cookie clause."
            except Exception:
                pass

        # Check for forbidden fake sponsors in index
        index_file = os.path.join(self.dist_dir, "index.html")
        if os.path.exists(index_file):
            try:
                with open(index_file, "r", encoding="utf-8") as f:
                    text = f.read().lower()
                for bad in ["sponsored by cloudflare", "cockroachlabs.com"]:
                    if bad in text:
                        return False, f"Forbidden fake sponsor found: {bad}"
            except Exception:
                pass

        return True, "AdSense compliance verified."

    # =========================================================================
    # MASTER AUDIT & HEAL CYCLE
    # =========================================================================

    def run_single_cycle(self):
        """Runs a complete inspection cycle and applies auto-healing if needed."""
        self.total_cycles += 1

        # 1. Source Mutations Check (Auto-build on change)
        has_mutation, mut_reason = self.probe_source_mutations()
        if has_mutation:
            self.heal_build(mut_reason)

        # 2. File Integrity Check
        int_ok, int_reason = self.probe_file_integrity()
        if not int_ok:
            self.heal_build(int_reason)

        # 3. Jinja Leak Check
        jinja_ok, jinja_reason = self.probe_unrendered_jinja()
        if not jinja_ok:
            self.heal_build(jinja_reason)

        # 4. AdSense Compliance Check
        adsense_ok, adsense_reason = self.probe_adsense_compliance()
        if not adsense_ok:
            self.heal_build(adsense_reason)

        # 5. HTTP Service Check
        http_ok, http_reason = self.probe_http_service()
        if not http_ok:
            self.heal_server(http_reason)

        # If everything passes cleanly
        if int_ok and jinja_ok and adsense_ok and http_ok:
            self.last_status = "100% HEALTHY / OPERATIONAL"

        self._save_ledger()

    def continuous_loop(self):
        """Infinite 24/7 background sentinel loop."""
        print(f"[SENTINEL] [ACTIVE] 24/7 Self-Healing Sentinel active (Cycle: {self.check_interval}s).")
        while self.running:
            try:
                self.run_single_cycle()
            except Exception as e:
                print(f"[SENTINEL UNEXPECTED ERROR] {e}")
            time.sleep(self.check_interval)

    def start_sentinel_thread(self):
        """Spawns the continuous sentinel thread in background."""
        if self.thread and self.thread.is_alive():
            return self.thread
        self.thread = threading.Thread(target=self.continuous_loop, daemon=True, name="SentinelThread")
        self.thread.start()
        return self.thread

    def stop(self):
        """Stops the continuous sentinel loop."""
        self.running = False
