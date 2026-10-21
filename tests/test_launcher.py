import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest

PATH = Path(__file__).resolve().parents[1] / "skills/gpt-image/scripts/generate.py"
spec = importlib.util.spec_from_file_location("skill_launcher", PATH)
launcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)


def test_repo_backend_is_current():
    assert callable(launcher._import_local_or_installed_main())


def test_old_path_backend_is_rejected_before_generation(monkeypatch):
    calls = []

    def run(command, **kwargs):
        calls.append(command)
        return SimpleNamespace(returncode=0, stdout="gpt-image 0.2.0")

    monkeypatch.setattr(launcher.subprocess, "run", run)
    with pytest.raises(RuntimeError, match="older than required"):
        launcher._delegate(["gpt-image"])
    assert calls == [["gpt-image", "--version"]]


def test_current_delegate_preserves_explicit_arguments(monkeypatch):
    calls = []

    def run(command, **kwargs):
        calls.append(command)
        return SimpleNamespace(returncode=0, stdout="gpt-image 0.3.0 (default: gpt-image-2.5-flare)")

    monkeypatch.setattr(launcher.subprocess, "run", run)
    monkeypatch.setattr(launcher.sys, "argv", ["generate.py", "--model", "gpt-image-2.5-sunburst", "--quality", "max", "-p", "A mug"])
    assert launcher._delegate(["gpt-image"]) == 0
    assert calls[1][1:] == launcher.sys.argv[1:]


def test_uv_fallback_is_checked_without_discarding_flags(monkeypatch):
    commands = []
    monkeypatch.setattr(launcher, "_import_local_or_installed_main", lambda: None)
    monkeypatch.setattr(launcher.shutil, "which", lambda name: "/bin/uv" if name == "uv" else None)
    monkeypatch.setattr(launcher, "_delegate", lambda command: commands.append(command) or 0)
    assert launcher.main() == 0
    assert commands == [["/bin/uv", "tool", "run", "--from", launcher._REPO_URL, "gpt-image"]]
