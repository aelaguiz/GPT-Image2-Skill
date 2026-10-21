# GPT Image 2.5 implementation and validation

**Status, 2026-09-08:** implementation, offline package validation and live image validation complete. **22 of 22 live requests succeeded:** 21 using GPT Image 2.5 and one Image 2 baseline. Every output was inspected; one campaign image needed a focused corrective edit. [Actual images, request records, usage and caveats](live/README.md) are saved alongside this document.

The default is now `gpt-image-2.5-flare` across the canonical CLI, skill instructions, launcher expectations, package/plugin metadata and current English/Chinese examples. Version diagnostics report:

```text
gpt-image 0.3.0 (default: gpt-image-2.5-flare)
```

## Implemented behavior

| Area | Result |
|---|---|
| Models and quality | Flare default; explicit Sunburst, snapshots and compatible legacy IDs preserved; `xhigh`/`max`; exact Image 2 fidelity restriction; no silent model substitution |
| Inputs and routing | No image → generations; actual ordered references → multipart edits; alpha mask targets first PNG input; file/count/size/format checks before credentials or API client |
| Output integrity | PNG/JPEG/WebP filename/encoding agreement, transparent PNG/WebP generation/editing, returned-byte preservation, decoding/dimension/alpha checks before writing, distinct batch filenames |
| SDK and launcher | OpenAI SDK ≥3.9.0, Pillow, explicit edit moderation via `extra_body`, closed upload handles, effective version diagnostics, stale-backend rejection; one canonical API implementation |
| Skill and documentation | Prompt-first workflow, reference roles, style/content separation, retained accepted edits, masks/annotations, alpha inspection, current sourced API guidance, historical archive labeling, bilingual current docs and contributor rules |

The live-tested [feature recipes](../../skills/gpt-image/references/gallery-gpt-image-2-5.md) add No. 163–172 without renumbering No. 1–162. All twelve [portable inputs](../../skills/gpt-image/assets/gpt-image-2-5/README.md) are original deterministic drawings (282,935 bytes total), visually inspected as a contact sheet. They are not AI outputs. The optional [fixture source](create_reference_assets.py) uses Pillow and local fonts, with no API calls. The source distribution includes the skill, references and inputs; the wheel provides the CLI backend.

## Completed verification

| Check | Observed result |
|---|---|
| `uv run pytest -q` | **45 passed**; actual SDK 3.9.0 request serialization over `httpx2.MockTransport`, with synthetic image responses |
| Source distribution tests | Built archive extracted to a temporary directory; isolated `uv run pytest -q`: **45 passed** |
| `uv build` | Built 0.3.0 source distribution and wheel successfully |
| Isolated wheel installation | Installed the built wheel into a temporary virtual environment, outside the checkout; command reports 0.3.0 / Flare |
| Folder-only skill, installed module | Copied only `skills/gpt-image` to a temporary directory; launcher finds the isolated installed package and reports 0.3.0 / Flare |
| Folder-only skill, `uv` script/PATH backend | Script environment has SDK dependencies; delegates to isolated compatible PATH CLI and reports 0.3.0 / Flare |
| Python compile, CLI help/version, whitespace | Passed required compile/help/version and `git diff --check` checks |
| Local skill validator | `quick_validate.py skills/gpt-image`: **Skill is valid!** |
| Metadata | Valid YAML/JSON/TOML; synchronized 0.3.0 package/plugin version; 353-character trigger description; `agents/openai.yaml` co-edited |
| Gallery and local links | 172 unique consecutive entry numbers; all 162 historical prompt code blocks preserved; all checked local document/image paths resolve in the checkout |
| README historical previews | Image paths/order preserved separately in each language: 125 English and 128 Chinese historical preview references; this pre-existing difference was not converted into artificial parity |
| Recipe preflight | 15 executable example/comparison commands validate against existing inputs; three follow-ups correctly require their earlier accepted outputs; no API client or credentials used |

Behavioral tests cover generation defaults, all four 2.5 aliases/snapshots with both new quality levels, Flare/Sunburst multipart edits at `xhigh`/`max`, input ordering, masks, fidelity/moderation omission versus explicit values, invalid requests before key loading, model-access errors without fallback, exact output bytes, alpha, dimensions/encoding, empty/malformed responses, batch naming, file closure and launcher routing/version rejection.

The local skill validator initially rejected the existing `compatibility` frontmatter key because its allowlist excludes it. Requirements now live in the body, preserving the information while passing that validator. The source package initially omitted the skill needed by its launcher tests; `MANIFEST.in` now includes the skill and portable assets, and tests pass from the extracted archive. No global skill/CLI installation was changed. The `skills` repository diagnostic was not installed; no unrelated package was installed solely to run it.

## Manual skill-contract walkthrough

These are **manual instruction/routing reviews**, not independent agent-trigger measurements or live image runs. They test whether the written skill yields a clear next action without hidden context.

| User ask | Reviewed behavior |
|---|---|
| “Make a shop photo of this mug.” | Inspect the supplied mug, preserve its identity, write a concise product brief and use Flare via edits; no mandatory gallery research or consultation |
| “Make it feel like this pencil drawing.” | Inspect both images, separate subject from style evidence, attach actual ordered inputs, exclude unrelated source content and inspect both identity and style |
| “Fix the price, leave the rest alone.” | Use the poster as edit base, quote the correction, preserve copy/layout, save a new file and inspect the entire result |
| “Design a botanical seed-packet illustration.” | Generalize the craft guidance to the new deliverable; choose relevant reference guidance only if useful, without a fixed category schema |
| “Extract a reusable prompt; don't generate anything.” / “Use the host's built-in image tool.” | Respect the image-to-prompt companion or host-managed tool boundary; do not execute the local-key CLI or claim an unavailable per-variant selector |

The live execution results are now recorded in [the live report](live/README.md). The recipe inputs deliberately make copy, geometry, identity and unwanted style-content transfer observable. The visual evaluator should compare actual results without a predetermined model winner.

## Completed live validation

The user provided a local credential-file location. The key was loaded into the test process without displaying it, copying it into this repository or changing the source environment file. The measurement driver invoked the canonical CLI and captured response metadata; no new image API implementation was added.

| Check | Observed outcome |
|---|---|
| Default generation and references | Flare default works live; product photo, subject/style, and three-input product/style/wordmark composition accepted |
| Exact copy and sequential edits | Correct Chinese price; blue-cap and date follow-ups retained earlier changes; Spanish copy and process labels checked visually |
| Layout, alpha, local edits | Sketch/material rendering accepted as a concept; transparent cutout and transparent follow-up succeeded; annotation and mask selected the correct sleeve |
| Models and quality | Flare and Sunburst both accepted high/xhigh/max edits; Image 2 baseline also succeeded; high was sufficient for this simple comparison |
| Campaign and correction | Shared style/identity across two scenes; a new white flank marking in the first arrival output was removed in one focused correction |

The 21 GPT Image 2.5 requests have an **uncached-rate usage estimate of $1.6824**, including comparisons and the correction, excluding the Image 2 baseline. This is calculated from returned usage and documented rates, not an invoice. Request records include actual parameters, input/output hashes, usage, timestamps, elapsed times and visual findings. Aliases were requested; dated snapshots were not returned by the API. Automatic SDK retries were not separately instrumented; each recorded case has one application-level attempt.

## Material limits found in the live outputs

1. Precise edits and masks preserved requested content/layout but introduced slight texture or shading outside the target. Exact pixel preservation still needs deterministic editing/compositing.
2. Both transparent results have alpha 0–254. They have real transparency and usable light/dark edges, but no fully opaque product pixels; inspect/correct alpha deliberately where full interior opacity is required.
3. Localization preserved exact strings and accents but increased headline weight. The interior sketch became a usable concept with extra pillows/rug, not an exact architectural reconstruction.
4. A new viewpoint introduced an unrequested dog marking. The original failed result and successful correction are retained, demonstrating the need for identity inspection.
5. This is a small visual test set, not a statistical model ranking. Live calls covered PNG; JPEG/WebP, optional fidelity and explicit edit moderation also have offline coverage but were not all separately live-tested.

The ten recipes now link to real inspected outputs, and both READMEs include matching current previews. The migration plan's live-output prerequisite is resolved. Publishing, pushing and global installation remain separate from this local implementation.
