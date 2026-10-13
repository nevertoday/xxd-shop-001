#!/usr/bin/env python3
"""Bitmap bridge for XXD Shop Soldiers.

Every request goes through the Responses API with the hosted image_generation
tool (`/v1/responses`). The per-image billed `/v1/images/*` endpoints are never
called.

Route sources, in order:
1. The line registry of an installed xxd-prompt-image-batch Skill
   (providers.json + its Keychain/config key lookup). Lines are chosen by number.
2. The active provider in the Codex config (~/.codex/config.toml), used only when
   no registry is installed.

Output is a sanitized JSON record. Keys, request headers, prompts and response
bodies are never printed. The line menu shows host:port so the user can tell
machines apart, as the registry itself does.
"""

from __future__ import annotations

import argparse
import base64
import importlib.util
import io
import json
import math
import mimetypes
import os
from pathlib import Path
import sys
import tomllib
import urllib.error
import urllib.parse
import urllib.request


DEFAULT_MODEL = "gpt-image-2"
DEFAULT_BASE_MODEL = "gpt-6-luna"
MAX_RESPONSE_BYTES = 120 * 1024 * 1024
GPT_IMAGE_2_MIN_PIXELS = 655_360
GPT_IMAGE_2_MAX_PIXELS = 8_294_400
GPT_IMAGE_2_MAX_EDGE = 3840
GPT_IMAGE_2_MAX_RATIO = 3.0
RELAY_INSTRUCTIONS = (
    "Call the image_generation tool exactly once. Pass the user's text to it verbatim as the "
    "prompt, without rewriting, summarising, translating or adding anything. Attached images are "
    "references whose roles are stated in the text. Do not answer in text."
)


class BridgeError(Exception):
    def __init__(self, reason: str, phase: str, status: int | None = None, detail: str = ""):
        super().__init__(reason)
        self.reason, self.phase, self.status, self.detail = reason, phase, status, detail


def emit(payload: dict, *, error: bool = False) -> None:
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), file=sys.stderr if error else sys.stdout)


# ---------- route source 1: xxd-prompt-image-batch registry ----------

def batch_skill_dir() -> Path | None:
    candidates = []
    if os.environ.get("XXD_IMAGE_BATCH_SKILL"):
        candidates.append(Path(os.environ["XXD_IMAGE_BATCH_SKILL"]).expanduser())
    for home in (Path.home() / ".claude" / "skills", Path.home() / ".codex" / "skills"):
        candidates.append(home / "xxd-prompt-image-batch")
    for path in candidates:
        if (path / "scripts" / "generate_prompt_images.py").is_file() and (path / "providers.json").is_file():
            return path.resolve()
    return None


def load_batch_module(skill: Path):
    scripts = skill / "scripts"
    sys.path.insert(0, str(scripts))
    spec = importlib.util.spec_from_file_location("xxd_batch_gen", scripts / "generate_prompt_images.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def registry_endpoints(module, skill: Path, selector: str, failover: bool) -> list[tuple[str, str, str, str]]:
    """Return [(label, base_url, api_key, model)] for the chosen line and its fallbacks."""
    registry = module.load_provider_registry(skill / "providers.json")
    endpoints, _warnings = module.build_provider_chain(registry, [selector], failover_enabled=failover)
    return [(e.label or e.provider_id, e.base_url, e.api_key, e.model) for e in endpoints]


# ---------- route source 2: Codex config ----------

def codex_endpoint() -> tuple[str, str, str, str]:
    root = Path(os.environ.get("XXD_IMAGEGEN_CODEX_DIR") or os.environ.get("CODEX_HOME") or Path.home() / ".codex").expanduser()
    try:
        config = tomllib.loads((root / "config.toml").read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise BridgeError("route_not_configured", "route") from exc
    except Exception as exc:
        raise BridgeError("route_config_unreadable", "route") from exc
    provider = (config.get("model_providers") or {}).get(config.get("model_provider"))
    if not isinstance(provider, dict) or not isinstance(provider.get("base_url"), str):
        raise BridgeError("route_not_configured", "route")
    base_url = provider["base_url"].strip().rstrip("/")
    for suffix in ("/responses", "/chat/completions", "/v1"):
        if base_url.endswith(suffix):
            base_url = base_url[: -len(suffix)]
    token = ""
    if isinstance(provider.get("env_key"), str):
        token = os.environ.get(provider["env_key"], "")
    if not token and isinstance(provider.get("experimental_bearer_token"), str):
        token = provider["experimental_bearer_token"]
    if not token and provider.get("requires_openai_auth") is True:
        try:
            token = json.loads((root / "auth.json").read_text(encoding="utf-8")).get("OPENAI_API_KEY") or ""
        except Exception:
            token = ""
    token = token or os.environ.get("OPENAI_API_KEY", "")
    if not token:
        raise BridgeError("credential_unavailable", "route")
    return ("codex-config", base_url, token, DEFAULT_MODEL)


# ---------- request ----------

def normalize_size(value: str) -> str | None:
    if value == "auto":
        return None
    try:
        width, height = (int(part) for part in value.lower().replace("×", "x").split("x", 1))
    except Exception as exc:
        raise BridgeError("invalid_size", "input") from exc
    if max(width, height) / min(width, height) > GPT_IMAGE_2_MAX_RATIO:
        raise BridgeError("unsupported_aspect_ratio", "input")
    pixels = width * height
    lower = math.sqrt(GPT_IMAGE_2_MIN_PIXELS / pixels)
    upper = min(math.sqrt(GPT_IMAGE_2_MAX_PIXELS / pixels), GPT_IMAGE_2_MAX_EDGE / max(width, height))
    if lower > upper:
        raise BridgeError("unsupported_size", "input")
    scale = min(max(1.0, lower), upper)
    for _ in range(200):
        out_w = max(16, round(width * scale / 16) * 16)
        out_h = max(16, round(height * scale / 16) * 16)
        if max(out_w, out_h) <= GPT_IMAGE_2_MAX_EDGE and GPT_IMAGE_2_MIN_PIXELS <= out_w * out_h <= GPT_IMAGE_2_MAX_PIXELS:
            return f"{out_w}x{out_h}"
        scale *= 1.005 if out_w * out_h < GPT_IMAGE_2_MIN_PIXELS else 0.995
    raise BridgeError("unsupported_size", "input")


def image_part(path: Path) -> dict:
    try:
        data = path.read_bytes()
    except Exception as exc:
        raise BridgeError("source_unreadable", "input") from exc
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    return {"type": "input_image", "image_url": f"data:{mime};base64,{base64.b64encode(data).decode('ascii')}"}


def request_once(base_url: str, api_key: str, model: str, prompt: str, images: list[Path], size: str | None,
                 quality: str, base_model: str, timeout: int,
                 labels: list[str] | None = None) -> tuple[bytes, str | None]:
    tool: dict[str, object] = {"type": "image_generation", "model": model, "quality": quality,
                               "output_format": "png", "background": "opaque"}
    if size:
        tool["size"] = size
    content: list[dict] = [{"type": "input_text", "text": prompt}]
    for index, path in enumerate(images):
        # the legend line sits right before its picture, so the role never depends on order alone
        if labels and labels[index]:
            content.append({"type": "input_text", "text": labels[index]})
        content.append(image_part(path))
    payload = {"model": base_model, "instructions": RELAY_INSTRUCTIONS,
               "input": [{"role": "user", "content": content}], "tools": [tool],
               "tool_choice": {"type": "image_generation"}, "stream": False}
    req = urllib.request.Request(f"{base_url}/v1/responses", method="POST",
                                 data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                                 headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read(MAX_RESPONSE_BYTES + 1)
    except urllib.error.HTTPError as exc:
        detail = exc.read(2000).decode("utf-8", errors="replace")
        short = "quota_or_rate_limit" if exc.code == 429 else ("overloaded" if "overload" in detail else "")
        raise BridgeError("image_request_rejected", "generate", exc.code, short) from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise BridgeError("route_unreachable", "generate") from exc
    if len(body) > MAX_RESPONSE_BYTES:
        raise BridgeError("response_too_large", "response")
    result = json.loads(body)
    calls = [o for o in result.get("output") or [] if isinstance(o, dict) and o.get("type") == "image_generation_call" and o.get("result")]
    if not calls:
        raise BridgeError("no_image_returned", "response", detail="relay_answered_in_text")
    return base64.b64decode(calls[0]["result"]), calls[0].get("revised_prompt")


def write_png(raw: bytes, out: Path, target: tuple[int, int] | None, force: bool, strip) -> dict:
    if out.suffix.lower() != ".png":
        raise BridgeError("output_must_be_png", "output")
    if out.exists() and not force:
        raise BridgeError("output_exists", "output")
    from PIL import Image, ImageOps
    with Image.open(io.BytesIO(raw)) as image:
        image.load()
        native = image.size
        if image.mode in {"RGBA", "LA", "P"}:
            background = Image.new("RGB", image.size, "white")
            background.paste(image.convert("RGBA"), mask=image.convert("RGBA").split()[-1])
            image = background
        elif image.mode != "RGB":
            image = image.convert("RGB")
        if target and image.size != target:
            # Never upscale to fake a resolution the line did not return: only crop to the
            # requested aspect at native scale, then report the real pixels.
            want = target[0] / target[1]
            have = image.size[0] / image.size[1]
            if abs(have - want) / want > 0.01:
                if have > want:
                    size = (round(image.size[1] * want), image.size[1])
                else:
                    size = (image.size[0], round(image.size[0] / want))
                image = ImageOps.fit(image, size, method=Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
    data = buffer.getvalue()
    delivered = f"{image.size[0]}x{image.size[1]}"
    if target and delivered != f"{target[0]}x{target[1]}" and f"{target[0]}x{target[1]}" in out.name:
        out = out.with_name(out.name.replace(f"{target[0]}x{target[1]}", delivered))
        if out.exists() and not force:
            raise BridgeError("output_exists", "output")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)  # keep the image even if metadata cleanup below fails
    removed: list[str] = []
    cleanup = "skipped"
    if strip is not None:
        try:
            cleaned = strip(data)
            removed = list(getattr(cleaned, "removed_chunk_types", ()) or ())
            out.write_bytes(cleaned.image_bytes)
            cleanup = "ok"
        except Exception:  # noqa: BLE001
            cleanup = "failed_image_kept"
    return {"path": str(out.resolve()), "native_size": f"{native[0]}x{native[1]}", "delivered_size": delivered,
            "size_matches_request": not target or delivered == f"{target[0]}x{target[1]}",
            "metadata_cleanup": cleanup, "metadata_removed": removed}


def resolve_endpoints(args) -> tuple[list[tuple[str, str, str, str]], object]:
    skill = batch_skill_dir()
    if skill is not None:
        module = load_batch_module(skill)
        if not args.provider:
            raise BridgeError("line_not_chosen", "route", detail="run `lines` and pass --provider N")
        endpoints = registry_endpoints(module, skill, args.provider, failover=not args.no_failover)
        if not endpoints:
            raise BridgeError("credential_unavailable", "route")
        return endpoints, module
    return [codex_endpoint()], None


def cmd_lines(_args) -> int:
    skill = batch_skill_dir()
    if skill is None:
        emit({"ok": True, "source": "codex-config", "lines": [], "note": "no registry; the Codex provider is used"})
        return 0
    module = load_batch_module(skill)
    registry = module.load_provider_registry(skill / "providers.json")
    lines = [{"n": i, "id": o.id, "label": o.base_url.split("//", 1)[-1], "machine": o.endpoint_label,
              "model": o.model, "default": o.id == registry.default_id, "note": o.note}
             for i, o in enumerate(registry.options, 1)]
    emit({"ok": True, "source": "xxd-prompt-image-batch", "lines": lines})
    return 0


def cmd_probe(args) -> int:
    endpoints, module = resolve_endpoints(args)
    report = []
    for label, base_url, api_key, model in endpoints:
        if module is not None:
            ok, elapsed, _detail = module.probe_provider(base_url, api_key, timeout=args.timeout)
        else:
            ok, elapsed = True, 0.0
        report.append({"line": label, "model": model, "answering": bool(ok), "latency_s": round(elapsed, 1)})
    ready = any(item["answering"] for item in report)
    emit({"ok": ready, "bitmap_route": ready, "api_mode": "responses", "lines": report})
    return 0 if ready else 2


def cmd_generate(args) -> int:
    # Saving needs Pillow; check before the request so a missing module never wastes a generation.
    if importlib.util.find_spec("PIL") is None:
        raise BridgeError("pillow_missing", "environment", detail=f"install Pillow for {sys.executable}")
    try:
        prompt = args.prompt_file.read_text(encoding="utf-8").strip()
    except Exception as exc:
        raise BridgeError("prompt_unreadable", "input") from exc
    if not prompt:
        raise BridgeError("prompt_empty", "input")
    images = [Path(p).expanduser() for p in args.image or []]
    labels = args.label or []
    if labels and len(labels) != len(images):
        raise BridgeError("labels_must_match_images", "input")
    target = None if args.size == "auto" else tuple(int(v) for v in args.size.lower().replace("×", "x").split("x", 1))
    request_size = normalize_size(args.size)
    endpoints, module = resolve_endpoints(args)
    strip = getattr(module, "strip_png_metadata", None) if module is not None else None
    last: BridgeError | None = None
    for label, base_url, api_key, model in endpoints:
        try:
            raw, revised = request_once(base_url, api_key, model, prompt, images, request_size,
                                        args.quality, args.base_model, args.timeout, labels)
            info = write_png(raw, Path(args.out).expanduser(), target, args.force, strip)
            emit({"ok": True, "bitmap_written": True,
                  "line": label, "api_mode": "responses", "reference_images": len(images),
                  "requested_size": request_size or "auto", "prompt_rewritten": bool(revised and revised.strip() != prompt), **info})
            return 0
        except BridgeError as exc:
            last = exc
            if exc.phase not in {"generate", "response"}:
                raise
    raise last or BridgeError("all_lines_failed", "generate")


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = root.add_subparsers(dest="command", required=True)
    sub.add_parser("lines", help="List available drawing lines (no network).")
    for name in ("probe", "generate", "edit"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--provider", help="Line number or id from `lines` (required when a registry exists).")
        cmd.add_argument("--no-failover", action="store_true")
        cmd.add_argument("--timeout", type=int, default=20 if name == "probe" else 420)
        if name != "probe":
            cmd.add_argument("--prompt-file", type=Path, required=True)
            cmd.add_argument("--out", required=True)
            cmd.add_argument("--size", default="auto")
            cmd.add_argument("--quality", choices=("low", "medium", "high", "auto"), default="high")
            cmd.add_argument("--base-model", default=DEFAULT_BASE_MODEL)
            cmd.add_argument("--force", action="store_true")
            cmd.add_argument("--image", action="append", help="Reference image; repeatable, product image first.")
            cmd.add_argument("--label", action="append",
                             help="Legend line for the --image at the same position (e.g. '图 2｜本套第 1 张：只继承……'); "
                                  "give one per --image or none.")
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        if args.command == "lines":
            return cmd_lines(args)
        if args.command == "probe":
            return cmd_probe(args)
        return cmd_generate(args)  # `edit` is kept as an alias of generate with --image
    except BridgeError as exc:
        payload = {"ok": False, "phase": exc.phase, "reason": exc.reason}
        if exc.status is not None:
            payload["http_status"] = exc.status
        if exc.detail:
            payload["detail"] = exc.detail
        emit(payload, error=True)
        return 2
    except Exception as exc:  # noqa: BLE001
        emit({"ok": False, "phase": "internal", "reason": type(exc).__name__}, error=True)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
