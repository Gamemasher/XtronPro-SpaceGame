# assets.py
# Helper routines for generating small sprite images and palettes.

STAR_COLORS = {
    'red': 2,
    'yellow': 5,
    'blue': 8,
    'binary': 7,
    'pulsar': 1
}


def make_star_image(star_type):
    color = 7
    if star_type in STAR_COLORS:
        color = STAR_COLORS[star_type]
    img = image.create(8, 8)
    img.fill(0)
    center = 4
    radius = 3
    img.draw_circle(center, center, radius, color)
    img.set_pixel(center, center, 15)
    return img


def make_cursor_image():
    img = image.create(10, 10)
    img.fill(0)
    x = 0
    while x < 10:
        img.set_pixel(x, 0, 9)
        img.set_pixel(x, 9, 9)
        x += 1
    y = 0
    while y < 10:
        img.set_pixel(0, y, 9)
        img.set_pixel(9, y, 9)
        y += 1
    return img


def make_ship_icon():
    img = image.create(12, 12)
    img.fill(0)
    img.fill_rect(5, 0, 2, 12, 12)
    img.fill_rect(0, 4, 12, 4, 13)
    img.fill_rect(4, 4, 4, 8, 1)
    return img

