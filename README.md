# Procedural Dungeon Generator

A BSP (Binary Space Partitioning) based procedural dungeon generator written in Python, built as a learning project for core CS fundamentals (trees, recursion vs. iteration, randomized algorithms).

**Goals:**
- Generate connected dungeon layouts using a BSP tree
- Visualize them as ASCII / terminal output (and later a web canvas)
- Export layouts as JSON for consumption by other tools (e.g. Godot)
- Eventually export dungeon tiles as STL files for 3D printing

## Project structure

```
dungeon-generator/
├── room.py     # Rect, Room, and Corridor data structures
├── bsp.py      # BSPNode: tree splitting, room carving, corridor connections
└── dungeon.py  # Dungeon: orchestrates generation and paints the grid
```

## Main concepts

- **`Rect`** ([room.py](dungeon-generator/room.py)) — a rectangle defined by its top-left corner and size. Exposes computed corners (`x_rect_top_right_corner`, `y_rect_bottom_left_corner`) and a `center` point.
- **`Room`** — wraps a `Rect` with an `id`.
- **`Corridor`** — three points (`center_room_A`, `center_room_B`, `center_L_shaped_corner`) describing an L-shaped path between two room centers, so corridors bend around walls instead of cutting straight through them.
- **`BSPNode`** ([bsp.py](dungeon-generator/bsp.py)) — represents one rectangular region of the map.
  - `split()` recursively divides a region into two children along its longer axis, stopping once a region is too small (`MIN_SIZE`).
  - `is_leaf` is true only for nodes that were never split — these are the nodes that get rooms carved into them.
  - `carve_room()` shrinks a leaf's region inward by a margin and places a randomly sized/positioned room inside it. The margin guarantees a wall gap between adjacent rooms.
  - `get_room()` returns one room from anywhere in a node's subtree (used to pick connection points).
  - `get_all_corridors()` walks the tree bottom-up, connecting one room from each node's left subtree to one room from its right subtree. Because every internal node connects its two children, the result is always fully connected — no room can be isolated.
- **`Dungeon`** ([dungeon.py](dungeon-generator/dungeon.py)) — the orchestrator:
  1. Fills the grid with walls.
  2. Builds the BSP tree **iteratively** using a queue (avoids Python's recursion limit on deep/large maps).
  3. Carves rooms into every leaf.
  4. Collects corridors from the tree.
  5. Paints rooms (`.`) and corridors (`,`) onto the wall grid (`#`).
  - Supports a `seed` so the same seed always reproduces the same dungeon.

## How to run it

Basic run with defaults:

```
cd dungeon-generator
python main.py
```

With custom parameters:

```

python main.py --width 80 --height 40 --depth 6
```

With a seed for a reproducible layout:

```
python main.py --seed 42
```
With a JSON output:
```
python main.py --seed 42 --json
```

Save to a file:
```
python main.py --seed 42 --json > dungeon.json
```
Run the tests:
```
pip install -r requirements-dev.txt
python -m pytest tests/ -v
```

**Tile legend:**
- `#` wall
- `.` room floor
- `,` corridor

**Constructor parameters (`Dungeon`):**
| Param | Default | Meaning |
|---|---|---|
| `width` | 64 | grid width in tiles |
| `height` | 40 | grid height in tiles |
| `max_depth` | 5 | maximum BSP split depth |
| `seed` | `None` | RNG seed for reproducible layouts |

## Status / what's next

- [x] `Rect` / `Room` / `Corridor` data structures
- [x] `BSPNode` splitting, room carving, corridor generation
- [x] `Dungeon` orchestrator (grid fill, tree build, carve, paint)
- [x] ASCII renderer module (`exporters/ascii.py`)
- [x] JSON exporter (`exporters/json_export.py`) — for Godot / web canvas consumption
- [x] `main.py` entry point
- [x] Tests

## Roadmap

### Next steps

- [x] **Flood fill connectivity check** — `Dungeon.is_connected() -> bool` BFS's from a room center over floor/corridor tiles and verifies every room's center is reachable.

- [x] **Room types** — `Room.room_type` field (`Enum`: `ENTRANCE`, `EXIT`, `TREASURE`, `BOSS`, `NORMAL`), assigned during generation: deepest leaf(s) → boss rooms, smallest remaining room → treasure, everything else → normal.

- [x] **ENTRANCE/EXIT assignment** — assign `RoomType.ENTRANCE` to `rooms[0]` and `RoomType.EXIT` to `rooms[-1]` (deliberately deferred out of the room types work above, folded into the spawn/exit step below instead).

- [ ] **Image Exporter** —  Colors rooms by room_type, and needs no event loop or window management.

- [ ] **Player spawn + exit** — render the ENTRANCE room as `@` (spawn) and the EXIT room as `>` on the ASCII grid. Small change, but makes the output feel like an actual dungeon and makes the JSON export meaningful to a game engine.

- [x] **Richer JSON export** — room id/type aren't in `exporters/json_export.py` yet — it still only exports x/y/width/height. Add `id`, `type`, and `center` to each room; add `room_a_id`/`room_b_id` to each corridor.

- [ ] **STL tile exporter** — export each tile type (wall, floor, corridor) as a printable 3D tile with standardized connectors, for physical dungeon sets. Builds directly on the STL generation work in [Drawer-Organizer-Builder](https://github.com/guustavomc/Drawer-Organizer-Builder).