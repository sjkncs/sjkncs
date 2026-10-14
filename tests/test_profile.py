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
