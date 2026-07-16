
from dungeon import Dungeon

class TestGenerate:
    def test_grid_matches_requested_dimensions(self):
        dungeon = Dungeon(width=50, height=30, seed=1).generate()
        assert len(dungeon.grid) == 30
        assert all(len(row) == 50 for row in dungeon.grid)

    def test_grid_only_contains_known_tiles(self):
        dungeon = Dungeon(width=50, height=30, seed=1).generate()
        allowed = {Dungeon.WALL, Dungeon.FLOOR, Dungeon.CORRIDOR}
        assert all(tile in allowed for row in dungeon.grid for tile in row)

    def test_same_seed_is_reproducible(self):
        a = Dungeon(width=64, height=40, seed=42).generate()
        b = Dungeon(width=64, height=40, seed=42).generate()

        assert a.grid == b.grid
        assert [r.rect for r in a.rooms] == [r.rect for r in b.rooms]
        assert a.corridors == b.corridors

    def test_all_rooms_are_connected(self):
        dungeon = Dungeon(width=64, height=40, max_depth=5, seed=42).generate()
        assert len(dungeon.rooms) > 1
        assert dungeon.is_connected()
