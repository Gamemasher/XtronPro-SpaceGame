# SpaceGame (MakeCode Arcade)

Procedurally generated space exploration game for Ovobot Xtron Pro using MakeCode Arcade Python.

## Repo Layout
- `main.py` – entry point, scene/state manager.
- `galaxy.py` – deterministic RNG helpers and system/planet seeding.
- `assets.py` – color palettes, tile definitions, sprite templates.
- `combat.py` – space encounter logic.
- `planet.py` – planet surface exploration loop.
- `station.py` – space station interactions and upgrades.
- `gameplay.py` – scene orchestration helpers and input routing.
- `settings.json` – MakeCode Arcade project metadata (import/export).
- `design.md` – architecture and gameplay notes.

## Getting Started
1. Open [MakeCode Arcade](https://arcade.makecode.com/).
2. Click **Import** and either:
   - **Import URL** → paste this repo’s GitHub link (with `pxt.json` MakeCode fetches every module automatically).
   - **Upload file** → drop a `.zip`/`.mkcd` archive of this folder.
   - Start a blank project and add each `.py` file manually via the Explorer.
3. Use the browser simulator for quick testing (`F5`).
4. When ready, click **Download** → select the Ovobot Xtron Pro board (or generic MakeCode Arcade hardware profile) → save the generated `.uf2`.
5. Put the Xtron Pro in bootloader mode, mount the USB drive, and drag the `.uf2` to flash.

## Development Workflow
- Edit scripts locally and re-import into MakeCode Arcade when needed.
- Use seeded galaxy values (shown on Game Over or Pause screen upgrades planned) to recreate runs.
- Keep sprite counts low; perform manual memory sweeps if you add new enemy types.

## Status
Galaxy navigator and first-pass gameplay loops for space, planet, and station scenes are scaffolded. Next steps include richer procedural variation, quest hooks, and balancing fuel/resource economy.
