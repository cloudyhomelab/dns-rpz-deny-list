# dns-rpz-deny-list

Deny list for blocklists that are not published as RPZ zone files. `deny-list.txt` is the `deny` input of the [cloudyhome-dns-rpz](https://github.com/cloudyhomelab/terraform-homelab-modules/tree/main/cloudyhome-dns-rpz) Terraform module, which blocks each entry and all its subdomains.

## Scope

- Blocklists published as RPZ zone files are loaded on the DNS server directly, not through this repository. Each one is listed under `loaded_rpz_zones` in `blocklists.json` so that names they already block are left out.
- Every entry becomes two Terraform resources and two dynamic DNS updates; `max_entries` caps the list size.

## Files

- `personal-deny-list.txt`: hand-entered domains, one per line, `#` comments allowed.
- `blocklists.json`:
  - `sources`: `{ "name", "url", "format" }` where `format` is `domains` (one name per line), `hosts` (`0.0.0.0 name`) or `adblock` (`||name^`; other rule types are ignored).
  - `loaded_rpz_zones`: `{ "name", "url" }` of each RPZ zone file the DNS server already loads.
  - `max_entries`: the most entries written; see Build for which are dropped.
  - `hosts_ignore`: names in hosts files that are not blocklist entries.
- `deny-list.txt`: generated; do not edit.
- `deny-list.txt.previous`: generated; the output of the last run without errors.

## Build

```sh
python3 scripts/build_deny_list.py
```

- Standard library only; no virtual environment needed.
- Steps: merge personal entries and sources, normalize (lowercase, strip trailing dot and `*.` prefix, convert IDN to punycode), validate against the module's deny pattern, drop names the loaded zones already block, drop names whose parent is listed, sort, write.
- A name counts as already blocked if a loaded zone blocks it and all its subdomains: a `*.parent` record, or both `name` and `*.name` records.
- Every input is processed independently; a failure discards only what it affects:
  - an invalid name is skipped; each source's rejections are counted and sampled
  - an unreadable source or `personal-deny-list.txt` is skipped
  - an unreadable or empty loaded zone is skipped, so names it blocks may be repeated here
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
- Personal entries reported as already blocked can be removed.
