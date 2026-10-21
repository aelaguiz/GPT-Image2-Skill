# Contributing

Contribute a useful prompt, an inspected example, a CLI fix or clearer skill guidance. The current execution default is GPT Image 2.5 Flare. The historical gallery remains attributed source material; do not relabel its outputs as newly generated.

## Add a gallery entry

1. Read the actual prompt and choose a relevant `skills/gpt-image/references/gallery-*.md` category. The split gallery is canonical; README is a selected showcase.
2. Append a stable number after the current maximum and update `references/gallery.md` ranges/counts. Do not renumber unrelated entries. The catalog currently contains 162 historical entries and 10 live-tested 2.5 recipes, No. 163–172.
3. Record prompt authorship/source separately from image provenance. “Curated” is an editorial label, not a generating-model record. Preserve an outside prompt's author and source URL; an unknown generating model remains unknown.
4. Add actual inspected outputs under `docs/<category-slug>/`. Small reusable original or rights-cleared input images belong inside `skills/gpt-image/assets/` with their provenance, so folder-only installs can use them. Mark recipes without outputs **unexecuted** and do not add nonexistent preview links.
5. Promote a selected rendered example to both `README.md` and `README.zh.md`, with matching input/output paths, model/settings and status. A catalog-only addition does not require duplicating the full entry into both READMEs.

## Record enough to reproduce and assess

For a generated result, include the actual model ID (snapshot when available), UTC date, endpoint, exact prompt, ordered input files/roles, size, quality, background, output format/compression, explicit moderation/fidelity, output path and post-processing. Preserve originals; disclose any crop, compositing or resizing. Record latency, usage and retries when evaluating cost or comparing quality/models. Do not call an unexecuted request a successful demonstration.

For an edit, show the input and output and inspect both the requested change and important unchanged regions. For a sequence, retain each accepted intermediate. For transparency, check real alpha and light/dark edges. For required text, verify every character against supplied copy. For factual diagrams, use verified data and check the relationships; visual polish is not evidence of factual accuracy.

Example entry shape (use only fields supported by actual evidence):

```markdown
### No. N · Descriptive title

Prompt author/source: original contribution, or Author + linked Source.
Generation: actual model; UTC date; endpoint; ordered inputs and roles.
Settings: size; quality; n; background; format; other explicit controls.
Output: existing file and preview, or “Unexecuted recipe; no output.”
Inspection: observed result and remaining defects.
Post-processing: none, or the actual disclosed transformation.

[Exact prompt and a runnable command with the real input order.]
```

## Keep the skill simple

Normal generation uses the canonical CLI, not new API wrappers. Teach art direction and reference judgment in prose, with examples loaded when useful. Keep current parameter facts in `model-api.md`; historical source archives should point to it rather than acquiring competing current tables. Update `SKILL.md` and `agents/openai.yaml` together when their contract changes.

## Verify the change

```bash
git diff --check
uv run python -m py_compile src/gpt_image_cli/cli.py src/gpt_image_cli/__init__.py skills/gpt-image/scripts/generate.py
uv run gpt-image --version
uv run gpt-image --help
uv run pytest -q
```

For documentation/assets, check local links, stable entry numbers/counts, input ordering, model labels, README parity for newly promoted entries and standalone skill paths. Historical repository-only previews may be absent in a folder-only install; the skill must label them optional. For runtime changes, add focused behavioral coverage only where it catches a wrong request, corrupt output or broken install. Mocked API tests do not validate model quality or account access.

A PR should state the concrete behavior changed, the relevant validation and any outstanding live verification. Publishing and global installation are separate actions from local implementation.

## 中文说明

完整图库以 `skills/gpt-image/references/gallery-*.md` 为准，README 仅展示精选。新条目使用稳定追加编号，不重排旧条目；只有晋升精选时才同步两种语言的 README。提示词来源与实际生成模型分开记录，缺少输出的示例标记为“未执行”。新生成结果放在 `docs/<category-slug>/`，可复用输入放在技能内 `assets/` 并注明来源。记录真实参数、输入顺序、修改步骤与检查结果；旧图片不重新标为 2.5 输出。提交前运行上述验证命令并检查链接、编号及中英文状态一致性。
