# GPT Image 2.5 migration plan

**Target outcome:** `gpt-image` generates and edits with **GPT Image 2.5 Flare by default**, supports deliberate selection of **GPT Image 2.5 Sunburst**, and teaches agents how to preserve subjects, apply visual styles, use sketches, make focused edits, and produce reusable assets with the new models.

**Status:** Research, implementation and live validation complete. The CLI/skill default to Flare at version 0.3.0; 45 behavioral tests and isolated package/launcher checks pass. All ten feature recipes have inspected outputs from **22 successful live requests** (21 GPT Image 2.5, one Image 2 baseline), including one focused campaign correction. See [the implementation validation record](gpt-image-2-5/validation.md) and [actual live outputs](gpt-image-2-5/live/README.md) for timings, usage and observed limits. No global installation or publication was performed.

**Research date:** September 8, 2026. **Repository baseline:** `135d873e1a843db5f122a15ddda02bd2845d4d25`. **Authoring method:** audit followed by an edit/refactor plan using `skill-authoring` and its required `prompt-authoring` discipline.

**Research result:** Direct retrieval of the current model pages, API guides, endpoint references, pricing, and the dedicated **GPT Image 2.5 prompting guide** resolved the earlier documentation gaps. Set the default to **`gpt-image-2.5-flare`**; offer **`gpt-image-2.5-sunburst`** explicitly. Both support **`xhigh` and `max` quality**, transparent output, custom dimensions, generation, editing, and explicit selection inside the Responses image tool. Search results lagged the directly retrieved pages. The plan below incorporates the current evidence; there is no model-ID or pricing research prerequisite left for the user.

## 1. Decisions to implement

1. **Default to Flare throughout the execution path.** Change the canonical CLI default, agent instructions, metadata, current SDK examples, and installation verification together. Keep the skill name and command `gpt-image`. Respect an explicitly requested model; never silently switch to Image 2 or Sunburst.
2. **Retain the existing Images API CLI.** Its generation/edit routing, repeated reference inputs, mask handling, and file saving are the right foundation. Add only the compatibility and validation needed for the migration. Conversational editing can use successive saved images without a new conversation controller.
3. **Make the skill a concise creative workflow.** Preserve useful art direction, typography, diagram grammar, and reference patterns. Replace mandatory gallery rituals and fixed prompt formulas with judgment about what the particular image needs.
4. **Make visual references and iterative editing first-class guidance.** Distinguish subject, style, layout, source artwork, and edit-target roles. Inspect actual images, identify what each contributes, preserve approved changes, and inspect the resulting image before reporting completion.
5. **Ship honest examples and metadata.** Add a small, tested 2.5 showcase while retaining historical examples and attribution. Distinguish new product features from model improvements and existing techniques that work better with 2.5.

## 2. Research findings and evidence boundaries

### 2.1 What the release establishes

OpenAI released ChatGPT Images 2.5 on September 8, 2026 and announced API access to Flare and Sunburst. Flare is the recommended general-purpose choice and is advertised as having up to 50% lower latency than Image 2. Sunburst emphasizes precision for demanding creative/editing work at longer generation times. These are product claims, not measurements from this repository. [OpenAI launch announcement](https://openai.com/index/introducing-chatgpt-images-2-5/)

| Announced improvement | Consequence for this migration |
|---|---|
| Better preservation of subjects from reference photos | Evaluate recognizable identity, distinctive features, product geometry, and material detail when changing setting or style. |
| More focused editing | Teach small change requests with explicit preservation constraints. |
| Greater consistency through successive edits | Make continuation from the accepted image an ordinary workflow. |
| Better visual style adherence, lighting, texture, and complex layouts | Improve reference interpretation and creative briefs; compare outputs rather than prescribing more prompt decoration. |

These capabilities are described in the [launch announcement](https://openai.com/index/introducing-chatgpt-images-2-5/). The [2.5 system card](https://deploymentsafety.openai.com/chatgpt-images-2-5) separately describes improved infographic accuracy/layout and retention of details when changing setting, style, or composition.

The release also introduces ChatGPT features: drawing with Sketch, templates, comments placed on images, and prompt sharing. These are interface features. This CLI can use a supplied sketch or annotated image as a reference, but must not advertise ChatGPT interface commands as Images API parameters. [Launch announcement](https://openai.com/index/introducing-chatgpt-images-2-5/)

### 2.2 Exact model identifiers and selection

| Variant | API alias | September 8 snapshot | Role in this package |
|---|---|---|---|
| Flare | `gpt-image-2.5-flare` | `gpt-image-2.5-flare-2026-09-08` | Default for generation and editing. |
| Sunburst | `gpt-image-2.5-sunburst` | `gpt-image-2.5-sunburst-2026-09-08` | Explicit choice when its quality/editing advantage is needed. |

Both model pages list text/image inputs, image outputs, generation/edit endpoints, and inpainting. Use the Flare alias as the ordinary default; record the selected alias or snapshot in examples. Offer dated snapshots through the existing `--model` override without inventing a new resolver. Sources: [Flare model page](https://developers.openai.com/api/docs/models/gpt-image-2.5-flare), [Sunburst model page](https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst).

The Images API accepts these IDs directly as `model`. Responses takes a mainline model such as `gpt-6-astra` at the top level and the image model inside `tools=[{"type": "image_generation", "model": "gpt-image-2.5-flare"}]`. The image model is not the Responses top-level model. [Image generation tool guide](https://developers.openai.com/api/docs/guides/tools-image-generation)

### 2.3 Verified request controls and limits

| Area | Confirmed 2.5 contract | Implementation consequence |
|---|---|---|
| Quality | `auto`, `low`, `medium`, `high`, `xhigh`, `max`; API default `auto` | Add `xhigh`/`max` to the CLI for both variants and their snapshots. Preserve the existing CLI `high` default for the first migration comparison. |
| Canvas | `auto` or `WIDTHxHEIGHT`; each edge ≤3840 and divisible by 16; aspect ratio between 1:3 and 3:1; total pixels 655,360–8,294,400 | Validate all constraints together. Sizes above 3,686,400 pixels are experimental. `1536x864`, `1152x1536`, and `3840x2160` are valid examples. |
| Output | PNG by default; PNG/JPEG/WebP supported; `auto`/`opaque`/`transparent` backgrounds | Alpha output requires PNG/WebP. Send compression only for JPEG/WebP. Preserve returned base64-decoded bytes. |
| References and edits | Generation and editing supported; multiple references, masks, and successive image edits documented | Keep repeated `-i`; make the first input the mask target. Reattach the accepted image on each independent CLI invocation. |
| Streaming | `partial_images` 0–3; 100 additional output-image tokens per partial | Explain as an optional API feature. Do not add streaming machinery to this CLI unless the user needs partial previews. |

Sources: [2.5 prompting guide: model parameters](https://developers.openai.com/api/docs/guides/image-prompting#model-parameters), [image generation guide](https://developers.openai.com/api/docs/guides/image-generation).

The current endpoint references specify a 32,000-character prompt limit, `n` from 1 to 10, and up to 16 edit inputs. Compression is 0–100. Edit requests expose `moderation=auto|low`, and the generic edit schema accepts optional `input_fidelity=high|low`. Sources: [generate endpoint](https://developers.openai.com/api/reference/resources/images/methods/generate), [edit endpoint](https://developers.openai.com/api/reference/resources/images/methods/edit).

For local image inputs, use PNG, JPEG, or WebP below 50 MB per image. Follow the current guide's mask requirements: matching image dimensions/format, alpha channel, and size below 50 MB. PNG base-plus-mask fixtures avoid an unnecessary format mismatch. Fully transparent mask regions identify the change area; masking is guidance rather than guaranteed pixel isolation. The mask applies to the first reference. [Image generation guide: masks](https://developers.openai.com/api/docs/guides/image-generation#edit-an-image-using-a-mask), [official Python image resource](https://github.com/openai/openai-python/blob/v3.9.0/src/openai/resources/images.py).

Rate limits and access depend on the API project/account. Use its actual Limits page or error response during integration; do not copy Image 2's tier table and label it a 2.5 guarantee. This is routine account validation, not a missing model identifier or a question Amir needs to answer.

### 2.4 Pricing and meaningful comparisons

Both variants have these standard rates per one million tokens:

| Token category | Flare | Sunburst |
|---|---:|---:|
| Image input | $8.00 | $8.00 |
| Cached image input | $2.00 | $2.00 |
| Image output | $30.00 | $30.00 |
| Text input | $5.00 | $5.00 |
| Cached text input | $1.25 | $1.25 |

Source: [API pricing: image generation](https://developers.openai.com/api/docs/pricing#image-generation). These are confirmed 2.5 rows. Equal rates do not establish equal cost per image; quality, model, input images, and output dimensions can change token consumption. Use returned usage to calculate actual costs. The old Image 2 calculator does not estimate 2.5 consumption. Responses additionally incurs its mainline model's usage. [Flare pricing notes](https://developers.openai.com/api/docs/models/gpt-image-2.5-flare), [Sunburst pricing notes](https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst), [image generation guide: costs](https://developers.openai.com/api/docs/guides/image-generation#gpt-image-25-costs).

Measure cost per accepted image, including retries, alongside typical/slow response times. Do not infer that Flare is cheaper per accepted asset simply because it is faster, or that `max` always improves the result. These are explicit comparison principles in the [2.5 migration and prompting guide](https://developers.openai.com/api/docs/guides/image-prompting#migrate-an-existing-workflow).

### 2.5 Answers to the five research questions

| Question | Research answer | Decision |
|---|---|---|
| Exact model IDs? | Both aliases and dated snapshots are published; see §2.2. | Set `DEFAULT_MODEL = "gpt-image-2.5-flare"`. |
| Parameters and features? | Current 2.5 guides and endpoint schemas establish the controls in §2.3, including two additional quality levels. | Implement those controls; leave unrequested optional fidelity unset. |
| Prices and limits? | Standard token prices and request limits are published; see §2.3–2.4. Per-image cost requires actual usage. | Record known rates and limits; measure workload cost during implementation validation. |
| Dedicated prompting guide? | Yes: [Image prompting](https://developers.openai.com/api/docs/guides/image-prompting), whose primary section is the GPT Image 2.5 guide with illustrated Flare/Sunburst examples. | Make it the current creative authority, superseding the old cookbook's parameter guidance. |
| Responses and native selection? | Responses explicitly selects the image variant in the tool object. The retrieved native product documentation still names Image 2 and exposes no documented Flare/Sunburst selector. | Document Responses correctly; use this package's explicit API path for a guaranteed requested model. |

The native-surface finding is grounded in [ChatGPT/Codex image-generation documentation](https://learn.chatgpt.com/docs/image-generation) and the installed host `imagegen` skill inspected during research. The launch announcement's general availability statement does not override a runtime's actual exposed controls. No changes to the host skill are part of this repository migration.

### 2.6 Source precedence and remaining narrow documentation ambiguities

Use current model pages for identifiers, the 2.5 prompting guide for creative practice, current API guides for model behavior, and endpoint schemas plus tested SDK serialization for transport. The old cookbook is useful historical material, not current parameter authority.

| Documentation issue | Concrete handling |
|---|---|
| Search returned older material while direct pages contained 2.5 | Follow the current documentation index and read the pages. Do not leave the work at search snippets. |
| Generic `input_fidelity` exists, but the 2.5 guide does not prescribe it or state a 2.5-specific default | Omit it in normal 2.5 requests. Restrict the known Image 2 prohibition to its exact alias/snapshot; preserve explicit 2.5 options and surface any server rejection. Do not advertise a new fidelity knob or assert inherited always-high behavior. |
| Python SDK 3.9.0 annotations lag the new quality values, and `images.edit` lacks a `moderation` keyword | Runtime serialization accepts both new qualities. Use the supported `extra_body` mechanism for an explicit edit moderation value; verify the payload, not just annotations. |
| Some SDK docstrings retain an older 4 MB mask limit; the current guide says below 50 MB | Use the current guide as the model contract. Keep small PNG fixtures and validate dimensions/alpha locally; do not treat a stale docstring as a new model restriction. |
| The new prompting guide deliberately keeps its complete runnable baseline on `gpt-image-2` | Preserve that source as a baseline. Author this package's current commands with explicit 2.5 models instead of copying the baseline and claiming the default was migrated. |

These details have implementation decisions; they do not require user research or prevent the ordinary 2.5 workflow. Live acceptance and visual quality remain implementation tests, not claims made by this plan.

### 2.7 SDK compatibility verified during research

Inspected the official Python SDK and exercised **`openai==3.9.0`** in an isolated `uv run --no-project` environment using `httpx2.MockTransport` and a placeholder credential. All **nine offline requests passed**: generation and multipart editing for each combination of the two variants with `xhigh`/`max`, plus a Responses request with explicit tool model, quality, action, and previous-response ID.

The checks confirmed model/quality serialization, custom sizes, transparent output controls, reference ordering, mask transport, edit `extra_body={"moderation": "low"}`, omission of unrequested fidelity, and parsing of new quality labels in mocked responses. No request reached OpenAI and no image was generated. This proves local SDK transport compatibility, not account access or model quality.

Use **`openai>=3.9.0`** as the initial tested support floor, synchronized across the project and both inline script declarations. This is a chosen tested baseline, not a claim that 3.9.0 was the first version capable of these requests. Its Python ≥3.10 requirement is compatible with this repository's Python ≥3.11 requirement. Source: [official SDK at v3.9.0](https://github.com/openai/openai-python/tree/v3.9.0).

## 3. Existing skill audit

### 3.1 Execution and compatibility findings

| Priority | Finding and consequence | Owning file/layer |
|---|---|---|
| P0 | `DEFAULT_MODEL` is `gpt-image-2`. Updating prose alone leaves actual generations on the old model. | `src/gpt_image_cli/cli.py:82` |
| P0 | `model_rejects_input_fidelity()` uses `startswith("gpt-image-2")`. Both verified 2.5 IDs match it and therefore inherit an unverified restriction that drops an explicit flag. | `src/gpt_image_cli/cli.py:104` and `:201` |
| P0 | CLI choices reject `transparent`, `xhigh`, and `max`, all documented 2.5 controls. A model-name replacement alone cannot expose them. | `src/gpt_image_cli/cli.py:138` and `:144`; skill flag table |
| P1 | A copied skill can delegate to an older installed CLI or fetch the upstream package. A changed local default alone does not establish the effective model across installation modes. | `skills/gpt-image/scripts/generate.py`; CLI resolution in `SKILL.md` |
| P1 | Current arguments provide little local compatibility validation. Size literals pass through; PNG compression is described as ignored but is forwarded; edits do not forward moderation. | `resolve_size`, `call_generate`, `call_edit`, `parse_args` |

The dependency floor is `openai>=1.55` in the project and both inline script declarations. Replace it with the tested `openai>=3.9.0` support baseline described in §2.7. Keep the transport accommodation for an explicit edit moderation value in the canonical CLI; do not duplicate it in the launcher.

### 3.2 Prompt and workflow findings

| Priority | Finding and consequence | Owning file/layer |
|---|---|---|
| P1 | Every request must search the gallery, and craft asks for 3–8 nearby cases. Precise edits can inherit irrelevant styles and unnecessary setup. | `SKILL.md` operating loop; `craft.md:27` |
| P1 | JSON/config prompts are treated as a core requirement; invented rendering flags and numeric noun quotas stand in for visual judgment. | `craft.md:69` and `:226` |
| P1 | References have a useful index/role pattern, but the workflow does not require inspecting actual inputs or clearly separating style from subject and composition. | `craft.md:284`; `SKILL.md` first move |
| P1 | Verification mainly checks files and CLI exit status. It does not establish that an edit preserved the correct details or that transparency is real. | `SKILL.md:100` |
| P2 | Fixed asset-type mappings for quality and size encourage automatic choices. Examples such as a 3:4 poster passed as `portrait` actually request 2:3 pixels. | Skill size/quality policies; typography gallery and README examples |

The broad trigger description also overlaps with the visible host `imagegen` skill and the sibling `get-prompt-from-image`. It should explain execution ownership, not list more image-related keywords.

### 3.3 Documentation and example findings

| Priority | Finding and consequence | Owning file/layer |
|---|---|---|
| P1 | The April 23 cookbook copy is labeled as parameter authority but contains contradictions: unavailable `input_fidelity` used in Image 2 examples, opaque-only product extraction, and a CLI `v1.3+` claim while the package is `0.2.0`. | `references/openai-cookbook.md` |
| P1 | Gallery previews use `../../../docs/...`, outside the standalone skill package. Those optional previews cannot be assumed to exist after folder-only installation. | All 31 category references |
| P1 | Existing images have provenance/attribution but usually no confirmed generation-model metadata. Relabeling all previews as 2.5 would fabricate provenance. | Gallery metadata; both READMEs |
| P2 | Some examples contain contradictory dimensions or unsupported literal sizes. No. 66 requests a strict 2:1 panorama but has a 16:9 metadata size and mentions a 4096-pixel edge. | `gallery-photography.md:42`; UI and typography examples |
| P2 | Research examples can look authoritative despite absent or inconsistent data; for example, No. 75's listed exclusions do not reconcile and No. 86's flow totals do not reconcile. | `gallery-research-paper-figures.md`; craft's factual-accuracy guidance |

`CONTRIBUTING.md` also mandates placing every example in both READMEs and using `Original`, while the active skill treats the atlas as complete, README as selected, and uses `Curated`. Resolve the contribution contract during the showcase update, rather than multiplying those contradictions.

### 3.4 Useful behavior to preserve

Keep the canonical CLI and thin launcher, natural-language user requests, exact copy preservation, concrete visual descriptions, selective reference loading, explicit edit invariants, named input roles, and visible source attribution. These are the existing package's strongest reusable ideas.

Keep environment-key precedence and installation behavior outside the migration's functional redesign. Correct misleading documentation where needed, but do not turn the image-model upgrade into a credential-management project. In particular, `unset OPENAI_API_KEY` does not disable fallback loading from `.env` or `~/.env`; the skill must not recommend it as a reliable opt-out from all local keys.

## 4. Skill contract and boundaries

### 4.1 Job and leverage claim

**Job:** Turn a user's visual intent and available references into a usable generated or edited raster asset through the packaged GPT Image CLI, choosing compatible parameters and checking the result against the brief.

**Leverage:** The skill combines visual judgment with reliable API execution. It reduces repeated mistakes involving reference roles, edit drift, exact text, alpha output, and mismatched model/parameter choices. This repeated workflow justifies a skill; the migration itself belongs in this plan document.

Canonical asks:

1. “Make a launch poster for this tea using these exact Chinese prices and this visual style.”
2. “Use the person in the first photo and the jacket in the second. Keep the face, pose, and room the same.”
3. “Turn this sketch into a product hero, then make a transparent version and change only the label color.”

Nearest anti-case: “Extract a reusable prompt from this image; do not generate anything.” That belongs to `get-prompt-from-image`.

### 4.2 Peer boundaries

| Surface | Owns | Handoff rule |
|---|---|---|
| `gpt-image` | GPT Image CLI/API generation and edits, including exact model selection | Use when explicitly selected or when the active workflow calls for this package. |
| `get-prompt-from-image` | Reverse engineering a reusable prompt from a reference | Do not run it as a mandatory prerequisite to editing; the actual reference is usually a better input than a reconstructed description. |
| Host `imagegen` | Host-native generation under that runtime's tool and billing rules | Respect the user's chosen execution path. Do not claim native tool model selection this repo cannot control. |
| Native drawing/chart/code tools | Editable vectors, exact data plots, working UI, and deterministic layouts | Use the appropriate artifact tool when the requested output requires those properties. A generated mockup remains a raster image. |

Draft trigger description, to refine during implementation:

> Generate and edit raster images through the packaged gpt-image CLI, using GPT Image 2.5 Flare by default. Use when the user selects this skill or requests its CLI/API workflow, including reference-based creation, style transfer, focused edits, masks, and transparent assets. Use get-prompt-from-image for prompt extraction without rendering; respect an explicitly requested host-native image tool.

Draft `agents/openai.yaml` intent:

```yaml
interface:
  display_name: "GPT Image"
  short_description: "Generate and edit with GPT Image 2.5 Flare"
  default_prompt: "Use $gpt-image to create or edit my image with GPT Image 2.5 Flare by default, using my references and checking the result against my brief."
```

Keep the description inside the runtime limit. Retain the existing OpenClaw eligibility metadata and verify it still describes the actual launcher requirements. No agent orchestration is needed for normal image work, so do not introduce model-agent dispatch or an orchestration policy dependency into this package.

### 4.3 Lean operating workflow

The rewritten `SKILL.md` should express five bounded actions, with detailed API rules and examples in references:

1. **Understand the deliverable.** Identify creation versus editing, destination, required copy, dimensions, budget, explicit model/tool choice, and what must remain true.
2. **Inspect the evidence.** Open supplied images. Assign reference roles. Read a gallery example or craft section only when it helps resolve a real design decision.
3. **Prepare the smallest adequate brief.** Preserve user intent and exact text, distinguish changes from invariants, and choose model-compatible flags.
4. **Generate or edit through the existing CLI.** Attach the required actual files, save a new output version, and use the accepted previous image for follow-ups.
5. **Inspect and deliver.** Check the important visual constraints and actual file properties. Correct a concrete defect when warranted; report files, effective model/settings, and any unresolved mismatch honestly.

A precise “make only this change” request should move directly through this loop. An ambiguous creative brief can benefit from one concise clarification or a reasonable stated assumption; price or polish alone must not become an automatic approval ceremony.

## 5. Model defaults and API implementation

### 5.1 Model policy

| User intent | Planned model behavior |
|---|---|
| No model specified, including a generic “use Image 2.5” | `gpt-image-2.5-flare`. |
| Explicit Sunburst or a deliberate request for that variant's precision tradeoff | `gpt-image-2.5-sunburst`. |
| Explicit Image 2 or another supported model | Honor that model and its own compatibility rules. |
| Requested/default model unavailable to the account | Return the actual access/model error with an actionable explanation. Do not silently substitute. |
| User asks for a host-native path | Use the host's workflow and state only the model information that surface exposes. |

Keep model selection separate from `quality`. Sunburst is not a quality enum, and Flare with `high` is not equivalent to selecting Sunburst. Preserve the supported current CLI `quality=high`, `size=1024x1024`, `n=1` defaults for the first migration. State that the API itself defaults to `quality=auto`. Expose all six 2.5 quality values without automatically choosing `max`; agents can select quality and size to meet the user's requirements.

### 5.2 Minimal CLI changes

1. **Change the true default and descriptions.** Set `DEFAULT_MODEL = "gpt-image-2.5-flare"`. Add `xhigh` and `max` to quality parsing, with a model-aware rejection for known legacy models. Update `--help`, module docstrings, package descriptions, and current usage examples. Add a conventional `--version` to diagnose the effective installed backend; use the package's canonical version.
2. **Replace the broad fidelity prefix heuristic.** Restrict the known Image 2 prohibition to `gpt-image-2` and `gpt-image-2-2026-04-21`. Omit unrequested optional fields. Preserve explicit fidelity for 2.5 as a generic endpoint option and surface server errors; do not declare a 2.5-specific default or silently drop the user's setting.
3. **Enable alpha output.** Accept `transparent`, pair it with PNG/WebP, and reject an explicit JPEG/transparency conflict before the API call. Preserve returned bytes and align file extensions with encoding. Reconcile compression handling with the documented format contract.
4. **Validate model-sensitive arguments.** Apply the exact dimensions/count/input rules in §2.3. Validate mask geometry/alpha/format. Forward an explicitly supplied edit moderation value through SDK 3.9.0's `extra_body`; preserve omission for edits when unspecified, and preserve the current generation-side `low` default. This requires distinguishing an omitted CLI flag from its generation default.
5. **Verify all execution paths.** Set the tested SDK floor to 3.9.0 across `pyproject.toml` and both script metadata blocks. Exercise the direct entrypoint and launcher paths with mocked calls and the actual upgraded backend. Keep Python ≥3.11.

A small local capability representation is justified for exact request compatibility. It should not become a general model registry, a remote model resolver run on every generation, or a new routing framework. Unknown model IDs can remain explicit pass-through choices with errors surfaced; they must not inherit guessed 2.5 behavior.

### 5.3 API facts to record in the new reference

Build `references/model-api.md` as the package's concise, dated API authority. Include the verified values, exact source links, and distinctions between API defaults and this CLI's defaults.

| Area | Record during implementation |
|---|---|
| Model selection | Flare/Sunburst IDs, available snapshots, supported endpoints, explicit override behavior, model-access failure behavior. |
| Output controls | Supported quality values, size constraints and examples, count limits, formats, compression, transparency, and moderation. |
| Reference/edit controls | Input count, input formats and byte limits, ordering, mask requirements, input-fidelity semantics, and whether controls differ by variant. |
| Response and transport | SDK minimum, multipart versus JSON shape where relevant, returned image data, usage availability, errors, and optional streaming support. |
| Cost and limitations | Published rates or a pricing link, image-input costs, measured versus advertised latency, known rendering limitations, and the evidence date. |

Use the verified limits and prices in §2.3–2.4. Do not invent 8K output, a style-weight parameter, a seed, or a separate negative-prompt field. Quality values belong in API parameters; a prompt containing “max quality” does not set `quality="max"`.

Style references use ordinary image inputs with their role explained in the prompt unless updated model documentation establishes a dedicated control. The existing generation reference scopes `style=natural` and `style=vivid` to DALL·E 3; do not introduce those as 2.5 options. [Generation API reference](https://developers.openai.com/api/reference/resources/images/methods/generate)

### 5.4 Default correctness across installs

The launcher can execute repo-local code, an installed Python module, a PATH executable, or a transient upstream package. Preserve a single implementation, but make effective-version diagnosis possible and document which backend a standalone installation will use.

Skill-authored calls should explicitly supply `--model gpt-image-2.5-flare` when a different backend version may be selected. Direct CLI calls without `--model` must independently default to Flare. If an old backend rejects a new required option, report that backend/version mismatch and the existing update path; do not drop the flag and pretend the requested feature succeeded.

A public release must contain the matching CLI and skill updates before transient installs are advertised as 2.5-ready. Verify repo-local execution first and the published install path at release time. No global installation, package publication, or repository rename is part of this planning task.

### 5.5 Responses and host-native boundaries

Keep the Images API CLI as this package's implementation. Include a short reference explaining the supported Responses alternative for a user who is building a conversational integration. It can explicitly select Flare or Sunburst, retain conversation state, and request generation versus editing:

```python
first = client.responses.create(
    model="gpt-6-astra",
    input="Draw a cream ceramic mug with a blue handle on a linen tablecloth.",
    tools=[{"type": "image_generation", "model": "gpt-image-2.5-flare"}],
    tool_choice={"type": "image_generation"},
)
second = client.responses.create(
    model="gpt-6-astra",
    previous_response_id=first.id,
    input="Edit the image: change only the handle to green. Preserve the rest.",
    tools=[{
        "type": "image_generation",
        "model": "gpt-image-2.5-flare",
        "action": "edit",
    }],
)
```

This is API reference material, not a new CLI subcommand or conversation controller. A complete runnable example must collect `image_generation_call` outputs and save their decoded `result`. Explain that `action="edit"` needs an image in context, the mainline model can revise the image prompt, and `revised_prompt` is available on the image-generation call. Preserve the user brief and the revised prompt separately when investigating fidelity. Source: [Responses image-generation tool guide](https://developers.openai.com/api/docs/guides/tools-image-generation).

Do not claim that a ChatGPT/Codex native tool accepts these SDK parameters. The retrieved native guide still documents Image 2 and no per-variant selector; the package can guarantee its own explicit API model selection. Honor a user-selected native path while accurately describing the controls actually available there.

## 6. Prompting changes

These changes apply the dedicated [GPT Image 2.5 prompting guide](https://developers.openai.com/api/docs/guides/image-prompting) to this package. The guide accepts several maintainable prompt formats and teaches image intent, reference roles, constraints, and iteration; it does not require a special syntax.

### 6.1 Start with intent and the constraints that affect the picture

Write an ordinary creative brief by default. State the artifact and its use, the subject or edit, the composition that matters, the visual treatment, and any exact copy. Add labels or JSON when the user supplied structured input or when it makes a complex brief easier to maintain. No fixed key schema, noun quota, prompt length, or universal ordering is required.

For a narrow edit, a short instruction can be enough. For a layout-sensitive poster, lead with the layout constraints. For a photo, establish the subject, framing, and light. For a supplied sketch, let the actual sketch carry geometry that words would describe poorly.

Replace vague quality tokens with visual decisions when a decision is needed. “8K_UHD,” “award-winning,” and a fake configuration version do not control output dimensions or create renderer features. Keep intentional medium cues such as grain, brushwork, paper texture, or flat colors when they describe the desired image.

### 6.2 Use direct style evidence without importing its content

A style reference describes **how** the image should look. A subject reference describes **what** should remain recognizable. A layout reference describes **where** elements belong. Those roles can overlap when the user intends them to, but should not be conflated by default.

Describe the reference's observable properties: contour character, brushwork, texture, palette relationships, contrast, lighting, simplification, depth, and typography treatment. Copy only the properties the user wants. If a reference contains a person, wordmark, or setting that is not part of the requested result, say what role it has and exclude accidental content transfer.

Named styles can be useful shorthand where allowed, but the reusable guidance should explain visible qualities rather than depend on long lists of studios or artist names. Follow the active runtime's applicable image rules without inventing a blanket prohibition on ordinary style references or benign likeness edits.

### 6.3 Separate literal content from creative freedom

Put required text in a clearly labeled copy block, with exact spelling, punctuation, language, line breaks where material, and placement/hierarchy. Preserve the user's words. Ask for approval of a translation only when its wording actually needs the user; otherwise use the agreed or supplied translation as the image brief.

Allow the model to make subordinate aesthetic decisions where the brief leaves room. Do not convert “make this poster elegant” into a rigid template that replaces the user's composition or automatically erases their branding.

When exact measurements, chart values, scientific relationships, or citations matter, prepare those facts outside the image model and supply them. A plausible diagram is not proof that the numbers or geometry are correct. Keep illustrative fictional data visibly identified. Use a plotting/layout tool for an exact chart or editable deliverable when that is the actual request.

### 6.4 Make follow-ups small but self-contained

An edit instruction should name the change and the invariants relevant to it. Keep prior accepted changes in the preservation instructions. Avoid repeatedly appending every historical prompt; pass the latest accepted image and a compact current brief.

If a lighting change necessarily changes reflections and shadows, permit those effects while protecting identity and geometry. “Change the lighting but keep every pixel identical” is a contradictory instruction. Conversely, changing a price should not invite a new layout, subject, or color grade.

### 6.5 Treat quality and sizing as deliberate choices

Choose quality by the task's actual tolerance for errors and the user's cost/latency preference. Use quick drafts for exploration where supported; compare higher settings when details matter. Remove the assertion that every medium-to-high step has a fixed cost multiplier or that every text-bearing image necessarily fails at medium.

For a migration comparison, hold the prompt, references, explicit quality, dimensions, and format constant first. If the result fails, test a higher supported quality before expanding the prompt. Try `xhigh` or `max` only against a specific unmet requirement, then test lower settings once quality passes. Equal quality labels across models do not guarantee equal output quality, speed, or cost. This follows the [2.5 guide's migration procedure](https://developers.openai.com/api/docs/guides/image-prompting#migrate-an-existing-workflow); it replaces the earlier plan's assumption that prompt retuning should be the first response to a failed comparison.

The requested API pixel dimensions control the canvas. Distinguish a depicted phone's screen dimensions from the output image dimensions. Keep existing shortcut meanings for compatibility, but explain them accurately: `portrait` is currently 1024×1536, not a universal 3:4 preset. Use `1152x1536` for a valid 3:4 canvas and `1536x864` for a valid 16:9 canvas. Describe 4K as experimental above the documented pixel threshold; `max` is a quality setting, not permission to exceed size limits.

### 6.6 Apply the new guide's examples without imposing a template

The dedicated guide includes actual Flare/Sunburst example pairs. Use these as targeted reference material when refreshing the existing gallery, with source links and original attribution:

| Existing package area | 2.5 guidance to carry into current examples |
|---|---|
| Photography, posters, and branded copy | Concrete framing/light/materials; natural poses and skin texture; exact copy and occurrence count. Camera details are appearance cues rather than physical guarantees. |
| Diagrams, slides, and interface mockups | Define hierarchy and real content. Check facts and every label. Describe UI as a usable interface; a raster mockup does not implement it. |
| Style transfer, clothing, and compositing | Identify the source of style separately from identity, garments, scene, or inserted objects. Match perspective, light, and scale where inputs combine. |
| Cutouts, sketches, and local changes | Pair explicit alpha output with preservation instructions; keep a sketch's geometry while adding realistic materials; isolate the intended change. |
| Sequential edits, characters, and merchandise | Reuse accepted outputs or stable character anchors; retain defining details while changing scenes; verify every stage rather than assuming consistency. |

Source: [GPT Image 2.5 prompting guide](https://developers.openai.com/api/docs/guides/image-prompting). Link directly to the relevant section in the new reference map. The old cookbook remains historical. The new guide's final Python example is intentionally an Image 2 baseline and must not be copied verbatim as the package's new default.

## 7. Reference images, style references, and editing

### 7.1 Before composing the request

1. **Open every relevant supplied image.** Do not infer content from a filename, gallery title, or a prompt describing a different result.
2. **Identify its role in the requested output.** Resolve conflicting reference instructions from the user's stated priorities; ask one question only if an essential priority is missing.
3. **Prepare usable files.** Preserve orientation, relevant detail, aspect ratio, and alpha. Download URL references only when needed for this local-file CLI. Rasterize a vector only when the task actually needs it as an image input.
4. **Map prompt labels to actual input order.** The order of `-i` arguments must match “Image 1,” “Image 2,” and so on. With a mask, place the edit target first.
5. **Attach the actual images.** Mentioning a path in the prompt does not give the model the file. Never claim a gallery preview was used visually when only its prompt text was read.

### 7.2 Roles to teach with examples

| Role | What to preserve or transfer | Typical failure to check |
|---|---|---|
| Subject/identity | Face or distinctive features, product silhouette, markings, proportions | A generic replacement subject; blended identities. |
| Style | Medium, line/brush language, texture, color relationships, rendering treatment | Reference subject, scenery, or text leaks into the new image. |
| Composition/sketch | Relative positions, framing, perspective, topology | Sketch is treated as texture; intended layout is redesigned. |
| Artwork/brand | Supplied logo, label, package artwork, exact copy | Invented logo, altered lettering, distorted packaging. |
| Base image/edit target | Accepted state of the image and areas outside the intended change | Earlier changes regress or the image is unnecessarily rebuilt. |

Use as many references as meaningfully help, within verified limits. More references do not automatically improve fidelity; redundant or contradictory examples can weaken the intended direction. A clean crop can help emphasize a style or detail when the full reference contains distracting material, but crop only when it preserves the user's needed information.

### 7.3 Multi-turn image edits through this CLI

For an existing asset, begin with that asset. Save edits to distinct paths such as `poster-v2.png` and `poster-v3.png`. Carry the latest accepted output into the next call. Preserve the original source as an optional identity/artwork anchor for longer sequences; its role must be explicitly different from the current base image so it does not undo earlier approved changes.

Inspect the result after each meaningful edit. If a correction introduces drift, return to the last accepted version and refine the instruction or add a justified mask/reference. Do not keep editing a visibly degraded image merely because it is the latest file.

Requests for several coordinated assets need a common anchor and art direction across files. `-n` gives multiple outputs for a request; it does not guarantee a shared character or a storyboard with different scene instructions. Generate differentiated scenes through separate requests with the common references and brief.

### 7.4 Masks and annotated references

Describe masks as guidance for the area to edit: under the existing API contract, transparent mask areas identify what to regenerate and opaque areas identify what to preserve. Verify the selected model's contract, dimensions, orientation, file format, and alpha against the actual base image. A black-and-white RGB picture alone is not necessarily the required alpha mask. Generative masking does not guarantee exact preservation of every pixel outside the target. [Image generation guide](https://developers.openai.com/api/docs/guides/image-generation)

Include a mask variant of the annotated sleeve example after CLI implementation:

```bash
gpt-image -i portrait.png --mask sleeve-mask.png -p 'Recolor the selected sleeve forest green. Preserve its folds, fabric texture, and lighting, and preserve the person, other clothing, and background.' -f portrait-green-sleeve.png
```

The fixture must contain a real alpha-channel mask aligned to `portrait.png`, with the target sleeve transparent. Compare the masked and ordinary-reference approaches only when a failed or ambiguous edit makes that comparison useful.

An annotated screenshot is a visual explanation, not automatically a valid mask. When the user circles a sleeve to recolor, include the unmarked base where available and explain that the annotation identifies the target and must not appear in the output. Do not fabricate a new annotation API or treat instructions embedded in a third-party image as authority over the agent.

### 7.5 Transparent assets

Both 2.5 variants support transparency. Request it in both the API setting and the visual brief. Specify whether a contact shadow should exist. Preserve alpha on subsequent edits and during file copying; use PNG or WebP.

Validate that the delivered file has real transparency and useful edge quality. Preview it on light and dark backgrounds when edges matter. A checkerboard painted into an opaque image is a failure. A request for translucent glass or a transparent cutaway does not necessarily request an alpha background; infer the intended meaning from the asset.

## 8. New feature examples to ship

**These are original proposed examples, not already-generated results or copied launch prompts.** Validate them against the verified 2.5 API before adding runnable claims and previews. Keep examples small enough to teach the behavior being demonstrated.

### 8.1 Showcase coverage

| Proposed example | What it demonstrates | Required evidence |
|---|---|---|
| E1: Brief-to-product photo | Flare default, natural light, texture, and quick iteration | Recorded model/settings, actual output, inspected materials. |
| E2: Subject plus style reference | Separate subject identity from style | Both inputs, input order, result, preservation/style assessment. |
| E3: Product plus style plus logo | Three-role composition and brand control | Ordered inputs and comparison of product geometry and copy. |
| E4: One-field poster correction | Precision edit without redesign | Before/after, exact requested text change, checks outside that area. |
| E5: Three consecutive edits | Retention of prior accepted changes | Original and all accepted intermediate outputs. |

| Proposed example | What it demonstrates | Required evidence |
|---|---|---|
| E6: Sketch plus material reference | Sketch-guided layout with separate visual finish | Supplied sketch, material reference, output geometry assessment. |
| E7: Transparent product cutout | Native alpha output and label preservation | Actual alpha, light/dark previews, label comparison. |
| E8: Annotated local change | Visual comments translated into normal reference/edit instructions | Base, annotation, final output without the annotation. |
| E9: Localization of an existing design | Exact multilingual copy and retained hierarchy | Approved copy mapping and visual text inspection. |
| E10: Coordinated two-image campaign | Shared identity/style across separate requests | Common anchors and individual outputs. |

Use E3 or E4 for a Flare/Sunburst comparison under the same brief, including targeted `high`/`xhigh`/`max` comparisons. That demonstrates the model and quality controls without needing a redundant gallery category. Include a small factual infographic or diagram task in the evaluation set to test the reported layout improvements; do not represent it as independently verified science.

### 8.2 E1: Small creative brief

```text
Create a product photograph for a small ceramic studio's online shop.
A handmade cream mug with a cobalt-blue handle sits beside a folded linen
napkin. Show the uneven glaze and fine clay texture. Morning window light
from the left, a soft shadow, warm neutral surroundings, and enough empty
space above the mug for website copy. No text inside the image.
```

After migration, the simple command must use Flare without a model flag:

```bash
gpt-image -p 'Create a product photograph for a ceramic studio: a handmade cream mug with a cobalt-blue handle beside folded linen. Show uneven glaze and fine clay texture, morning window light from the left, a soft shadow, warm neutral surroundings, and empty space above for website copy. No text inside the image.' -f mug.png
```

The example should show the actual image and chosen quality, rather than claiming a fixed speed improvement from one run.

### 8.3 E2: Subject identity plus style-only reference

```text
Image 1 is the subject reference: preserve this dog's muzzle shape, ear
positions, black-and-white markings, and red collar.
Image 2 is a style reference only: use its coarse pencil contours, flat
ochre and blue shapes, and visible paper grain. Do not include its person,
furniture, or lettering.
Create a new illustration of the dog waiting beside a front door, viewed
at the dog's eye level. Keep the dog recognizable while rendering the
whole scene in the visual language of Image 2. No text.
```

```bash
gpt-image -i dog.png -i pencil-style.png -p 'Image 1 provides the dog: preserve its muzzle, ears, markings, and red collar. Image 2 provides only coarse pencil contours, flat ochre and blue shapes, and paper grain. Illustrate this dog waiting beside a front door at dog-eye level. Exclude the person, furniture, and lettering from Image 2. No text.' -f dog-at-door.png
```

This is new-image creation from references, even though the CLI correctly calls `images.edit`.

### 8.4 E3: Product, style, and supplied logo

```text
Image 1 provides the bottle: preserve its silhouette, cap, proportions,
and material. Image 2 provides only the lighting and color treatment:
warm side light, pale stone, muted olive shadows. Image 3 provides the
exact approved wordmark.
Create a campaign photograph of the bottle standing on pale stone.
Use Image 3's wordmark on the front label with the exact additional copy
"COLD BREW" and "250 ml". Keep the bottle centered with generous top space.
Do not copy Image 2's product, typography, or background objects.
```

Run with `-i bottle.png -i lighting-reference.png -i approved-wordmark.png`. Evaluate whether the extra logo reference improves the result. If exact vector artwork placement is mandatory, composite the approved artwork with a deterministic design tool rather than claiming a generative edit is exact.

### 8.5 E4 and E5: Focused correction and successive edits

```bash
gpt-image -i tea-poster.png -p 'Change only the price text "16 元" to "18 元". Keep its location, font treatment, size, and alignment. Preserve every other word, the product, background, composition, and color treatment.' -f tea-poster-v2.png
```

Continue from `tea-poster-v2.png`, changing only the bottle-cap color. Then continue from that accepted result to replace the date. Each prompt preserves the already-updated price and cap color as appropriate. The example must show all three outputs and record whether earlier changes survive.

An explicit Sunburst comparison uses `--model gpt-image-2.5-sunburst`. Keep the source image, exact edit prompt, size, and quality the same as the Flare run before tuning.

### 8.6 E6: Sketch and style/material references

```text
Image 1 is the layout sketch. Preserve the window position, sofa footprint,
table placement, and viewpoint; the scribbled notes are instructions for
the concept and should not appear in the image.
Image 2 is a material reference only: light oak, woven cream upholstery,
and matte green ceramic accents.
Render the sketched room as a believable daylight interior. Keep the
furniture arrangement from Image 1 and apply only the materials from
Image 2. Do not add furniture or copy Image 2's room layout.
```

This supports a supplied sketch using ordinary references. Explain the relationship to ChatGPT Sketch without pretending this CLI implements the drawing interface.

### 8.7 E7: Transparent product cutout

```text
Extract the bottle from Image 1 onto a fully transparent background.
Preserve the cap, bottle geometry, label text, and surface texture.
Keep the complete silhouette with clean edges. No backdrop, painted
checkerboard, extra objects, or ground shadow.
```

After CLI implementation:

```bash
gpt-image -i bottle.png -p 'Extract this bottle onto a fully transparent background. Preserve cap, geometry, label text, and texture. Keep the complete silhouette and clean edges. No backdrop, checkerboard, added objects, or ground shadow.' --background transparent --format png -f bottle-cutout.png
```

Show actual alpha plus light/dark previews. A follow-up should recolor the cap while preserving transparency, which checks both editing and downstream alpha retention.

### 8.8 E8–E10: Annotation, localization, and a coherent set

| Example | Prompt core | What to inspect |
|---|---|---|
| Annotated sleeve change | “Image 1 is the unmarked base. Image 2 only indicates the sleeve to recolor. Make that sleeve forest green, preserve the rest, and omit all annotation marks.” | Correct sleeve, unchanged subject/background, no circle or comment text. |
| Poster localization | “Replace only the supplied English copy with this exact Spanish copy mapping. Preserve imagery, price, alignment, hierarchy, and typography character; adjust line breaks only where the new text needs room.” | Spelling, accents, line wrapping, prices, unchanged visuals. |
| Two-scene campaign | “Use this character anchor and this style reference. Scene A shows arrival; scene B shows a purchase. Preserve character design and visual treatment; create each scene as its own image.” | Shared identity and style without duplicating the entire composition. |

### 8.9 Example provenance and portability

Place new showcase outputs under `docs/gpt-image-2-5/` and their prompts in a feature-focused gallery reference. Use new stable entry numbers after No. 162; do not renumber unrelated historical examples simply to insert the feature section near the README top.

For each new entry, record the prompt author/source, actual generation model, date, endpoint, ordered inputs, settings, and any post-processing. “Prompt source: OpenAI” and “Image generated by this repo” are separate facts. Mark a prompt without a rendered output as untested; do not create a preview link to a nonexistent file.

When examples require reusable starter images, include the smallest useful rights-cleared input set inside the skill's `assets/` directory, or provide an explicit external download with attribution and explain that it is optional. Full-resolution showcase outputs can remain in `docs/`. Standalone installs must not require the entire repository's image archive to perform ordinary work.

### 8.10 Demonstrate the new quality settings explicitly

After implementing CLI support, include commands that hold the brief and references constant while testing quality. For example, use the E4 poster correction:

```bash
brief='Change only the price text "16 元" to "18 元". Preserve all other copy, layout, typography, product details, lighting, and colors.'
gpt-image --model gpt-image-2.5-flare -i tea-poster.png -p "$brief" --quality high --size 1152x1536 -f price-flare-high.png
gpt-image --model gpt-image-2.5-flare -i tea-poster.png -p "$brief" --quality xhigh --size 1152x1536 -f price-flare-xhigh.png
gpt-image --model gpt-image-2.5-flare -i tea-poster.png -p "$brief" --quality max --size 1152x1536 -f price-flare-max.png
```

Use a source poster already at the intended 3:4 aspect ratio. Inspect the price and unrelated regions, and record latency/usage for each output. Retain the least expensive or fastest setting that satisfies the requirement. Compare Sunburst at the same explicit quality before drawing a model conclusion. Do not publish an assumed winner or describe the unexecuted commands as rendered results.

## 9. File-by-file change map

### 9.1 Runtime and core guidance

| File | Planned change | Completion condition |
|---|---|---|
| `src/gpt_image_cli/cli.py` | Flare default, `xhigh`/`max`, exact capability handling, transparency, explicit edit moderation transport, validation, help, and file checks | Default and override calls send correct payloads and save usable images. |
| `skills/gpt-image/scripts/generate.py` | Keep thin launcher; synchronize supported dependency floor; clarify effective backend behavior | Repo and standalone paths execute the intended upgraded implementation or explain incompatibility. |
| `skills/gpt-image/SKILL.md` | Rewrite the compact contract and selective workflow; refer to current API and reference guidance | A clear image request runs without forced prompt menus or gallery detours. |
| `skills/gpt-image/agents/openai.yaml` | Match new default, scope, and output expectations | Metadata selects the right skill and no longer promises Image 2. |
| `src/gpt_image_cli/__init__.py`, `pyproject.toml` | Update product wording, supported SDK floor, and synchronized release version when shipping | Installed metadata and CLI implementation agree. |

### 9.2 Reference package

| File | Planned change | Why this belongs here |
|---|---|---|
| `references/craft.md` | Apply the dedicated 2.5 guide; retain visual judgment; remove mandatory JSON, arbitrary counts, and fixed size/quality mappings | Shared prompt principles are read when needed. |
| New `references/reference-images.md` | Ordered roles, inspection, style transfer, sketch/annotation use, masks, and iterative edits | This detail would overwhelm the lean entrypoint and is relevant only to image-input workflows. |
| New `references/model-api.md` | Dated, source-backed model and parameter contract; CLI versus API defaults | Current API truth needs one small owner. |
| `references/openai-cookbook.md` | Label clearly as a historical snapshot and remove it from the current parameter-authority path; identify known contradictions in an editorial note | Preserve useful source history without laundering old examples into 2.5 guidance. |
| `references/gallery.md` and new `references/gallery-gpt-image-2-5.md` | Add the feature showcase and accurate counts; make lookup optional when useful | Detailed examples remain progressively disclosed. |

Keep a compatibility link/note at the existing cookbook path so local and README links remain valid. Do not rewrite the archived source's model names and falsely label the result an unchanged official guide. Author the current reference as this repository's synthesis with citations and a verification date.

### 9.3 Existing gallery and publication surfaces

| Surface | Planned change |
|---|---|
| All 31 existing `gallery-*.md` files | Retain prompts/attribution; clarify historical status and optional preview paths; add targeted migration notes where semantics or dimensions conflict. |
| `README.md`, `README.zh.md` | Update current branding/defaults/parameter examples and prompting advice together; add a selected 2.5 showcase with matching images and claims. |
| `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` | Update visible behavior and descriptions; synchronize release version where present. Keep repository URLs and plugin names stable. |
| `CONTRIBUTING.md`, `CHANGELOG.md`, relevant gallery issue template | Align atlas-first contribution ownership, selected README promotion, attribution versus generation provenance, and verification expectations. |
| New targeted tests and example assets | Add meaningful behavioral coverage and the minimum required reference fixtures; avoid a runtime evaluation framework. |

Inspect `skills/get-prompt-from-image/` as a peer. Its general reverse-prompt output format can remain its own contract. At the `gpt-image` handoff, preserve the user's exact text/branding requirements and translate relevant negative constraints into the ordinary prompt rather than assuming a separate API field. Co-edit the sibling only if an actual handoff instruction is added; do not broaden this into an unsolicited rewrite of its bilingual output policy.

### 9.4 Why the script remains justified

The CLI already owns deterministic transport, credential lookup, file handles, argument validation, response decoding, and saving. Rewriting that behavior in ad hoc prompts for every image would reduce reliability and duplicate code. The migration therefore keeps that script and makes narrow repairs. It does not add a batch controller, prompt compiler, reference-ranking engine, local agent runner, or mandatory manifest for normal user requests.

Keep stdout useful: output paths for successful generation; compact actionable errors on stderr. Detailed evaluation receipts belong in files used during development, not an unbounded default CLI response.

## 10. Implementation sequence

### Phase 1 — Encode the researched API contract

**Estimate:** 30–60 minutes. Research is already complete; this phase transfers the verified facts into the shipped skill.

1. Write `model-api.md` using the exact aliases/snapshots, controls, limits, and prices in §2.
2. Record the supported SDK 3.9.0 request shapes and the explicit edit-moderation accommodation.
3. Write concise model/quality/reference guidance from the dedicated 2.5 prompting guide, with source links.
4. Capture the existing Image 2 baseline for representative workflows before changing execution.
5. Check the configured API account during implementation smoke testing; report real access errors without silent fallback.

**Exit:** The skill's new API reference is concrete and self-contained. There is no outstanding model-ID, pricing, or prompting-guide discovery step.

### Phase 2 — Implement the execution path

**Estimate:** 90–150 minutes.

1. Change the canonical model default, add both new quality levels, and repair exact-model compatibility behavior.
2. Add transparency and coherent output-format handling.
3. Add targeted argument validation and preserve existing routing/output contracts.
4. Synchronize dependency declarations, descriptions, and version diagnostics.
5. Run the focused mocked behavioral tests for direct CLI and launcher execution.

**Exit:** Model-unspecified requests reach Flare; explicit overrides remain honored; known invalid combinations fail before network calls.

### Phase 3 — Rewrite the skill and references

**Estimate:** 90–150 minutes.

1. Rewrite `SKILL.md` and `agents/openai.yaml` together around the canonical asks and peer boundaries.
2. Refactor craft into reusable principles with optional examples.
3. Add the reference-image/editing guidance and its compact reference map.
4. Mark the old cookbook snapshot and identify corrected current guidance.
5. Check trigger quality, self-containment, and a realistic one-line edit walkthrough.

**Exit:** The skill guides correct 2.5 use with actual references and visual verification, without requiring unnecessary ceremony.

### Phase 4 — Validate and publish examples in the repo

**Estimate:** 120–240 minutes including image inspection and targeted retries; model queue time may extend this.

1. Prepare a small reusable input set with clear provenance.
2. Run the focused showcase/evaluation tasks and capture settings, outputs, and observed failures.
3. Inspect and fix concrete defects in prompts or code, retaining honest evidence of unresolved limitations.
4. Add the tested feature gallery and selected matching README examples.
5. Reconcile current documentation, historical labels, contribution guidance, and plugin/package metadata.

**Exit:** New 2.5 examples have actual outputs and trustworthy provenance; earlier images remain accurately identified.

### Phase 5 — Final package and installation verification

**Estimate:** 45–90 minutes.

1. Run the required repository checks and the targeted test suite.
2. Verify isolated folder-only loading and an installed CLI backend without modifying the user's global installation.
3. Check both READMEs, local links, gallery counts, and runtime metadata for consistency.
4. Confirm no active default or current example silently chooses the wrong image model.
5. Prepare a concise release note with what changed, validation performed, and remaining material limitations.

**Exit:** The upgraded package is reviewable and ready for its normal release process. Publishing or installing is a separate action when requested. The total estimated implementation effort is **6–12 hours**, excluding extended API queues and any broader gallery regeneration.

## 11. Validation plan

### 11.1 Behavioral tests worth adding

Use mocked SDK calls for deterministic request behavior. No paid generation is needed for these tests, and no secret should enter a fixture.

| Test family | Assertions |
|---|---|
| Default and explicit models | No model option sends verified Flare; Sunburst and explicit legacy IDs are preserved; model errors never trigger silent substitutions. |
| Routing and reference ordering | Requests without reference inputs use generations; requests with image references use edits; repeated references retain order; mask target is the first image; file handles close. |
| Parameter compatibility | `xhigh`/`max` reach both 2.5 variants and snapshots, but are rejected for known legacy models; optional fidelity stays unset unless requested; size/count/alpha conflicts fail locally; explicit edit moderation is transmitted without changing omitted-flag behavior. |
| Output integrity | Base64 bytes are saved without losing alpha; format/extension agree; multiple outputs are not overwritten; empty or malformed results fail clearly. |
| Launcher/backend compatibility | Repo-local and standalone paths use the expected backend; an older backend cannot silently erase the requested model or feature. |

Do not add tests that merely assert the new constant's spelling or snapshot every line of skill prose. Tests should catch a wrong API request, corrupted output, or broken install behavior.

### 11.2 Visual and prompt evaluation

Use a small common set of source images and compare the same briefs before prompt retuning. Compare Image 2, Flare, and Sunburst where useful, preserving explicit quality and other supported settings first. Test higher quality against unmet requirements before rewriting the prompt; then change only the instructions that still need improvement. This follows the dedicated 2.5 guide and separates model, quality-setting, and prompt effects.

| Evaluation group | Success criteria |
|---|---|
| Reference fidelity and style transfer | Correct subject, distinguishing features, geometry, and intended style; no unintended reference-content transfer. |
| Precision and sequential edits | Requested change made; unrelated details and earlier accepted changes retained; no progressive visible degradation. |
| Alpha and reusable assets | Real alpha, good edges, correct encoding, no checkerboard backdrop, transparency retained after an edit. |
| Typography and factual layout | Exact copy, readable placement, retained hierarchy, and supplied relationships/numbers checked against their source. |
| Creative rendering and efficient defaults | Brief satisfied, appropriate texture/light/materials, correct effective model, and recorded latency/usage when exposed. |

Include a simple paraphrased user ask that omits model jargon, a prompt-only anti-case, and a host-native request. Include one new task outside the selected gallery categories to check that the skill generalizes rather than memorizing a route table.

Keep evaluation briefs separate from proposed prompts and expected conclusions. A reviewer should see the user brief, source images, and actual outputs, without being told which model should win. The release criterion is useful execution, not winning a cherry-picked comparison.

Record actual elapsed time and available usage for each run. Do not claim statistical performance from a handful of examples. Begin with the small showcase set and repeat only when a failure, changed implementation, or unresolved question justifies it.

### 11.3 Package checks

Run these basic package checks after implementation:

```bash
git diff --check
python3 -m py_compile src/gpt_image_cli/cli.py src/gpt_image_cli/__init__.py
uv run gpt-image --help
```

Run the new behavioral tests using the repository's chosen lightweight test command. Also check valid skill frontmatter, description length, quoted metadata, existing self-references, actual gallery counts, README image/claim parity, and isolated skill-folder usability.

A search for `gpt-image-2` is a classification check, not a zero-match requirement. Historical source links, explicit compatibility examples, old output provenance, and archival text may retain it. Active defaults and current runnable 2.5 examples must not retain it accidentally.

### 11.4 Acceptance criteria

1. **Default works:** CLI and skill-directed ordinary requests select the verified Flare ID; deliberate model choices remain intact across supported install paths.
2. **2.5 features work:** New quality values and required reference, edit, multi-turn, and transparency scenarios produce inspected usable outputs with correct API semantics.
3. **Prompt guidance helps:** Short clear requests stay short; complex requests gain useful structure; reference roles and critical invariants are explicit.
4. **Package is coherent:** Core skill, metadata, API reference, CLI help, READMEs, examples, and dependency declarations agree and do not require hidden repo context.
5. **Claims are supportable:** New examples identify actual model/settings; historical images are preserved honestly; unpublished parameters, prices, and API IDs are not invented.

## 12. Research coverage and sources

### 12.1 Repository material reviewed

Read the complete `skills/gpt-image/SKILL.md`, its `agents/openai.yaml`, the full launcher, canonical CLI, package metadata, and **all 34 Markdown reference files**: the gallery index, craft, the 1,004-line local cookbook, and all **31 category files containing 162 prompts**. This was a text and implementation audit; it did not visually inspect or regenerate all historical gallery images.

Also reviewed the sibling `get-prompt-from-image` entrypoint/metadata and the visible host-native `imagegen` boundaries; the relevant installation, usage, prompting, and example surfaces in both READMEs; plugin/marketplace manifests; contribution rules; changelog; and repository file inventory. No repository-local `AGENTS.md` was found. The session's supplied global instructions were applied.

### 12.2 Official release and capability sources

| Source | What it contributed |
|---|---|
| [Introducing ChatGPT Images 2.5](https://openai.com/index/introducing-chatgpt-images-2-5/) | Release, variant positioning, product features, announced improvements, and claimed speed. |
| [ChatGPT Images 2.5 system card](https://deploymentsafety.openai.com/chatgpt-images-2-5) | Corroboration of model names, capability context, safeguard/provenance behavior, and limits of safety evaluations. |
| [Flare model page](https://developers.openai.com/api/docs/models/gpt-image-2.5-flare) | Exact alias/snapshot, endpoints, quality values, and pricing caveats. |
| [Sunburst model page](https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst) | Exact alias/snapshot, editing/quality positioning, and supported controls. |
| [API pricing](https://developers.openai.com/api/docs/pricing#image-generation) | Confirmed standard image/text input, cached-input, and image-output rates for both variants. |

The system card describes C2PA provenance plus SynthID watermarking across the relevant products/API. Preserve original generated bytes when possible and do not teach the skill to remove provenance. The card's adversarial safety percentages are not ordinary-request refusal rates or creative-quality benchmarks. [System card](https://deploymentsafety.openai.com/chatgpt-images-2-5)

### 12.3 Official implementation and prompting sources

| Source | What it contributed |
|---|---|
| [Image generation guide](https://developers.openai.com/api/docs/guides/image-generation) | 2.5 generation/editing, masks, alpha output, new quality levels, size limits, pricing, Responses selection, and separate legacy-model notes. |
| [Generate image API reference](https://developers.openai.com/api/reference/resources/images/methods/generate) | Current generation request/response fields, model strings, output controls, and parameter scoping. |
| [Edit image API reference](https://developers.openai.com/api/reference/resources/images/methods/edit) | Current edit request/response fields, reference structure, moderation field, and count/format controls. |
| [GPT Image 2.5 prompting guide](https://developers.openai.com/api/docs/guides/image-prompting) | Full guide read: model selection, parameter table, migration method, illustrated generation/editing workflows, sequential edits, validation, and separately labeled legacy references. |
| [Responses image-generation tool guide](https://developers.openai.com/api/docs/guides/tools-image-generation) | Exact tool model selection, action controls, conversation continuation, prompt revision, and streaming. |

### 12.4 Additional cross-checks and research method

| Source | What it contributed |
|---|---|
| [Official model catalog](https://developers.openai.com/api/docs/models) | Current model entries and direct links to Flare/Sunburst. |
| [ChatGPT/Codex image generation](https://learn.chatgpt.com/docs/image-generation) | Native workflow and reference guidance; retrieved page still names Image 2, so no unsupported native 2.5 selector is promised. |
| [Official Python SDK v3.9.0](https://github.com/openai/openai-python/tree/v3.9.0) | Actual SDK method/type surface, supported extra-body transport, and the version used for nine passing offline serialization checks. |
| [Earlier cookbook rendering](https://developers.openai.com/cookbook/examples/multimodal/image-gen-models-prompting-guide) | Comparison with the repository's older guidance; not the current 2.5 parameter authority. |
| [Original cookbook notebook](https://github.com/openai/openai-cookbook/blob/main/examples/multimodal/image-gen-models-prompting-guide.ipynb) | Provenance of the repository's local MIT-licensed cookbook snapshot; current prompting guidance was read through the new developer guide. |

Official documentation search preceded direct retrieval. When search results continued returning older pages, the follow-up inspected the [API documentation index](https://developers.openai.com/api/docs/llms.txt), cookbook index, current model pages, and full page bodies. That located the dedicated 2.5 guide and resolved the first draft's open research items. Endpoint Markdown exports returned 404, so the actual HTML references were read instead. Unrelated community results were excluded.

The research read the dedicated guide end to end, including its reference-image prompts, model comparison examples, baseline Python example, and legacy-model tabs. Published illustrations are OpenAI's examples, not this repository's benchmark results. No claim in this plan implies that the ten proposed repository examples have already been generated or visually validated.

### 12.5 Authoring references applied

The design follows [skill-authoring](/Users/aelaguiz/.agents/skills/skill-authoring/SKILL.md), but that authoring environment path is **not a runtime dependency of the shipped skill**. Specifically applied: its skill-pattern contract, workflow modes, peer boundaries, packaging/trigger validation, and script-output economy; the `prompt-authoring` skill and prompt-pattern contract; and official-documentation model-migration guidance.

**Implementation outcome:** the researched migration is implemented and live-tested. Review [the actual outputs and limits](gpt-image-2-5/live/README.md); the price/sequence, references, alpha, masks, localization and quality/model controls were exercised. Historical prompts and image attribution remain intact. Publishing or global installation can follow the repository's normal release process when requested.
