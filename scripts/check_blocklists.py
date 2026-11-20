#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Fail if a blocklists.json lists the same name or URL more than once across sources and loaded RPZ zones."""

import json
import sys
from collections import Counter
from pathlib import Path

SECTIONS = ("sources", "loaded_rpz_zones")
UNIQUE_KEYS = ("name", "url")


def duplicates(config: dict) -> list[str]:
    entries = [entry for section in SECTIONS for entry in config.get(section, [])]
    problems = []
    for key in UNIQUE_KEYS:
        counts = Counter(entry[key] for entry in entries if key in entry)
        problems.extend(f"{key} {value!r} appears {count} times" for value, count in counts.items() if count > 1)
    return problems


def main(paths: list[str]) -> int:
    failed = False
    for path in paths:
        try:
            config = json.loads(Path(path).read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            print(f"{path}: {error}", file=sys.stderr)
            failed = True
            continue
        for problem in duplicates(config):
            print(f"{path}: {problem}", file=sys.stderr)
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
