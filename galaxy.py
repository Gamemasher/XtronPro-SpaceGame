# galaxy.py
# Deterministic galaxy and planet seeding utilities for MakeCode Arcade.

GALAXY_SYSTEM_COUNT = 25
SYSTEMS_PER_ROW = 5
STAR_TYPES = ['red', 'yellow', 'blue', 'binary', 'pulsar']
PLANET_BIOMES = ['ice', 'desert', 'jungle', 'volcanic', 'ocean', 'crystal']


def _lcg_next(state):
    # Linear congruential generator parameters tuned for 32-bit.
    state[0] = (1664525 * state[0] + 1013904223) & 0xffffffff
    return state[0]


def _rng_next(state, max_value):
    if max_value <= 0:
        return 0
    value = _lcg_next(state)
    return value % max_value


def _base_seed(galaxy_seed, system_index):
    return (galaxy_seed + system_index * 7919) & 0xffffffff


def build_galaxy(galaxy_seed):
    systems = []
    index = 0
    while index < GALAXY_SYSTEM_COUNT:
        rng_state = [_base_seed(galaxy_seed, index)]
        star_type = STAR_TYPES[_rng_next(rng_state, len(STAR_TYPES))]
        difficulty = 1 + _rng_next(rng_state, 4)
        has_station = _rng_next(rng_state, 100) < 20
        planet_count = 1 + _rng_next(rng_state, 3)
        planets = []
        planet_idx = 0
        while planet_idx < planet_count:
            planets.append(_create_planet(index, planet_idx, rng_state))
            planet_idx += 1
        systems.append({
            'index': index,
            'seed': rng_state[0],
            'star_type': star_type,
            'difficulty': difficulty,
            'has_station': has_station,
            'planets': planets
        })
        index += 1
    return systems


def system_coordinates(system_index):
    col = system_index % SYSTEMS_PER_ROW
    row = system_index // SYSTEMS_PER_ROW
    margin_x = 20
    margin_y = 12
    spacing_x = (160 - 2 * margin_x) // (SYSTEMS_PER_ROW - 1)
    spacing_y = (120 - 2 * margin_y) // ((GALAXY_SYSTEM_COUNT // SYSTEMS_PER_ROW) - 1)
    x = margin_x + spacing_x * col
    y = margin_y + spacing_y * row
    return x, y


def _create_planet(system_index, planet_index, rng_state):
    biome = PLANET_BIOMES[_rng_next(rng_state, len(PLANET_BIOMES))]
    size = 16 + _rng_next(rng_state, 24)
    hostility = _rng_next(rng_state, 100)
    resource_richness = 1 + _rng_next(rng_state, 3)
    return {
        'system_index': system_index,
        'planet_index': planet_index,
        'biome': biome,
        'size': size,
        'hostility': hostility,
        'richness': resource_richness
    }


def regenerate_system(galaxy_seed, system_index):
    rng_state = [_base_seed(galaxy_seed, system_index)]
    return _create_planet(system_index, 0, rng_state)
