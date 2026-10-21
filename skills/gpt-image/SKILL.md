---
name: gpt-image
description: "Generate and edit images through the OpenAI Images API, defaulting to GPT Image 2.5 Flare. Use for explicit GPT Image requests, reference-guided artwork, style transfer, precise image edits, inpainting, transparent assets, posters, typography, UI concepts, and diagrams. Use the packaged CLI; inspect references and assign their roles before generation."
metadata: {"openclaw":{"requires":{"anyBins":["gpt-image","uv","uvx"]},"primaryEnv":"OPENAI_API_KEY","homepage":"https://github.com/wuyoscar/gpt_image_2_skill"}}
---

# GPT Image

**Requirements:** Python 3.11+ and gpt-image-cli 0.3.0+ or uv/uvx. Requires `OPENAI_API_KEY`; API calls may incur charges.

Produce a usable image from the user's brief and references with the packaged `gpt-image` CLI. The default is **`gpt-image-2.5-flare`**, quality **high**, **1024×1024**, one image. Honor an explicit model choice; use `gpt-image-2.5-sunburst` when requested or when comparison shows it improves a requirement that Flare missed. Never silently substitute another model after an API error.

## Work through the image

1. **Understand the deliverable.** Identify the intended use, subject, required copy, composition, output format and any constraints that affect the picture. A clear request is enough to proceed. Resolve ordinary design choices yourself; ask only when a missing answer materially affects the result and cannot be inferred.
2. **Inspect supplied references.** Open the actual images. Assign their roles in attachment order: edit base, subject/identity, style, layout, or exact artwork. Describe what to preserve or borrow from each. A filename or written description does not attach an image. Read [reference-images.md](references/reference-images.md) for multi-reference work, masks, successive edits, or transparency.
3. **Write the brief and choose controls.** State the intended image, then the visible details and constraints that matter. Quote required copy verbatim. For edits, name the change and the properties to preserve. Consult [craft.md](references/craft.md) for a difficult prompt or [gallery.md](references/gallery.md) when an example would help; neither is a prerequisite for a simple request. Start from the user's prompt when comparing models. Check [model-api.md](references/model-api.md) for parameter limits or unfamiliar settings.
4. **Execute with the existing CLI.** Use the commands below; normal image work does not need a new SDK wrapper. No reference uses generations; any `-i` uses edits, including creation of a new scene from references. For a follow-up, attach the latest accepted image and preserve earlier accepted changes in the new prompt. Choose another output filename so the accepted image remains available.
5. **Inspect and deliver.** Open the result and check the brief: identity, copy, layout, style, changed region, and retained details as relevant. The CLI checks decoding, format, requested dimensions, and real alpha when requested; visual inspection still determines success. Return the actual output path and any material defect. If a requirement fails, make a focused correction or compare a higher quality setting; do not claim an uninspected result is correct.

## Execute

Check `gpt-image --version` before relying on an existing PATH installation. This skill expects **0.3.0+** and a Flare default. Prefer the bundled launcher when the existing command is stale or its source is unclear:

```bash
# Existing compatible installation
gpt-image -p 'A cream ceramic mug with a cobalt handle on linen, lit by a morning window. Product photo, visible glaze texture, empty space above, no text.' -f mug.png

# Use the skill directory supplied by the runtime, not an assumed home path
uv run "$SKILL_DIR/scripts/generate.py" -p 'YOUR BRIEF' -f image.png

# An explicit model choice
gpt-image --model gpt-image-2.5-sunburst -p 'YOUR BRIEF' --quality xhigh -f image-sunburst.png

# Actual files in the same order as the prompt's image numbers
gpt-image -i subject.png -i style.png -p 'Image 1 supplies the subject and markings. Image 2 supplies only pencil contours, ochre/blue shapes, and paper grain. Illustrate the subject from Image 1 beside a doorway; exclude Image 2’s people and lettering.' -f illustration.png
```

The launcher resolves repo-local Python module → installed module → PATH command → transient `uvx`/`uv` backend. It rejects backends older than 0.3.0 before sending an image request. If the remote package has not been updated yet, use this updated checkout with `uv run gpt-image` or explicitly install from it; do not bypass the version guard.

Keep setup proportional to the request. Use existing tools and credentials. Do not overwrite shared skill folders or create secret files during ordinary generation. A requested setup/update authorizes the corresponding installation work. This skill owns direct Images API execution. If the user chooses a host-managed image tool, use that tool's contract and report only the model selection it actually exposes. Do not promise that a host's generic image tool selects Flare or Sunburst. Extracting a reusable prompt from an image without generating an output belongs to `get-prompt-from-image`.

## Controls that change the result

| Control | CLI behavior |
|---|---|
| `--model` | Flare by default; Sunburst and explicit model IDs pass through. Dated 2.5 snapshots are documented in [model-api.md](references/model-api.md). |
| `--quality` | `auto`, `low`, `medium`, `high`, `xhigh`, `max`; CLI default `high`, API default `auto`. `xhigh`/`max` are 2.5 controls. |
| `--size` | `auto`, literal `WIDTHxHEIGHT`, or a shortcut below. Match the actual canvas to the requested ratio. |
| `-i, --image` / `-m, --mask` | Repeat `-i` in prompt order; mask applies to the first input. A mask guides an edit; it does not guarantee unchanged pixels elsewhere. |
| `--background` / `--format` | `auto`, `opaque`, `transparent`; PNG/JPEG/WebP. Real transparency needs PNG/WebP and `--background transparent` on each applicable call. |

Other options: required `-p/--prompt`; `-f/--file`; `-n/--n` (1–10); JPEG/WebP `--compression` (0–100); `--moderation auto|low`; optional edit `--input-fidelity low|high`; `--user`; `--version`. Full semantics and restrictions live in [model-api.md](references/model-api.md), and `gpt-image --help` lists the executable interface.

| Shortcut | Pixels | Ratio |
|---|---|---|
| `1k`, `square` | 1024×1024 | 1:1 |
| `portrait`, `landscape` | 1024×1536 / 1536×1024 | 2:3 / 3:2 |
| `wide` | 2048×1152 | 16:9 |
| `2k` | 2048×2048 | 1:1; experimental pixel area |
| `4k`, `tall` | 3840×2160 / 2160×3840 | 16:9 / 9:16; experimental pixel area |

For 3:4 use `1152x1536`; for 4:3 use `1536x1152`; for 2:1 use `2048x1024`. A camera resolution mentioned in a prompt does not set API dimensions. Outputs above 3,686,400 pixels are experimental. Do not choose `4k` just because the deliverable is a hero image or a print asset.

Use the existing high default for the first migration comparison, with prompt, references, size and format held constant. If a requirement fails, compare `xhigh` or `max` before expanding the prompt. Once an output meets the brief, lower quality may reduce latency/cost. Inspect the result; no quality setting guarantees exact lettering or identity. `-n` produces variants of one request, not a coordinated sequence of different scenes.

## Credentials, errors, and files

Credentials load from process `OPENAI_API_KEY`, then the current directory's `.env`, then `~/.env`, without overwriting existing values. Never print a key. Unsetting the process variable does **not** disable dotenv loading: if the user declines local-key use, do not call this CLI. Missing credentials require local configuration by the user or an already-authorized setup path.

Successful stdout contains output paths only. Automatic filenames use the current directory, or its `fig/` subdirectory if present. An extension can select PNG/JPEG/WebP; an explicit conflicting `--format` is rejected. Multiple outputs receive `_0`, `_1`, … suffixes. Explicit existing filenames may be overwritten on success, so retain accepted edits under new filenames.

Exit codes: `0` success, `1` API or output failure, `2` invalid input/configuration. Surface the actionable API error and request ID when available. A model-access or parameter error requires correcting access or the request, not silently changing model, dropping references, or claiming a result.

## Reference shelf

| Read when | Reference |
|---|---|
| API/model/size/quality questions | [model-api.md](references/model-api.md), current contract, checked 2026-09-08 |
| Reference roles, masks, chained edits, alpha | [reference-images.md](references/reference-images.md) |
| Exact text, art direction, layouts, prompt repair | [craft.md](references/craft.md) |
| A concrete example helps | [gallery.md](references/gallery.md) → [2.5 recipes](references/gallery-gpt-image-2-5.md) or a relevant historical category |
| Historical cookbook provenance | [openai-cookbook.md](references/openai-cookbook.md), archived Image 2-era material; current contract takes precedence |

Load the smallest useful slice. Preserve prompt attribution separately from the actual generating model and output provenance. The old gallery is historical; its previews are not evidence of 2.5 performance.
