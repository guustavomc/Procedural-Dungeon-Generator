# Orchestrator: builds the BSP tree, carves rooms, connects them with
# corridors, and paints the result onto a 2D character grid.

import random
from typing import Optional
from bsp import BSPNode
from room import Rect, Room, Corridor
from collections import deque


class Dungeon:
    WALL        = "#"
    FLOOR       = "."
    CORRIDOR    = ","

    def __init__(self, width=64, height=40, max_depth=5, seed=None):
        self.width = width
        self.height = height
        self.max_depth = max_depth
        self.seed = seed       # same seed -> same dungeon, every time
        self.grid = []
        self.rooms = []
        self.corridors = []

    def generate(self):
        if self.seed is not None:
            random.seed(self.seed)

        # 1. fill everything with walls
        self.grid = [[self.WALL] * self.width for _ in range(self.height)]

        # 2. build the BSP tree. Iterative (queue-based) rather than
        # recursive so deep/large maps can't hit Python's recursion limit.
        root = BSPNode(Rect(0, 0, self.width, self.height))
        queue = [(root, 0)]
        while queue:
            node, depth = queue.pop()
            if depth < self.max_depth:
                if node.split():
                    queue.append((node.left,  depth + 1))
                    queue.append((node.right, depth + 1))

        # 3. carve rooms into leaves
        self.rooms = []
        self._carve_leaves(root, counter=[0])

        # 4. collect corridors from the tree (bottom-up, guarantees connectivity)
        self.corridors = root.get_all_corridors()

        # 5. paint rooms and corridors onto the grid
        self._paint_rooms()
        self._paint_corridors()
        return self

    def _carve_leaves(self, node, counter):
        # Recursive walk of the finished tree: every leaf gets a room
        # attempt; counter assigns sequential ids across the whole tree.
        if node is None:
            return
        if node.is_leaf:
            room = node.carve_room(room_id=counter[0])
            if room:
                self.rooms.append(room)
                counter[0] += 1
        else:
            self._carve_leaves(node.left, counter)
            self._carve_leaves(node.right, counter)

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
                    if self.grid[ny][nx] in (self.FLOOR, self.CORRIDOR):
                        visited.add((nx, ny))
                        queue.append((nx, ny))

        return all(room.center in visited for room in self.rooms)