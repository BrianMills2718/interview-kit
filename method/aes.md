# AES: a machine-checked plan (optional)

`aes` is a small command-line tool that keeps the plan in a file it can check: each outcome links
to requirements, each requirement to a success criterion with a disproof, each criterion to the
test that proves it. `aes status` then says, per criterion, whether a current test run supports
it. It makes no AI calls, so it is allowed wherever a terminal is; it is not a second assistant.

Use it when the test is long enough (3 hours or more) and you want the plan-to-test links to be
shown rather than claimed. Otherwise `PLAN.md` plus `check.sh` is enough; skip it in the 2-hour
practice unless you are rehearsing `aes` itself.

**Layout limit:** `aes` governs only files under subfolders (`src/` and `tests/` by default). Code
at the project root (`solution.py`) cannot be governed: `.` is not accepted as a root
(AES issue 540). Decide the layout before the first file, or skip `aes`.

## Set up (about 1 minute)

```bash
bash kit/method/install_aes.sh            # installs `aes` with uv at the tested revision; replaces any installed `aes`
git init -q && git add -A && git commit -qm "Start"   # `aes plan validate` needs at least one commit
aes init --project-id myproj --actor "<who uses it>" --outcome "<what they get, in one sentence>"
git add .aes && git commit -qm "Initialize AES"
```

Code goes under `src/` and tests under `tests/` (the default governed folders). To keep an
existing `aes` instead, run it without installing: `uvx --from "$(bash kit/method/install_aes.sh --spec)" aes ...`.

## Each requirement

1. Copy [aes-plan.example.yaml](aes-plan.example.yaml), change the ids and text: one behavior
   (`NI-`), its success criterion with a `disproof` (`SC-`), the test that proves it (`VS-`), and
   the files you will write.
2. `aes plan validate plan.yaml` then `aes plan accept plan.yaml`; commit `.aes`.
3. Write the test, see it fail, write the code, see it pass.
4. `aes evidence record VS-<id> --depends-on <source file>`; commit `.aes/observations`.
5. `aes status`: every criterion should read as supported. One that is not is the next thing
   to do, or a limitation to state in the README.

`trace_review` in the plan says whether the work runs a model or agent. If it does, set
`runs_traced_work: true` and keep the run's trace (the logged steps) next to the test.

## What it shows a reviewer

The `.aes/` folder, committed step by step, is the plan and its evidence over time: what was
promised, what proves it, and what is still unproven.
