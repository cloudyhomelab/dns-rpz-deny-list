# dns-rpz-deny-list

Deny list built from blocklists that are not published as RPZ zone files. Each entry in `deny-list.txt` stands for the domain and all its subdomains.

## Scope

- Blocklists published as RPZ zone files are not merged here. Each one is listed under `loaded_rpz_zones` in `blocklists.json` so that names they already block are left out.

## Files

- `personal-deny-list.txt`: hand-entered domains, one per line, `#` comments allowed.
- `blocklists.json`:
  - `sources`: `{ "name", "url", "format" }` where `format` is `domains` (one name per line), `hosts` (`0.0.0.0 name`), `adblock` (`||name^`; other rule types are ignored) or `pihole-regex` (`(\.|^)zone$` and `^host$` rules; any other regex is rejected, since it cannot be listed as names).
  - `loaded_rpz_zones`: `{ "name", "url" }` of each RPZ zone file whose blocked names are left out.
  - `max_entries`: the most entries written; valid personal entries are always kept.
  - `hosts_ignore`: names in hosts files that are not blocklist entries.
- `deny-list.txt`: generated; do not edit.
- `deny-list.txt.previous`: generated; the output of the last run without errors.

## Usage

- Add or remove a hand-entered domain in `personal-deny-list.txt`, or a source in `blocklists.json`, and merge it to `main`.
- A workflow then rebuilds `deny-list.txt` and proposes it as a pull request; it also rebuilds daily to pick up source changes.
- Names that a loaded RPZ zone already blocks, or whose parent domain is listed, are left out of `deny-list.txt`.

Build details and automation: [CONTRIBUTING.md](CONTRIBUTING.md).

## License

- Copyright (C) 2026 Sujoy Das.
- Licensed under the GNU General Public License, version 3 or (at your option) any later version; see `LICENSE`.
