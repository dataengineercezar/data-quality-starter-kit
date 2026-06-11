# Publication Checklist: Data Quality Starter Kit

Status: local checklist only. No remote repository, push or public publication is authorized by this file.

Last local review: 2026-06-10.

## Current Local Baseline

- Project: `data-quality-starter-kit`.
- Local checkpoint: `186cf04 Initial MVP checkpoint`.
- Remote repository: not created.
- External dependencies: none.
- Publication status: not published.
- Current local review status: publication candidate after local-only polish.

## Local Verification Evidence

- `python -B -m unittest discover -s tests -v`: 9 tests passed.
- Valid demo command returned `passed`, 7 checks and 0 failures.
- Error demo JSON returned `failed`, 7 checks, 6 failed checks and 10 expected failures.
- `docs/demo-output/validation_report.html` exists.
- `docs/demo-output/validation_report.png` exists.
- Redacted secret scan found only a false positive in this checklist.
- `git remote -v` returned no configured remote.

## Public Readiness Review

- [x] README explains the business problem clearly.
- [x] README includes local setup instructions.
- [x] README includes runnable CLI examples.
- [x] README includes architecture section.
- [x] README includes limitations section.
- [x] README includes license section.
- [x] Demo screenshot is visible in the README.
- [x] Demo docs explain the business scenario and expected output.
- [x] Tests pass locally.
- [x] Generated HTML demo exists in `docs/demo-output/validation_report.html`.
- [x] Screenshot exists in `docs/demo-output/validation_report.png`.
- [x] `dependencies = []` remains intentional and documented.
- [x] `.gitignore` avoids generated reports, caches and local environment files.
- [x] `LICENSE` is present and matches README.

## Privacy And Safety Review

- [x] No employer, client or consulting code is present.
- [x] No private datasets are present.
- [x] No credentials, tokens, keys or secrets are present.
- [x] No real customer data is present.
- [x] No paid service or external integration is configured.
- [x] No publication claim exceeds the MVP scope.

## Suggested Repository Metadata

Repository name:

```text
data-quality-starter-kit
```

Short description:

```text
Lightweight Python starter kit for validating CSV files with configurable data quality rules and HTML reports.
```

Suggested topics:

```text
python, data-engineering, data-quality, csv, validation, portfolio-project
```

Suggested visibility:

```text
public, only after explicit approval
```

## Remote Creation Gate

Before creating a remote repository, confirm all items below explicitly:

- [ ] Authorize creating a public GitHub repository.
- [ ] Confirm repository name.
- [ ] Confirm repository visibility.
- [ ] Confirm whether the initial branch should be renamed to `main` if needed.
- [ ] Confirm pushing the local commit to the remote.

Until those confirmations happen:

- do not create a remote repository;
- do not add a remote;
- do not push;
- do not publish the technical post.

## Post Publication Draft Gate

Before publishing `docs/technical-post-draft.md`:

- [ ] Replace local-only notes with final public wording.
- [ ] Add repository link only after the repository is public.
- [ ] Attach or reference the demo screenshot.
- [ ] Keep limitations visible.
- [ ] Avoid employer, client or consulting references.

## Next Local Step

Commit this local publication polish after explicit approval. After that, the next separate decision is whether to create a public remote repository.
