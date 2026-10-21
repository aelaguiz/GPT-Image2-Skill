#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "openai>=3.9.0",
#     "python-dotenv>=1.0",
#     "pillow>=11.3",
# ]
# ///
"""Generate and edit images with GPT Image 2.5 Flare by default.

The canonical implementation for the installed command and the skill launcher.
No reference inputs: images.generate. One or more references: images.edit.
Credentials: process environment, then ./.env, then ~/.env. Successful stdout
contains output paths only. Exit codes: 0 success, 1 API/output failure, 2 input
or configuration error. Use --version to identify the effective backend.
"""
from __future__ import annotations

import argparse
import base64
import binascii
import io
import os
import re
import sys
import urllib.request
from contextlib import ExitStack
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import APIError, OpenAI
from PIL import Image, UnidentifiedImageError

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from gpt_image_cli import __version__

SIZE_SHORTCUTS = {
    "1k": "1024x1024", "2k": "2048x2048", "4k": "3840x2160",
    "portrait": "1024x1536", "landscape": "1536x1024", "square": "1024x1024",
    "wide": "2048x1152", "tall": "2160x3840",
}
DEFAULT_MODEL = "gpt-image-2.5-flare"
DEFAULT_SIZE = "1024x1024"
DEFAULT_MODERATION = "low"
IMAGE_25_MODELS = frozenset({
    "gpt-image-2.5-flare", "gpt-image-2.5-flare-2026-09-08",
    "gpt-image-2.5-sunburst", "gpt-image-2.5-sunburst-2026-09-08",
})
IMAGE_2_MODELS = frozenset({"gpt-image-2", "gpt-image-2-2026-04-21"})
OLDER_IMAGE_MODELS = frozenset({
    "gpt-image-1", "gpt-image-1-mini", "gpt-image-1.5", "chatgpt-image-latest",
})
LEGACY_QUALITY_MODELS = IMAGE_2_MODELS | OLDER_IMAGE_MODELS | {"dall-e-2", "dall-e-3"}
FORMATS = {".png": "png", ".jpg": "jpeg", ".jpeg": "jpeg", ".webp": "webp"}
MAX_INPUT_BYTES = 50 * 1024 * 1024


def _load_env_chain() -> None:
    """Existing environment wins over local dotenv files."""
    load_dotenv(Path.cwd() / ".env", override=False)
    load_dotenv(Path.home() / ".env", override=False)


def slugify(text: str, max_len: int = 30) -> str:
    cleaned = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    return re.sub(r"[-\s]+", "-", cleaned)[:max_len] or "image"


def default_output_path(prompt: str, extension: str) -> Path:
    cwd = Path.cwd()
    target = cwd / "fig" if (cwd / "fig").is_dir() else cwd
    stamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
    return target / f"{stamp}-{slugify(prompt)}.{extension}"


def resolve_size(value: str) -> str:
    return SIZE_SHORTCUTS.get(value.lower(), value.lower())


def model_rejects_input_fidelity(model: str) -> bool:
    """Only Image 2's documented aliases have the fixed-fidelity restriction."""
    return model.strip() in IMAGE_2_MODELS


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="gpt-image",
        description="Generate or edit with GPT Image 2.5 Flare using the official OpenAI SDK.",
    )
    p.add_argument("--version", action="version", version=f"gpt-image {__version__} (default: {DEFAULT_MODEL})")
    p.add_argument("-p", "--prompt", required=True, help="Image brief or edit instruction; up to 32,000 characters.")
    p.add_argument("-f", "--file", help="Output path. Encoding follows --format or a PNG/JPEG/WebP extension; default PNG.")
    p.add_argument("-i", "--image", action="append", type=Path, help="Reference file; repeat in prompt order. Uses the edits endpoint.")
    p.add_argument("-m", "--mask", type=Path, help="PNG alpha mask for the first PNG input: transparent = edit, opaque = preserve.")
    p.add_argument("--model", default=DEFAULT_MODEL, help=f"Explicit model ID. Default: {DEFAULT_MODEL}; Sunburst: gpt-image-2.5-sunburst.")
    p.add_argument("--size", default=DEFAULT_SIZE, help="auto, WIDTHxHEIGHT, or 1k/2k/4k/portrait/landscape/square/wide/tall. Default: 1024x1024. 2.5: 16px multiples, max edge 3840, max ratio 3:1, 655360–8294400 pixels; above 3686400 experimental.")
    p.add_argument("--quality", default="high", choices=["auto", "low", "medium", "high", "xhigh", "max"], help="Default high (API default auto). xhigh/max require 2.5; compare results, latency, and cost.")
    p.add_argument("-n", "--n", type=int, default=1, help="Output variants for this prompt, 1–10. Default 1.")
    p.add_argument("--background", choices=["auto", "opaque", "transparent"], help="Default API auto. transparent requires PNG or WebP.")
    p.add_argument("--moderation", choices=["auto", "low"], help="Generation default low; edits use API default unless explicitly set.")
    p.add_argument("--input-fidelity", choices=["low", "high"], help="Optional edit control. Omitted by default; unavailable for Image 2's exact aliases. 2.5 values are forwarded without an assumed default.")
    p.add_argument("--format", dest="output_format", choices=["png", "jpeg", "webp"], help="Output encoding; otherwise inferred from the filename, default png.")
    p.add_argument("--compression", dest="output_compression", type=int, help="0–100, JPEG/WebP only. Omitted by default.")
    p.add_argument("--user", help="Optional end-user identifier passed to OpenAI.")
    return p.parse_args(argv)


def _inspect_input(path: Path, flag: str) -> tuple[str, tuple[int, int], bool]:
    if not path.is_file():
        raise ValueError(f"{flag} file not found: {path}")
    if path.stat().st_size >= MAX_INPUT_BYTES:
        raise ValueError(f"{flag} must be below 50 MB: {path}")
    try:
        with Image.open(path) as image:
            image_format = image.format or ""
            size = image.size
            has_alpha = "A" in image.getbands() or "transparency" in image.info
            image.verify()
    except (OSError, ValueError, UnidentifiedImageError, Image.DecompressionBombError) as exc:
        raise ValueError(f"{flag} is not a readable image: {path}") from exc
    if image_format not in {"PNG", "JPEG", "WEBP"}:
        raise ValueError(f"{flag} must contain PNG, JPEG, or WebP data: {path}")
    return image_format, size, has_alpha


def validate_args(args: argparse.Namespace) -> Path:
    """Validate before opening an API client, and resolve effective output options."""
    if not args.prompt.strip() or len(args.prompt) > 32000:
        raise ValueError("--prompt must contain 1–32,000 characters of text")
    args.model = args.model.strip()
    if not args.model:
        raise ValueError("--model must not be empty")
    if not 1 <= args.n <= 10:
        raise ValueError("--n must be between 1 and 10")
    if args.quality in {"xhigh", "max"} and args.model in LEGACY_QUALITY_MODELS:
        raise ValueError(f"{args.model} does not support --quality {args.quality}; choose low/medium/high/auto or explicitly select a 2.5 model")
    args.size = resolve_size(args.size)
    if args.size != "auto":
        match = re.fullmatch(r"([1-9]\d*)x([1-9]\d*)", args.size)
        if not match:
            raise ValueError("--size must be auto, WIDTHxHEIGHT, or a documented shortcut")
        width, height = map(int, match.groups())
        if args.model in IMAGE_25_MODELS | IMAGE_2_MODELS:
            if (width % 16 or height % 16 or max(width, height) > 3840
                    or max(width, height) > 3 * min(width, height)
                    or not 655360 <= width * height <= 8294400):
                raise ValueError("--size requires 16px multiples, edges ≤3840, ratio ≤3:1, and 655360–8294400 total pixels")
        elif args.model in OLDER_IMAGE_MODELS and args.size not in {"1024x1024", "1024x1536", "1536x1024"}:
            raise ValueError(f"{args.model} requires 1024x1024, 1024x1536, 1536x1024, or auto")
    if args.mask and not args.image:
        raise ValueError("--mask requires --image")
    if args.input_fidelity and not args.image:
        raise ValueError("--input-fidelity requires --image")
    if args.input_fidelity and model_rejects_input_fidelity(args.model):
        raise ValueError(f"{args.model} always uses high input fidelity; omit --input-fidelity")
    inputs = []
    if args.image:
        if len(args.image) > 16:
            raise ValueError("at most 16 --image references are supported")
        args.image = [path.expanduser().resolve() for path in args.image]
        inputs = [_inspect_input(path, "--image") for path in args.image]
    if args.mask:
        args.mask = args.mask.expanduser().resolve()
        mask_format, mask_size, has_alpha = _inspect_input(args.mask, "--mask")
        if mask_format != "PNG" or inputs[0][0] != "PNG":
            raise ValueError("--mask and the first --image must be PNG; convert the edit target without changing its dimensions")
        if mask_size != inputs[0][1] or not has_alpha:
            raise ValueError("--mask needs an alpha channel and the same pixel dimensions as the first --image")
    out = Path(args.file).expanduser().resolve() if args.file else None
    suffix_format = FORMATS.get(out.suffix.lower()) if out else None
    if out and out.suffix and suffix_format is None:
        raise ValueError("--file must use a .png, .jpg, .jpeg, or .webp extension (or no extension)")
    if args.output_format and suffix_format and args.output_format != suffix_format:
        raise ValueError(f"--format {args.output_format} conflicts with --file extension {out.suffix}")
    args.output_format = args.output_format or suffix_format or "png"
    if args.background == "transparent" and args.output_format == "jpeg":
        raise ValueError("transparent backgrounds require --format png or webp, not jpeg")
    if args.output_compression is not None:
        if not 0 <= args.output_compression <= 100:
            raise ValueError("--compression must be between 0 and 100")
        if args.output_format == "png":
            raise ValueError("--compression is only supported for JPEG/WebP; omit it for PNG")
    if out is None:
        out = default_output_path(args.prompt, args.output_format)
    elif not out.suffix:
        out = out.with_suffix("." + args.output_format)
    if out.is_dir():
        raise ValueError(f"output path is a directory: {out}")
    return out


def _filter_none(values: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in values.items() if value is not None}


def _output_params(args: argparse.Namespace) -> dict[str, Any]:
    return _filter_none({
        "model": args.model, "prompt": args.prompt, "size": resolve_size(args.size),
        "quality": args.quality, "n": args.n, "background": args.background,
        "output_format": args.output_format, "output_compression": args.output_compression,
        "user": args.user,
    })


def call_generate(client: OpenAI, args: argparse.Namespace) -> Any:
    return client.images.generate(**_output_params(args), moderation=args.moderation or DEFAULT_MODERATION)


def call_edit(client: OpenAI, args: argparse.Namespace) -> Any:
    # ExitStack also closes earlier handles if opening a later input fails.
    with ExitStack() as stack:
        values = _output_params(args)
        values["image"] = [stack.enter_context(path.open("rb")) for path in args.image]
        if args.mask:
            values["mask"] = stack.enter_context(args.mask.open("rb"))
        if args.input_fidelity:
            values["input_fidelity"] = args.input_fidelity
        if args.moderation:
            # SDK 3.9 has no edit moderation keyword; extra_body works with multipart.
            values["extra_body"] = {"moderation": args.moderation}
        return client.images.edit(**values)


def write_outputs(
    data: list[Any], out_path: Path, n: int, *, expected_format: str | None = None,
    transparent: bool = False, expected_size: str = "auto",
) -> list[Path]:
    if not data:
        raise ValueError("the API returned no image data")
    decoded = []
    for index, item in enumerate(data):
        if getattr(item, "b64_json", None):
            try:
                raw = base64.b64decode(item.b64_json, validate=True)
            except (ValueError, binascii.Error) as exc:
                raise ValueError(f"response image {index} contains invalid base64") from exc
        elif getattr(item, "url", None):
            with urllib.request.urlopen(item.url, timeout=300) as response:
                raw = response.read()
        else:
            raise ValueError(f"response image {index} has neither image bytes nor a URL")
        try:
            with Image.open(io.BytesIO(raw)) as image:
                image.load()
                actual_format = (image.format or "").lower()
                if expected_format and actual_format != expected_format:
                    raise ValueError(f"response image {index} is {actual_format}, expected {expected_format}")
                if expected_size != "auto" and image.size != tuple(map(int, expected_size.split("x"))):
                    raise ValueError(f"response image {index} has dimensions {image.width}x{image.height}, expected {expected_size}")
                if transparent and image.convert("RGBA").getchannel("A").getextrema()[0] == 255:
                    raise ValueError(f"response image {index} has no transparent pixels despite --background transparent")
        except (OSError, UnidentifiedImageError, Image.DecompressionBombError) as exc:
            raise ValueError(f"response image {index} is not a readable image") from exc
        decoded.append(raw)
    # Validate the complete response before writing any files; preserve original bytes.
    out_path.parent.mkdir(parents=True, exist_ok=True)
    multiple = n > 1 or len(decoded) > 1
    written = []
    for index, raw in enumerate(decoded):
        target = out_path.with_name(f"{out_path.stem}_{index}{out_path.suffix}") if multiple else out_path
        target.write_bytes(raw)
        written.append(target)
    return written


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        out_path = validate_args(args)
    except (ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    _load_env_chain()
    if not os.environ.get("OPENAI_API_KEY"):
        print("error: OPENAI_API_KEY is not set in the environment, .env, or ~/.env. Configure it locally and retry.", file=sys.stderr)
        return 2
    try:
        with OpenAI() as client:
            result = call_edit(client, args) if args.image else call_generate(client, args)
        paths = write_outputs(
            result.data or [], out_path, args.n, expected_format=args.output_format,
            transparent=args.background == "transparent", expected_size=args.size,
        )
    except APIError as exc:
        request_id = getattr(exc, "request_id", None)
        detail = f" (request {request_id})" if request_id else ""
        print(f"error: {type(exc).__name__}{detail}: {exc.message}", file=sys.stderr)
        return 1
    except TypeError as exc:
        print(f"error: incompatible CLI/SDK request: {exc}. Use gpt-image-cli ≥0.3.0 with openai ≥3.9.0.", file=sys.stderr)
        return 2
    except (ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    for path in paths:
        print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
