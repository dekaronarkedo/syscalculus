"""
SysCalculus - Autonomous SRE & Site Reliability Department Agent
Monitors system health, page build verification, AdSense compliance, and updates the Company Ledger.
"""

import os
import json
import time
from datetime import datetime

class SreAgent:
    def __init__(self, workspace_root):
        self.workspace_root = workspace_root
        self.ledger_file = os.path.join(workspace_root, 'data', 'company_ledger.json')

    def log_event(self, event_type, details):
        """Appends a structured audit event to the company ledger."""
        ledger = []
        if os.path.exists(self.ledger_file):
            try:
                with open(self.ledger_file, 'r', encoding='utf-8') as f:
                    ledger = json.load(f)
            except Exception:
                ledger = []

        entry = {
            "id": f"evt_{int(time.time()*1000)}",
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "details": details
        }
        ledger.append(entry)

        # Retain last 500 events
        if len(ledger) > 500:
            ledger = ledger[-500:]

        os.makedirs(os.path.dirname(self.ledger_file), exist_ok=True)
        with open(self.ledger_file, 'w', encoding='utf-8') as f:
            json.dump(ledger, f, indent=2)

        return entry

    def run_health_check(self, dist_dir):
        """Audits generated static build assets and verifies core requirements."""
        checks = {
            "dist_exists": os.path.exists(dist_dir),
            "index_exists": os.path.exists(os.path.join(dist_dir, "index.html")),
            "privacy_exists": os.path.exists(os.path.join(dist_dir, "privacy.html")),
            "about_exists": os.path.exists(os.path.join(dist_dir, "about.html")),
            "sitemap_exists": os.path.exists(os.path.join(dist_dir, "sitemap.xml")),
            "robots_exists": os.path.exists(os.path.join(dist_dir, "robots.txt")),
            "tools_count": 0,
            "broken_links": [],
            "adsense_ready": False
        }

        tools_dist = os.path.join(dist_dir, "tools")
        if os.path.exists(tools_dist):
            checks["tools_count"] = len([f for f in os.listdir(tools_dist) if f.endswith('.html')])

        # Check privacy for DoubleClick DART
        privacy_path = os.path.join(dist_dir, "privacy.html")
        if os.path.exists(privacy_path):
            with open(privacy_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if "DART" in content and "GDPR" in content and "CCPA" in content:
                    checks["adsense_ready"] = True

        status = "HEALTHY" if (checks["dist_exists"] and checks["index_exists"] and checks["adsense_ready"]) else "DEGRADED"

        self.log_event("SRE_HEALTH_CHECK", {
            "status": status,
            "checks": checks
        })

        return {
            "status": status,
            "checks": checks
        }
