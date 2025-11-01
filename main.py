# main.py
# Entry point for the SpaceGame MakeCode Arcade project.

import galaxy
import assets
import gameplay

galaxy_scene = 0
space_scene = 1
planet_scene = 2
station_scene = 3

galaxy_star_kind = SpriteKind.create()
galaxy_cursor_kind = SpriteKind.create()

game_state = {
    'scene': galaxy_scene,
    'galaxy_seed': 0,
    'systems': [],
    'cursor_index': 0,
    'star_sprites': [],
    'cursor_sprite': None,
    'hud_text': None,
    'station_text': None,
    'player': {
        'hull': 5,
        'shield': 3,
        'credits': 0,
        'weapon': 0,
        'fuel': 100,
        'resources': 0
    },
    'space_player': None,
    'space_enemies': [],
    'space_status': 'idle',
    'planet_player': None
}


def _generate_seed():
    base = control.millis()
    if base == 0:
        base = 1234567
    return base & 0x7fffffff


def start_new_galaxy(seed):
    game_state['galaxy_seed'] = seed
    game_state['systems'] = galaxy.build_galaxy(seed)
    game_state['cursor_index'] = 0
    game_state['player'] = {
        'hull': 5,
        'shield': 3,
        'credits': 0,
        'weapon': 0,
        'fuel': 100,
        'resources': 0
    }
    _enter_scene(galaxy_scene)


def _enter_scene(scene_id):
    if game_state['scene'] == galaxy_scene:
        _teardown_galaxy_scene()
    elif game_state['scene'] == space_scene:
        gameplay.teardown_current_scene(game_state)
    elif game_state['scene'] == planet_scene:
        gameplay.teardown_current_scene(game_state)
    elif game_state['scene'] == station_scene:
        gameplay.teardown_current_scene(game_state)
    game_state['scene'] = scene_id
    if scene_id == galaxy_scene:
        _setup_galaxy_scene()
    elif scene_id == space_scene:
        gameplay.setup_space_encounter(game_state)
    elif scene_id == planet_scene:
        gameplay.setup_planet_surface(game_state)
    elif scene_id == station_scene:
        gameplay.setup_space_station(game_state)


def _setup_galaxy_scene():
    scene.set_background_color(1)
    _build_star_sprites()
    _ensure_cursor_sprite()
    _update_cursor_position()
    _ensure_hud_text()
    _refresh_galaxy_info()


def _teardown_galaxy_scene():
    _destroy_star_sprites()
    if game_state['cursor_sprite']:
        game_state['cursor_sprite'].destroy()
        game_state['cursor_sprite'] = None


def _build_star_sprites():
    _destroy_star_sprites()
    sprites_list = []
    index = 0
    systems = game_state['systems']
    while index < len(systems):
        system = systems[index]
        img = assets.make_star_image(system['star_type'])
        star_sprite = sprites.create(img, galaxy_star_kind)
        coords = galaxy.system_coordinates(system['index'])
        star_sprite.set_position(coords[0], coords[1])
        star_sprite.set_data_number('index', index)
        sprites_list.append(star_sprite)
        index += 1
    game_state['star_sprites'] = sprites_list


def _destroy_star_sprites():
    sprites_list = game_state['star_sprites']
    index = 0
    while index < len(sprites_list):
        sprites_list[index].destroy()
        index += 1
    game_state['star_sprites'] = []


def _ensure_cursor_sprite():
    cursor = game_state['cursor_sprite']
    if cursor is None:
        cursor = sprites.create(assets.make_cursor_image(), galaxy_cursor_kind)
        cursor.z = 10
        game_state['cursor_sprite'] = cursor


def _update_cursor_position():
    cursor = game_state['cursor_sprite']
    systems = game_state['systems']
    index = game_state['cursor_index']
    if cursor and index < len(systems):
        coords = galaxy.system_coordinates(index)
        cursor.set_position(coords[0], coords[1])


def _ensure_hud_text():
    if game_state['hud_text'] is None:
        hud = textsprite.create('', 1, 15)
        hud.set_flag(SpriteFlag.RELATIVE_TO_CAMERA, True)
        hud.top = 2
        hud.left = 4
        game_state['hud_text'] = hud


def _set_hud_text(text):
    hud = game_state['hud_text']
    if hud:
        hud.set_text(text)


def _refresh_galaxy_info():
    systems = game_state['systems']
    index = game_state['cursor_index']
    if index < len(systems):
        system = systems[index]
        label = 'Sys ' + str(index + 1) + ' ' + system['star_type']
        label = label + ' | diff ' + str(system['difficulty'])
        if system['has_station']:
            label = label + ' | station'
        label = label + ' | planets ' + str(len(system['planets']))
        _set_hud_text(label)


def _cursor_move(delta):
    index = game_state['cursor_index'] + delta
    if index < 0:
        index = 0
    if index >= len(game_state['systems']):
        index = len(game_state['systems']) - 1
    game_state['cursor_index'] = index
    _update_cursor_position()
    _refresh_galaxy_info()


def _cursor_move_xy(dx, dy):
    current = game_state['cursor_index']
    row = current // galaxy.SYSTEMS_PER_ROW
    col = current % galaxy.SYSTEMS_PER_ROW
    row += dy
    col += dx
    if row < 0:
        row = 0
    if col < 0:
        col = 0
    max_row = (galaxy.GALAXY_SYSTEM_COUNT - 1) // galaxy.SYSTEMS_PER_ROW
    if row > max_row:
        row = max_row
    if col >= galaxy.SYSTEMS_PER_ROW:
        col = galaxy.SYSTEMS_PER_ROW - 1
    index = row * galaxy.SYSTEMS_PER_ROW + col
    if index >= len(game_state['systems']):
        index = len(game_state['systems']) - 1
    game_state['cursor_index'] = index
    _update_cursor_position()
    _refresh_galaxy_info()


def _enter_selected_system():
    system = game_state['systems'][game_state['cursor_index']]
    game_state['active_system'] = system
    _enter_scene(space_scene)


def _randomize_galaxy():
    start_new_galaxy(_generate_seed())


def _register_controls():
    controller.left.on_event(ControllerButtonEvent.PRESSED, _on_left_press)
    controller.right.on_event(ControllerButtonEvent.PRESSED, _on_right_press)
    controller.up.on_event(ControllerButtonEvent.PRESSED, _on_up_press)
    controller.down.on_event(ControllerButtonEvent.PRESSED, _on_down_press)
    controller.A.on_event(ControllerButtonEvent.PRESSED, _on_button_a)
    controller.B.on_event(ControllerButtonEvent.PRESSED, _on_button_b)
    controller.menu.on_event(ControllerButtonEvent.PRESSED, _on_menu_press)


def _on_left_press():
    if game_state['scene'] == galaxy_scene:
        _cursor_move_xy(-1, 0)
    else:
        action = gameplay.handle_direction(game_state, -1, 0)
        _process_action(action)


def _on_right_press():
    if game_state['scene'] == galaxy_scene:
        _cursor_move_xy(1, 0)
    else:
        action = gameplay.handle_direction(game_state, 1, 0)
        _process_action(action)


def _on_up_press():
    if game_state['scene'] == galaxy_scene:
        _cursor_move_xy(0, -1)
    else:
        action = gameplay.handle_direction(game_state, 0, -1)
        _process_action(action)


def _on_down_press():
    if game_state['scene'] == galaxy_scene:
        _cursor_move_xy(0, 1)
    else:
        action = gameplay.handle_direction(game_state, 0, 1)
        _process_action(action)


def _on_button_a():
    scene_id = game_state['scene']
    if scene_id == galaxy_scene:
        _enter_selected_system()
    else:
        action = gameplay.handle_button_a(game_state)
        _process_action(action)


def _on_button_b():
    scene_id = game_state['scene']
    if scene_id == galaxy_scene:
        _randomize_galaxy()
    else:
        action = gameplay.handle_button_b(game_state)
        _process_action(action)


def _on_menu_press():
    action = gameplay.handle_menu(game_state)
    _process_action(action)


def _process_action(action):
    if action is None:
        return
    if action == 'map':
        _enter_scene(galaxy_scene)
        _refresh_galaxy_info()
    elif action == 'land':
        _transition_to_planet()
    elif action == 'station':
        _enter_scene(station_scene)


def _transition_to_planet():
    system = game_state['active_system']
    if len(system['planets']) == 0:
        game.splash('No planets here')
        _enter_scene(galaxy_scene)
        return
    game_state['active_planet'] = system['planets'][0]
    _enter_scene(planet_scene)


_register_controls()
start_new_galaxy(_generate_seed())