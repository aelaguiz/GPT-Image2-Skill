# Reference images and successive edits

Use the actual image files as evidence. Before composing the request, inspect dimensions, crop, orientation, subject details, existing copy, lighting and any annotation. Name roles in the same order as the repeated `-i` flags. The model receives the file data, not the meaning of the filenames.

## Assign roles that match the intent

| Role | What the reference controls | What the prompt should resolve |
|---|---|---|
| Edit base | The existing image being changed | Exact change and important properties to preserve; put this image first |
| Subject / identity | Person, character, animal or product | Which shape, markings, face, clothing, proportions or label must remain recognizable |
| Style | Medium, contours, palette, texture, lighting, rendering treatment | Borrow the visual treatment; explicitly exclude unrelated subjects, text and composition when needed |
| Layout / sketch | Geometry, placement, relative scale, viewpoint | Preserve spatial relationships; treat notes/arrows as instructions unless they should be visible |
| Exact artwork | Approved logo, label or graphic | Where it belongs, its literal copy, and whether generative approximation is acceptable |

One image may serve several roles when that is intentional. If references conflict, use the user's stated priorities or explain the narrow assumption in the brief. Add references because they convey relevant evidence; sixteen is a limit, not a target. Crop irrelevant material when helpful, keeping originals and describing any crop that affects identity or layout.

### Subject plus style

```bash
gpt-image -i dog.png -i pencil-style.png -p 'Image 1 supplies the dog: preserve its muzzle, ears, black-and-white markings and red collar. Image 2 supplies only coarse pencil contours, flat ochre and blue shapes, and paper grain. Illustrate this dog waiting beside a front door at dog-eye level. Exclude Image 2’s person, furniture and lettering. No text.' -f dog-at-door.png
```

Inspect both references first; the named traits above must match the actual dog and style image. A good style prompt describes visible evidence rather than relying only on a famous name or a stack of generic quality words. Inspect the output for both identity retention and unwanted copying from the style source.

### Product plus style plus artwork

```bash
gpt-image -i bottle.png -i lighting-reference.png -i approved-wordmark.png -p 'Image 1 supplies the bottle: preserve its silhouette, cap, proportions and material. Image 2 supplies only warm side light, pale stone and muted olive shadows. Image 3 supplies the approved wordmark. Photograph the bottle on pale stone, centered with empty space above. Place Image 3’s wordmark on the front label above the exact copy "COLD BREW" and "250 ml". Do not copy Image 2’s product, typography or props.' -f bottle-campaign.png
```

These are three ordinary image inputs; there is no `style_reference` or logo-lock parameter. Inspect wordmark shape and spelling. If approved artwork must remain pixel- or vector-exact, generate the surrounding scene and place the artwork with deterministic compositing. Do not describe a model's redrawing as exact reproduction.

## Continue from the accepted image

The Images API CLI is stateless. An edit has access only to the current prompt and attached files. Keep the most recent accepted image as the first input, use a new output filename, and state the earlier changes that must survive.

```bash
# First accepted change
gpt-image -i poster.png -p 'Change only "16 元" to "18 元". Preserve all other copy, imagery, layout, colors and typography treatment.' --size 1152x1536 -f poster-v2.png

# Run after inspecting and accepting v2
gpt-image -i poster-v2.png -p 'Change only the bottle cap to cobalt blue. Preserve the updated price "18 元", all other text, bottle shape, layout, lighting and background.' --size 1152x1536 -f poster-v3.png

# Run after inspecting and accepting v3
gpt-image -i poster-v3.png -p 'Change only "9月8日" to "9月15日". Preserve price "18 元", cobalt-blue cap, all remaining copy, layout, product details and background.' --size 1152x1536 -f poster-v4.png
```

If identity drifts, attach the original identity anchor as another reference and explain that it restores identity while the first input owns the accepted composition and edits. Do not restart from the original and accidentally discard accepted changes. For a coordinated campaign, use separate scene requests with common identity/style anchors; `-n 2` is two variants of one prompt, not two named scenes.

## Sketches, annotations and masks

A sketch is a layout reference, even when rough. Describe the spatial relationships that matter, and separate them from a material/style reference. Check door/window positions, object footprints and viewpoint in the result. ChatGPT's drawing interface is not required; upload the saved sketch through `-i`.

For annotations, attach the clean base first and the marked copy second. Say what the marker identifies and require the final image to omit all circles, arrows and notes. An annotated JPEG is visual guidance, not an alpha mask. If no clean base exists, state that the model must remove annotation marks while editing; preservation is harder to judge.

```bash
gpt-image -i coat.png -i coat-annotated.png -p 'Image 1 is the clean base. Image 2 only marks the sleeve on the viewer’s right. Recolor that sleeve forest green. Preserve the other sleeve, buttons, person, pose and background. Include no annotation marks or notes.' -f coat-green-sleeve.png
```

For an alpha mask, prepare a PNG first input and PNG mask with exactly the same pixel dimensions. The mask needs an alpha channel: transparent pixels designate the region to change, opaque pixels the region to preserve. Merely drawing black and white regions in an opaque image is not an alpha mask. The mask applies to the first input even when later style/subject references are attached.

```bash
gpt-image -i room.png -m chair-mask.png -p 'Replace the masked chair with a low oak chair with cream upholstery. Match the existing room lighting and perspective; preserve the surrounding room.' -f room-new-chair.png
```

A mask guides generation; inspect the entire image for collateral changes. If every pixel outside the selected region must remain identical, use the generated region in a deterministic composite over the original and inspect its boundary. Current format/file-size limits are in [model-api.md](model-api.md).

## Transparent assets

Request a cutout in both prompt and API control:

```bash
gpt-image -i bottle.png -p 'Extract this bottle onto a fully transparent background. Preserve the cap, full silhouette, label text and texture. Clean edges; no backdrop, painted checkerboard, extra objects or ground shadow.' --background transparent --format png -f bottle-cutout.png

# Continue only after accepting the cutout
gpt-image -i bottle-cutout.png -p 'Change only the cap to cobalt blue. Preserve bottle geometry, label text, edge detail and the fully transparent background.' --background transparent --format png -f bottle-cutout-blue.png
```

The CLI checks for an alpha channel containing non-opaque pixels. Also check that intended opaque subject regions are actually opaque when the deliverable requires it: the recorded 2.5 cutout had a maximum alpha of 254 rather than 255. That does not establish a clean cutout: inspect against light and dark backgrounds for halos, clipped edges, missing holes and unwanted shadows. Keep preview composites separate from the returned transparent file. Repeat `--background transparent` on follow-ups so the request is self-contained. JPEG cannot preserve alpha.

## Evaluate the result against the reference

| Task | Check |
|---|---|
| Identity or product preservation | Silhouette, proportions, distinct markings, face, label and materials |
| Style transfer | Intended medium/palette/texture, with no unwanted source subject or lettering |
| Local edit | Requested region and all important unchanged regions |
| Exact copy / localization | Every character, accent, number, occurrence and line break against supplied copy |
| Sequence / transparent edit | Earlier accepted changes, shared anchors, real alpha and edge quality |

Correct a visible failure with a focused instruction or a controlled model/quality comparison. Do not silently replace missing references with imagined ones. If the input is unavailable, ask for the missing file or proceed only with a clearly identified text-only approximation when the task allows it.

Based on the [official 2.5 prompting guide](https://developers.openai.com/api/docs/guides/image-prompting) and [Images API guide](https://developers.openai.com/api/docs/guides/image-generation), checked 2026-09-08. The prompts here are original instructional examples, not claims of executed generations.
