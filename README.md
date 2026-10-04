# Yuya's Pages

[Open the site](https://yaoyu-33.github.io/my-pages/) ·
[Read the Gym tutorial](https://yaoyu-33.github.io/my-pages/gym-design-tutorial/)

The Chinese tutorial uses a weather-tool example to explain Gym's contracts,
serving and async, server `app.py`, startup, repository structure, core design,
and SWE-Pro × Hermes with Harbor comparisons. It has 16 chapters, 15 diagrams,
a guided 15-step code reader and an eight-step benchmark command lab.
The learning layer adds three study routes, a linked weather tool-call example,
seven feedback questions and a standard-library async lab. Configuration precedence
and task/rollout/attempt examples are checked against the pinned implementation.
Static answer panels support reading without JavaScript and printing.

[Chapter 16](https://yaoyu-33.github.io/my-pages/gym-design-tutorial/#run-log-study)
adds ten anonymized lessons from historical run logs: protocol compatibility,
container runtimes, result denominators, verifier coverage, retry accounting,
service lifetime, token usage, fair comparisons, reference exposure and diagnosis.
It includes a denominator calculator and a downloadable run-log template.
These are evidence-scoped lessons, not a new benchmark or a harness ranking.

The 2026-10-04 revision received three successive reviews by three specialists:
teaching structure, code/documentation accuracy, and serving/async explanations.
It borrows instructional approaches from official Hugging Face courses, with
attribution in the tutorial; its examples, diagrams and questions are original.
This is editorial/source review and local validation, not a reader-learning study.

## Content and provenance

- `gym-design-tutorial/index.html`: standalone tutorial, with no external runtime assets.
- `gym-design-tutorial/provenance.json`: public input/output hashes, cited source
  file hashes and export substitutions.
- `tutorial-source/`: editable templates, builders, examples and privacy-reviewed
  evidence. The current builder uses `native-evidence.json`; `evidence.json`
  remains historical V2 evidence.
- `tutorial-source/public-redactions.json`: current public-input redaction report.
- `tools/prepare_public_sources.py`: copies an explicit input allowlist and omits
  private locations. New prose always needs manual review.
- `tools/export_tutorial.py`: exports a built public tutorial, changing only
  three homepage links for this project site.
- `tools/check_public_content.py`: checks current content and embedded ZIP members
  for known private-location and signed-link patterns.

Code explanations are pinned to NeMo Gym
`3ef478df1ee163134d32a3f291f0a9e5981d0e52`. The historical native Hermes smoke
used `d5f13f54cf762c7e687dd2d50d2583efe2c9b717`: reward 1, 18/18 required tests,
and an incomplete agent / final-summary HTTP 422. It used a flat-row outer
adapter before the native lifecycle; the typed example has offline validation,
not a new model run. The weather lab separately exercised the pinned service on
loopback, checking nine HTTP behaviors before terminating it. That did not run
Gym's full CLI/Head stack or a model/agent rollout.

Chapter 16 combines records from different historical revisions. Source links
explain related mechanisms; they do not identify each historical run's revision.
The complete case-to-record mapping remains in the restricted knowledge board.

A separate current-code note was checked at
`128eab40a08c5bab71171feb6a55ba294574bd29`. The native implementation and recipe
files cited in that comparison are unchanged; optional W&B/MLflow SDK behavior
is version-scoped. Examples and historical evidence keep their original pins.
The local async lab uses Python standard-library timers, no services or models;
`async-mini-evidence.json` records the script hash and observed in-flight counts.

## Privacy scope

The current public page, editable inputs and downloads omit private cluster and
host addresses, machine artifact paths and internal record links. Original
measurements, public code pins and evidence limitations remain. Private originals
and public redacted evidence have separate hashes; they are not byte-identical.
No raw run logs are added here. Public inference examples remain illustrative.

This update sanitizes the current tree. Previously published Git commits are
**not rewritten**, so this is not a claim that repository history is sanitized.
Pattern checks supplement manual review; they cannot certify arbitrary logs.

## Update

1. Edit the relevant public inputs, or prepare them from the maintained private
   tutorial directory:

   ```sh
   python3 tools/prepare_public_sources.py /path/to/private-tutorial-inputs
   ```

   Review the output diff and `public-redactions.json` before building. Never
   copy raw logs, restricted source maps, credentials or private publisher files.
   Preserve source attribution and the distinction between historical observations,
   hypotheses and reproduced behavior.

2. Build against the exact pinned Gym checkout and export:

   ```sh
   python3 tutorial-source/build.py --source-root /path/to/pinned/Gym
   python3 tools/export_tutorial.py tutorial-source
   python3 tools/check_public_content.py .
   ```

   `learning_guide.py` embeds `learning-guide.html/json/css/js`, the downloadable
   `async-mini-lab.py` and its separate evidence record. Keep them together;
   the builder verifies the lab's source hash. `study_lesson.py` renders `run-log-lessons.json`, `run-log-lessons.html` and
   `run-log-template.txt`. The app reader uses `app-reading.*`,
   `app-walkthrough.json` and the weather evidence. The benchmark lesson uses
   `command_lesson.py`, `benchmark-lab.*`, the YAML examples and task converter;
   its embedded ZIP is deterministic. Keep these inputs beside `build.py`.

3. Exercise chapter navigation, source links, copy/download controls, the
   denominator calculator, seven answer choices/static explanations, async-lab download
   and desktop/mobile layouts. Review both HTML and
   downloadable evidence. Offline command validation is available through
   `validate-command-lab.py --source-root /path/to/pinned/Gym`; it does not
   certify a new model run. `verify-weather-lab.py` reproduces the HTTP lab.
4. Commit and push to `main`. Pages publishes the repository root; `.nojekyll`
   keeps standalone files unchanged. Verify the anonymous page and its SHA256
   against `provenance.json` after deployment.

Changing a source pin requires re-reading cited code and updating affected links
and explanations. Do not reinterpret an old smoke as evidence for a new revision.
