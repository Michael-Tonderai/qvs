# Pipeline evidence - REQ-N-001, REQ-N-004

Recorded 2026-09-14, session 018. Transcribed by hand from `gh run view --json`
output held in `dev_reports\`, not pasted from the Actions web interface: the run
pages and `gh`'s own table output both emit box-drawing characters and status glyphs,
which `tools\Check-Ascii.ps1` rejects under `docs\` (D-018). Requesting JSON rather
than the default table is what makes a faithful transcription possible.

Two runs are recorded. One shows continuous integration on a change; the other is the
quality gate that let that change reach production. The assignment names CI pipelines
and CI/CD quality gates as separate things, and these are this project's instances of
each.

---

## The workflow

`.github/workflows/ci.yml` defines two jobs:

| Job | Purpose |
|---|---|
| `Lint, security and tests` | Standards, static analysis, security scan, test suite, coverage |
| `Container image builds and serves` | Builds the image and proves the container answers on a non-default port (D-028) |

The first is the required status check on `main` under D-031, with `strict` set, so a
stale head must rebuild before it can merge.

---

## Run A - integration on a feature pull request

| | |
|---|---|
| Run | 34790488993 |
| Title | Tier B: authenticated record search and detail (REQ-F-009, REQ-F-010) |
| Trigger | `pull_request` |
| Head branch | `feature/REQ-F-009-search-and-retrieve` |
| Head sha | f8e7743 |
| Started | 2026-09-13 23:42:50 UTC |
| Finished | 2026-09-13 23:44:06 UTC |
| Conclusion | success |
| URL | https://github.com/Michael-Tonderai/qvs/actions/runs/34790488993 |

Job `Lint, security and tests` - 41 seconds, success:

| # | Step | Duration | Result |
|---|---|---|---|
| 1 | Set up job | 1s | success |
| 2 | Check out the repository | 0s | success |
| 3 | Set up Python 3.12 | 2s | success |
| 4 | Install dependencies | 6s | success |
| 5 | ASCII purity check | 7s | success |
| 6 | Lint | 0s | success |
| 7 | Format check | 0s | success |
| 8 | Security scan | 0s | success |
| 9 | Tests with coverage | 21s | success |
| 10 | Upload coverage report | 0s | success |

Job `Container image builds and serves` - 30 seconds, success:

| # | Step | Duration | Result |
|---|---|---|---|
| 1 | Set up job | 1s | success |
| 2 | Check out the repository | 1s | success |
| 3 | Build the image | 21s | success |
| 4 | Start the container | 0s | success |
| 5 | Wait for the health endpoint | 4s | success |
| 6 | Container logs | 0s | success |

This run is the evidence behind PR #30, which merged Tier B to `develop`.

---

## Run B - the quality gate on the release to production

| | |
|---|---|
| Run | 34791241238 |
| Title | feat: release search and record retrieval to production |
| Trigger | `pull_request` (PR #31, `develop` into `main`) |
| Head sha | d3b192b |
| Started | 2026-09-13 23:59:15 UTC |
| Finished | 2026-09-14 00:00:15 UTC |
| Conclusion | success |
| URL | https://github.com/Michael-Tonderai/qvs/actions/runs/34791241238 |

Job `Lint, security and tests` - 37 seconds, success:

| # | Step | Duration | Result |
|---|---|---|---|
| 1 | Set up job | 1s | success |
| 2 | Check out the repository | 0s | success |
| 3 | Set up Python 3.12 | 1s | success |
| 4 | Install dependencies | 7s | success |
| 5 | ASCII purity check | 6s | success |
| 6 | Lint | 0s | success |
| 7 | Format check | 0s | success |
| 8 | Security scan | 0s | success |
| 9 | Tests with coverage | 19s | success |
| 10 | Upload coverage report | 1s | success |

Job `Container image builds and serves` - 19 seconds, success:

| # | Step | Duration | Result |
|---|---|---|---|
| 1 | Set up job | 0s | success |
| 2 | Check out the repository | 1s | success |
| 3 | Build the image | 11s | success |
| 4 | Start the container | 0s | success |
| 5 | Wait for the health endpoint | 4s | success |
| 6 | Container logs | 0s | success |

A third run, 34791028432, ran against the `develop` push carrying the same tree and
also passed both jobs - 44s and 23s. Read from `gh pr checks 31` rather than from a
run view, which is why it carries less detail here than the two above.

This is the run D-031 required. PR #31 merged on it, producing merge commit 6ad6f41 on
`main`, and Render's `autoDeploy` rebuilt from that commit. The deployed instance
re-seeded at 00:04:27 UTC, 49 seconds after the merge, which is how the running system
is dated to this release without relying on the platform dashboard.

---

## How the steps map to the assignment's assessed criteria

| Assignment criterion | Step that evidences it |
|---|---|
| Automated build process | Build the image |
| Automated testing | Tests with coverage |
| Test coverage reporting | Upload coverage report, plus the `fail_under` threshold in `pyproject.toml` |
| Static code analysis | Lint (ruff), Security scan (bandit) |
| Coding standards compliance | Format check (ruff format), ASCII purity check (D-018) |
| CI/CD quality gate | The required status check on `main` (D-031), exercised by Run B |

---

## What this evidence does NOT establish

Stated because a reader would otherwise reasonably infer it.

**No failing run is transcribed here.** A gate is best evidenced by something it
stopped, and both runs above are successes. Nothing in this project's history has yet
been blocked by a red check, so the strength of the gate rests on its configuration
(D-031) rather than on a caught defect.

**The coverage percentage is not in this record.** The run reports that the coverage
step passed, not what it measured. The 96.95 per cent figure quoted elsewhere comes
from the local gate on 7426a5e and from the `fail_under` threshold the CI step
enforces, not from these run pages.

**The image job proves the container starts on a runner, not that the deployment is
healthy.** It builds the image, starts it with `PORT` set to a non-default value and
requests `/health/` from outside the container. Evidence about the running public
instance is in `deployment.md`.

**Step durations are runner timings, not a benchmark.** The same image build took 21
seconds in Run A and 11 seconds in Run B, on the same Dockerfile, because of layer
caching and runner variation.
