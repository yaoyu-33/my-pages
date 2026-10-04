# Yuya's Pages

[Open the site](https://yaoyu-33.github.io/my-pages/) ·
[Read the Gym tutorial](https://yaoyu-33.github.io/my-pages/gym-design-tutorial/)

The Chinese tutorial starts with a minimal weather-tool example and a glossary,
then covers shared contracts, serving and async, a guided `app.py` reading,
configuration and startup, the repository map, core design and evaluation/training
boundaries, and SWE-Pro × Hermes with Harbor comparisons. Chapter 06 now adds an [eight-step command lab](https://yaoyu-33.github.io/my-pages/gym-design-tutorial/#benchmark-lab): commands, configuration, source excerpts, expected results and a downloadable native Collector setup.
The V6 edition rewrites
unclear wording, reorders chapters concrete-first and removes repeated
explanations; all evidence and limitations are kept. V5 added a guided server `app.py` reading lab with 15 steps across
Resources, Model and Agent examples, plus recorded loopback HTTP behavior. It retains a soft cream/mint/lavender theme, a small
reading companion and thirteen diagrams. It teaches native `single_agent_turn` and Hermes
sessions, with a verified native-session smoke and direct typed request examples.
All 15 chapters, interactions, source excerpts and embedded evidence
from the workstation edition are preserved. Only navigation targets are adapted
for this GitHub project site; internal references retain their original addresses.

## Content and provenance

- `index.html`: site homepage.
- `gym-design-tutorial/index.html`: standalone tutorial; no external runtime assets.
- `gym-design-tutorial/provenance.json`: source and published hashes, cited source
  file hashes and the precise navigation substitutions.
- `tutorial-source/`: editable tutorial template, repo chapters, builder, native
  evidence and copyable config/request examples. The older `evidence.json` is
  retained as historical V2 provenance; the current builder uses `native-evidence.json`.
- `tools/export_tutorial.py`: exports built tutorial HTML to this site.

Code explanations are pinned to NeMo Gym
`3ef478df1ee163134d32a3f291f0a9e5981d0e52`. The independently inspected historical
native Hermes smoke used `d5f13f54cf762c7e687dd2d50d2583efe2c9b717`: reward 1,
18/18 required tests, and an incomplete agent / final-summary HTTP 422. The smoke
used a flat-row outer adapter before the native lifecycle; the pure typed example
has offline configuration/schema validation, not a new model run. Publishing this site
does not rerun or validate a new benchmark configuration. V5 separately launched
the real pinned weather service through `run_webserver()` on loopback and checked
nine HTTP behaviors, then terminated it. This uses explicit child configuration;
it does not run the full Gym CLI/Head stack or a model/agent rollout. The page preserves the
difference between source walkthroughs, simulations and recorded runtime evidence.

## Update

1. Edit `tutorial-source/index.template.html` or `tutorial-source/repo-chapters.html`.
   Diagrams live in `diagrams.html`; `illustrated.css` and `illustrated.js` provide
   the visual theme, responsive connectors and synchronized flow highlighting.
   Keep these three files beside the builder; it embeds them in the standalone HTML.
   The app.py lab additionally uses `app-reading.html`, `app-reading.css`,
   `app-reading.js`, `app-walkthrough.json`, `weather-lab.py` and
   `weather-http-evidence.json`. Source snippets are extracted from the pinned
   checkout with their original line numbers; the new HTTP evidence is checked
   against the weather app hash. `verify-weather-lab.py` reproduces the HTTP checks.
   The command lesson needs `command_lesson.py`, `benchmark-lab.html`,
   `benchmark-lab.json`, `lab.yaml`, `model-provider.yaml`, and
   `prepare-tutorial-tasks.py`. Its ZIP is embedded and generated deterministically;
   `validate-command-lab.py --source-root /path/to/pinned/Gym` checks configuration,
   task conversion, actual Collector planning/result unwrapping, synthetic reward
   profiling and CLI parsing offline. These checks do not certify a new model run.
2. Keep `native-evidence.json`, `native-hermes.yaml` and `prepare-native-request.py`
   beside the builder. Build against an exact checkout of the pinned Gym revision:

   ```sh
   python3 tutorial-source/build.py --source-root /path/to/pinned/Gym
   python3 tools/export_tutorial.py tutorial-source
   ```

3. Inspect the generated page, exercise its interactions and check desktop/mobile
   layouts. Keep source and historical-evidence scopes explicit.
4. Commit and push to `main`. GitHub Pages publishes the repository root;
   `.nojekyll` keeps the standalone files unchanged.
5. Verify the public page and its hash against `provenance.json` after deployment.

Changing a source SHA requires re-reading the cited code and updating affected
line links and explanations. Do not update only the SHA or reinterpret the old
smoke as evidence for a new code revision.

The workstation original remains at
`http://10.111.115.167:8765/gym-design-tutorial/`. This repository publishes only
the tutorial and its maintenance sources, not the other workstation pages.
