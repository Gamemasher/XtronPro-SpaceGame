# gameplay.py
# Scene coordinator tying main.py to combat, planet, and station modules.

import combat
import planet
import station

SPACE_SCENE = 1
PLANET_SCENE = 2
STATION_SCENE = 3


def setup_space_encounter(state):
    combat.start_space_encounter(state)


def setup_planet_surface(state):
    planet.start_planet_scene(state)


def setup_space_station(state):
    station.start_station_scene(state)


def teardown_current_scene(state):
    if state['scene'] == SPACE_SCENE:
        combat.cleanup_space_scene(state)
    elif state['scene'] == PLANET_SCENE:
        planet.cleanup_planet_scene(state)
    elif state['scene'] == STATION_SCENE:
        station.cleanup_station_scene(state)
    sprites.destroy_all_sprites_of_kind(SpriteKind.projectile)


def handle_button_a(state):
    if state['scene'] == SPACE_SCENE:
        return combat.space_press_a(state)
    if state['scene'] == PLANET_SCENE:
        return planet.handle_button_a(state)
    if state['scene'] == STATION_SCENE:
        return station.handle_button_a(state)
    return None


def handle_button_b(state):
    if state['scene'] == SPACE_SCENE:
        return combat.space_press_b(state)
    if state['scene'] == PLANET_SCENE:
        return planet.handle_button_b(state)
    if state['scene'] == STATION_SCENE:
        return station.handle_button_b(state)
    return None


def handle_direction(state, dx, dy):
    if state['scene'] == STATION_SCENE:
        return station.handle_direction(state, dx, dy)
    if state['scene'] == PLANET_SCENE:
        return planet.handle_direction(state, dx, dy)
    return None


def handle_menu(state):
    if state['scene'] == SPACE_SCENE or state['scene'] == PLANET_SCENE or state['scene'] == STATION_SCENE:
        return 'map'
    return None