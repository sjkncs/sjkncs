# Profile maintenance

## Content and assets

`README.md` is the public profile. Update its introduction, focus and selected projects manually when their actual scope changes. All visuals are self-contained repository SVGs: no font, image or script is fetched by the assets. README image URLs use the repository's Raw endpoint directly to avoid GitHub redirect failures. The contribution animation remains in a collapsible section on the separate `output` branch.

## Automatic public metadata

The layout puts representative projects before tools and statistics. Six 360px SVG cards wrap from two columns to one when the GitHub content column gets narrower. The cards contain dark-mode styles. `data/featured.json` is the manually curated card index; `assets/projects/*.svg` are generated from this index and the public metadata snapshot. Keep captions within the enforced length budgets. Reference profiles and adaptation decisions are recorded in [PROFILE_REFERENCES.md](PROFILE_REFERENCES.md).

`scripts/update_profile.py` uses GitHub's public user and repository endpoints through GitHub CLI. It collects every page, excludes private repositories, checks the public repository count and stores a dated snapshot in `data/profile.json`. It does not access private project content, collect commit histories or infer achievements.

The snapshot drives `assets/activity.svg`, the six featured project SVGs and the accessible README table. Featured repository metadata is taken from the same complete public repository response, not separate best-effort requests. A missing, private or forked featured repository fails the refresh. Total public repositories include forks; the separate non-fork count excludes them. Stars are summed over public non-fork repositories. Primary-language counts describe GitHub's single main language per non-fork repository; they are not language-byte percentages or proficiency. Recent activity lists non-fork, non-archived public repositories by push date, excluding this profile repository. Non-fork status does not imply original authorship: mirrors and derivative work may be included.

Run from the repository root:

```powershell
py -3.11 scripts/update_profile.py
py -3.11 -m unittest discover -s tests -v
py -3.11 scripts/update_profile.py --check
```

GitHub Actions runs the same checks for pull requests. On pushes to `main`, manual dispatches and the daily schedule, it refreshes metadata and commits only the generated files. Pull requests never run the publishing job. Refresh failures retain the previous committed assets and their timestamp. GitHub can delay scheduled runs; the visible date is the data collection time, not a promise of real-time updates.

The generator requires Python 3.11+ and GitHub CLI, with no third-party Python packages. GitHub Actions dependencies are pinned to verified commit SHAs. Public GitHub API responses are the data source; no external statistics renderer or visitor-tracking service is used.
