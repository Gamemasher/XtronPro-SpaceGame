# combat.py
# Space encounter logic for SpaceGame.

import assets

SPACE_PLAYER_KIND = SpriteKind.create()
SPACE_ENEMY_KIND = SpriteKind.create()
SPACE_LOOT_KIND = SpriteKind.create()

MAX_ENEMIES = 4

_handlers_registered = False
_active_state = None


def start_space_encounter(state):
    global _active_state
    _active_state = state
    state['space_status'] = 'active'
    scene.set_background_color(6)
    _ensure_handlers()
    _setup_player(state)
    _spawn_enemy_wave(state)
    _update_hud(state)


def cleanup_space_scene(state):
    global _active_state
    sprites.destroy_all_sprites_of_kind(SPACE_PLAYER_KIND)
    sprites.destroy_all_sprites_of_kind(SPACE_ENEMY_KIND)
    sprites.destroy_all_sprites_of_kind(SPACE_LOOT_KIND)
    sprites.destroy_all_sprites_of_kind(SpriteKind.projectile)
    state['space_player'] = None
    state['space_enemies'] = []
    state['space_status'] = 'idle'
    _active_state = None


def space_press_a(state):
    if state.get('space_status') == 'finished':
        return 'land'
    _fire_laser(state)
    return None


def space_press_b(state):
    if state.get('space_status') == 'finished':
        if state['active_system'].get('has_station'):
            return 'station'
        return 'map'
    return None


def _ensure_handlers():
    global _handlers_registered
    if _handlers_registered:
        return

    def on_player_enemy(player, enemy):
        if _active_state:
            _handle_player_collision(_active_state, player, enemy)

    def on_projectile_enemy(projectile, enemy):
        if _active_state:
            _handle_projectile_hit(_active_state, projectile, enemy)

    def on_player_loot(player, loot):
        if _active_state:
            _handle_loot_pickup(_active_state, loot)

    sprites.on_overlap(SPACE_PLAYER_KIND, SPACE_ENEMY_KIND, on_player_enemy)
    sprites.on_overlap(SpriteKind.projectile, SPACE_ENEMY_KIND, on_projectile_enemy)
    sprites.on_overlap(SPACE_PLAYER_KIND, SPACE_LOOT_KIND, on_player_loot)
    _handlers_registered = True


def _setup_player(state):
    player = sprites.create(assets.make_ship_icon(), SPACE_PLAYER_KIND)
    player.set_flag(SpriteFlag.STAY_IN_SCREEN, True)
    player.set_data_number('shield', state['player'].get('shield', 3))
    player.set_data_number('hull', state['player'].get('hull', 5))
    controller.move_sprite(player, 60, 60)
    player.set_position(80, 60)
    state['space_player'] = player


def _spawn_enemy_wave(state):
    system = state['active_system']
    rng = [system['seed'] & 0xffffffff]
    enemies = []
    count = 0
    while count < MAX_ENEMIES:
        enemy = _create_enemy_sprite(rng, system['difficulty'])
        enemies.append(enemy)
        count += 1
    state['space_enemies'] = enemies


def _create_enemy_sprite(rng_state, difficulty):
    img = image.create(10, 10)
    img.fill(0)
    color = 10
    if difficulty >= 2:
        color = 7
    if difficulty >= 3:
        color = 2
    img.fill_rect(2, 2, 6, 6, color)
    enemy = sprites.create(img, SPACE_ENEMY_KIND)
    enemy.set_position(_rand_range(rng_state, 10, 150), _rand_range(rng_state, 10, 110))
    enemy.set_velocity(_rand_range(rng_state, -40, 40), _rand_range(rng_state, -40, 40))
    enemy.set_flag(SpriteFlag.STAY_IN_SCREEN, True)
    enemy.set_data_number('hp', 2 + difficulty)
    return enemy


def _fire_laser(state):
    player = state.get('space_player')
    if not player:
        return
    img = image.create(2, 4)
    img.fill(0)
    img.fill_rect(0, 0, 2, 4, 9)
    proj = sprites.create_projectile_from_sprite(img, player, 0, -90)
    proj.set_data_number('damage', 1 + state['player'].get('weapon', 0))


def _handle_projectile_hit(state, projectile, enemy):
    projectile.destroy()
    hp = enemy.data_number('hp') - projectile.data_number('damage')
    if hp <= 0:
        _enemy_destroyed(state, enemy)
    else:
        enemy.set_data_number('hp', hp)


def _handle_player_collision(state, player, enemy):
    enemy.destroy()
    shield = player.data_number('shield')
    if shield > 0:
        player.set_data_number('shield', shield - 1)
    else:
        hull = player.data_number('hull') - 1
        player.set_data_number('hull', hull)
        if hull <= 0:
            game.over(False)
    _update_hud(state)


def _handle_loot_pickup(state, loot):
    loot.destroy()
    state['player']['credits'] = state['player'].get('credits', 0) + 5
    _update_hud(state)


def _enemy_destroyed(state, enemy):
    x = enemy.x
    y = enemy.y
    enemy.destroy()
    loot = sprites.create(image.create(4, 4), SPACE_LOOT_KIND)
    loot.fill(0)
    loot.fill_rect(0, 0, 4, 4, 2)
    loot.set_position(x, y)
    loot.set_flag(SpriteFlag.STAY_IN_SCREEN, True)
    _check_wave_completion(state)


def _check_wave_completion(state):
    if len(sprites.all_of_kind(SPACE_ENEMY_KIND)) > 0:
        return
    state['space_status'] = 'finished'
    if state['active_system'].get('has_station'):
        _set_hud_text(state, 'Victory! A:Land  B:Station')
    else:
        _set_hud_text(state, 'Victory! A:Land  B:Map')


def _update_hud(state):
    player = state.get('space_player')
    if not player:
        return
    hull = player.data_number('hull')
    shield = player.data_number('shield')
    credits = state['player'].get('credits', 0)
    msg = 'Hull {} | Shield {} | Cr {}'.format(hull, shield, credits)
    _set_hud_text(state, msg)


def _set_hud_text(state, text):
    hud = state.get('hud_text')
    if hud:
        hud.image.fill(0)
        hud.image.print(text, 1, 1, 1)


def _rand_range(rng_state, minimum, maximum):
    span = maximum - minimum + 1
    if span <= 0:
        return minimum
    value = _lcg_step(rng_state)
    return minimum + value % span


def _lcg_step(state):
    state[0] = (1103515245 * state[0] + 12345) & 0x7fffffff
    return state[0]

