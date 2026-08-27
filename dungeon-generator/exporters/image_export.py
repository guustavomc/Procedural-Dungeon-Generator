from PIL import Image, ImageDraw

from room_type import RoomType

WALL_COLOR = (30, 30, 30)
CORRIDOR_COLOR = (170, 140, 100)

ROOM_COLORS = {
    RoomType.ENTRANCE: (80, 200, 120),
    RoomType.EXIT: (200, 60, 60),
    RoomType.TREASURE: (230, 200, 40),
    RoomType.BOSS: (150, 40, 180),
    RoomType.NORMAL: (200, 200, 200),
}

def export(dungeon, tile_size=16):
    img = Image.new("RGB", (dungeon.width * tile_size, dungeon.height * tile_size), WALL_COLOR,)
    draw = ImageDraw.Draw(img)

    for y, row in enumerate(dungeon.grid):
        for x, title in enumerate(row):
            if tile == dungeon.CORRIDOR:
                _fill_block(draw, x, y, 1, 1, tile_size, CORRIDOR_COLOR)
