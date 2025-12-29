#!/usr/bin/env python3

import os
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional
from urllib.request import Request, urlopen


API_BASE = os.environ.get(
    "NUMBERS4_API_BASE",
    "https://hazimekom.github.io/numbers4-api/api/v1",
).rstrip("/")
LATEST_URL = f"{API_BASE}/latest.json"
ALL_URL = f"{API_BASE}/numbers4_all_min.json"


@dataclass(frozen=True)
class Draw:
    draw_no: str
    date: str
    digits: str


def _fetch_json(url: str, timeout_sec: int = 20) -> Any:
    req = Request(url, headers={"User-Agent": "numbers4-web build-time fetch"})
    with urlopen(req, timeout=timeout_sec) as resp:
        raw = resp.read().decode("utf-8")
    return json.loads(raw)


def _digits_to_str(value: Any) -> str:
    if isinstance(value, list):
        return "".join(str(x) for x in value)
    if value is None:
        return "----"
    return str(value)


_DATE_YYYY_MM_DD = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")


def _normalize_date(value: Any) -> str:
    if value is None:
        return "----"
    s = str(value)
    m = _DATE_YYYY_MM_DD.match(s)
    if m:
        return f"{m.group(1)}/{m.group(2)}/{m.group(3)}"
    return s


def _safe_int(value: Any) -> Optional[int]:
    try:
        return int(str(value))
    except Exception:
        return None


def _replace_between_markers(text: str, start: str, end: str, replacement: str) -> str:
    pattern = re.compile(
        rf"({re.escape(start)}\n)(.*?)(\n{re.escape(end)})",
        re.DOTALL,
    )
    m = pattern.search(text)
    if not m:
        raise RuntimeError(f"Markers not found: {start} ... {end}")
    return text[: m.start(2)] + replacement + text[m.end(2) :]


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    target = repo_root / "docs" / "results" / "index.md"

    try:
        latest = _fetch_json(LATEST_URL)
        all_items = _fetch_json(ALL_URL)
    except Exception as e:
        print(f"ERROR: failed to fetch JSON: {e}", file=sys.stderr)
        return 2

    if not isinstance(latest, dict):
        print("ERROR: latest.json is not an object", file=sys.stderr)
        return 2
    if not isinstance(all_items, list):
        print("ERROR: numbers4_all_min.json is not a list", file=sys.stderr)
        return 2

    latest_draw = Draw(
        draw_no=str(latest.get("draw_no") or latest.get("drawNo") or latest.get("draw") or "---"),
        date=_normalize_date(latest.get("date")),
        digits=_digits_to_str(latest.get("digits")),
    )

    parsed: list[Draw] = []
    for x in all_items:
        if isinstance(x, dict):
            draw_no = x.get("draw_no") or x.get("drawNo") or x.get("draw")
            parsed.append(
                Draw(
                    draw_no=str(draw_no) if draw_no is not None else "",
                    date=_normalize_date(x.get("date")),
                    digits=_digits_to_str(x.get("digits")),
                )
            )

    def sort_key(d: Draw):
        n = _safe_int(d.draw_no)
        return (n if n is not None else -1, d.date)

    parsed = [
        d
        for d in parsed
        if d.draw_no and d.digits != "----" and d.date != "----"
    ]
    parsed.sort(key=sort_key)

    last10 = list(reversed(parsed[-10:]))

    latest_md = f"- **第{latest_draw.draw_no}回**（{latest_draw.date}）：**{latest_draw.digits}**"
    history_rows = "\n".join(
        f"| {d.draw_no} | {d.date} | {d.digits} |" for d in last10
    )

    try:
        text = target.read_text(encoding="utf-8")
    except Exception as e:
        print(f"ERROR: failed to read {target}: {e}", file=sys.stderr)
        return 2

    try:
        text = _replace_between_markers(
            text,
            "<!-- STATIC_LATEST_START -->",
            "<!-- STATIC_LATEST_END -->",
            latest_md,
        )
        text = _replace_between_markers(
            text,
            "<!-- STATIC_HISTORY_START -->",
            "<!-- STATIC_HISTORY_END -->",
            history_rows,
        )
    except Exception as e:
        print(f"ERROR: failed to inject static content: {e}", file=sys.stderr)
        return 2

    try:
        target.write_text(text, encoding="utf-8")
    except Exception as e:
        print(f"ERROR: failed to write {target}: {e}", file=sys.stderr)
        return 2

    print(f"Injected static results into: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
