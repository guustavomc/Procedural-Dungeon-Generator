from dungeon import Dungeon
from exporters.image_export import export, WALL_COLOR


class TestImageExport:
    def test_image_size_matches_grid(self):
        dungeon = Dungeon(width=50, height=30, seed=1).generate()
        img = export(dungeon, tile_size=8)
        assert img.size == (50 * 8, 30 * 8)

    def test_corner_tile_is_wall_colored(self):
        dungeon = Dungeon(width=50, height=30, seed=1).generate()
        img = export(dungeon, tile_size=8)
        assert img.getpixel((0, 0)) == WALL_COLOR
