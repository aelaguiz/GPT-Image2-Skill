# GPT Image 2.5 model and API contract

Checked **2026-09-08** against current OpenAI documentation. This file owns model and parameter facts for this skill. The archived cookbook and historical gallery do not override it. Recheck the linked primary source before asserting a later change.

## Model selection

| Choice | API model ID | Use |
|---|---|---|
| Default | `gpt-image-2.5-flare` | General generation/editing; speed-oriented 2.5 variant |
| Explicit alternative | `gpt-image-2.5-sunburst` | Compare when precision or visual quality remains unmet |
| Pinned Flare | `gpt-image-2.5-flare-2026-09-08` | Reproducible version selection |
| Pinned Sunburst | `gpt-image-2.5-sunburst-2026-09-08` | Reproducible version selection |
| Historical baseline | `gpt-image-2` | Explicit compatibility or controlled migration comparison |

Aliases may advance; a dated snapshot pins the model, not a deterministic image. There is no documented seed flag in this CLI. Both 2.5 variants accept text and image inputs and support generation, editing, and inpainting. OpenAI describes Flare as up to 50% lower latency than Image 2; treat this as a release claim, not a promised per-call speedup. [Flare model](https://developers.openai.com/api/docs/models/gpt-image-2.5-flare), [Sunburst model](https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst), [release](https://openai.com/index/introducing-chatgpt-images-2-5/).

Explicit `--model` is honored. Known older models reject `xhigh`/`max` locally. Unknown future IDs pass through without guessed model-specific limits; the API remains responsible for their support. Do not turn an access error into automatic fallback. Legacy IDs remain available where their request controls are compatible; this CLI does not promise complete DALL·E compatibility.

## Endpoints and defaults

| Request | Endpoint | SDK method |
|---|---|---|
| No reference files | `POST /v1/images/generations` | `client.images.generate(...)` |
| One or more reference files | `POST /v1/images/edits` | `client.images.edit(...)`, multipart uploads |
| References plus mask | Same edits endpoint | Mask applies to the **first** image |

A new composition made from reference images still uses edits. Each CLI invocation is independent: neither filenames nor prior prompts establish server-side image history. [Images guide](https://developers.openai.com/api/docs/guides/image-generation).

| Parameter | Supported values and limits | CLI default / handling |
|---|---|---|
| `model` | IDs above | `gpt-image-2.5-flare` |
| `prompt` | Up to 32,000 characters | Required, nonblank |
| `quality` | `auto`, `low`, `medium`, `high`, `xhigh`, `max` | `high`; the API default is `auto` |
| `size` | `auto` or valid literal dimensions | `1024x1024`; shortcuts expanded before sending |
| `n` | 1–10 | 1; variants from the same prompt |
| `image` | Up to 16 PNG, JPEG or WebP files, each below 50 MB | Ordered repeatable `-i`; actual file uploads |
| `mask` | Alpha mask, same format and dimensions as first image, below 50 MB | CLI accepts a PNG mask with a PNG first input; transparent regions indicate the change |
| `background` | `auto`, `opaque`, `transparent` | Omitted, API `auto`; applicable to generation and edits |
| `output_format` | `png`, `jpeg`, `webp` | Infer from file suffix, otherwise PNG; reject suffix/flag conflict |
| `output_compression` | Integer 0–100, JPEG/WebP only | Omitted; explicit PNG compression is an error |
| `moderation` | `auto`, `low` | Generations retain this CLI's existing `low` default; edits omit unless explicitly supplied |
| `input_fidelity` | Generic edit schema accepts `low`, `high`; see qualification below | Omitted; explicit values forwarded on 2.5 |
| `user` | Optional end-user identifier | Omitted unless provided |

The CLI's 50 MB check uses 50 × 1024 × 1024 bytes as the local ceiling; server limits still apply. Input image dimensions can differ from the desired output; only the mask must match the first input. [Generation schema](https://developers.openai.com/api/reference/resources/images/methods/generate), [edit schema](https://developers.openai.com/api/reference/resources/images/methods/edit), [current guide](https://developers.openai.com/api/docs/guides/image-generation).

**Input fidelity qualification:** current documentation explicitly says the exact Image 2 aliases always use high fidelity and should omit `input_fidelity`. The 2.5-specific default/semantics are not separately stated. Do not apply an `startswith("gpt-image-2")` ban to 2.5. Omit by default; if the user explicitly requests a generic schema value for 2.5, send it and surface any API rejection. The CLI rejects an explicit fidelity flag on `gpt-image-2` and `gpt-image-2-2026-04-21` instead of silently dropping it. No normal 2.5 example depends on this parameter.

The guide permits masks below 50 MB while older SDK docstrings mention 4 MB. This implementation follows the current guide, with conservative PNG format matching. A mask is guidance, not a guarantee that every unmasked pixel remains identical. For exact preservation, composite the accepted edit region over the original with an ordinary image editor.

## Dimensions and quality

For both 2.5 variants, each edge must be a multiple of 16 and at most 3840. The longer edge may be at most three times the shorter edge. Pixel area must be **655,360–8,294,400**. Areas above **3,686,400** are experimental. `auto` delegates size choice; inspect the resulting dimensions. [Size guidance](https://developers.openai.com/api/docs/guides/image-generation).

| Intended shape | Valid literal | Relationship to shortcuts |
|---|---|---|
| Square | `1024x1024` | `1k`, `square`, default |
| 2:3 / 3:2 | `1024x1536` / `1536x1024` | `portrait` / `landscape` |
| 3:4 / 4:3 | `1152x1536` / `1536x1152` | Use literal; `portrait` is not 3:4 |
| 16:9 / 2:1 | `2048x1152` / `2048x1024` | `wide` / literal |
| Large square / landscape / vertical | `2048x2048` / `3840x2160` / `2160x3840` | `2k` / `4k` / `tall`; all experimental by area |

A request for a 1290×2796 phone screen can describe a device being depicted, but those dimensions are not valid API output dimensions. Render on an appropriate valid canvas, or perform a disclosed downstream crop/resize if the deliverable needs other dimensions. Likewise, “8K,” “300 DPI,” or camera EXIF text inside a prompt cannot override API size or create print metadata.

For migration, compare Image 2 and Flare with the **same prompt, ordered references, explicit quality, size and format**. Compare Flare and Sunburst the same way. If a requirement fails, try `xhigh`/`max` before rewriting an already clear brief. After acceptance, lower quality can be evaluated for speed/cost. Record elapsed time, response usage and retries; do not assume every increment helps. [2.5 prompting guide](https://developers.openai.com/api/docs/guides/image-prompting).

## Transparency and outputs

Use `--background transparent --format png` (or WebP) for a cutout. Request transparency again on a transparent-image follow-up. JPEG cannot store alpha. A prompt asking for a checkerboard is not transparency; inspect actual alpha and composite a preview against light and dark backgrounds to check the edges. Image 2 already had transparency preview support; this is not a feature first introduced in 2.5. [Background guidance](https://developers.openai.com/api/docs/guides/image-generation).

The CLI decodes and validates every returned image before writing any result: readable data, requested encoding, explicit output dimensions, and some non-opaque alpha if transparency was requested. It preserves returned bytes without re-encoding. This check does not establish perfect cutout edges, correct copy or edit locality. Multiple results use `_0`, `_1`, … names. Inspection/previews should be separate files, leaving the original result available. OpenAI describes C2PA and SynthID provenance for ChatGPT Images 2.5; do not remove provenance as a cleanup step. [System card](https://deploymentsafety.openai.com/chatgpt-images-2-5).

## Pricing and SDK compatibility

Published **standard** rates for both 2.5 variants, USD per million tokens:

| Token type | Input | Cached input | Output |
|---|---|---|---|
| Image | $8.00 | $2.00 | $30.00 |
| Text | $5.00 | $1.25 | — |

Rates checked 2026-09-08. Equal token rates do not establish equal cost per image: settings, input references, generated tokens and retries matter. Use usage and actual billing to compare cost per accepted output. Do not reuse Image 2 per-image price tables as 2.5 quotes. [Pricing](https://developers.openai.com/api/docs/pricing#image-generation).

The package uses **OpenAI Python SDK ≥3.9.0**, Python ≥3.11, python-dotenv and Pillow. Version 3.9.0 is the inspected and tested floor, not a claim that earlier versions cannot serialize a 2.5 request. Some 3.9.0 type literals omit `xhigh`/`max`; runtime request serialization accepts them. The edit method lacks a named `moderation` keyword, so the canonical CLI uses `extra_body={"moderation": value}` for an explicitly requested edit moderation setting. This preserves the multipart request. [Official SDK v3.9.0](https://github.com/openai/openai-python/tree/v3.9.0).

## Responses API and host tools

The CLI deliberately uses the two Images endpoints. Applications that need retained conversational image state can use the Responses image-generation tool. The top-level model orchestrates the conversation; the image tool's model selects the image variant:

```python
from openai import OpenAI
client = OpenAI()
response = client.responses.create(
    model="gpt-6-astra",
    input="Create a cream ceramic mug product photo with a cobalt handle.",
    tools=[{
        "type": "image_generation",
        "model": "gpt-image-2.5-flare",
        "action": "generate",
        "quality": "high",
        "size": "1024x1024",
    }],
    tool_choice={"type": "image_generation"},
)
```

The tool supports `action="auto"|"generate"|"edit"`. Follow-up applications can use `previous_response_id` and image-generation call IDs according to the guide; the CLI has no such flags. The orchestrator can revise the prompt; retain `revised_prompt` when evaluating what actually ran. Responses also incurs mainline-model costs. Optional partial-image streaming supports 0–3 partials, each adding 100 image output tokens. This is an application integration example, not a command to build a second wrapper for normal skill use. [Responses image tool guide](https://developers.openai.com/api/docs/guides/tools-image-generation).

ChatGPT Sketch, templates, comments and sharing are product interfaces. Ordinary Images API references can carry a supplied sketch or annotation, but there are no corresponding CLI flags. A host-managed image tool may not expose per-variant selection; inspect its runtime contract and do not infer Flare from the name “image generation.” [Release](https://openai.com/index/introducing-chatgpt-images-2-5/), [host image tool documentation](https://learn.chatgpt.com/docs/image-generation).
