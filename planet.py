# planet.py
# Planet surface exploration logic.

PLANET_PLAYER_KIND = SpriteKind.create()
PLANET_RESOURCE_KIND = SpriteKind.create()
PLANET_ENEMY_KIND = SpriteKind.create()

_biome_colors = {
    'ice': 9,
    'desert': 4,
    'jungle': 7,
    'volcanic': 6,
    'ocean': 1,
    'crystal': 5
}

_handlers_registered = False
_active_state = None


def start_planet_scene(state):
    global _active_state
    _active_state = state
    planet = state.get('active_planet')
    state['planet_status'] = 'explore'
    scene.set_background_color(_biome_colors.get(planet['biome'], 3))
    _ensure_handlers()
    _spawn_player(state)
    _spawn_resources(state, planet)
    _spawn_enemies(state, planet)
    _consume_fuel(state)
    _update_hud(state)


def cleanup_planet_scene(state):
    global _active_state
    controller.move_sprite(None, 0, 0)
    sprites.destroy_all_sprites_of_kind(PLANET_PLAYER_KIND)
    sprites.destroy_all_sprites_of_kind(PLANET_RESOURCE_KIND)
    sprites.destroy_all_sprites_of_kind(PLANET_ENEMY_KIND)
    state['planet_player'] = None
    state['planet_status'] = 'idle'
    _active_state = None


def handle_button_a(state):
    # Action handled through overlap; no extra behavior
    return None


def handle_button_b(state):
    state['planet_status'] = 'depart'
    return 'map'


def handle_direction(state, dx, dy):
    # Planet exploration uses analog movement, no menu navigation.
    return None


def _ensure_handlers():
    global _handlers_registered
    if _handlers_registered:
        return

    def on_resource_overlap(player, resource):
        if _active_state:
            _collect_resource(_active_state, resource)

    def on_enemy_overlap(player, enemy):
        if _active_state:
            _enemy_collision(_active_state, enemy)

    sprites.on_overlap(PLANET_PLAYER_KIND, PLANET_RESOURCE_KIND, on_resource_overlap)
    sprites.on_overlap(PLANET_PLAYER_KIND, PLANET_ENEMY_KIND, on_enemy_overlap)
    _handlers_registered = True


def _spawn_player(state):
    img = image.create(12, 12)
    img.fill(0)
    img.fill_rect(2, 2, 8, 8, 11)
    explorer = sprites.create(img, PLANET_PLAYER_KIND)
    explorer.set_flag(SpriteFlag.STAY_IN_SCREEN, True)
    explorer.set_position(80, 60)
    controller.move_sprite(explorer, 50, 50)
    state['planet_player'] = explorer


def _spawn_resources(state, planet):
    rng = [planet['size'] & 0xffffffff]
    richness = planet['richness'] + 2
    resources = []
    index = 0
    while index < richness:
        node = sprites.create(image.create(6, 6), PLANET_RESOURCE_KIND)
        node.image.fill(0)
        node.image.fill_rect(0, 0, 6, 6, 13)
        node.set_position(_rand_range(rng, 10, 150), _rand_range(rng, 10, 110))
        node.set_flag(SpriteFlag.STAY_IN_SCREEN, True)
        resources.append(node)
        index += 1
    state['planet_resources'] = resources


def _spawn_enemies(state, planet):
    hostility = planet['hostility']
    count = 0
    if hostility > 70:
        count = 3
    elif hostility > 40:
        count = 2
    elif hostility > 20:
        count = 1
    rng = [planet['hostility'] & 0xffffffff]
    enemies = []
    idx = 0
    while idx < count:
        enemy = sprites.create(image.create(10, 10), PLANET_ENEMY_KIND)
        enemy.image.fill(0)
        enemy.image.fill_rect(1, 1, 8, 8, 2)
        enemy.set_position(_rand_range(rng, 10, 150), _rand_range(rng, 10, 110))
        enemy.set_velocity(_rand_range(rng, -30, 30), _rand_range(rng, -30, 30))
        enemy.set_flag(SpriteFlag.STAY_IN_SCREEN, True)
        enemies.append(enemy)
        idx += 1
    state['planet_enemies'] = enemies


def _consume_fuel(state):
    fuel = state['player'].get('fuel', 100)
    fuel = max(0, fuel - 5)
    state['player']['fuel'] = fuel


def _collect_resource(state, resource):
    resource.destroy()
    state['player']['resources'] = state['player'].get('resources', 0) + 1
    _update_hud(state)
    _check_completion(state)


def _enemy_collision(state, enemy):
    enemy.set_velocity(-enemy.vx, -enemy.vy)
    hull = state['player'].get('hull', 5) - 1
    state['player']['hull'] = hull
    if hull <= 0:
        game.over(False)
    _update_hud(state)


def _check_completion(state):
    remaining = sprites.all_of_kind(PLANET_RESOURCE_KIND)
    if len(remaining) == 0:
        _set_hud_text(state, 'Resources gathered! B:Depart')


def _update_hud(state):
    resources = state['player'].get('resources', 0)
    fuel = state['player'].get('fuel', 0)
    hull = state['player'].get('hull', 0)
    text = 'Res {} | Fuel {} | Hull {}'.format(resources, fuel, hull)
    _set_hud_text(state, text)


def _set_hud_text(state, text):
    hud = state.get('hud_text')
    if hud:
        hud.set_text(text)


def _rand_range(rng_state, minimum, maximum):
    span = maximum - minimum + 1
    if span <= 0:
        return minimum
    value = _lcg_step(rng_state)
    return minimum + value % span


def _lcg_step(state):
    state[0] = (1103515245 * state[0] + 12345) & 0x7fffffff
    return state[0]