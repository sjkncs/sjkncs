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


def collect(fetch=api, today=None):
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
    }


def activity_markdown(data):
    lines = [
        f"Public GitHub metadata, collected **{data['collected_on']} (UTC)**. / 公开数据快照，每日尝试同步。",
        "", "| Metric / 指标 | Value / 数值 |", "| :--- | ---: |",
        f"| Public repositories / 公开仓库（含 fork） | {data['public_repositories']} |",
        f"| Non-fork repositories / 非 fork 仓库 | {data['nonfork_repositories']} |",
        f"| Forks / 分叉仓库 | {data['forks']} |",
        f"| Stars on non-fork repositories / 非 fork 仓库获星总数 | {data['nonfork_stars']} |",
        "", "Recent pushes / 最近推送（非 fork、非归档，不含主页仓库）：", "",
    ]
    lines.extend(f"- [{r['name']}]({r['url']}) · {r['pushed_on']}" for r in data["recent_pushes"])
    languages = "; ".join(f"{name}: {count}" for name, count in data["primary_languages"].items())
    lines.extend([
        "", f"Primary language by repository / 非 fork 仓库主语言计数：{languages or 'None'}。",
        f"No primary language reported / 未报告主语言：{data['without_primary_language']}。",
        "", "Language counts describe repositories, not code-byte percentages or proficiency. Non-fork does not establish original authorship. / 主语言计数不是代码占比或熟练度，非 fork 也不代表全部原创。",
        "", "[Snapshot data / 快照数据](data/profile.json) · [Refresh workflow / 同步状态](https://github.com/sjkncs/sjkncs/actions/workflows/profile.yml)",
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
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 410" role="img" aria-labelledby="title desc">',
        '<title id="title">Public GitHub repository snapshot</title>',
        f'<desc id="desc">Collected {escape(data["collected_on"])} UTC. '
        + escape(". ".join(f"{label}: {value}" for label, value in metrics)) + '.</desc>',
        '<rect width="960" height="410" rx="12" fill="#f1f5f1"/>',
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
        y = 207 + i * 30
        parts.extend([
            f'<text x="30" y="{y + 12}" font-size="12">{escape(name)}</text>',
            f'<rect x="206" y="{y}" width="650" height="16" rx="4" fill="#dce6df"/>',
            f'<rect x="206" y="{y}" width="{650 * count / maximum:.1f}" height="16" rx="4" fill="#28685c"/>',
            f'<text x="926" y="{y + 12}" text-anchor="end" font-size="12">{count}</text>',
        ])
    parts.extend([
        '<text x="30" y="387" font-size="10" fill="#526a63">TOP 5 PRIMARY LANGUAGES / COUNTS, NOT PROFICIENCY OR CODE-BYTE PERCENTAGES</text>',
        '</g>', '</svg>', '',
    ])
    return "\n".join(parts)


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


def outputs(data, readme):
    updated = replace_activity(readme, activity_markdown(data))
    if EMOJI.search(updated):
        raise ValueError("Emoji found in profile README")
    svg = activity_svg(data)
    validate_svg(svg)
    return {
        ROOT / "data/profile.json": json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        ROOT / "assets/activity.svg": svg,
        ROOT / "README.md": updated,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate saved artifacts without API requests")
    args = parser.parse_args()
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    data = json.loads((ROOT / "data/profile.json").read_text(encoding="utf-8")) if args.check else collect()
    rendered = outputs(data, readme)
    for asset in (ROOT / "assets").rglob("*.svg"):
        validate_svg(asset.read_text(encoding="utf-8"))
    for src in re.findall(r'<img[^>]+src="([^"]+)"', readme):
        owned_prefix = f"https://raw.githubusercontent.com/{OWNER}/{OWNER}/main/"
        if src.startswith(owned_prefix):
            asset = ROOT / src.removeprefix(owned_prefix)
            if not asset.is_file() or not asset.resolve().is_relative_to((ROOT / "assets").resolve()):
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
