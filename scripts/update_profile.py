"""Refresh public GitHub metadata and render repository-owned profile assets."""

import argparse
from collections import Counter
from datetime import datetime, timezone
from html import escape
import json
from pathlib import Path
import re
import subprocess
import time
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OWNER = "sjkncs"
START = "<!-- activity:start -->"
END = "<!-- activity:end -->"
EMOJI = re.compile("[\U0001f000-\U0001faff\u2600-\u27bf\ufe0f\u200d]")


def api(endpoint):
    for attempt in range(3):
        try:
            result = subprocess.run(
                ["gh", "api", endpoint], check=True, capture_output=True,
                encoding="utf-8", timeout=60,
            )
            return json.loads(result.stdout)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            if attempt == 2:
                raise RuntimeError(f"Public GitHub API unavailable after three attempts: {endpoint}") from None
            time.sleep(attempt + 1)


def collect(fetch=api, today=None, featured_names=()):
    user = fetch(f"users/{OWNER}")
    repos = []
    for page in range(1, 101):
        batch = fetch(f"users/{OWNER}/repos?type=owner&per_page=100&page={page}")
        if not isinstance(batch, list):
            raise ValueError("Repository endpoint did not return a list")
        repos.extend(batch)
        if len(batch) < 100:
            break
    else:
        raise ValueError("Repository pagination did not terminate")
    public = [r for r in repos if not r["private"]]
    if len(public) != user["public_repos"]:
        raise ValueError("Incomplete public repository collection; retry the refresh")
    if len({r["name"] for r in public}) != len(public):
        raise ValueError("Duplicate repositories in paginated response")
    for repo in public:
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", repo["name"]):
            raise ValueError("Unsafe repository name")
        if repo["owner"]["login"].lower() != OWNER:
            raise ValueError("Unexpected repository owner")
        if repo["html_url"] != f"https://github.com/{OWNER}/{repo['name']}":
            raise ValueError("Unexpected repository URL")
    nonfork = [r for r in public if not r["fork"]]
    by_name = {r["name"]: r for r in nonfork}
    if len(set(featured_names)) != len(featured_names) or any(name not in by_name for name in featured_names):
        raise ValueError("Featured repositories must be unique public non-fork repositories")
    languages = Counter(r["language"] for r in nonfork if r["language"])
    recent = sorted(
        (r for r in nonfork if not r["archived"] and r["name"] != OWNER and r["pushed_at"]),
        key=lambda r: (r["pushed_at"], r["name"]), reverse=True,
    )[:5]
    return {
        "owner": OWNER,
        "collected_on": today or datetime.now(timezone.utc).date().isoformat(),
        "source": f"https://api.github.com/users/{OWNER}",
        "repositories_source": f"https://api.github.com/users/{OWNER}/repos?type=owner",
        "public_repositories": len(public),
        "nonfork_repositories": len(nonfork),
        "forks": len(public) - len(nonfork),
        "nonfork_stars": sum(r["stargazers_count"] for r in nonfork),
        "without_primary_language": sum(r["language"] is None for r in nonfork),
        "primary_languages": dict(sorted(languages.items(), key=lambda p: (-p[1], p[0]))),
        "recent_pushes": [
            {"name": r["name"], "url": r["html_url"], "pushed_on": r["pushed_at"][:10]}
            for r in recent
        ],
        "featured_repositories": [
            {key: by_name[name][key] for key in ("name", "html_url", "language", "stargazers_count", "pushed_at")}
            for name in featured_names
        ],
    }


def activity_markdown(data):
    lines = [
        f"Snapshot / 快照：**{data['collected_on']} UTC** · 每日尝试同步。",
        "", "Recent pushes / 最近推送：", "",
    ]
    lines.extend(f"- [{r['name']}]({r['url']}) · {r['pushed_on']}" for r in data["recent_pushes"][:3])
    lines.extend([
        "", "<details>", "<summary>Full data & methodology / 完整数据与统计口径</summary>",
        "", "| Metric / 指标 | Value / 数值 |", "| :--- | ---: |",
        f"| Public repositories / 公开仓库（含 fork） | {data['public_repositories']} |",
        f"| Non-fork repositories / 非 fork 仓库 | {data['nonfork_repositories']} |",
        f"| Forks / 分叉仓库 | {data['forks']} |",
        f"| Stars on non-fork repositories / 非 fork 仓库获星总数 | {data['nonfork_stars']} |",
    ])
    languages = "; ".join(f"{name}: {count}" for name, count in data["primary_languages"].items())
    lines.extend([
        "", f"Primary language by repository / 非 fork 仓库主语言计数：{languages or 'None'}。",
        f"No primary language reported / 未报告主语言：{data['without_primary_language']}。",
        "", "Language counts describe repositories, not code-byte percentages or proficiency. Non-fork does not establish original authorship. / 主语言计数不是代码占比或熟练度，非 fork 也不代表全部原创。",
        "", "最近推送仅包含非 fork、非归档的公开仓库，不含主页仓库。卡片的星数、主语言与推送日期来自同一快照，不代表质量或上线状态。",
        "", "[Snapshot data / 快照数据](data/profile.json) · [Refresh workflow / 同步状态](https://github.com/sjkncs/sjkncs/actions/workflows/profile.yml)",
        "", "</details>",
    ])
    return "\n".join(lines)


def replace_activity(readme, block):
    if readme.count(START) != 1 or readme.count(END) != 1:
        raise ValueError("README must contain exactly one activity marker pair")
    before, rest = readme.split(START)
    _, after = rest.split(END)
    return before + START + "\n\n" + block + "\n\n" + END + after


def activity_svg(data):
    metrics = [
        ("PUBLIC REPOS", data["public_repositories"]),
        ("NON-FORK REPOS", data["nonfork_repositories"]),
        ("STARS / NON-FORK", data["nonfork_stars"]),
        ("FORKS", data["forks"]),
    ]
    langs = list(data["primary_languages"].items())[:5]
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 252" role="img" aria-labelledby="title desc">',
        '<title id="title">Public GitHub repository snapshot</title>',
        f'<desc id="desc">Collected {escape(data["collected_on"])} UTC. '
        + escape(". ".join(f"{label}: {value}" for label, value in metrics)) + '.</desc>',
        '<rect width="960" height="252" rx="8" fill="#f1f5f1"/>',
        '<g font-family="Verdana, sans-serif" fill="#153f39">',
        '<text x="30" y="34" font-size="12" letter-spacing="1.5">PUBLIC REPOSITORY SNAPSHOT</text>',
        f'<text x="930" y="34" text-anchor="end" font-size="11">{escape(data["collected_on"])} / UTC</text>',
    ]
    for i, (label, value) in enumerate(metrics):
        x = 30 + i * 235
        parts.extend([
            f'<text x="{x}" y="98" font-family="Georgia, serif" font-size="44">{value}</text>',
            f'<text x="{x}" y="126" font-size="10" fill="#526a63">{label}</text>',
        ])
    parts.extend([
        '<path d="M30 151H930" stroke="#d0dcd3"/>',
        '<text x="30" y="179" font-size="12">PRIMARY LANGUAGE / NON-FORK REPOSITORY COUNTS</text>',
    ])
    maximum = max((count for _, count in langs), default=1)
    for i, (name, count) in enumerate(langs):
        x = 30 + i * 182
        parts.extend([
            f'<text x="{x}" y="204" font-size="12">{escape(name)} / {count}</text>',
            f'<rect x="{x}" y="215" width="152" height="5" rx="2" fill="#dce6df"/>',
            f'<rect x="{x}" y="215" width="{152 * count / maximum:.1f}" height="5" rx="2" fill="#28685c"/>',
        ])
    parts.extend([
        '<text x="30" y="242" font-size="9" fill="#526a63">TOP 5 PRIMARY LANGUAGES / REPOSITORY COUNTS, NOT PROFICIENCY</text>',
        '</g>', '</svg>', '',
    ])
    return "\n".join(parts)


def project_svg(project, metadata):
    if metadata["name"] != project["name"] or not re.fullmatch(r"#[0-9a-fA-F]{6}", project["accent"]):
        raise ValueError("Invalid featured project metadata")
    for field, limit in (("title", 24), ("category", 30), ("en", 42), ("zh", 25), ("stack", 30)):
        if len(project[field]) > limit:
            raise ValueError(f"Featured project text exceeds its layout budget: {field}")
    icon_paths = {
        "code": "M8 4l-6 8 6 8M16 4l6 8-6 8M14 3l-4 18",
        "book": "M12 5v16M12 5C9 2 4 2 2 3v16c3-1 7-1 10 2 3-3 7-3 10-2V3c-2-1-7-1-10 2Z",
        "map": "M2 5l7-3 6 3 7-3v17l-7 3-6-3-7 3ZM9 2v17M15 5v17",
        "terminal": "M3 3h18v18H3ZM6 8l4 4-4 4M13 16h5",
    }
    if project["icon"] not in icon_paths:
        raise ValueError("Unknown featured project icon")
    label = escape(project["title"])
    accent = project["accent"]
    stars = int(metadata["stargazers_count"])
    star_label = f"{stars} {'star' if stars == 1 else 'stars'}"
    pushed = escape(metadata["pushed_at"][:10])
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="360" height="194" viewBox="0 0 360 194" role="img" aria-labelledby="title desc">
<title id="title">{label}</title>
<desc id="desc">{escape(project["en"])}. {escape(project["zh"])}. {star_label}. Last push {pushed}.</desc>
<style>.bg{{fill:#fff;stroke:#d9e0e7}}.ink{{fill:#233044}}.muted{{fill:#526479}}.rule{{stroke:#e2e7ed}}@media(prefers-color-scheme:dark){{.bg{{fill:#161b22;stroke:#30363d}}.ink{{fill:#eef2f6}}.muted{{fill:#b2bbc6}}.rule{{stroke:#30363d}}}}</style>
<rect class="bg" x="1" y="1" width="358" height="192" rx="8"/>
<path d="M8 2H352" stroke="{accent}" stroke-width="3"/>
<g transform="translate(22 20)" fill="none" stroke="{accent}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="{icon_paths[project["icon"]]}"/></g>
<g font-family="Verdana, Microsoft YaHei, sans-serif">
<text class="muted" x="57" y="35" font-size="9">{escape(project["category"])}</text>
<text class="ink" x="22" y="72" font-size="22" font-weight="600">{label}</text>
<text class="muted" x="22" y="99" font-size="11">{escape(project["en"])}</text>
<text class="ink" x="22" y="122" font-size="12">{escape(project["zh"])}</text>
<text x="22" y="147" font-size="10" fill="{accent}">{escape(project["stack"])}</text>
<path class="rule" d="M22 158H338"/>
<text class="muted" x="22" y="179" font-size="10">{star_label}</text>
<text class="muted" x="338" y="179" text-anchor="end" font-size="10">Pushed {pushed}</text>
</g></svg>
'''


def validate_svg(content):
    root = ET.fromstring(content)
    if root.tag != "{http://www.w3.org/2000/svg}svg" or "viewBox" not in root.attrib:
        raise ValueError("Expected a scalable SVG document")
    for node in root.iter():
        if node.tag.rsplit("}", 1)[-1] in {"script", "foreignObject", "image"}:
            raise ValueError("SVG must be self-contained and script-free")
        for key, value in node.attrib.items():
            if key.startswith("on") or "https:" in value or "http:" in value:
                raise ValueError("External resource or executable SVG attribute")
    if EMOJI.search(content):
        raise ValueError("Emoji found in profile asset")


def outputs(data, readme, featured=None):
    updated = replace_activity(readme, activity_markdown(data))
    if EMOJI.search(updated):
        raise ValueError("Emoji found in profile README")
    svg = activity_svg(data)
    validate_svg(svg)
    rendered = {
        ROOT / "data/profile.json": json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        ROOT / "assets/activity.svg": svg,
        ROOT / "README.md": updated,
    }
    featured = featured if featured is not None else json.loads((ROOT / "data/featured.json").read_text(encoding="utf-8"))
    by_name = {repo["name"]: repo for repo in data.get("featured_repositories", [])}
    for project in featured:
        if project["name"] not in by_name:
            raise ValueError("Missing featured repository metadata; refresh the snapshot")
        svg = project_svg(project, by_name[project["name"]])
        validate_svg(svg)
        rendered[ROOT / "assets/projects" / f"{project['name']}.svg"] = svg
    return rendered


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate saved artifacts without API requests")
    args = parser.parse_args()
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    featured = json.loads((ROOT / "data/featured.json").read_text(encoding="utf-8"))
    data = json.loads((ROOT / "data/profile.json").read_text(encoding="utf-8")) if args.check else collect(featured_names=[p["name"] for p in featured])
    rendered = outputs(data, readme)
    for asset in (ROOT / "assets").rglob("*.svg"):
        validate_svg(asset.read_text(encoding="utf-8"))
    for src in re.findall(r'<img[^>]+src="([^"]+)"', readme):
        owned_prefix = f"https://raw.githubusercontent.com/{OWNER}/{OWNER}/main/"
        if src.startswith(owned_prefix):
            asset = ROOT / src.removeprefix(owned_prefix)
            if (not asset.is_file() and asset not in rendered) or not asset.resolve().is_relative_to((ROOT / "assets").resolve()):
                raise ValueError("Missing or unexpected owned SVG asset")
            continue
        if src.startswith("https://"):
            if src != f"https://raw.githubusercontent.com/{OWNER}/{OWNER}/output/github-snake.svg":
                raise ValueError("Unexpected remote image dependency")
        elif not (ROOT / src).is_file() and src != "assets/activity.svg":
            raise ValueError(f"Missing profile image: {src}")
    if args.check:
        for path, content in rendered.items():
            if path.read_text(encoding="utf-8") != content:
                raise ValueError(f"Generated artifact is out of sync: {path.name}")
        print("PASS: snapshot, SVGs, README synchronization, image paths and emoji check")
    else:
        # Finish all API collection and rendering before replacing any saved artifact.
        for path, content in rendered.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
        print(f"Updated {data['collected_on']}: {data['public_repositories']} public repositories")


if __name__ == "__main__":
    main()
