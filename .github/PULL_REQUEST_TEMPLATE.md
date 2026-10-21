## Change

<!-- Name the concrete problem and resulting behavior. -->

## Gallery / skill checks

- [ ] Added/updated the canonical reference category and stable index numbering where applicable
- [ ] Separated prompt attribution from actual model, settings, inputs and output provenance; unexecuted recipes labeled
- [ ] Kept portable input assets inside the skill; preview links target existing files
- [ ] Updated both READMEs when promoting a selected example or changing current behavior
- [ ] Updated skill metadata and current API guidance where their contract changed

## Validation

<!-- Relevant tests/checks and actual results. Distinguish mocked requests, live API runs and visual inspection. -->

```text
git diff --check
uv run gpt-image --version
uv run gpt-image --help
uv run pytest -q
```

## Remaining limitations

<!-- Only material unresolved issues, including missing live image verification. -->
