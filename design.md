# SpaceGame Design Overview

## Target Platform
- Device: Ovobot Xtron Pro running MakeCode Arcade Python (v1.0.3 firmware)
- Display: 160x120 px, 16-color palette, tile size 16x16 (Arcade defaults)
- Input: D-Pad, A, B, Menu, Back
- Audio: MakeCode Arcade sound effects API
- Storage: Single MakeCode project exported as `.uf2`

## High-Level Experience
An open-galaxy exploration roguelite inspired by No Man’s Sky:
- Fly between star systems plotted on a galaxy map.
- Engage in lightweight space combat encounters.
- Land on seeded planets with unique biomes, resources, and ground enemies.
- Dock at procedural space stations to trade, refuel, and accept missions.
- Persistent player progression: ship upgrades, fuel, credits, inventory.

## Scene & State Model
| Scene | Description | Transition Triggers |
|-------|-------------|---------------------|
| `GALAXY_MAP` | Scrollable star chart UI showing 25 seeded systems. | `A` to enter system; Menu for ship status. |
| `SPACE_ENCOUNTER` | Wrap-around arena with player ship and seeded enemies/asteroids. | Win -> `PLANET_SELECT` if planets available, `STATION` if station present; Lose -> Game Over. |
| `PLANET_SURFACE` | 64x64 tilemap biome with resources/enemies. | `Menu` to launch, `A` to interact, fuel depletion triggers return. |
| `SPACE_STATION` | Static hub with traders/upgrades/quest board UI. | `Menu` returns to Galaxy Map. |
| `GAME_OVER` | Summary screen with stats and seed for rerun. | `A` restarts run. |

Global `game_state` struct holds:
- `galaxy_seed`: base seed for deterministic generation (persisted across sessions by rewriting settings later).
- `systems`: array of 25 system descriptors (see data schema). Stored as parallel arrays to minimize memory.
- `player`: hull, shields, fuel, credits, cargo, equipped modules.
- `active_system`: index currently engaged.
- `active_planet`: descriptor when landed.

## Procedural Generation
### Deterministic RNG
- Seed derived from `galaxy_seed + system_index * 7919`.
- Custom linear congruential generator (LCG) ensuring deterministic values without relying on MakeCode global RNG.
- Provide helper: `rng_next(rng_state, max)` returning next int and updated state.

### System Descriptor Structure
```
system = {
    'seed': base_seed,
    'star_type': enum (red, yellow, blue, binary, pulsar),
    'difficulty': 0..3,
    'has_station': bool,
    'planets': [planet_refs],
}
```
Memory optimization: store arrays `system_seed[i]`, `system_flags[i]`, `planet_offsets[i]` rather than nested dicts. Each planet offset indexes into a global `planet_table` generated on demand and cached (max 12 planets active).

### Planet Generation
- Biome palette chosen from 6 presets (ice, desert, jungle, volcanic, ocean, crystal).
- Terrain built from 2-layer noise:
  1. Base mask via cellular automata (random fill + smoothing iterations).
  2. Feature overlay (lakes, cliffs) using flood fill from random seeds.
- Resource nodes: weighted spawn of 3 resource types; recorded in planet struct for consistent respawn.
- Ground enemies: 2 archetypes per planet (walker, flyer). Stats keyed to difficulty + biome.

### Space Encounter Generator
- Each system spawns 1–3 waves; each wave limited to 4 enemies to stay within sprite budget.
- Enemy archetypes: interceptor (fast), bomber (slow but high damage), drone swarm (multiple low-HP).
- AI implemented via `sprites.on_overlap` events and velocity steering toward player within range.
- Loot table ties to system difficulty and previous missions.

### Station Layout
- Simplified UI using `sprites.create` for NPC icons and `game.show_long_text` for trade dialogues.
- Features: refuel (credits -> fuel), repair, upgrade modules (boost hull/shields/weapons), mission generator (visit X system, defeat pirates, bring back resource).
- Missions tracked in `player['missions']` list with simple objectives.

## Memory & Performance Considerations
- Keep total active sprites < 40. Reuse sprite instances via pools where possible.
- Tilemaps generated once per visit and stored in `planet_cache`; evict oldest when cache exceeds 3 entries.
- Use integer math; avoid Python lists of dicts in hot loops—prefer arrays & indices.
- Compress persisted state using Arcade’s `settings` (key-value) for seed & unlocks.

## File Layout (MakeCode Project)
```
SpaceGame/
  ├── main.py          # core state machine and event handlers
  ├── galaxy.py        # deterministic generator utilities
  ├── assets.py        # palettes, tile data encoded as strings
  ├── gameplay.py      # scene orchestration and input routing
  ├── combat.py        # space encounter logic
  ├── planet.py        # planet surface exploration loop
  ├── station.py       # space station interactions
  ├── pxt.json         # MakeCode Arcade project manifest (for GitHub import)
  ├── settings.json    # MakeCode Arcade project metadata
  └── README.md        # build & flashing instructions
```

MakeCode Arcade packs all `.py` files into a single project; we keep them modular for clarity. When importing into the web editor, upload the folder contents or paste concatenated script into `main.py`.

## Next Implementation Steps
1. Scaffold `settings.json` for Arcade project metadata.
2. Implement RNG utilities and system seeding in `galaxy.py`.
3. Build scene manager and galaxy map UI in `main.py`.
4. Add space encounter loop with enemy spawning.
5. Add planet surface generator and resource collection.
6. Implement station interactions and upgrade economy.
7. Playtest & tune resource/fuel loops; ensure `.uf2` export <= hardware limits.
