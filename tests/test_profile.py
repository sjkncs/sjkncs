import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch
import subprocess

SPEC = importlib.util.spec_from_file_location("profile", Path(__file__).resolve().parents[1] / "scripts/update_profile.py")
profile = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(profile)


def repo(name, **kwargs):
    return dict(name=name, owner={"login": "sjkncs"}, private=False, fork=False,
                archived=False, language="Python", stargazers_count=2,
                pushed_at="2026-10-13T12:00:00Z",
                html_url=f"https://github.com/sjkncs/{name}", **kwargs)


class ProfileTests(unittest.TestCase):
    def test_transient_api_failure_is_retried_with_a_bound(self):
        error = subprocess.CalledProcessError(1, ["gh", "api"])
        success = subprocess.CompletedProcess([], 0, stdout='{"ok": true}')
        with patch.object(profile.subprocess, "run", side_effect=[error, success]) as run, patch.object(profile.time, "sleep"):
            self.assertEqual(profile.api("users/sjkncs"), {"ok": True})
            self.assertEqual(run.call_count, 2)
        with patch.object(profile.subprocess, "run", side_effect=error) as run, patch.object(profile.time, "sleep"):
            with self.assertRaises(RuntimeError):
                profile.api("users/sjkncs")
            self.assertEqual(run.call_count, 3)

    def fetcher(self, pages, total):
        def fetch(endpoint):
            if "?" not in endpoint:
                return {"public_repos": total, "followers": 16}
            return pages[int(endpoint.rsplit("=", 1)[1]) - 1]
        return fetch

    def test_all_pages_collected(self):
        data = profile.collect(self.fetcher([[repo(f"r{i}") for i in range(100)], [repo("last")]], 101), "2026-10-13")
        self.assertEqual(data["public_repositories"], 101)
        self.assertEqual(data["nonfork_stars"], 202)

    def test_public_scope_and_recent_push_rules(self):
        rows = [repo("normal"), repo("fork"), repo("archived"), repo("sjkncs"), repo("private")]
        rows[1].update(fork=True, stargazers_count=999, language="Rust")
        rows[2].update(archived=True, language=None)
        rows[4].update(private=True, stargazers_count=999)
        data = profile.collect(self.fetcher([rows], 4), "2026-10-13")
        self.assertEqual(data["nonfork_repositories"], 3)
        self.assertEqual(data["nonfork_stars"], 6)
        self.assertEqual(data["primary_languages"], {"Python": 2})
        self.assertEqual(data["without_primary_language"], 1)
        self.assertEqual([r["name"] for r in data["recent_pushes"]], ["normal"])

    def test_incomplete_and_duplicate_responses_fail(self):
        for pages, count in [([[repo("one")]], 2), ([[repo("same"), repo("same")]], 2)]:
            with self.assertRaises(ValueError):
                profile.collect(self.fetcher(pages, count))

    def test_failed_second_page_produces_no_snapshot(self):
        def fetch(endpoint):
            if "?" not in endpoint:
                return {"public_repos": 101, "followers": 16}
            if endpoint.endswith("page=1"):
                return [repo(f"r{i}") for i in range(100)]
            raise RuntimeError("API unavailable")
        with self.assertRaises(RuntimeError):
            profile.collect(fetch)

    def test_featured_metadata_comes_from_public_nonfork_repositories(self):
        rows = [repo("selected"), repo("unrelated"), repo("fork")]
        rows[2]["fork"] = True
        data = profile.collect(self.fetcher([rows], 3), "2026-10-14", featured_names=["selected"])
        self.assertEqual(data["featured_repositories"][0]["name"], "selected")
        self.assertEqual(data["featured_repositories"][0]["stargazers_count"], 2)
        for names in (["missing"], ["fork"], ["selected", "selected"]):
            with self.assertRaises(ValueError):
                profile.collect(self.fetcher([rows], 3), featured_names=names)

    def test_featured_card_is_self_contained_and_layout_bounded(self):
        project = {"name": "selected", "title": "Project <&", "category": "RESEARCH", "accent": "#3178c6", "icon": "code",
                   "en": "Public source", "zh": "公开项目", "stack": "Python"}
        svg = profile.project_svg(project, repo("selected"))
        profile.validate_svg(svg)
        self.assertIn("Project &lt;&amp;", svg)
        self.assertIn("2026-10-13", svg)
        self.assertIn("2 stars", svg)
        self.assertIn("prefers-color-scheme:dark", svg)
        project["title"] = "x" * 25
        with self.assertRaises(ValueError):
            profile.project_svg(project, repo("selected"))

    def test_project_outputs_match_snapshot_and_missing_metadata_fails(self):
        project = {"name": "selected", "title": "Selected", "category": "TOOLS", "accent": "#3178c6", "icon": "terminal",
                   "en": "Public source", "zh": "公开项目", "stack": "Python"}
        data = profile.collect(self.fetcher([[repo("selected")]], 1), "2026-10-14", featured_names=["selected"])
        readme = profile.START + profile.END
        rendered = profile.outputs(data, readme, featured=[project])
        self.assertEqual(len(rendered), 4)
        self.assertIn("2 stars", rendered[profile.ROOT / "assets/projects/selected.svg"])
        self.assertIn("Full data & methodology", rendered[profile.ROOT / "README.md"])
        data["featured_repositories"] = []
        with self.assertRaises(ValueError):
            profile.outputs(data, readme, featured=[project])

    def test_svg_escaping_and_empty_languages(self):
        data = profile.collect(self.fetcher([[repo("normal")]], 1), "2026-10-13")
        data["primary_languages"] = {"C<&": 1}
        svg = profile.activity_svg(data)
        profile.validate_svg(svg)
        self.assertIn("C&lt;&amp;", svg)
        data["primary_languages"] = {}
        profile.validate_svg(profile.activity_svg(data))

    def test_marker_integrity_and_manual_content_preserved(self):
        original = "Before\n" + profile.START + "old" + profile.END + "\nAfter"
        result = profile.replace_activity(original, "new")
        self.assertTrue(result.startswith("Before\n"))
        self.assertTrue(result.endswith("\nAfter"))
        for malformed in ["no markers", original + profile.START, profile.END + profile.START]:
            with self.assertRaises(ValueError):
                profile.replace_activity(malformed, "new")

    def test_external_or_executable_svg_fails(self):
        for element in ['<script/>', '<image href="https://example.com/a.png"/>', '<g onclick="alert(1)"/>']:
            with self.assertRaises(ValueError):
                profile.validate_svg(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">{element}</svg>')


if __name__ == "__main__":
    unittest.main()
