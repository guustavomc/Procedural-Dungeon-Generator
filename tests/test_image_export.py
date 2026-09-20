from dungeon import Dungeon
from exporters.image_export import export, WALL_COLOR


class TestImageExport:
    def test_image_size_matches_grid_without_legend(self):
        dungeon = Dungeon(width=50, height=30, seed=1).generate()
        img = export(dungeon, tile_size=8, include_legend=False)
        assert img.size == (50 * 8, 30 * 8)

    def test_legend_adds_extra_height(self):
        dungeon = Dungeon(width=50, height=30, seed=1).generate()
        without_legend = export(dungeon, tile_size=8, include_legend=False)
        with_legend = export(dungeon, tile_size=8, include_legend=True)
        assert with_legend.size[0] == without_legend.size[0]
        assert with_legend.size[1] > without_legend.size[1]

    def test_corner_tile_is_wall_colored(self):
        dungeon = Dungeon(width=50, height=30, seed=1).generate()
        img = export(dungeon, tile_size=8)
        assert img.getpixel((0, 0)) == WALL_COLOR
