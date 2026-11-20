# Contributing

## Setup

Needs [uv](https://docs.astral.sh/uv/).

```sh
uv sync
uv run pre-commit install
```

- `uv sync` creates `.venv` with the tools pinned in `uv.lock`; the build itself needs only the standard library.
- `pre-commit` then checks each commit: valid JSON and YAML, JSON formatted with 2-space indent (fixed in place), no duplicate source names or URLs in `blocklists.json` and no duplicate domains in `personal-deny-list.txt` or `exclude-list.txt`, LF line endings, final newline, no trailing whitespace, no merge markers or large files.
- A commit with files the hooks fixed is stopped; review the fixes, `git add` them and commit again.
- `uv run pre-commit run --all-files` checks the whole repository.
- `.editorconfig` applies the same layout in editors that support it.

## Build

```sh
python3 scripts/build_deny_list.py
```

- Standard library only; no virtual environment needed.
- Steps: merge personal entries and sources, normalize (lowercase, strip trailing dot and `*.` prefix, convert IDN to punycode), validate (labels of `a-z`, `0-9`, `_` and `-`, not starting or ending with `-`, at most 63 characters each; at most 253 characters in total; at least two labels; last label not all digits), drop `exclude-list.txt` entries (except personal ones), drop names the loaded zones already block, drop names whose parent is listed, sort, write.
- A name counts as already blocked if a loaded zone blocks it and all its subdomains: a `*.parent` record, or both `name` and `*.name` records.
- Every input is processed independently; a failure discards only what it affects:
  - an invalid name is skipped; each source's rejections are counted and sampled
  - an invalid `exclude-list.txt` entry is skipped and is an error
  - an unreadable source or `personal-deny-list.txt` is skipped, as is a source missing `license`, `author` or `homepage`, since it could not be credited
  - an unreadable or empty loaded zone is skipped, as is one missing `license`, `author` or `homepage`, so names it blocks may be repeated here
  - entries beyond `max_entries` are dropped: first those from `deny-list.txt.previous`, then sources from the last one in `sources` backwards; valid personal entries are never dropped, even if they alone exceed the cap
- Errors (a skipped source, personal list or loaded zone) decide what is written:
  - no errors: `deny-list.txt` and `deny-list.txt.previous` both get the new list
  - errors: `deny-list.txt` gets the new list merged with `deny-list.txt.previous`, so a failed input does not drop entries; `deny-list.txt.previous` is left as is
  - rejected names and the `max_entries` cut are not errors
- Exit codes:
  - `0`: no errors
  - `1`: no input could be read; both files left unchanged
  - `2`: written with errors, merged with `deny-list.txt.previous`
- Each error is one stderr line starting with `error: `, e.g. for a CI job summary: `grep '^error: ' stderr.log >> "$GITHUB_STEP_SUMMARY"`. Other stderr lines (counts, rejected samples, `warning: ` for the `max_entries` cut) are informational.
- Personal entries reported as already blocked, and `exclude-list.txt` entries reported as matching nothing, can be removed.
- An `exclude-list.txt` entry reported as still blocked has no effect: its parent is listed or a loaded zone blocks it.

## Automation

- `.github/workflows/update-deny-list.yml` runs the build daily, on manual dispatch, and on pushes to `main` that change `personal-deny-list.txt`, `blocklists.json` or the script.
- A changed list is committed to `chore/update-deny-list` and proposed as a pull request to `main`; each run replaces that branch and updates the open pull request.
- The job summary lists per-source counts and every `error: ` line; the pull request description repeats the errors.
- Exit code `2` still opens the pull request, then fails the job so the errors get noticed; exit code `1` fails before any change.
- `peter-evans/create-pull-request` commits and opens the pull request with a GitHub App token, so commits are signed as the app and the pull request triggers other workflows; with no changes left, it deletes the branch. Secrets: `CLOUDYHOME_BOT_CLIENT_ID`, `CLOUDYHOME_BOT_PRIVATE_KEY`; the app needs read and write access to contents and pull requests on this repository.
- `.github/workflows/pre-commit.yml` runs the same hooks on every pull request, so a commit made without them installed is still checked.
- `.github/workflows/renovate.yml` runs self-hosted Renovate (`npx renovate`) weekly and on manual dispatch with the same app token; `renovate.json` keeps GitHub Action pins (SHA plus version comment), the Python and Node versions in the workflows, and Renovate's own version up to date. Releases younger than 3 days are held back. The app additionally needs write access to issues (dependency dashboard), workflows and commit statuses, and read access to checks.
