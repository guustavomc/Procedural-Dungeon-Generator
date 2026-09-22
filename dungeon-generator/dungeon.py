# Orchestrator: builds the BSP tree, carves rooms, connects them with
# corridors, and paints the result onto a 2D character grid.

import random
from typing import Optional
from bsp import BSPNode
from room import Rect, Room, Corridor
from collections import deque
from room_type import RoomType



class Dungeon:
    WALL        = "#"
    FLOOR       = "."
    CORRIDOR    = ","
    SPAWN       = "@"
    EXIT_TILE   = ">"

    def __init__(self, width=64, height=40, max_depth=5, seed=None):
        self.width = width
        self.height = height
        self.max_depth = max_depth
        self.seed = seed       # same seed -> same dungeon, every time
        self.grid = []
        self.rooms = []
        self.corridors = []

    def generate(self):
        self.rng = random.Random(self.seed)

        # 1. fill everything with walls
        self.grid = [[self.WALL] * self.width for _ in range(self.height)]

        # 2. build the BSP tree. Iterative (queue-based) rather than
        # recursive so deep/large maps can't hit Python's recursion limit.
        root = BSPNode(Rect(0, 0, self.width, self.height), self.rng)
        queue = [(root, 0)]
        while queue:
            node, depth = queue.pop()
            if depth < self.max_depth:
                if node.split():
                    queue.append((node.left,  depth + 1))
                    queue.append((node.right, depth + 1))

        # 3. carve rooms into leaves
        self.rooms = []
        self._room_depths = {}
        self._carve_leaves(root, counter=[0])
        self.corridors = root.get_all_corridors()
        self._assign_room_types()

        # 4. paint rooms and corridors onto the grid
        self._paint_rooms()
        self._paint_corridors()
        self._paint_spawn_exit()
        return self

    def _carve_leaves(self, node, counter, depth=0):
        # Recursive walk of the finished tree: every leaf gets a room
        # attempt; counter assigns sequential ids across the whole tree.
        if node is None:
            return
        if node.is_leaf:
            room = node.carve_room(room_id=counter[0])
            if room:
                self.rooms.append(room)
                self._room_depths[room.id] = depth
                counter[0] += 1
        else:
            self._carve_leaves(node.left, counter, depth + 1)
            self._carve_leaves(node.right, counter, depth + 1)

    def _assign_room_types(self):
        if not self.rooms:
            return

        entrance = self.rooms[0]
        entrance.room_type = RoomType.ENTRANCE

        if len(self.rooms) == 1:
            return

        exit_room = self._farthest_room_from(entrance)
        exit_room.room_type = RoomType.EXIT

        candidates = [r for r in self.rooms if r.id not in (entrance.id, exit_room.id)]
        if not candidates:
            return

        max_depth = max(self._room_depths[r.id] for r in candidates)
        boss_ids = {r.id for r in candidates if self._room_depths[r.id] == max_depth}

        # max_depth often acts as a hard cutoff before MIN_SIZE would stop
        # splitting naturally, so most/all candidates can tie for "deepest".
        # Cap the boss set so at least one candidate is left for treasure.
        if len(candidates) > 1 and len(boss_ids) == len(candidates):
            boss_ids = {min(boss_ids)}

        remaining = [r for r in candidates if r.id not in boss_ids]
        treasure_ids = set()
        if remaining:
            smallest = min(remaining, key=lambda r: r.rect.rect_width * r.rect.rect_height)
            treasure_ids = {smallest.id}

        for room in candidates:
            if room.id in boss_ids:
                room.room_type = RoomType.BOSS
            elif room.id in treasure_ids:
                room.room_type = RoomType.TREASURE
            else:
                room.room_type = RoomType.NORMAL

    def _farthest_room_from(self, start_room):
        # BFS over the corridor graph (a tree, so shortest path is the only
        # path) to find the room with the greatest distance from start_room.
        adjacency = {room.id: [] for room in self.rooms}
        for c in self.corridors:
            adjacency[c.room_a_id].append(c.room_b_id)
            adjacency[c.room_b_id].append(c.room_a_id)

        rooms_by_id = {room.id: room for room in self.rooms}

        visited = {start_room.id}
        queue = deque([start_room.id])
        farthest_id = start_room.id

        while queue:
            current_id = queue.popleft()
            farthest_id = current_id
            for neighbor_id in adjacency[current_id]:
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    queue.append(neighbor_id)

        return rooms_by_id[farthest_id]

    def _paint_rooms(self):
        # Overwrite WALL with FLOOR for every tile inside each room's rect.
        for room in self.rooms:
            r = room.rect
            for y in range(r.y_rect_top_left_corner, r.y_rect_bottom_left_corner):
                for x in range(r.x_rect_top_left_corner, r.x_rect_top_right_corner):
                    self.grid[y][x] = self.FLOOR

    def _paint_corridors(self):
        # Each corridor is drawn as two straight segments through its bend point.
        for c in self.corridors:
            self._line(c.center_room_A, c.center_L_shaped_corner)
            self._line(c.center_L_shaped_corner, c.center_room_B)

    def _paint_spawn_exit(self):
        for room in self.rooms:
            x, y = room.center
            if room.room_type == RoomType.ENTRANCE:
                self.grid[y][x] = self.SPAWN
            elif room.room_type == RoomType.EXIT:
                self.grid[y][x] = self.EXIT_TILE

    def _line(self, a, b):
        # Draws one straight L-segment: horizontal leg then vertical leg.
        # Only overwrites WALL tiles, so corridors never stomp on room floors.
        ax, ay = a
        bx, by = b
        # horizontal segment
        for x in range(min(ax, bx), max(ax, bx) + 1):
            if self.grid[ay][x] == self.WALL:
                self.grid[ay][x] = self.CORRIDOR
        # vertical segment
        for y in range(min(ay, by), max(ay, by) + 1):
            if self.grid[y][bx] == self.WALL:
                self.grid[y][bx] = self.CORRIDOR

    def is_connected(self) -> bool:
        if not self.rooms:
            return True

        start = self.rooms[0].center
        visited = {start}
        queue = deque([start])

        while queue:
            x, y = queue.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height and (nx, ny) not in visited:
                    if self.grid[ny][nx] in (self.FLOOR, self.CORRIDOR, self.SPAWN, self.EXIT_TILE):
                        visited.add((nx, ny))
                        queue.append((nx, ny))

        return all(room.center in visited for room in self.rooms)