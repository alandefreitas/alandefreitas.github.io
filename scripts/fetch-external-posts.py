#!/usr/bin/env python3
"""Mirror Alan's posts from the C++ Alliance blog into _posts/cppalliance/.

Reads the _posts folder of cppalliance/cppalliance.github.io (branch develop,
shallow sparse clone), keeps the posts whose front matter has `author-id: alan`,
and writes each one as a local post so readers stay on this site. The post
layout shows where and when it was first published (front matter
`original_url`, `original_site`). The Alliance site's custom Liquid blocks are
translated to plain HTML: `{% admonition %}` becomes a div.admonition and
`{% mermaid %}` a pre.mermaid (the layout loads Mermaid when `mermaid: true`).
Links between Alan's own posts point to the local copies. Everything else is
wrapped in {% raw %} so the Markdown is rendered as written.

Run it whenever a new post goes live on the Alliance site, then commit. The
folder _posts/cppalliance/ is wiped and rewritten on every run: never edit the
mirrored files by hand.
"""
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

REPO = "cppalliance/cppalliance.github.io"
BRANCH = "develop"
SITE = "cppalliance.org"
OUT_DIR = Path("_posts/cppalliance")
LOCAL_PERMALINK = "/blog/{y}/{m}/{d}/{slug}/"


def front_matter(text):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.S)
    if not m:
        return {}, text
    fm = {}
    for line in m.group(1).splitlines():
        k, sep, v = line.partition(":")
        if sep and not line.startswith(" "):
            fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm, m.group(2)


def slugify(title):
    s = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return s or "post"


def convert_blocks(body):
    def admonition(m):
        args = m.group(1).strip().split(" ", 1)
        kind = args[0] if args and args[0] else "note"
        title = args[1] if len(args) > 1 else {"warning": "Warning", "tip": "Tip"}.get(kind, "Note")
        cls = "admonition" + ("" if kind == "note" else f" admonition-{kind}")
        return (f'<div class="{cls}" markdown="1">\n<p class="admonition-title">{title}</p>\n\n'
                f"{m.group(2).strip()}\n\n</div>")

    body = re.sub(r"\{%\s*admonition(.*?)%\}(.*?)\{%\s*endadmonition\s*%\}", admonition, body, flags=re.S)
    body = re.sub(r"\{%\s*mermaid\s*%\}(.*?)\{%\s*endmermaid\s*%\}",
                  lambda m: f'<pre class="mermaid">\n{m.group(1).strip()}\n</pre>', body, flags=re.S)
    return body


def main():
    tmp = tempfile.mkdtemp(prefix="cppalliance-posts-")
    subprocess.run(["git", "clone", "--quiet", "--depth", "1", "--branch", BRANCH, "--filter=blob:none",
                    "--sparse", f"https://github.com/{REPO}.git", tmp], check=True)
    subprocess.run(["git", "-C", tmp, "sparse-checkout", "set", "--no-cone", "_posts"], check=True)

    posts = []
    for f in sorted(Path(tmp, "_posts").iterdir()):
        m = re.match(r"^(\d{4})-(\d{2})-(\d{2})-(.+)\.(md|markdown|html)$", f.name)
        if not m:
            continue
        fm, body = front_matter(f.read_text(encoding="utf-8", errors="replace"))
        if fm.get("author-id") != "alan":
            continue
        y, mo, d, name = m.group(1), m.group(2), m.group(3), m.group(4)
        cats = fm.get("categories", "").strip("[]").replace(",", " ").split()
        original_path = "/" + "/".join(p for p in [cats[0] if cats else "", y, mo, d, name + ".html"] if p)
        title = fm.get("title", name)
        slug = slugify(title)
        posts.append({
            "title": title, "y": y, "m": mo, "d": d, "slug": slug, "body": body,
            "original_path": original_path,
            "local_path": LOCAL_PERMALINK.format(y=y, m=mo, d=d, slug=slug),
        })
    shutil.rmtree(tmp, ignore_errors=True)

    link_map = {p["original_path"]: p["local_path"] for p in posts}

    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    for p in posts:
        body = convert_blocks(p["body"])
        for orig, local in link_map.items():
            body = body.replace(f"]({orig})", f"]({local})")
        body = re.sub(r"\]\((/[^)]*)\)", lambda m: f"](https://{SITE}{m.group(1)})", body)
        body = re.sub(r'src="(/[^"]*)"', lambda m: f'src="https://{SITE}{m.group(1)}"', body)
        mermaid = 'class="mermaid"' in body
        title = p["title"].replace('"', '\\"')
        out = OUT_DIR / f'{p["y"]}-{p["m"]}-{p["d"]}-{p["slug"]}.md'
        out.write_text(
            "---\n"
            "layout: post\n"
            f'title: "{title}"\n'
            f'date: {p["y"]}-{p["m"]}-{p["d"]}\n'
            f'original_url: https://{SITE}{p["original_path"]}\n'
            f"original_site: {SITE}\n"
            + ("mermaid: true\n" if mermaid else "")
            + "---\n"
            "{% raw %}\n" + body.strip() + "\n{% endraw %}\n",
            encoding="utf-8",
        )
        print(out, "<-", p["original_path"], file=sys.stderr)
    print(f"{len(posts)} posts mirrored into {OUT_DIR}/", file=sys.stderr)


if __name__ == "__main__":
    main()
