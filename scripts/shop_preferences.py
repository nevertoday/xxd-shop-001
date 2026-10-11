#!/usr/bin/env python3
"""Store and retrieve the safe, family-wide XXD Shop delivery preference."""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
TEXT_MODES = {"prompt", "exact", "plan", "none"}
MAX_COUNT = 8
SIZE_RE = re.compile(r"^(?:auto|source|[1-9][0-9]*:[1-9][0-9]*|[1-9][0-9]*x[1-9][0-9]*)$")


class PreferenceError(ValueError):
    pass


def _config_dir() -> Path:
    override = os.environ.get("XXD_SHOP_PREFS_DIR")
    if override:
        return Path(override).expanduser()
    if os.name == "nt" and os.environ.get("APPDATA"):
        return Path(os.environ["APPDATA"]) / "xxd-shop" / "preferences"
    xdg = os.environ.get("XDG_CONFIG_HOME")
    base = Path(xdg).expanduser() if xdg else Path.home() / ".config"
    return base / "xxd-shop" / "preferences"


def _preference_path() -> Path:
    return _config_dir() / "last-delivery.json"


def _split_values(values: list[str] | None) -> list[str]:
    result: list[str] = []
    for value in values or []:
        for item in value.replace("，", ",").split(","):
            item = item.strip()
            if item and item not in result:
                result.append(item)
    return result


def _clean_text(value: str | None, field: str, limit: int = 1024) -> str | None:
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    if len(value) > limit or any(ord(char) < 32 for char in value):
        raise PreferenceError(f"invalid {field}")
    return value


def _normalise_size(value: str) -> str:
    return value.strip().lower().replace("×", "x")


def _validate_profile(profile: dict[str, Any]) -> dict[str, Any]:
    allowed = {"sizes", "count", "text_mode", "locale", "output_root"}
    if set(profile) - allowed:
        raise PreferenceError("unsupported preference field")

    sizes = profile.get("sizes")
    if not isinstance(sizes, list) or not sizes or len(sizes) > 32:
        raise PreferenceError("sizes are required")
    clean_sizes: list[str] = []
    for size in sizes:
        if not isinstance(size, str):
            raise PreferenceError("invalid size")
        clean_size = _normalise_size(size)
        if not SIZE_RE.fullmatch(clean_size):
            raise PreferenceError("invalid size")
        if clean_size not in clean_sizes:
            clean_sizes.append(clean_size)

    count = profile.get("count", 1)
    if not isinstance(count, int) or isinstance(count, bool) or not 1 <= count <= MAX_COUNT:
        raise PreferenceError("invalid count")

    text_mode = profile.get("text_mode")
    if text_mode not in TEXT_MODES:
        raise PreferenceError("text mode is required")
    locale = _clean_text(profile.get("locale"), "locale", 64)
    # locale is optional: a brief may fix the language, and then it must not be remembered
    if text_mode == "none":
        locale = None

    output_root = _clean_text(profile.get("output_root"), "output root")

    result: dict[str, Any] = {"sizes": clean_sizes, "count": count, "text_mode": text_mode}
    if locale:
        result["locale"] = locale
    if output_root:
        result["output_root"] = output_root
    return result


def _load() -> dict[str, Any]:
    path = _preference_path()
    if not path.is_file():
        return {"status": "missing"}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or data.get("schema_version") != SCHEMA_VERSION:
            raise PreferenceError("unsupported preference schema")
        preferences = data.get("preferences")
        if not isinstance(preferences, dict):
            raise PreferenceError("invalid preference payload")
        clean = _validate_profile(preferences)
        return {"status": "found", "updated_at": data.get("updated_at"), "preferences": clean}
    except (OSError, json.JSONDecodeError, PreferenceError):
        return {"status": "invalid"}


def _save(args: argparse.Namespace) -> dict[str, Any]:
    profile: dict[str, Any] = {
        "sizes": [_normalise_size(item) for item in _split_values(args.sizes)],
        "count": args.count,
        "text_mode": args.text_mode,
        "locale": args.locale,
        "output_root": args.output_root,
    }
    clean = _validate_profile(profile)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "preferences": clean,
    }
    directory = _config_dir()
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    try:
        os.chmod(directory, stat.S_IRWXU)
    except OSError:
        pass
    fd, temporary_name = tempfile.mkstemp(prefix=".last-delivery-", suffix=".json", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.chmod(temporary_name, stat.S_IRUSR | stat.S_IWUSR)
        os.replace(temporary_name, _preference_path())
    finally:
        if os.path.exists(temporary_name):
            os.unlink(temporary_name)
    return {"status": "saved", "preferences": clean}


def _clear() -> dict[str, str]:
    try:
        _preference_path().unlink()
        return {"status": "cleared"}
    except FileNotFoundError:
        return {"status": "missing"}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("load", help="load the last safe delivery preference")
    subparsers.add_parser("clear", help="remove the remembered delivery preference")

    save = subparsers.add_parser("save", help="replace the remembered delivery preference")
    save.add_argument("--sizes", action="append", required=True)
    save.add_argument("--count", type=int, default=1)
    save.add_argument("--text-mode", choices=sorted(TEXT_MODES), required=True)
    save.add_argument("--locale")
    save.add_argument("--output-root")
    return parser


def main() -> int:
    args = _parser().parse_args()
    try:
        if args.command == "load":
            result = _load()
        elif args.command == "save":
            result = _save(args)
        else:
            result = _clear()
        print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
        return 0
    except (OSError, PreferenceError) as error:
        print(json.dumps({"status": "error", "message": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
