import json

from dungeon import Dungeon
from exporters.ascii_export import render
from exporters.json_export import export


class TestAsciiExport:
    def test_render_matches_grid_dimensions(self):
        dungeon = Dungeon(width=30, height=15, seed=1).generate()
        lines = render(dungeon).split("\n")

        assert len(lines) == 15
        assert all(len(line) == 30 for line in lines)


class TestJsonExport:
    def test_output_is_valid_json_with_expected_shape(self):
        dungeon = Dungeon(width=30, height=15, seed=1).generate()
        data = json.loads(export(dungeon))

        assert data["width"] == 30
        assert data["height"] == 15
        assert len(data["rooms"]) == len(dungeon.rooms)
        assert len(data["corridors"]) == len(dungeon.corridors)
        assert data["grid"] == dungeon.grid

    def test_room_fields_match_source_room(self):
        dungeon = Dungeon(width=30, height=15, seed=1).generate()
        data = json.loads(export(dungeon))

        first = data["rooms"][0]
        room = dungeon.rooms[0]
        rect = room.rect
        assert first == {
            "x": rect.x_rect_top_left_corner,
            "y": rect.y_rect_top_left_corner,
            "width": rect.rect_width,
            "height": rect.rect_height,
            "id": room.id,
            "type": room.room_type.name,
            "center": list(room.center)
        }

    def test_corridor_fields_reference_real_rooms(self):
        dungeon = Dungeon(width=30, height=15, seed=1).generate()
        data = json.loads(export(dungeon))

        room_ids = {r.id for r in dungeon.rooms}
        for corridor in data["corridors"]:
            assert corridor["room_a_id"] in room_ids
            assert corridor["room_b_id"] in room_ids

    def test_grid_omitted_when_not_requested(self):
        dungeon = Dungeon(width=30, height=15, seed=1).generate()
        data = json.loads(export(dungeon, include_grid=False))

        assert "grid" not in data