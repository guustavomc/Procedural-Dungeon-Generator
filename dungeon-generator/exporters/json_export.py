import json

def export(dungeon):
    return json.dumps({
        "width": dungeon.width,
        "height": dungeon.height,
        "rooms": [
            {
                "id":r.id,
                "x": r.x_rect_top_left_corner,
                "y": r.y_rect_top_left_corner,
                "width": r.rect_width,
                "height": r.rect_height
            }
            for r in dungeon.rooms
        ],
        "corridors": [
            {
                "start": list(c.center_room_A),
                "end": list(c.center_room_B),
                "bend": list(c.center_L_shaped_corner)
            }
            for c in dungeon.corridors
        ],
        "grid": dungeon.grid
    }, indent=2
    )