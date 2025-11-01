# station.py
# Space station interactions for upgrades and refueling.

STATION_TEXT_KIND = SpriteKind.create()

STATION_OPTIONS = [
    {
        'name': 'Refuel (+30)',
        'cost': 15,
        'effect': 'refuel'
    },
    {
        'name': 'Repair (+3 hull)',
        'cost': 12,
        'effect': 'repair'
    },
    {
        'name': 'Upgrade weapon',
        'cost': 25,
        'effect': 'weapon'
    }
]

_active_state = None


def start_station_scene(state):
    global _active_state
    _active_state = state
    scene.set_background_color(8)
    state['station_index'] = 0
    state['station_status'] = 'menu'
    _ensure_option_text(state)
    _refresh_station_text(state)


def cleanup_station_scene(state):
    label = state.get('station_text')
    if label:
        label.destroy()
        state['station_text'] = None
    state['station_status'] = 'idle'


def handle_button_a(state):
    if state.get('station_status') != 'menu':
        return None
    option = STATION_OPTIONS[state['station_index']]
    cost = option['cost']
    if state['player'].get('credits', 0) < cost:
        _set_hud_text(state, 'Need {} credits'.format(cost))
        return None
    state['player']['credits'] -= cost
    effect = option['effect']
    if effect == 'refuel':
        state['player']['fuel'] = min(100, state['player'].get('fuel', 0) + 30)
        _set_hud_text(state, 'Refueled +30')
    elif effect == 'repair':
        state['player']['hull'] = min(10, state['player'].get('hull', 5) + 3)
        _set_hud_text(state, 'Hull repaired')
    elif effect == 'weapon':
        state['player']['weapon'] = state['player'].get('weapon', 0) + 1
        _set_hud_text(state, 'Weapon upgraded')
    _refresh_station_text(state)
    return None


def handle_button_b(state):
    state['station_status'] = 'exit'
    return 'map'


def handle_direction(state, dx, dy):
    if dy == 0:
        return None
    index = state.get('station_index', 0)
    index += -1 if dy < 0 else 1
    if index < 0:
        index = len(STATION_OPTIONS) - 1
    if index >= len(STATION_OPTIONS):
        index = 0
    state['station_index'] = index
    _refresh_station_text(state)
    return None


def _ensure_option_text(state):
    if state.get('station_text') is None:
        img = image.create(160, 48)
        label = sprites.create(img, STATION_TEXT_KIND)
        label.set_flag(SpriteFlag.RELATIVE_TO_CAMERA, True)
        label.left = 0
        label.top = 20
        label.z = 90
        state['station_text'] = label


def _refresh_station_text(state):
    option = STATION_OPTIONS[state['station_index']]
    credits = state['player'].get('credits', 0)
    label = state.get('station_text')
    if label:
        img = label.image
        img.fill(0)
        img.print('Station Services', 2, 2, 1)
        img.print(option['name'], 2, 14, 1)
        img.print('Cost {} cr'.format(option['cost']), 2, 26, 1)
        img.print('Credits {}'.format(credits), 2, 38, 1)
    _set_hud_text(state, 'Use up/down to cycle, A to buy, B to depart')


def _set_hud_text(state, text):
    hud = state.get('hud_text')
    if hud:
        hud.image.fill(0)
        hud.image.print(text, 1, 1, 1)

