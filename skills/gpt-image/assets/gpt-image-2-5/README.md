# Portable reference fixtures

These twelve PNGs are **original deterministic drawings**, authored for this repository on 2026-09-08 and distributed under its MIT license. They were drawn with Pillow and local fonts; **none is a GPT Image 2.5 output or a model-quality demonstration**. No font files are distributed. The fictional MORA label is a test wordmark. Inputs deliberately contain distinctive traits and unrelated style content so an edit can be evaluated.

| Files | Purpose |
|---|---|
| `dog.png`, `pencil-style.png` | Subject identity (black patch on viewer-left eye, upright ears, red collar) versus style (ochre/blue, sparse contours, paper grain). Exclude style source's person, chair and “STUDY” text. |
| `bottle.png`, `lighting-reference.png`, `approved-wordmark.png` | Product geometry/label, separate light/palette/stone cues, supplied MORA artwork with real alpha |
| `tea-poster.png`, `english-poster.png` | 1152×1536 exact-copy edit bases; Chinese price/date and English localization |
| `room-sketch.png`, `materials.png` | 1536×1024 room layout, with separate oak/cream weave/green ceramic material swatches |
| `coat.png`, `coat-annotated.png`, `sleeve-mask.png` | Clean coat, annotated viewer-right sleeve, same-size PNG alpha mask for that sleeve |

The example commands and inspection criteria are in [the 2.5 recipes](../../references/gallery-gpt-image-2-5.md). Use these files directly; no checkout or regeneration is required. The optional source generator is `docs/gpt-image-2-5/create_reference_assets.py` in the repository. It requires Pillow and local Latin/CJK font paths; use `--font` and `--cjk-font` on systems without the documented macOS defaults. Existing PNGs remain portable.
