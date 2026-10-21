import base64
import io
import json
from email.parser import BytesParser
from email.policy import default
from types import SimpleNamespace

import httpx2
import pytest
from openai import OpenAI
from PIL import Image

from gpt_image_cli import cli


def png(size=(1024, 1024), alpha=255, image_format="PNG"):
    image = Image.new("RGBA", size, (35, 90, 160, alpha))
    if image_format == "JPEG":
        image = image.convert("RGB")
    buffer = io.BytesIO()
    image.save(buffer, format=image_format)
    return buffer.getvalue()


@pytest.fixture
def images(tmp_path):
    paths = [tmp_path / name for name in ("subject.png", "style.png", "mask.png")]
    for index, path in enumerate(paths):
        path.write_bytes(png((32, 32), alpha=0 if index == 2 else 255))
    return paths


@pytest.fixture
def api(monkeypatch):
    calls = []
    options = {"status": 200, "count": None}

    def handle(request):
        raw = request.read()
        content_type = request.headers.get("content-type", "")
        if content_type.startswith("multipart/"):
            message = BytesParser(policy=default).parsebytes(
                ("Content-Type: " + content_type + "\r\nMIME-Version: 1.0\r\n\r\n").encode() + raw
            )
            body, files = {}, []
            for part in message.iter_parts():
                name = part.get_param("name", header="content-disposition")
                if part.get_filename():
                    files.append((name, part.get_filename()))
                else:
                    body[name] = part.get_payload(decode=True).decode()
            body["files"] = files
        else:
            body = json.loads(raw)
        calls.append((request.url.path, body))
        if options["status"] != 200:
            return httpx2.Response(options["status"], json={"error": {"message": "Model access denied", "type": "invalid_request_error", "code": "model_not_found"}})
        size = tuple(map(int, body["size"].split("x"))) if body["size"] != "auto" else (1024, 1024)
        encoded = base64.b64encode(png(size, alpha=0 if body.get("background") == "transparent" else 255,
                                      image_format=body.get("output_format", "png").upper())).decode()
        count = int(body["n"]) if options["count"] is None else options["count"]
        return httpx2.Response(200, json={"created": 1, "data": [{"b64_json": encoded}] * count,
                                         "quality": body["quality"], "size": body["size"]})

    def client():
        return OpenAI(api_key="offline-test", base_url="https://mock.invalid/v1", max_retries=0,
                      http_client=httpx2.Client(transport=httpx2.MockTransport(handle)))

    monkeypatch.setattr(cli, "OpenAI", client)
    monkeypatch.setattr(cli, "_load_env_chain", lambda: None)
    monkeypatch.setenv("OPENAI_API_KEY", "offline-test")
    return calls, options


def test_default_request_and_saved_output(api, tmp_path, capsys):
    target = tmp_path / "mug.png"
    assert cli.main(["-p", "A ceramic mug", "-f", str(target)]) == 0
    path, body = api[0][0]
    assert path == "/v1/images/generations"
    assert body["model"] == "gpt-image-2.5-flare"
    assert body["quality"] == "high" and body["size"] == "1024x1024"
    assert body["moderation"] == "low"
    assert "input_fidelity" not in body and "output_compression" not in body
    assert capsys.readouterr().out.strip() == str(target)
    with Image.open(target) as image:
        assert image.format == "PNG" and image.size == (1024, 1024)


@pytest.mark.parametrize("model", sorted(cli.IMAGE_25_MODELS))
@pytest.mark.parametrize("quality", ["xhigh", "max"])
def test_new_quality_and_model_ids_survive_sdk(api, tmp_path, model, quality):
    assert cli.main(["-p", "A label", "--model", model, "--quality", quality,
                     "--size", "1536x864", "-f", str(tmp_path / "label.png")]) == 0
    assert api[0][0][1]["model"] == model
    assert api[0][0][1]["quality"] == quality


@pytest.mark.parametrize("model", ["gpt-image-2.5-flare", "gpt-image-2.5-sunburst"])
@pytest.mark.parametrize("quality", ["xhigh", "max"])
def test_edits_keep_reference_order_mask_alpha_and_explicit_controls(api, images, tmp_path, model, quality):
    output = tmp_path / "cutout.webp"
    argv = ["-p", "Recolor the cap", "-i", str(images[0]), "-i", str(images[1]), "-m", str(images[2]),
            "--model", model, "--input-fidelity", "high", "--quality", quality, "--background", "transparent",
            "--moderation", "low", "--compression", "85", "-f", str(output)]
    assert cli.main(argv) == 0
    path, body = api[0][0]
    assert path == "/v1/images/edits"
    assert [name for _, name in body["files"]] == ["subject.png", "style.png", "mask.png"]
    assert body["model"] == model and body["input_fidelity"] == "high" and body["quality"] == quality
    assert body["moderation"] == "low" and body["output_compression"] == "85"
    with Image.open(output) as image:
        assert image.format == "WEBP" and image.getchannel("A").getextrema()[0] == 0


def test_omitted_edit_controls_are_not_injected(api, images, tmp_path):
    assert cli.main(["-p", "Change only the price", "-i", str(images[0]), "-f", str(tmp_path / "edit.png")]) == 0
    body = api[0][0][1]
    assert "moderation" not in body and "input_fidelity" not in body


def test_explicit_legacy_and_unknown_models_are_honored(api, tmp_path):
    for model in ["gpt-image-2", "an-explicit-future-model"]:
        assert cli.main(["-p", "A mug", "--model", model, "-f", str(tmp_path / "mug.png")]) == 0
        assert api[0][-1][1]["model"] == model


@pytest.mark.parametrize("extra", [
    ["--size", "4096x2048"], ["--size", "1025x1024"], ["--size", "512x512"],
    ["--size", "3840x3840"], ["--size", "3072x768"], ["--size", "wide-ish"],
    ["--n", "0"], ["--n", "11"], ["--compression", "90"],
    ["--format", "jpeg", "--background", "transparent"],
    ["--format", "webp", "--compression", "101"],
    ["--input-fidelity", "high"], ["--model", "gpt-image-2", "--quality", "max"],
    ["--model", "gpt-image-1.5", "--size", "1536x864"],
])
def test_invalid_arguments_fail_before_api_or_credentials(monkeypatch, tmp_path, extra, capsys):
    monkeypatch.setattr(cli, "_load_env_chain", lambda: pytest.fail("credentials loaded for invalid arguments"))
    assert cli.main(["-p", "A mug", "-f", str(tmp_path / "out"), *extra]) == 2
    assert capsys.readouterr().err.startswith("error:")


def test_rejects_exact_image2_fidelity_without_dropping_user_flag(api, images, tmp_path):
    assert cli.main(["-p", "An edit", "-i", str(images[0]), "--model", "gpt-image-2-2026-04-21",
                     "--input-fidelity", "high", "-f", str(tmp_path / "edit.png")]) == 2
    assert not api[0]


def test_bad_masks_and_missing_references_fail_locally(api, images, tmp_path):
    bad = tmp_path / "bad-mask.png"
    Image.new("RGB", (32, 32)).save(bad)
    for mask in [bad, tmp_path / "absent.png"]:
        assert cli.main(["-p", "An edit", "-i", str(images[0]), "-m", str(mask)]) == 2
    bad.write_bytes(png((16, 16), alpha=0))
    assert cli.main(["-p", "An edit", "-i", str(images[0]), "-m", str(bad)]) == 2
    assert cli.main(["-p", "An edit", "-i", str(tmp_path / "missing.png")]) == 2
    assert cli.main(["-p", "An edit", "-m", str(images[2])]) == 2
    assert not api[0]


def test_too_many_references_fail_before_api(api, images):
    args = ["-p", "An edit"] + [part for _ in range(17) for part in ["-i", str(images[0])]]
    assert cli.main(args) == 2
    assert not api[0]


def test_encoding_inferred_and_conflicts_rejected(api, tmp_path):
    assert cli.main(["-p", "A mug", "-f", str(tmp_path / "mug.jpg")]) == 0
    assert api[0][0][1]["output_format"] == "jpeg"
    assert cli.main(["-p", "A mug", "-f", str(tmp_path / "mug.png"), "--format", "webp"]) == 2
    assert len(api[0]) == 1


def test_access_error_does_not_fallback(api, tmp_path, capsys):
    api[1]["status"] = 403
    assert cli.main(["-p", "A mug", "-f", str(tmp_path / "mug.png")]) == 1
    assert len(api[0]) == 1 and api[0][0][1]["model"] == "gpt-image-2.5-flare"
    assert "Model access denied" in capsys.readouterr().err
    assert not list(tmp_path.glob("*.png"))


def test_empty_response_is_an_error(api, tmp_path):
    api[1]["count"] = 0
    assert cli.main(["-p", "A mug", "-f", str(tmp_path / "mug.png")]) == 1
    assert not list(tmp_path.glob("*.png"))


def test_batch_output_preserves_bytes_and_never_collapses_multiple_results(tmp_path):
    raw = png(alpha=0)
    item = SimpleNamespace(b64_json=base64.b64encode(raw).decode())
    paths = cli.write_outputs([item, item], tmp_path / "logo.png", 1, expected_format="png", transparent=True)
    assert [path.name for path in paths] == ["logo_0.png", "logo_1.png"]
    assert all(path.read_bytes() == raw for path in paths)


@pytest.mark.parametrize("kind", ["malformed", "opaque", "wrong-format", "wrong-size"])
def test_invalid_output_does_not_overwrite_existing_file(tmp_path, kind):
    target = tmp_path / "protected.png"
    target.write_bytes(b"existing asset")
    data = "not base64!" if kind == "malformed" else base64.b64encode(png()).decode()
    kwargs = {"transparent": kind == "opaque", "expected_format": "webp" if kind == "wrong-format" else "png",
              "expected_size": "1536x864" if kind == "wrong-size" else "auto"}
    with pytest.raises(ValueError):
        cli.write_outputs([SimpleNamespace(b64_json=data)], target, 1, **kwargs)
    assert target.read_bytes() == b"existing asset"


def test_input_handles_close_on_api_failure(images):
    handles = []

    def fail(**kwargs):
        handles.extend(kwargs["image"] + [kwargs["mask"]])
        raise RuntimeError("transport failed")

    args = cli.parse_args(["-p", "An edit", "-i", str(images[0]), "-m", str(images[2])])
    cli.validate_args(args)
    with pytest.raises(RuntimeError):
        cli.call_edit(SimpleNamespace(images=SimpleNamespace(edit=fail)), args)
    assert all(handle.closed for handle in handles)
