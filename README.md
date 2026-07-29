[![Codacy Badge](https://api.codacy.com/project/badge/Grade/c4fb741e9a4f430dae15fd2b8e812dd5)](https://www.codacy.com/gh/codacy/codacy-prospector?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=codacy/codacy-prospector&amp;utm_campaign=Badge_Grade)
[![Build Status](https://circleci.com/gh/codacy/codacy-pylint.svg?style=shield&circle-token=:circle-token)](https://circleci.com/gh/codacy/codacy-prospector)

# Codacy Prospector

This is the docker engine we use at Codacy to have [Prospector](https://github.com/PyCQA/prospector) support.
You can also create a docker to integrate the tool and language of your choice!
See the [codacy-engine-scala-seed](https://github.com/codacy/codacy-engine-scala-seed) repository for more information.

## Usage

You can create the docker by doing:

  ```bash
  docker build -t codacy-prospector:latest .
  ```

The docker is ran with the following command:

  ```bash
  docker run -it -v $srcDir:/src codacy-prospector:latest
  ```

## Test

We use the [codacy-plugins-test](https://github.com/codacy/codacy-plugins-test) to test our external tools integration.
You can follow the instructions there to make sure your tool is working as expected.

## Agent Playbook: Updating This Repository End-to-End

This section is written for an AI coding agent (or a human) tasked with updating this repo — most commonly bumping the wrapped [Prospector](https://github.com/PyCQA/prospector) version or one of its sub-linters, but also base image / CI orb bumps. Follow it top to bottom.

### 1. What this repository is

This is a **Codacy engine**: a small Python wrapper (`src/codacy_prospector.py`) that invokes [Prospector](https://github.com/PyCQA/prospector) — a Python meta-linter that aggregates Pylint, Pyflakes, McCabe, pycodestyle, pydocstyle, Bandit, Dodgy, Vulture, Pyroma, mypy, pyright and its own `profile-validator` — and packages it as a Docker image Codacy's platform runs against customer source code. `src/codacy_prospector_test.py` is the engine's own unit test suite (not `codacy-plugins-test`).

Unlike engines such as `codacy-checkstyle`, there is **no `DocGenerator`-style script** here and **no per-rule pattern list**. `docs/patterns.json` in this repo models the **sub-tools** Prospector bundles (`pylint`, `pyflakes`, `mccabe`, `dodgy`, `pycodestyle`, `pydocstyle`, `profile-validator`, `vulture`, `pyroma`, `mypy`, `bandit`, `pyright`) as twelve coarse-grained "patterns" — one per tool, each individually enable/disable-able and categorized — rather than one pattern per individual lint rule. `docs/description/description.json` + `docs/description/*.md` give each of those twelve tools a title/description for the Codacy UI. Both are **hand-maintained** (edit directly when a sub-tool is added/removed/renamed) — there is no generator to run. `docs/multiple-tests/*` are fixtures (source + expected `results.xml`/`patterns.xml`) used by `codacy-plugins-test`'s "multiple" test mode.

### 2. Files that encode versions — check all of these on every update

| File | What it controls | What to check |
|---|---|---|
| `requirements.txt` | Pinned versions of `prospector[with_everything]` and every sub-linter it needs installed alongside it (`pylint`, `mypy`, plus `Django`/`Flask`/`jsonpickle` used as test fixtures/deps) | Bump the target package(s). `pylint` and `mypy` versions here are independent of the versions Prospector bundles internally — check they stay compatible with the new Prospector release (see its changelog/`setup.py`). |
| `Dockerfile` → `FROM python:<version>-alpine<version>` | Python runtime + base OS the image runs on | Bump only if required by the new package versions (e.g. a Prospector/pylint release drops support for an old Python) or asked explicitly. Also installs `nodejs npm gcompat` via apk — needed by some Prospector sub-tools; don't remove without checking. |
| `docs/patterns.json` → `"version"` field | Advertised Prospector version in the pattern manifest | Historically this lags behind `requirements.txt` and is only bumped when the set of exposed tools/patterns changes, not on every dependency bump — check recent history before assuming it must move in lockstep. |
| `docs/patterns.json` → `patterns[]` list | Which sub-tools are exposed to Codacy and enabled by default | Add/remove an entry here if the Prospector release adds/drops/renames a bundled tool (see commit `46ec8a4` removing a stale pydocstyle rule reference, and `cce1cca` for a results-parser fix accompanying a `patterns.json` tweak). |
| `docs/description/description.json` + `docs/description/<tool>.md` | Human-readable title/description per sub-tool in the Codacy UI | Keep in sync with `patterns.json`'s `patternId`s whenever a tool is added/removed. |
| `.circleci/config.yml` → `codacy/base` orb | Shared CircleCI steps (checkout, versioning, docker build/publish, tagging) | Check the latest published version if asked to update it; not tied to Prospector bumps. |
| `.circleci/config.yml` → `codacy/plugins-test` orb | Runs `codacy-plugins-test` in CI after the image is built | Same as above. |

### 3. Step-by-step update procedure

1. **Bump the version(s)** in `requirements.txt` (Prospector and/or the specific sub-linter(s) named in the task).
2. **Update `docs/patterns.json` and `docs/description/*` by hand** only if the release adds, removes, or renames a bundled sub-tool — otherwise leave them untouched.
3. **Rebuild the Docker image**: `docker build -t codacy-prospector:latest .`
4. **Run the engine's own unit tests inside the image** (this is what CI's `publish_docker_local` job does): `docker run codacy-prospector:latest codacy_prospector_test.py`
5. **Run `codacy-plugins-test` locally** before pushing — clone https://github.com/codacy/codacy-plugins-test and run its "multiple" DockerTest command against your local image tag (this repo's CI runs `run_multiple_tests: true`, with `run_json_tests`/`run_pattern_tests` disabled — mirror that locally).
6. **Iterate on failures** using the fixtures under `docs/multiple-tests/*` — update a fixture's expected `results.xml` only after confirming the new output is actually correct, not just different.
7. **Commit** the version bump(s) together with any `docs/patterns.json`/`docs/description/*` edits in one change.
8. **Push and open a PR.** CI (`.circleci/config.yml`) runs `checkout_and_version` -> `publish_docker_local` (build + run the unit tests in-image) -> `plugins_test` (multiple-tests) -> `publish_docker` (master only) -> `tag_version`.
9. **Poll the PR's real CI checks until they all pass — local validation is NOT the finish line.** After every push, run `gh pr checks <pr-url>` and keep re-polling (short sleep while any check is `pending`) until all checks finish. If a check fails, fetch its actual log (CircleCI API/UI for the failing job — don't guess), find the true root cause, fix it, push again (never `--no-verify`, never force-push), and re-poll. Repeat until every check is green. The CI environment's toolchain can differ from your local one, so a clean local run does not guarantee CI passes. Only stop iterating when every check passes, or you hit a genuine product/infra decision that needs a human — in which case explain it in the PR rather than guessing.

### 4. Common failure modes and fixes

| Symptom | Likely cause | Fix |
|---|---|---|
| `docker run ... codacy_prospector_test.py` fails in CI | New Prospector/sub-linter version changed CLI output format that `src/codacy_prospector.py`'s results parser depends on | Adjust the parser (see commit `cce1cca`, "Fix results parser") and update the unit tests |
| `multiple` DockerTest fails on a specific fixture folder under `docs/multiple-tests/` | A sub-tool changed its rule set/message text/line numbers between versions | Regenerate the expected `results.xml` for that fixture after verifying the new output is correct upstream behavior, not a regression |
| `pip3 install -r requirements.txt` fails during `docker build` | Version conflict between `prospector[with_everything]`'s pinned sub-dependencies and this file's explicit pins (`pylint`, `mypy`, `jsonpickle`, `Django`, `Flask`) | Check Prospector's own `setup.py`/changelog for the sub-dependency versions it expects and align the explicit pins here |

### 5. Definition of done

- Version bump(s) reflected in `requirements.txt` (and `Dockerfile` base image, if required).
- `docs/patterns.json` / `docs/description/*` updated by hand if the tool set changed, otherwise left alone.
- Docker image builds successfully.
- In-image unit tests pass: `docker run codacy-prospector:latest codacy_prospector_test.py`.
- `codacy-plugins-test` "multiple" tests pass locally against the freshly built image.
- **After pushing and opening/updating the PR, every CI check on it is green.** Poll `gh pr checks <pr-url>` and iterate on any failure (fetch the real CI log, fix, push, re-poll) until all pass — a passing local build is not sufficient, because the CI toolchain can differ from your local one (see step 9).

## What is Codacy?

[Codacy](https://www.codacy.com/) is an Automated Code Review Tool that monitors your technical debt, helps you improve your code quality, teaches best practices to your developers, and helps you save time in Code Reviews.

### Among Codacy’s features

- Identify new Static Analysis issues
- Commit and Pull Request Analysis with GitHub, BitBucket/Stash, GitLab (and also direct git repositories)
- Auto-comments on Commits and Pull Requests
- Integrations with Slack, HipChat, Jira, YouTrack
- Track issues in Code Style, Security, Error Proneness, Performance, Unused Code and other categories

Codacy also helps keep track of Code Coverage, Code Duplication, and Code Complexity.

Codacy supports PHP, Python, Ruby, Java, JavaScript, and Scala, among others.

### Free for Open Source

Codacy is free for Open Source projects.
