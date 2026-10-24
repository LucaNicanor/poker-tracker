# Clean Code tooling review

GitHub public API snapshot retrieved during this task (2026-10-23 local date).
These are popular relevant repositories, ranked within this shortlist, not an
exhaustive ranking of every Clean Code project. Stars measure popularity, not
correctness. These developer tools do not change the poker model/provider.

| Repository | Stars | Purpose | Project decision |
| --- | ---: | --- | --- |
| [Prettier](https://github.com/prettier/prettier) | 52,377 | Consistent JavaScript, HTML, JSON and Markdown formatting | Useful for the web inbox; introduce as a dev dependency and scoped check in a separate formatting change. |
| [Ruff](https://github.com/astral-sh/ruff) | 50,247 | Python linting, import sorting, docstring checks and formatting | Use now: installed version 0.17.2 verified the analyst and its tests. |
| [Black](https://github.com/psf/black) | 41,999 | Python formatting | Good alternative, but redundant with Ruff format here. |
| [ESLint](https://github.com/eslint/eslint) | 27,575 | JavaScript correctness and maintainability rules | Useful for server.js, analyze_context.js and browser code; configure Node/browser globals separately. |
| [Biome](https://github.com/biomejs/biome) | 25,987 | JavaScript linting and formatting | Alternative to ESLint plus Prettier; avoid adding overlapping formatters. |
| [pre-commit](https://github.com/pre-commit/pre-commit) | 15,655 | Run checks before commits | Useful when this folder is managed as a Git repository; run Ruff plus the chosen JS checks. |
| [Flake8](https://github.com/PyCQA/flake8) | 3,829 | Python linting with extension plugins | Redundant for this change: Ruff covers the selected checks without an additional plugin stack. |

Counts came directly from `https://api.github.com/repos/{owner}/{repo}` for each
linked repository. Scope includes widely used linters and formatters rather than
installing arbitrary GitHub agent plugins on the basis of star counts.

## Checks used for this change

```powershell
python -m ruff check gpt_poker_analyst.py test_gpt_poker_analyst.py --select E,F,I,D,B --ignore D203,D213
python -m ruff format --check gpt_poker_analyst.py test_gpt_poker_analyst.py
python -m unittest test_gpt_poker_analyst -v
node --test inbox.test.js
```

The selected rules cover PEP 8, undefined/unused names, import ordering,
docstrings, and common bug patterns. D203 and D213 are disabled to use the
compatible one-line-summary convention. No claim is made that unrelated legacy
Python files pass these stricter checks. Linters do not prove production safety.
Ruff is already installed; no redundant packages or arbitrary plugins were added.

## Astra analyst operation

Run `python gpt_poker_analyst.py` or the existing `run_gpt_analysis.bat`.
The analyst uses the native `codex.exe exec -m gpt-6-astra` executable and existing
Codex authentication. Set `CODEX_EXE` to the native executable path if automatic
discovery fails. `--timeout 600` sets the per-request timeout in seconds.

Supported raw inputs under `hands/raw/` are PNG, JPEG, WebP, JSON and UTF-8 text.
Each image is attached to Astra; exported JSON hand arrays are processed in groups
of 20 without discarding hands. Each run scans newly added files. This is a batch
reviewer, not a background watcher. Existing automatic snapshot heuristics are
outside this change and do not feed invented card readings into the analyst.

Astra records readable seated names, including Hero with `is_hero`, and the seven
requested profile fields in `hands/processed/opponents.json`. It preserves
legacy fields and evidence, separates same-name accounts across platforms, and
scopes visibly truncated handles to a table. Names remain display handles, not
verified real-world identities. Unreadable text is reported as a limitation; no
vision model can guarantee recovery of hidden or illegible names.

`typical_stack_bb` is an Astra estimate during session synthesis; per-capture
values are observed snapshots. Unknown values are null. Observed actions and
source references are deduplicated. Astra supplies conditional preflop/postflop
playbooks and Hero coaching, with uncertainty rather than invented statistics.

Successful capture results are cached under `hands/processed/astra_cache/` using
content, source, model, instructions, schema and Hero context. A changed file is
reanalyzed. Profile writes are atomic. A later failed request leaves prior
successful observations and the last successful report intact; the process exits
nonzero and does not fabricate a successful report. The final coaching report is
`hands/processed/GPT_ASTRA_SESSION_REPORT.md`.

Do not run the legacy `opponent_profiler.py` concurrently: it writes the same
store and seeds hardcoded claims. The analyst lock excludes other analyst runs,
not unrelated writers. A forcibly terminated process may leave `.astra.lock`;
remove that file only after confirming its recorded PID is no longer running.
The final session synthesis includes all accumulated profiles/review summaries;
very large archives may eventually exceed model context and require hierarchical
summarization. Capture cache permits retries without repeating completed work.

Validation result: six regression tests passed; the existing Node inbox test passed. Ruff lint and format checks passed. A live GPT-6-Astra structured-output connectivity request succeeded through the native CLI. The full archive was not submitted during implementation.
