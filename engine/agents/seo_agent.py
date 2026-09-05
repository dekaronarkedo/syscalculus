"""
SysCalculus - Autonomous SEO Department Agent
Manages JSON-LD Structured Data, XML Sitemaps, Internal PageRank Graph, and High-CPC Keyword Auditing.
"""

import os
import json
import xml.etree.ElementTree as ET
from datetime import datetime

class SeoAgent:
    def __init__(self, workspace_root):
        self.workspace_root = workspace_root
        self.content_dir = os.path.join(workspace_root, 'content', 'tools')
        self.high_cpc_keywords = [
            "database connection pool", "postgresql deadlock", "hikaricp sizing",
            "aws egress cost", "cloudflare r2", "aws nat gateway cost",
            "log sanitizer", "air-gapped", "web crypto redactor",
            "crontab visualizer", "thundering herd problem", "systemd timer",
            "docker compose converter", "hardened docker", "rootless container",
            "llm vram calculator", "vllm kv cache", "gpu vram sizer", "llama 3 70b"
        ]

    def audit_keyword_coverage(self, tools_data):
        """Audits high-CPC keyword density and semantic placement across all tools."""
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "tools_audited": len(tools_data),
            "keyword_scores": {}
        }
        for tool in tools_data:
            content = (tool.get('title', '') + ' ' + 
                       tool.get('meta_description', '') + ' ' + 
                       tool.get('raw_content', '')).lower()
            matched = [kw for kw in self.high_cpc_keywords if kw in content]
            density = round((len(matched) / len(self.high_cpc_keywords)) * 100, 1)
            report["keyword_scores"][tool.get('slug')] = {
                "matched_keywords": matched,
                "coverage_score": f"{density}%"
            }
        return report

    def generate_sitemap_xml(self, tools_data, base_url="https://syscalculus.dev"):
        """Generates Google-compliant XML sitemap."""
        urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

        # Static core routes
        core_pages = [
            ("/", "1.0", "daily"),
            ("/about.html", "0.7", "monthly"),
            ("/privacy.html", "0.5", "monthly"),
        ]
        now_str = datetime.utcnow().strftime("%Y-%m-%d")

        for path, priority, freq in core_pages:
            url_elem = ET.SubElement(urlset, "url")
            ET.SubElement(url_elem, "loc").text = f"{base_url}{path}"
            ET.SubElement(url_elem, "lastmod").text = now_str
            ET.SubElement(url_elem, "changefreq").text = freq
            ET.SubElement(url_elem, "priority").text = priority

        # Dynamic tool routes
        for tool in tools_data:
            url_elem = ET.SubElement(urlset, "url")
            ET.SubElement(url_elem, "loc").text = f"{base_url}/tools/{tool.get('slug')}.html"
            ET.SubElement(url_elem, "lastmod").text = tool.get('date_modified', now_str)
            ET.SubElement(url_elem, "changefreq").text = "weekly"
            ET.SubElement(url_elem, "priority").text = "0.9"

        tree = ET.ElementTree(urlset)
        ET.indent(tree, space="  ", level=0)
        return ET.tostring(urlset, encoding="utf-8", method="xml").decode("utf-8")

    def generate_robots_txt(self, base_url="https://syscalculus.dev"):
        """Generates robots.txt with sitemap reference."""
        return f"""User-agent: *
Allow: /

Sitemap: {base_url}/sitemap.xml
"""

    def generate_rss_xml(self, tools_data, base_url="https://syscalculus.dev"):
        """Generates RSS 2.0 Feed for developer syndication."""
        rss = ET.Element("rss", version="2.0")
        channel = ET.SubElement(rss, "channel")
        ET.SubElement(channel, "title").text = "SysCalculus | Air-Gapped Systems Simulators"
        ET.SubElement(channel, "link").text = base_url
        ET.SubElement(channel, "description").text = "Zero-server-latency visual systems simulators and post-mortems for cloud architects."
        ET.SubElement(channel, "language").text = "en-us"

        for tool in tools_data:
            item = ET.SubElement(channel, "item")
            ET.SubElement(item, "title").text = tool.get('title', '')
            ET.SubElement(item, "link").text = f"{base_url}/tools/{tool.get('slug')}.html"
            ET.SubElement(item, "description").text = tool.get('meta_description', '')
            ET.SubElement(item, "guid").text = f"{base_url}/tools/{tool.get('slug')}.html"
            ET.SubElement(item, "pubDate").text = datetime.utcnow().strftime("%a, %d %b %Y 00:00:00 GMT")

        tree = ET.ElementTree(rss)
        ET.indent(tree, space="  ", level=0)
        return ET.tostring(rss, encoding="utf-8", method="xml").decode("utf-8")

    def run_seo_audit(self, tools_data, dist_dir):
        """Executes full SEO compilation and generates sitemap, robots, and audit reports."""
        os.makedirs(dist_dir, exist_ok=True)
        sitemap_xml = self.generate_sitemap_xml(tools_data)
        with open(os.path.join(dist_dir, "sitemap.xml"), "w", encoding="utf-8") as f:
            f.write(sitemap_xml)

        robots_txt = self.generate_robots_txt()
        with open(os.path.join(dist_dir, "robots.txt"), "w", encoding="utf-8") as f:
            f.write(robots_txt)

        rss_xml = self.generate_rss_xml(tools_data)
        with open(os.path.join(dist_dir, "rss.xml"), "w", encoding="utf-8") as f:
            f.write(rss_xml)

        audit_report = self.audit_keyword_coverage(tools_data)
        audit_path = os.path.join(self.workspace_root, "data", "seo_audit_report.json")
        with open(audit_path, "w", encoding="utf-8") as f:
            json.dump(audit_report, f, indent=2)

        return audit_report
