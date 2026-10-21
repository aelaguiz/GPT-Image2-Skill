# Changelog

## Unreleased — v0.3.0

- Default skill and CLI requests to `gpt-image-2.5-flare`; preserve explicit Sunburst, snapshot and compatible legacy selections. Add `xhigh`/`max`, effective `--version`, and a launcher guard against stale backends.
- Support transparent PNG/WebP generation and editing, coherent filename/encoding selection, ordered reference uploads, validated masks and output integrity. Keep fidelity omitted by default, scope Image 2's restriction to its exact aliases, and send explicit edit moderation through SDK `extra_body`.
- Rewrite the skill around clear briefs, inspected reference roles, retained accepted edits and visual verification. Add current model/API and reference-image guides; preserve useful craft and label the old cookbook/gallery as historical.
- Add ten live-tested 2.5 feature recipes, twelve portable original reference drawings, actual output/usage records and inspected previews. Complete 22 live requests, including an Image 2 baseline and a focused identity correction; document observed edit/alpha limitations without claiming a general benchmark.
- Align English/Chinese current guidance, plugin/package metadata and contributor rules. Add request/output/launcher regression tests and raise the inspected SDK floor to 3.9.0 with Pillow validation.

## v0.2.0 — 2026-04-25

This release collects the recent documentation, gallery, skill, and discoverability updates after the initial public release.

### Highlights

- **Full split Reference Gallery Atlas** — expanded the skill references into category-level `gallery-*.md` files so agents can load the relevant prompt slice without filling the context window.
- **README selected showcase refresh** — compacted the README into representative visual panels while keeping the full 162-prompt catalog in the Reference Gallery.
- **New and reorganized gallery material** — added/updated examples for research paper figures, scientific education, screen photography, gaming HUDs, events maps, beauty/lifestyle, cinematic references, and more.
- **Codex installation clarity** — clarified that `$skill-installer` is a built-in Codex skill-management helper and added a manual Codex fallback path.
- **Bilingual README navigation** — added visible English / 中文 switching near the README top.
- **SEO and discovery polish** — added natural search terms, expanded package/plugin keywords, GitHub topics, and Star History.

### Merged PRs

- #1 — Sync the full prompt gallery into the skill reference atlas
- #3 — Polish README showcase and sync split gallery atlas
- #4 — Add README language switch
- #5 — Clarify Codex skill installation
- #6 — Improve README SEO and add star history
