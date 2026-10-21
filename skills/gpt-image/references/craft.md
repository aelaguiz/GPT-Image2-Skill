# Prompt craft for GPT Image 2.5

Write the smallest brief that makes the intended picture and its important constraints clear. A detailed brief is useful when the image itself is detailed; length, JSON syntax and repeated quality adjectives do not establish correctness. Adapt the following techniques to the user's deliverable. Current model and parameter facts live in [model-api.md](model-api.md).

## Start with the intended image

Name the use and the subject, then describe the visible details that determine success: setting, composition, materials, lighting, text and preservation requirements. A short request does not need a consultation or a gallery search before execution.

> Create a product photograph for a ceramic studio's online shop: a handmade cream mug with a cobalt-blue handle beside folded linen. Show uneven glaze and fine clay texture, morning window light from the left, a soft shadow and warm neutral surroundings. Leave room above for website copy. No text inside the image.

This gives the model a use, an object, a material treatment and a composition. “8K masterpiece, award-winning, highest quality” cannot substitute for those decisions or change the API's output dimensions. Camera/lens terms can describe a visual effect when useful; they do not produce real camera metadata or prove photographic authenticity.

Use prose, a few labeled sections or a structured object as convenient. For a complicated brief, labels such as **Scene**, **Layout**, **Exact copy** and **Preserve** help separate responsibilities. They are prompt text, not API fields. Avoid invented controls such as `render_flags: 8K_UHD`, fixed noun counts, compulsory section schemas or a mandatory number of references.

## Separate literal content from creative freedom

Quote text that must appear, preserving spelling, accents, case, punctuation, units and currency. State where it belongs, how often it appears and its hierarchy when those matter. Treat dates, prices and product claims as supplied content, not an invitation to invent plausible replacements.

> Design a quiet vertical tea poster. Headline: "山间冷泡" at the top, exactly once. Price: "18 元" beside the bottle. Date: "9月15日" at the bottom. Keep these strings verbatim. A cream bottle on pale stone is the main image; use restrained olive and cobalt accents. Leave generous margins and add no other lettering.

Specify Simplified versus Traditional Chinese when it matters; do not translate the user's copy by default. For localization, provide the approved source-to-target mapping, preserve unchanged numbers, and allow only the line-break or spacing adjustments needed to fit the new copy. Inspect every character after generation. Higher quality can help difficult lettering but does not guarantee it.

For real charts, educational visuals and scientific figures, ground facts, quantities and relationships in supplied or verified data before asking for the image. Generated text and geometry are not a source of scientific truth. Prefer a deterministic plotting tool when the deliverable requires accurate scales, calculable geometry or reproducible publication figures; GPT Image can still help with illustrations and visual concepts.

## Make layout explicit where it matters

Choose output shape to fit the deliverable. A 3:4 poster needs an actual 3:4 canvas such as `1152x1536`; the `portrait` shortcut is 2:3. A depicted phone screen or print sheet can have its own dimensions inside a differently shaped output. Resolve contradictions between the prompt and canvas before a paid call.

For an infographic, describe regions and reading order, label placement, connectors and any data relationships. Choose a diagram grammar suited to the content: numbered steps for a process, branching lines for hierarchy, arrows for directed flow, or consistent axes for a comparison. State what arrows and colors mean. Do not rely on the model to repair inconsistent totals.

> Create a three-step coffee process card, read left to right. Each step has one simple illustration above its label: "1. Grind", "2. Brew", "3. Serve". Use one arrow between adjacent steps, all pointing right. Cream paper, dark-brown linework and a single muted-blue accent. Equal column widths and consistent label baselines. No additional steps or text.

For UI concepts, supply the product purpose, key state, important controls and representative real content. Specify hierarchy, component relationships, selection states and navigation when visible. Avoid illegible pseudo-text and decorative controls with no function. A generated UI image is a design concept; it does not create functioning components, accessibility semantics or a tested application.

For multiple panels, specify panel count, order, the event in each panel and the anchors shared across panels. Keep the focal subject clear. Use a grid only when comparison or narrative benefits from it; do not force every idea into a contact sheet. For separate campaign assets, generate separate scenes from common identity/style anchors and compare them side by side.

## Describe style as visible evidence

A style reference is especially useful when medium, contour, palette, texture or lighting is hard to convey in words. Inspect the reference, name those properties, and distinguish them from its subject, typography and composition. Attach the file; naming its path in the prompt alone does not supply it.

> Image 1 supplies the dog and its markings. Image 2 supplies only rough pencil contours, flat ochre/blue shapes and visible paper grain. Draw the dog from Image 1 beside a doorway using that treatment. Exclude Image 2's person, chair and lettering.

Without a style image, describe the visual treatment directly: transparent watercolor washes with pooled pigment, blocky limited-palette pixels, cut-paper layers with soft contact shadows, or thin ink contours with sparse hatching. Name only the traits the deliverable needs. Historical gallery prompts may use named studios or artists as shorthand; concrete traits make the instruction clearer and easier to evaluate.

Separate **materials**, **lighting** and **palette** when they play different roles. “Brushed aluminum” describes the object; “large soft window light from the left” describes illumination; “cool gray with a small amber accent” describes color relationships. This distinction helps when a follow-up changes one property while preserving the others.

## Retain useful category judgment

| Deliverable | Useful decisions to state |
|---|---|
| Photography / products | Subject geometry, surface texture, light direction/softness, viewpoint, depth and intended context; imperfect real-world details when appropriate |
| Illustration / identity | Medium, contour, palette, texture, recognizable subject traits and permitted simplification |
| Poster / brand work | Hero image, supplied headline/claim/price/CTA, hierarchy, margins and exact artwork responsibilities |
| UI / diagram / infographic | Reading order, components or regions, data/labels, connections, alignment and visible state |
| Storyboard / series / interior | Scene beats or spatial anchors, shared identity/style, viewpoint, geometry and what varies |

These are decisions to consider, not compulsory fields. Open only the relevant [gallery category](gallery.md) if it offers a useful pattern. Read the actual prompt before adapting it, preserve its attribution, and discard details that do not serve the new task. Historical previews show those entries' provenance; they do not establish current model behavior.

## Make edits focused and self-contained

For an edit, name the specific change first. Name the important invariants: identity, pose, crop, typography, materials, lighting or previously approved changes. Avoid a long generic negative-prompt block; targeted exclusions belong in ordinary prompt text. There is no separate negative-prompt CLI flag.

> Change only the price "16 元" to "18 元". Keep its placement, scale and typography treatment. Preserve the bottle, all other copy, background, lighting and composition.

After accepting that output, attach it to the next request. Mention the updated price if a later change must retain it. For reference order, identity recovery, masks, annotations, exact-artwork compositing and alpha follow-ups, read [reference-images.md](reference-images.md).

## Iterate against an observable failure

Keep the original prompt, reference order, size, quality and format constant when first comparing Image 2 with Flare. A simultaneous rewrite cannot isolate whether the model improved the result. Use the same controls for Flare/Sunburst comparisons.

If a clear brief misses a requirement, compare `xhigh` or `max` before making it longer. If the result exposes ambiguity, fix that specific ambiguity. If a localized defect can be corrected, edit the accepted composition instead of redesigning it. Once the result passes, test lower quality only when optimizing latency or cost matters. Record retries as part of cost per accepted image.

Inspect what the user will rely on: exact copy, recognizable identity, important geometry, input-role separation, edit locality or transparent edges. Report a remaining defect plainly. Do not infer quality from the API returning success or from a flattering aesthetic description.

Adapted as original instructional guidance from OpenAI's [GPT Image 2.5 prompting guide](https://developers.openai.com/api/docs/guides/image-prompting), checked 2026-09-08. The guide includes product photography, exact text, diagrams, UI, localization, wardrobe edits, compositing and sketch workflows. Its final Image 2-pinned Python sample is a migration baseline, not this skill's default.
