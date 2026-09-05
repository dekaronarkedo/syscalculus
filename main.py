"""
================================================================================
RuntimeZero - Autonomous Ghost Founder Multi-Agent DAC Engine
Single Unified Master Entry Point
================================================================================
Controls:
- Multi-Threaded HTTP Server on Port 3000
- 5 Autonomous AI Department Agents (SRE, SEO, Growth, Editor, Principal Engineer)
- 24/7 Background Scheduler & Company Ledger
- Interactive CLI Console
================================================================================
"""

import os
import sys
import time
import threading
import json

from build import build_site
from server import ServerController
from engine.agents.editor_agent import EditorAgent
from engine.agents.seo_agent import SeoAgent
from engine.agents.growth_agent import GrowthAgent
from engine.agents.sre_agent import SreAgent
from engine.agents.engineer_agent import EngineerAgent
from engine.agents.sentinel_agent import SentinelAgent

PORT = int(os.environ.get("PORT", 3000))
WORKSPACE_ROOT = os.path.dirname(os.path.abspath(__file__))

class RuntimeZeroDAC:
    def __init__(self):
        self.workspace_root = WORKSPACE_ROOT
        self.dist_dir = os.path.join(WORKSPACE_ROOT, "dist")
        self.server_controller = ServerController(port=PORT)
        self.editor = EditorAgent(self.workspace_root)
        self.seo = SeoAgent(self.workspace_root)
        self.growth = GrowthAgent(self.workspace_root)
        self.sre = SreAgent(self.workspace_root)
        self.engineer = EngineerAgent(self.workspace_root)
        self.sentinel = SentinelAgent(
            workspace_root=self.workspace_root,
            port=PORT,
            check_interval=15,
            sre_agent=self.sre,
            server_controller=self.server_controller
        )
        self.running = True

    def run_autonomous_cycle(self):
        """Executes a full operational cycle across all departments."""
        print("\n[DAC CYCLE] Running Autonomous Operational Cycle...")
        # 1. Initial compile
        build_site()
        
        # 2. Autonomous Engineer: generate next high-CPC tool if catalog not full
        tool_res = self.engineer.generate_next_autonomous_tool()
        if tool_res.get("status") == "generated":
            print(f"[DAC CYCLE] New tool generated: {tool_res['slug']}. Recompiling site...")
            build_site()

        # 3. Autonomous Growth: dispatch pending syndications
        dispatch_res = self.growth.dispatch_pending_queue(max_items=2)
        if dispatch_res.get("dispatched", 0) > 0:
            print(f"[DAC CYCLE] Dispatched {dispatch_res['dispatched']} syndicated items.")

        # 4. SRE Health check
        health = self.sre.run_health_check(self.dist_dir)
        print(f"[DAC CYCLE] SRE System Health: {health['status']}")
        
        # 5. Log event
        self.sre.log_event("AUTONOMOUS_CYCLE_COMPLETE", {
            "status": health["status"],
            "tool_generated": tool_res.get("slug"),
            "dispatched": dispatch_res.get("dispatched", 0),
            "timestamp": time.time()
        })
        print("[DAC CYCLE] [OK] Operational cycle finished successfully.\n")

    def start_scheduler_thread(self, interval_seconds=3600):
        """Runs the autonomous operational cycle every interval_seconds (default 1 hour)."""
        def loop():
            while self.running:
                time.sleep(interval_seconds)
                try:
                    self.run_autonomous_cycle()
                except Exception as e:
                    print(f"[SCHEDULER ERROR] {e}")

        thread = threading.Thread(target=loop, daemon=True, name="SchedulerThread")
        thread.start()
        return thread

    def show_status(self):
        """Displays executive company dashboard."""
        tools = self.editor.load_and_parse_all_tools()
        health = self.sre.run_health_check(self.dist_dir)
        
        queue_count = 0
        queue_file = os.path.join(self.workspace_root, "data", "social_queue.json")
        if os.path.exists(queue_file):
            try:
                with open(queue_file, "r", encoding="utf-8") as f:
                    queue_count = len(json.load(f))
            except Exception:
                pass

        print("\n" + "="*65)
        print("  RUNTIMEZERO (runtimezero.dev) - GHOST FOUNDER DAC DASHBOARD")
        print("="*65)
        print(f"  * Platform URL:       http://localhost:{PORT}")
        print(f"  * Active Tools:       {len(tools)} Systems Simulators")
        print(f"  * SRE Health Status:  {health['status']}")
        print(f"  * AdSense Readiness:  {'READY (DART & GDPR Disclosed)' if health['checks']['adsense_ready'] else 'PENDING'}")
        print(f"  * SEO Architecture:   XML Sitemap + RSS + JSON-LD Active")
        print(f"  * Growth Queue:       {queue_count} Syndication Items Pending")
        print(f"  * Sentinel Watchdog:  ACTIVE (Cycles: {self.sentinel.total_cycles} | Heals: {self.sentinel.auto_heals_executed})")
        print(f"  * System Integrity:   {self.sentinel.last_status}")
        print("="*65 + "\n")

    def show_sentinel(self):
        """Displays detailed self-healing telemetry and recent incidents."""
        print("\n" + "="*65)
        print("  RUNTIMEZERO - AUTONOMOUS SELF-HEALING SENTINEL TELEMETRY")
        print("="*65)
        print(f"  * Sentinel Status:     {self.sentinel.last_status}")
        print(f"  * Total Patrol Cycles: {self.sentinel.total_cycles}")
        print(f"  * Anomalies Detected:  {self.sentinel.anomalies_detected}")
        print(f"  * Auto-Heals Executed: {self.sentinel.auto_heals_executed}")
        print(f"  * Inspection Interval: Every {self.sentinel.check_interval}s")
        print(f"  * Ledger File:         data/autonomous_audit_ledger.json")
        print("="*65)
        if self.sentinel.recent_incidents:
            print("\nRecent Autonomous Incidents & Self-Heal Actions:")
            for inc in self.sentinel.recent_incidents[-5:]:
                print(f"  [{inc['timestamp']}] {inc['type']} -> {inc['action_taken']}")
        else:
            print("  Zero incidents detected. System running with 100% autonomous stability.")
        print()

    def show_syndication(self):
        """Displays pending syndication items from data/social_queue.json."""
        queue_file = os.path.join(self.workspace_root, "data", "social_queue.json")
        if not os.path.exists(queue_file):
            print("[GROWTH] No syndication items in queue.")
            return

        with open(queue_file, "r", encoding="utf-8") as f:
            queue = json.load(f)

        print(f"\n[GROWTH] Found {len(queue)} items ready for syndication:")
        for idx, item in enumerate(queue[:6], 1):
            plat = item.get("platform", "").upper()
            target = item.get("target") or item.get("handle") or ""
            title = item.get("title") or (item.get("thread", [""])[0][:45] + "...")
            print(f"  {idx}. [{plat} -> {target}] {title}")
        if len(queue) > 6:
            print(f"  ... and {len(queue) - 6} more items in data/social_queue.json")
        print()

def main():
    print(r"""
  ____             _   _                  ___             
 |  _ \ _   _ _ __ | |_(_)_ __ ___   ___  |__ / ___ _ __ ___  
 | |_) | | | | '_ \| __| | '_ ` _ \ / _ \   |_ \/ _ \ '__/ _ \ 
 |  _ <| |_| | | | | |_| | | | | | |  __/  ___) | __/ | | (_) |
 |_| \_\\__,_|_| |_|\__|_|_| |_| |_|\___| |____/ \___|_|  \___/ 
      Autonomous Multi-Agent Digital Company (DAC) Engine
    """)

    dac = RuntimeZeroDAC()

    # 1. Initial Site Compilation
    dac.run_autonomous_cycle()

    # 2. Start Live Multi-Threaded HTTP Server
    dac.server_controller.start()
    time.sleep(0.5)

    # 3. Start 24/7 Continuous Self-Healing Sentinel Watchdog
    dac.sentinel.start_sentinel_thread()

    # 4. Start 24/7 Autonomous Background Scheduler (Growth & Company Ledger)
    dac.start_scheduler_thread(interval_seconds=3600)

    # 5. Display Executive Status
    dac.show_status()

    print("[CONSOLE] Interactive Command Console Active.")
    print("Commands: [status] [sentinel] [build] [syndicate] [help] [exit]")

    # Check if running interactively or in headless environment
    if not sys.stdin.isatty():
        print("[SYSTEM] Running in non-interactive background daemon mode. Press Ctrl+C to terminate.")
        try:
            while True:
                time.sleep(3600)
        except KeyboardInterrupt:
            print("\n[SYSTEM] Terminating daemon cleanly.")
            dac.server_controller.stop()
            dac.sentinel.stop()
            return

    # Interactive loop
    while True:
        try:
            cmd = input("runtimezero> ").strip().lower()
            if not cmd:
                continue
            if cmd in ["exit", "quit", "q"]:
                print("[SYSTEM] Shutting down RuntimeZero DAC...")
                dac.server_controller.stop()
                dac.sentinel.stop()
                break
            elif cmd == "status":
                dac.show_status()
            elif cmd == "sentinel":
                dac.show_sentinel()
            elif cmd == "build":
                dac.run_autonomous_cycle()
            elif cmd == "syndicate":
                dac.show_syndication()
            elif cmd == "help":
                print("\nAvailable Commands:")
                print("  status    - View live executive dashboard & SRE health")
                print("  sentinel  - View 24/7 self-healing watchdog metrics & auto-repairs")
                print("  build     - Trigger full static site recompilation & audit")
                print("  syndicate - View Reddit/Twitter syndication queue")
                print("  exit      - Terminate server and background workers\n")
            else:
                print(f"Unknown command: '{cmd}'. Type 'help' for options.")
        except (KeyboardInterrupt, EOFError):
            print("\n[SYSTEM] Exiting cleanly.")
            dac.server_controller.stop()
            dac.sentinel.stop()
            break

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ["--cron", "--cycle", "-c"]:
        dac = RuntimeZeroDAC()
        dac.run_autonomous_cycle()
        sys.exit(0)
    main()
