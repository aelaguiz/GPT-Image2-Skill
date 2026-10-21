#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "openai>=3.9.0",
#     "python-dotenv>=1.0",
#     "pillow>=11.3",
# ]
# ///
"""Skill launcher for the shared gpt-image CLI.

Resolution order:
1. Repo checkout / full plugin install: import ../../../src/gpt_image_cli/cli.py.
2. Python environment already has gpt_image_cli installed: import it directly.
3. Shell has a gpt-image executable: delegate to it.
4. Final fallback: uvx installs/runs the GitHub CLI package transiently.

This keeps `skills/gpt-image` usable when copied as a standalone skill folder
while preserving one canonical implementation for the installable Python CLI.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import re
from pathlib import Path

_REPO_URL = "git+https://github.com/wuyoscar/gpt_image_2_skill"
_MIN_BACKEND = (0, 3, 0)


def _compatible_version(value: str) -> bool:
    match = re.search(r"\b(\d+)\.(\d+)\.(\d+)\b", value)
    return bool(match and tuple(map(int, match.groups())) >= _MIN_BACKEND)


def _old_backend(version: str) -> RuntimeError:
    return RuntimeError(
        f"gpt-image CLI backend {version!r} is older than required 0.3.0. "
        "Install an updated checkout with 'uv tool install /path/to/checkout' "
        "or upgrade to the published 0.3.0+ release, then retry. No image request was sent."
    )


def _import_local_or_installed_main():
    """Return gpt_image_cli.cli.main from repo-local src or installed package."""
    script_path = Path(__file__).resolve()

    # Full plugin/repo layout: <repo>/skills/gpt-image/scripts/generate.py
    # Standalone skill installs do not have this sibling src/ tree, so guard it.
    if len(script_path.parents) > 3:
        repo_src = script_path.parents[3] / "src"
        if (repo_src / "gpt_image_cli" / "cli.py").is_file():
            sys.path.insert(0, str(repo_src))

    try:
        from gpt_image_cli import __version__
        from gpt_image_cli.cli import main  # type: ignore
    except ModuleNotFoundError as exc:
        if exc.name == "gpt_image_cli":
            return None
        raise RuntimeError(f"CLI backend dependency is missing: {exc.name}. Run with uv or install the matching CLI package.") from exc
    except ImportError as exc:
        raise _old_backend("unversioned") from exc
    if not _compatible_version(__version__):
        raise _old_backend(__version__)
    return main


def _delegate(command: list[str]) -> int:
    """Check the actual backend before delegating any generation request."""
    check = subprocess.run(command + ["--version"], check=False, capture_output=True, text=True)
    if check.returncode or not _compatible_version(check.stdout):
        raise _old_backend(check.stdout.strip() or "unknown")
    completed = subprocess.run(command + sys.argv[1:], check=False)
    return completed.returncode


def _run() -> int:
    cli_main = _import_local_or_installed_main()
    if cli_main is not None:
        return int(cli_main() or 0)

    executable = shutil.which("gpt-image")
    if executable:
        return _delegate([executable])

    uvx = shutil.which("uvx") or shutil.which("uv")
    if uvx:
        if Path(uvx).name == "uv":
            return _delegate([uvx, "tool", "run", "--from", _REPO_URL, "gpt-image"])
        return _delegate([uvx, "--from", _REPO_URL, "gpt-image"])

    print(
        "error: could not find the gpt-image CLI backend. Install uv and run this skill "
        "again, or install the CLI first with:\n"
        f"  uv tool install {_REPO_URL}\n"
        "Then retry the same command.",
        file=sys.stderr,
    )
    return 2


def main() -> int:
    try:
        return _run()
    except (RuntimeError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
