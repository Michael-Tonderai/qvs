# Deployment evidence - REQ-N-003

Recorded 2026-09-12, session 013. Transcribed by hand from the Render deploy log and
the GitHub Actions run pages rather than pasted, because `tools\Check-Ascii.ps1` runs
over this directory and both sources emit non-ASCII glyphs that arrive corrupted.

---

## The deployment

| | |
|---|---|
| Public URL | https://qvs-f3dk.onrender.com |
| Platform | Render, free instance, Docker runtime |
| Region | Frankfurt |
| Deployed commit | 1e02381, `Merge pull request #21 from Michael-Tonderai/develop` |
| Blueprint | `render.yaml`, committed at the repository root |
| Blueprint sync | 1e02381, matching the commit above |
| Deploy branch | `main`, protected under D-031 |

The blueprint reports the commit it synced from, so the running system is traceable to
a single sha that reached `main` through the required status check. No configuration
was entered into the platform's console except `QVS_ALLOWED_HOSTS`, which
`render.yaml` marks `sync: false` and which is not load-bearing - `config/settings.py`
reads the platform's own hostname at runtime.

## What the platform reported

Port binding, which is the fix that could not be established by reading:

    ==> Detected service running on port 10000

The exec-form `CMD` this project carried until session 013 could not expand a shell
variable, so it would have bound 8000. The container would have started cleanly,
listened on the wrong port, failed the health check, and reported nothing that named
the cause. See D-036.

Health checking, once every five seconds, continuously:

    "GET /health/ HTTP/1.1" 200 34 "-" "Render/1.0"

34 bytes is the exact length of the health endpoint's response body. A 200 here also
establishes that `ALLOWED_HOSTS` accepted the Host header the platform sends, which
was the failure considered most likely before the first deploy.

## Browser confirmation

Confirmed by Sir Ton on 2026-09-12, in a browser, over HTTPS:

- The root path redirects to `/verify/`.
- The verification page renders to an anonymous visitor with no redirect to login,
  which is REQ-F-005's public half holding in a deployed environment rather than under
  the test client.

REQ-N-003 moves to VERIFIED on this evidence. A green pipeline was explicitly not
treated as sufficient: the register's VERIFIED means browser-confirmed.

## Pipeline evidence for the image

GitHub Actions, workflow `CI`, job `Container image builds and serves`, added under
D-028 in `.github/workflows/ci.yml`.

| Run | Trigger | Result |
|---|---|---|
| 34717387428 | PR #20 into `develop` | pass |
| 34718748559 | PR #21 into `main` | pass |
| 34719180059 | push to `develop` | pass |

The job builds the image, starts the container with `PORT` set to a non-default value,
and requests `/health/` from outside the container. Before the first of these runs the
Dockerfile had never been executed on any machine, by anyone - D-026 removed Docker
from the development machine, and D-028 made this job the merge gate in place of a
local run. It passed first time.

## What this evidence does NOT establish

Stated because a reader would otherwise reasonably infer it.

**The CSRF and proxy configuration is unverified.** Everything exercised above is a
GET. `SECURE_PROXY_SSL_HEADER` only matters on a POST, where Django compares an
`https` Origin header against a request it believes is insecure. No POST has yet been
made against the deployed site, because the database starts empty and the free
instance offers no shell with which to create a user. The first login submission is
what will prove or disprove that configuration.

**The deployment is a demonstration, not a system of record.** The free instance has
no persistent disk, so records registered through the live site do not survive a
restart or a redeployment, and the instance sleeps after fifteen minutes idle, taking
thirty to sixty seconds to wake on the next request. Both are properties of the tier
rather than of the system, both are named in D-036, and both belong in the technical
report's critical evaluation.
