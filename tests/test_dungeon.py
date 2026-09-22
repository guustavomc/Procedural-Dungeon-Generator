import pytest

from dungeon import Dungeon
from room_type import RoomType

class TestGenerate:
    def test_grid_matches_requested_dimensions(self):
        dungeon = Dungeon(width=50, height=30, seed=1).generate()
        assert len(dungeon.grid) == 30
        assert all(len(row) == 50 for row in dungeon.grid)

    def test_grid_only_contains_known_tiles(self):
        dungeon = Dungeon(width=50, height=30, seed=1).generate()
        allowed = {Dungeon.WALL, Dungeon.FLOOR, Dungeon.CORRIDOR, Dungeon.SPAWN, Dungeon.EXIT_TILE}
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

    def test_room_types_are_assigned(self):
        dungeon = Dungeon(width=64, height=40, max_depth=5, seed=42).generate()
        types = {room.room_type for room in dungeon.rooms}
        assert RoomType.BOSS in types
        assert RoomType.TREASURE in types
        assert all(rt in RoomType for rt in types)

    def test_entrance_and_exit_are_assigned(self):
        dungeon = Dungeon(width=64, height=40, max_depth=5, seed=42).generate()
        types = [r.room_type for r in dungeon.rooms]
        assert types.count(RoomType.ENTRANCE) == 1
        assert types.count(RoomType.EXIT) == 1

    def test_spawn_and_exit_markers_are_placed(self):
        dungeon = Dungeon(width=64, height=40, max_depth=5, seed=42).generate()
        entrance = next(r for r in dungeon.rooms if r.room_type == RoomType.ENTRANCE)
        exit_room = next(r for r in dungeon.rooms if r.room_type == RoomType.EXIT)

        spawn_tiles = [
            (x, y)
            for y, row in enumerate(dungeon.grid)
            for x, tile in enumerate(row)
            if tile == Dungeon.SPAWN
        ]
        exit_tiles = [
            (x, y)
            for y, row in enumerate(dungeon.grid)
            for x, tile in enumerate(row)
            if tile == Dungeon.EXIT_TILE
        ]

        assert spawn_tiles == [entrance.center]
        assert exit_tiles == [exit_room.center]

    def test_unseeded_generation_does_not_crash(self):
        dungeon = Dungeon(width=50, height=30).generate()
        assert dungeon.rooms
        assert dungeon.is_connected()

    @pytest.mark.parametrize("seed", range(50))
    def test_special_rooms_survive_assignment(self, seed):
        d = Dungeon(width=64, height=40, max_depth=5, seed=seed).generate()
        types = [r.room_type for r in d.rooms]
        assert types.count(RoomType.ENTRANCE) == 1
        assert types.count(RoomType.EXIT) == 1
        if len(d.rooms) >= 4:
            assert RoomType.BOSS in types
            assert RoomType.TREASURE in types
