# Yuya's Pages

[Open the site](https://yaoyu-33.github.io/my-pages/) ·
[Read the Gym tutorial](https://yaoyu-33.github.io/my-pages/gym-design-tutorial/)

The Chinese tutorial covers the whole NeMo Gym repository, shared contracts,
serving and async, configuration and startup, a minimal weather-tool example,
core design, evaluation/training boundaries, and SWE-Pro × Hermes with Harbor
comparisons. All 14 chapters, interactions, source excerpts and embedded evidence
from the workstation edition are preserved. Only navigation targets are adapted
for this GitHub project site; internal references retain their original addresses.

## Content and provenance

- `index.html`: site homepage.
- `gym-design-tutorial/index.html`: standalone tutorial; no external runtime assets.
- `gym-design-tutorial/provenance.json`: source and published hashes, cited source
  file hashes and the precise navigation substitutions.
- `tutorial-source/`: editable tutorial template, repo chapters, builder and evidence.
- `tools/export_tutorial.py`: exports built tutorial HTML to this site.

Code explanations are pinned to NeMo Gym
`3ef478df1ee163134d32a3f291f0a9e5981d0e52`. The independently inspected historical
Hermes smoke used `7a19900a114f8c349c9fac031b016575e39cfa36`. Publishing this site
does not rerun or validate a new benchmark configuration. The page preserves the
difference between source walkthroughs, simulations and recorded runtime evidence.

## Update

1. Edit `tutorial-source/index.template.html` or `tutorial-source/repo-chapters.html`.
2. Build against an exact checkout of the pinned Gym revision:

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
