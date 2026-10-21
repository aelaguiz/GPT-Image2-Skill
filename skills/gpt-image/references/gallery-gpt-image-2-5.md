# GPT Image 2.5 feature recipes — No. 163–172

**Status: rendered and visually inspected on 2026-09-08.** All ten recipes were exercised through the real API, with 21 GPT Image 2.5 requests plus one Image 2 baseline. One campaign result required a focused correction. See [actual outputs, records and limitations](../../../docs/gpt-image-2-5/live/README.md). These are original prompts authored for this repository, using techniques from the [official 2.5 prompting guide](https://developers.openai.com/api/docs/guides/image-prompting) and [Images guide](https://developers.openai.com/api/docs/guides/image-generation).

Use a compatible `gpt-image` 0.3.0+ command. Run the following setup from **the installed skill's directory**, which contains `SKILL.md`; `refs` then points to bundled files. API calls need your configured key and incur usage charges. Each command states its local output filename. Recorded outputs are linked below; previews are optional repository assets and may be absent in a standalone skill install. The bundled inputs and runnable prompts remain self-contained.

```bash
refs="$PWD/assets/gpt-image-2-5"
out="$PWD/image-25-results"
mkdir -p "$out"
gpt-image --version
```

Inputs are [original deterministic drawings](../assets/gpt-image-2-5/README.md), not photographs or generated results. They make the examples runnable without an external image archive. Use real product/person/style inputs for production work, inspect them, and adjust the traits in the brief accordingly. Unless overridden below, requests use Flare, high quality, 1024×1024, PNG, `n=1`, background auto, fidelity omitted. Generation moderation retains CLI `low`; edits use the API default.

## No. 163 — E1: Brief to product photograph

**Observed:** Flare/high: product brief met; 19.29 seconds. [Output](../../../docs/gpt-image-2-5/live/e1-mug.png) · [request and review](../../../docs/gpt-image-2-5/live/e1-mug.json).

**Endpoint:** generations. **Inputs:** none. **Checks:** cream mug, cobalt handle, visible glaze/clay texture, left window light, space above, no text. This checks the default model without a model flag.

```bash
gpt-image -p 'Create a product photograph for a ceramic studio’s online shop: a handmade cream mug with a cobalt-blue handle beside folded linen. Show uneven glaze and fine clay texture, morning window light from the left, a soft shadow, warm neutral surroundings, and empty space above for website copy. No text inside the image.' -f "$out/e1-mug.png"
```

## No. 164 — E2: Subject identity plus style-only reference

**Observed:** Subject markings and style treatment retained; no copied person, chair or lettering. [Output](../../../docs/gpt-image-2-5/live/e2-dog-at-door.png) · [request and review](../../../docs/gpt-image-2-5/live/e2-dog-at-door.json).

**Endpoint:** edits. **Ordered inputs:** `dog.png`, `pencil-style.png`. **Checks:** upright ears, viewer-left black eye patch, white muzzle/belly, red collar; ochre/blue treatment and grain; no borrowed person, chair or “STUDY” lettering.

```bash
gpt-image -i "$refs/dog.png" -i "$refs/pencil-style.png" -p 'Image 1 supplies the dog: preserve its upright ears, black patch around the eye on the viewer’s left, white muzzle and belly, dark body and red collar. Image 2 supplies only sparse pencil contours, flat ochre and blue shapes, and paper grain. Illustrate this dog waiting beside a front door at dog-eye level. Exclude Image 2’s person, chair and lettering. No text.' -f "$out/e2-dog-at-door.png"
```

This creates a new composition via the edits endpoint. The style reference is an ordinary uploaded image with a role explained in the prompt.

## No. 165 — E3: Product, lighting/style and approved artwork

**Observed:** Product/style/wordmark roles worked and label copy is correct; artwork remains a generative rendering. [Output](../../../docs/gpt-image-2-5/live/e3-bottle-campaign.png) · [request and review](../../../docs/gpt-image-2-5/live/e3-bottle-campaign.json).

**Endpoint:** edits. **Ordered inputs:** `bottle.png`, `lighting-reference.png`, `approved-wordmark.png`. **Checks:** bottle proportions/cap, MORA wordmark, exact “COLD BREW” and “250 ml”, warm side light and olive shadows; no copied cup or “LIGHT STUDY” text. The product fixture is a drawing; the prompt asks for photographic rendering.

```bash
gpt-image -i "$refs/bottle.png" -i "$refs/lighting-reference.png" -i "$refs/approved-wordmark.png" -p 'Image 1 supplies the bottle design: preserve silhouette, cap, proportions and label layout. Render its body as matte cream ceramic. Image 2 supplies only warm side light, pale stone and muted olive shadows. Image 3 supplies the approved MORA wordmark. Create a campaign photograph of this bottle on pale stone, centered with generous space above. Use Image 3’s wordmark on the label with the exact additional copy "COLD BREW" and "250 ml". Do not copy Image 2’s cup, typography or layout.' -f "$out/e3-bottle-campaign.png"
```

If exact artwork is a delivery requirement, place the original wordmark with deterministic compositing and disclose that step. This recipe tests generative preservation, not a pixel-exact logo guarantee.

## No. 166 — E4: Correct one price without redesigning

**Observed:** Correct 18 元 and retained copy/layout; fine texture changed outside the price region. [Output](../../../docs/gpt-image-2-5/live/e4-price-flare-high.png) · [request and review](../../../docs/gpt-image-2-5/live/e4-price-flare-high.json).

**Endpoint:** edits. **Input:** `tea-poster.png`. **Settings:** 1152×1536 (3:4). **Checks:** only “16 元” changes to “18 元”; all other copy, bottle and layout remain. Inspect original and output side by side.

```bash
price_brief='Change only the price text "16 元" to "18 元". Keep its location, size, alignment and typography treatment. Preserve all other copy, bottle details, cap color, background, composition and colors.'
gpt-image -i "$refs/tea-poster.png" -p "$price_brief" --size 1152x1536 -f "$out/e4-price-flare-high.png"
```

## No. 167 — E5: Retain three successive accepted changes

**Observed:** All three edits retained: 18 元, cobalt cap, 9月15日; some cumulative texture change. [Output](../../../docs/gpt-image-2-5/live/e5-new-date.png) · [request and review](../../../docs/gpt-image-2-5/live/e5-new-date.json).

**Endpoint:** edits for each call. **Start:** the accepted E4 result, which is the first edit of this sequence. **Checks:** final image keeps “18 元”, blue cap and “9月15日”, with all other content retained. Do not run the next command until the preceding output is inspected and accepted.

```bash
gpt-image -i "$out/e4-price-flare-high.png" -p 'Change only the bottle cap to cobalt blue. Preserve the updated price "18 元", all other copy including "9月8日", bottle geometry, label, background, layout and colors.' --size 1152x1536 -f "$out/e5-blue-cap.png"
```

After accepting the blue-cap result:

```bash
gpt-image -i "$out/e5-blue-cap.png" -p 'Change only the date "9月8日" to "9月15日". Preserve price "18 元", cobalt-blue cap, all remaining copy, bottle details, background and composition.' --size 1152x1536 -f "$out/e5-new-date.png"
```

Retain the original plus all three accepted outputs. If an earlier change is lost, correct from the latest usable result with explicit invariants; do not describe the chain as successful.

## No. 168 — E6: Sketch geometry plus separate materials

**Observed:** Layout relationships and materials retained; added pillow/rug and approximate geometry limit exact architectural use. [Output](../../../docs/gpt-image-2-5/live/e6-room.png) · [request and review](../../../docs/gpt-image-2-5/live/e6-room.json).

**Endpoint:** edits. **Ordered inputs:** `room-sketch.png`, `materials.png`. **Settings:** 1536×1024. **Checks:** left-wall window, sofa underneath, low table to the right, viewpoint and relative footprints; oak, cream weave and matte green ceramic; no visible sketch labels.

```bash
gpt-image -i "$refs/room-sketch.png" -i "$refs/materials.png" -p 'Image 1 is the layout sketch: preserve its window position, sofa footprint, table placement and viewpoint. The WINDOW, SOFA and TABLE notes identify objects and must not appear in the result. Image 2 supplies only light oak, woven cream upholstery and matte green ceramic material cues. Render the sketched room as a believable daylight interior: oak table, cream sofa and one small green ceramic bowl on the table. Retain Image 1’s furniture arrangement; do not copy Image 2 as a swatch board.' --size landscape -f "$out/e6-room.png"
```

This uses an uploaded sketch through ordinary references. It does not expose ChatGPT's Sketch UI as a CLI feature.

## No. 169 — E7: Transparent cutout and transparent follow-up

**Observed:** Real alpha retained through the edit; alpha 0–254 means even the product interior is fractionally translucent. [Output](../../../docs/gpt-image-2-5/live/e7-cutout-blue.png) · [request and review](../../../docs/gpt-image-2-5/live/e7-cutout-blue.json).

**Endpoint:** edits. **Input:** `bottle.png`, then the accepted cutout. **Settings:** PNG, transparent. **Checks:** actual alpha, complete silhouette, intact “MORA / COLD BREW / 250 ml”, no backdrop/shadow; clean edges on light and dark preview backgrounds.

```bash
gpt-image -i "$refs/bottle.png" -p 'Extract the bottle from Image 1 onto a fully transparent background. Preserve its drawing style, cap, geometry, label text and colors. Keep the complete silhouette with clean edges. No backdrop, painted checkerboard, extra objects or ground shadow.' --background transparent --format png -f "$out/e7-cutout.png"
```

After inspecting and accepting the cutout:

```bash
gpt-image -i "$out/e7-cutout.png" -p 'Change only the cap to cobalt blue. Preserve the bottle drawing, geometry, exact label text, clean edges and fully transparent background.' --background transparent --format png -f "$out/e7-cutout-blue.png"
```

Keep the original transparent outputs. Any light/dark inspection composites are separate preview files, not replacements. Transparency already existed in Image 2 preview; this demonstrates correct 2.5 use rather than a claim of first introduction.

## No. 170 — E8: Annotation-guided local change and mask alternative

**Observed:** Correct sleeve recolor without annotations; mask variant also worked, with minor changes outside the target. [Output](../../../docs/gpt-image-2-5/live/e8-annotation.png) · [request and review](../../../docs/gpt-image-2-5/live/e8-annotation.json).

**Endpoint:** edits. **Ordered inputs:** `coat.png`, `coat-annotated.png`. **Checks:** only the sleeve on the viewer's right becomes forest green; coat body, opposite sleeve and buttons retained; no annotation or note text. This fixture is a flat coat drawing with no person.

```bash
gpt-image -i "$refs/coat.png" -i "$refs/coat-annotated.png" -p 'Image 1 is the clean base. Image 2 only identifies the sleeve on the viewer’s right. Recolor that sleeve forest green. Preserve the coat body, other sleeve, buttons, outlines, composition and background. Include no annotation marks or note text.' -f "$out/e8-annotation.png"
```

An alternative uses the supplied 1024×1024 PNG alpha mask on the first PNG input. Transparent mask pixels mark the sleeve:

```bash
gpt-image -i "$refs/coat.png" -m "$refs/sleeve-mask.png" -p 'Recolor the masked sleeve forest green. Preserve the coat body, other sleeve, buttons, outlines, composition and background.' -f "$out/e8-mask.png"
```

Compare collateral changes across the full image. Neither method guarantees unchanged pixels outside the target; deterministic compositing is required for that guarantee.

## No. 171 — E9: Exact-copy localization

**Observed:** Exact Spanish copy, accents and price retained; headline weight increased. [Output](../../../docs/gpt-image-2-5/live/e9-spanish-poster.png) · [request and review](../../../docs/gpt-image-2-5/live/e9-spanish-poster.json).

**Endpoint:** edits. **Input:** `english-poster.png`. **Settings:** 1152×1536. **Checks:** three exact replacements, accents/copy/line breaks, unchanged price “$16” and bottle label, retained hierarchy and imagery.

```bash
gpt-image -i "$refs/english-poster.png" -p 'Localize only these three poster strings: "MOUNTAIN BREW" becomes "CAFÉ DE MONTAÑA"; "FRESH EVERY DAY" becomes "FRESCO CADA DÍA"; "SEPTEMBER 8" becomes "8 DE SEPTIEMBRE". Preserve price "$16", the MORA wordmark, COLD BREW and 250 ml bottle label, imagery, colors, alignment and hierarchy. Retain the typography character; adjust line breaks only where the Spanish copy needs room. Add no other text.' --size 1152x1536 -f "$out/e9-spanish-poster.png"
```

## No. 172 — E10: Two scenes with shared identity and style

**Observed:** A focused correction removed an invented flank marking; final arrival and purchase scenes share identity/style. [Output](../../../docs/gpt-image-2-5/live/e10-arrival-corrected.png) · [request and review](../../../docs/gpt-image-2-5/live/e10-arrival-corrected.json).

**Endpoint:** two separate edits calls. **Ordered anchors in each:** `dog.png`, `pencil-style.png`. **Checks:** same dog markings, red collar, palette, contour/texture across different compositions; scene A arrival and scene B purchase. These are distinct briefs, not `-n 2`.

```bash
campaign_anchor='Image 1 supplies the dog: preserve upright ears, viewer-left black eye patch, white muzzle and belly, dark body and red collar. Image 2 supplies only sparse pencil contours, flat ochre/blue shapes and paper grain; exclude its person, chair and lettering.'
gpt-image -i "$refs/dog.png" -i "$refs/pencil-style.png" -p "$campaign_anchor Scene A: the dog arrives at a small neighborhood bakery, seen from outside the open door. A warm welcoming illustration. No text." -f "$out/e10-arrival.png"
```

After inspecting scene A, keep the same anchors for scene B. If A introduced an approved new identity/style detail, attach A as an additional reference and name that detail:

```bash
gpt-image -i "$refs/dog.png" -i "$refs/pencil-style.png" -p "$campaign_anchor Scene B: the same dog stands beside the bakery counter as a paper bag of bread is handed down toward it. Interior viewpoint, warm welcoming illustration. No text." -f "$out/e10-purchase.png"
```

### Observed correction: an invented campaign marking

The first arrival scene added a round white spot to the dog's hindquarter. Inspecting the output caught it. This focused edit, with the original identity anchor attached, removed the spot while retaining the scene:

```bash
gpt-image -i "$out/e10-arrival.png" -i "$refs/dog.png" -p 'Image 1 is the campaign image to edit. Image 2 is the original dog identity anchor. Remove only the round white patch on the visible hindquarter in Image 1, filling it with the same dark coat as the surrounding body. Preserve the dog pose, white paws, white muzzle and belly, eye marking, red collar, round collar tag, bakery, framing, palette and paper texture. Do not add or move any other markings. No text.' -f "$out/e10-arrival-corrected.png"
```

[Initial arrival](../../../docs/gpt-image-2-5/live/e10-arrival.png), [corrected arrival](../../../docs/gpt-image-2-5/live/e10-arrival-corrected.png), and [purchase scene](../../../docs/gpt-image-2-5/live/e10-purchase.png) are retained. A front-view identity anchor leaves unseen markings ambiguous; specify critical anatomy/markings when a new viewpoint reveals them, and inspect the result.

## Controlled quality and model comparisons

Use E4's same original input and exact `price_brief`. Keep size, output format, background and reference order fixed. Each command is an additional billed request, not a required step for an ordinary image task.

```bash
# Baseline from E4 is Flare/high. Compare the new quality settings:
gpt-image --model gpt-image-2.5-flare -i "$refs/tea-poster.png" -p "$price_brief" --quality xhigh --size 1152x1536 -f "$out/price-flare-xhigh.png"
gpt-image --model gpt-image-2.5-flare -i "$refs/tea-poster.png" -p "$price_brief" --quality max --size 1152x1536 -f "$out/price-flare-max.png"

# Compare variants at the same quality:
gpt-image --model gpt-image-2.5-sunburst -i "$refs/tea-poster.png" -p "$price_brief" --quality high --size 1152x1536 -f "$out/price-sunburst-high.png"

# Optional migration baseline; do not retune its prompt first:
gpt-image --model gpt-image-2 -i "$refs/tea-poster.png" -p "$price_brief" --quality high --size 1152x1536 -f "$out/price-image2-high.png"
```

If Sunburst needs its own quality evaluation, repeat that same brief/input with `--quality xhigh` and `--quality max`, using distinct filenames. In the recorded simple price edit, high already met the requirement; xhigh/max added output tokens without a needed visual improvement. This is one task, not a general model ranking. Do not compare defaults of different qualities and call that a model comparison.

For a small factual layout check independent of poster editing, use the original brief: **“Create three equal columns on cream paper with exactly these labels in left-to-right order: ‘1. Grind’, ‘2. Brew’, ‘3. Serve’. One coffee-related icon above each label, exactly two arrows connecting adjacent columns and both pointing right. Dark-brown lines and one muted-blue accent. No other text.”** Check count, reading order, arrows and text; it is a process illustration, not scientific evidence.

## Provenance to record after a live run

For each accepted result, record actual model (snapshot if returned), UTC date, endpoint, exact prompt, ordered input filenames, size, quality, background, format/compression, explicit moderation/fidelity, latency, usage, retries, output file and any post-processing. Keep rejected results available for the comparison. Record inspection findings and remaining defects instead of declaring success from HTTP status.

Repository showcase outputs belong in `docs/gpt-image-2-5/`. Standalone users can keep their results in `image-25-results/`. Add preview links only after the corresponding output exists and has been inspected. The recorded run retains originals, corrected outputs and derived previews separately. The [live report](../../../docs/gpt-image-2-5/live/README.md) contains all observed timings, usage and caveats.
