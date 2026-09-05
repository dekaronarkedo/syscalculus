"""
SysCalculus - Master Static Site Generator (SSG) Compiler
Compiles Markdown & Jinja2 templates into a high-performance, SEO-optimized production bundle in dist/
"""

import os
import shutil
from jinja2 import Environment, FileSystemLoader

from engine.agents.editor_agent import EditorAgent
from engine.agents.seo_agent import SeoAgent
from engine.agents.growth_agent import GrowthAgent
from engine.agents.sre_agent import SreAgent

def build_site():
    workspace_root = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(workspace_root, "dist")
    templates_dir = os.path.join(workspace_root, "templates")
    static_dir = os.path.join(workspace_root, "static")

    print("[BUILD] Initializing SysCalculus Production Compiler...")

    # Ensure dist exists without crashing on Windows file locks
    if os.path.exists(dist_dir):
        try:
            shutil.rmtree(dist_dir)
        except Exception:
            pass
    os.makedirs(dist_dir, exist_ok=True)
    os.makedirs(os.path.join(dist_dir, "tools"), exist_ok=True)

    # Initialize Autonomous Agents
    editor = EditorAgent(workspace_root)
    seo = SeoAgent(workspace_root)
    growth = GrowthAgent(workspace_root)
    sre = SreAgent(workspace_root)

    # 1. Parse all tools and articles
    tools = editor.load_and_parse_all_tools()
    print(f"[BUILD] Loaded {len(tools)} production systems tools.")

    # 2. Setup Jinja2 Environment
    env = Environment(loader=FileSystemLoader(templates_dir), autoescape=False)

    # Optional AdSense Pub ID (defaults to empty/fallback sponsor unless configured)
    adsense_pub_id = os.environ.get("ADSENSE_PUB_ID", "")

    # Read static assets for guaranteed self-contained inline loading (works on file:/// and http://)
    css_path = os.path.join(static_dir, "css", "syscalculus.css")
    inline_css = ""
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            inline_css = f.read()

    simulators_js_path = os.path.join(static_dir, "js", "simulators.js")
    inline_simulators_js = ""
    if os.path.exists(simulators_js_path):
        with open(simulators_js_path, "r", encoding="utf-8") as f:
            inline_simulators_js = f.read()

    app_js_path = os.path.join(static_dir, "js", "app.js")
    inline_app_js = ""
    if os.path.exists(app_js_path):
        with open(app_js_path, "r", encoding="utf-8") as f:
            inline_app_js = f.read()

    # 3. Render Homepage (dist/index.html)
    index_template = env.get_template("index.html")
    rendered_index = index_template.render(
        tools=tools,
        adsense_pub_id=adsense_pub_id,
        inline_css=inline_css,
        inline_simulators_js=inline_simulators_js,
        inline_app_js=inline_app_js
    )
    with open(os.path.join(dist_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(rendered_index)
    print("[BUILD] Compiled dist/index.html")

    # 4. Render Individual Tool Pages (dist/tools/<slug>.html)
    tool_template = env.get_template("tool.html")
    for tool in tools:
        rendered_tool = tool_template.render(
            tool=tool,
            tools=tools,
            adsense_pub_id=adsense_pub_id,
            inline_css=inline_css,
            inline_simulators_js=inline_simulators_js,
            inline_app_js=inline_app_js
        )
        tool_out_path = os.path.join(dist_dir, "tools", f"{tool['slug']}.html")
        with open(tool_out_path, "w", encoding="utf-8") as f:
            f.write(rendered_tool)
    print(f"[BUILD] Compiled {len(tools)} tool workbenches in dist/tools/")

    # 5. Render Legal & Compliance Pages (Privacy & About)
    privacy_template = env.get_template("privacy.html")
    rendered_privacy = privacy_template.render(
        adsense_pub_id=adsense_pub_id,
        inline_css=inline_css,
        inline_simulators_js=inline_simulators_js,
        inline_app_js=inline_app_js
    )
    with open(os.path.join(dist_dir, "privacy.html"), "w", encoding="utf-8") as f:
        f.write(rendered_privacy)
    print("[BUILD] Compiled dist/privacy.html (AdSense/GDPR/CCPA Compliant)")

    about_template = env.get_template("about.html")
    rendered_about = about_template.render(
        adsense_pub_id=adsense_pub_id,
        inline_css=inline_css,
        inline_simulators_js=inline_simulators_js,
        inline_app_js=inline_app_js
    )
    with open(os.path.join(dist_dir, "about.html"), "w", encoding="utf-8") as f:
        f.write(rendered_about)
    print("[BUILD] Compiled dist/about.html")

    # 6. Copy Static Assets (CSS, JS, Images)
    dist_static = os.path.join(dist_dir, "static")
    if os.path.exists(static_dir):
        shutil.copytree(static_dir, dist_static, dirs_exist_ok=True)
        print("[BUILD] Copied static assets to dist/static/")

    # 6b. Copy Cloudflare Edge Config (_headers, _redirects)
    for edge_cfg in ["_headers", "_redirects"]:
        src_cfg = os.path.join(static_dir, edge_cfg)
        if os.path.exists(src_cfg):
            shutil.copyfile(src_cfg, os.path.join(dist_dir, edge_cfg))
            print(f"[BUILD] Deployed Cloudflare Edge config: {edge_cfg}")

    # 7. SEO Agent: Generate Sitemap, Robots, RSS, and Keyword Audit
    seo_audit = seo.run_seo_audit(tools, dist_dir)
    print("[BUILD] SEO Agent generated sitemap.xml, robots.txt, and rss.xml")

    # 8. Growth Agent: Generate Reddit, Twitter & Dev.to Syndication Queues
    social_res = growth.sync_all_social_queues(tools)
    print(f"[BUILD] Growth Agent synced social queues: {social_res['total_queued']} items ready in data/social_queue.json")

    # 9. SRE Agent: Validate Build Health & Log to Ledger
    health = sre.run_health_check(dist_dir)
    sre.log_event("BUILD_COMPLETED", {
        "tools_compiled": len(tools),
        "status": health["status"]
    })
    print(f"[BUILD] SRE Health Status: {health['status']} - Build Completed Successfully.")

if __name__ == "__main__":
    build_site()
