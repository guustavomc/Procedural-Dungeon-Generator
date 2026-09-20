from PIL import Image, ImageDraw, ImageFont

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

LEGEND_ENTRIES = [
    ("Wall", WALL_COLOR), 
    ("Corridor", CORRIDOR_COLOR)] + [
    (rt.name.title(), color) for rt, 
    color in ROOM_COLORS.items()
]

LEGEND_SWATCH_SIZE = 12
LEGEND_PADDING = 6
LEGEND_ROW_HEIGHT = 18

def legend_segment_height():
    return LEGEND_PADDING * 2 + len(LEGEND_ENTRIES) * LEGEND_ROW_HEIGHT

def export(dungeon, tile_size=16, include_legend=True):
    grid_width = dungeon.width * tile_size
    grid_height = dungeon.height * tile_size
    legend_height = legend_segment_height() if include_legend else 0

    img = Image.new(
        "RGB",
        (grid_width, grid_height + legend_height),
        WALL_COLOR,
    )    
    draw = ImageDraw.Draw(img)

    for y, row in enumerate(dungeon.grid):
        for x, tile in enumerate(row):
            if tile == dungeon.CORRIDOR:
                fill_block(draw, x, y, 1, 1, tile_size, CORRIDOR_COLOR)

    for room in dungeon.rooms:
        r = room.rect
        fill_block(
            draw,
            r.x_rect_top_left_corner,
            r.y_rect_top_left_corner,
            r.rect_width,
            r.rect_height,
            tile_size,
            ROOM_COLORS[room.room_type],
        )

    if include_legend:
        _draw_legend(draw, y_start=grid_height)

    return img


    

def fill_block(draw, 
               x_rect_top_left_corner, 
               y_rect_top_left_corner, 
               rect_width, 
               rect_height, 
               tile_size,
               color):
    draw.rectangle(
        [
            x_rect_top_left_corner * tile_size,
            y_rect_top_left_corner * tile_size,
            (x_rect_top_left_corner + rect_width) * tile_size - 1,
            (y_rect_top_left_corner + rect_height) * tile_size - 1,
        ],
        fill=color,
    )

def _draw_legend(draw, y_start):
    font = ImageFont.load_default()
    y = y_start + LEGEND_PADDING

    for label, color in LEGEND_ENTRIES:
        draw.rectangle(
            [LEGEND_PADDING, y, LEGEND_PADDING + LEGEND_SWATCH_SIZE, y + LEGEND_SWATCH_SIZE],
            fill=color,
        )
        draw.text(
            (LEGEND_PADDING + LEGEND_SWATCH_SIZE + LEGEND_PADDING, y),
            label,
            font=font,
            fill=(255, 255, 255),
        )
        y += LEGEND_ROW_HEIGHT

        
    