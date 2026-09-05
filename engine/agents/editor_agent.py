"""
RuntimeZero - Autonomous Editor-in-Chief Agent
Reviews, enriches, and formats 1,500+ word engineering post-mortems and technical articles.
"""

import os
import markdown
import frontmatter

class EditorAgent:
    def __init__(self, workspace_root):
        self.workspace_root = workspace_root
        self.tools_dir = os.path.join(workspace_root, 'content', 'tools')

    def load_and_parse_all_tools(self):
        """Loads and parses all Markdown tools into structured dictionaries with rendered HTML."""
        tools = []
        if not os.path.exists(self.tools_dir):
            return tools

        for fname in os.listdir(self.tools_dir):
            if fname.endswith('.md'):
                fpath = os.path.join(self.tools_dir, fname)
                with open(fpath, 'r', encoding='utf-8') as f:
                    post = frontmatter.load(f)

                html_content = markdown.markdown(
                    post.content,
                    extensions=['extra', 'codehilite', 'tables', 'fenced_code']
                )

                tool_data = {
                    "slug": post.get('slug', fname[:-3]),
                    "title": post.get('title', 'Untitled Simulator'),
                    "category": post.get('category', 'DevOps / Systems'),
                    "subtitle": post.get('subtitle', ''),
                    "meta_description": post.get('meta_description', ''),
                    "article_headline": post.get('article_headline', post.get('title')),
                    "date_published": post.get('date_published', '2026-09-01'),
                    "date_modified": post.get('date_modified', '2026-09-05'),
                    "faqs": post.get('faqs', []),
                    "article_html": html_content,
                    "raw_content": post.content
                }
                tools.append(tool_data)

        # Sort alphabetically by title
        tools.sort(key=lambda x: x['title'])
        return tools
