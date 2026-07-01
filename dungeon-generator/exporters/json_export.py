import json

def export(dungeon):
    return json.dumps({
        "width": dungeon.width,
        "height": dungeon.height
    }
    )