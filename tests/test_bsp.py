import random

from bsp import BSPNode, MIN_SIZE
from room import Rect

class TestSplit:
    def test_region_too_small_stays_leaf(self):
        node = BSPNode(Rect(0, 0, MIN_SIZE * 2 - 1, MIN_SIZE * 2 - 1))
        assert node.split() is False
        assert node.is_leaf

    def test_split_produces_two_children_covering_parent(self):
        random.seed(1)
        node = BSPNode(Rect(0, 0, 40, 20))
        assert node.split() is True
        assert not node.is_leaf

        left, right = node.left.region, node.right.region
        assert left.rect_width * left.rect_height + right.rect_width * right.rect_height == 40 * 20

    def test_already_split_node_returns_false(self):
        random.seed(1)
        node = BSPNode(Rect(0, 0, 40, 20))
        node.split()
        assert node.split() is False


class TestCarveRoom:
    def test_no_room_when_margin_too_large(self):
        node = BSPNode(Rect(0, 0, 6, 6))
        room = node.carve_room(room_id=0, margin=3)
        assert room is None

    def test_room_fits_within_region(self):
        random.seed(2)
        node = BSPNode(Rect(0, 0, 20, 16))
        room = node.carve_room(room_id=0)

        assert room is not None
        r = room.rect
        assert r.x_rect_top_left_corner >= node.region.x_rect_top_left_corner
        assert r.y_rect_top_left_corner >= node.region.y_rect_top_left_corner
        assert r.x_rect_top_right_corner <= node.region.x_rect_top_right_corner
        assert r.y_rect_bottom_left_corner <= node.region.y_rect_bottom_left_corner

    def test_non_leaf_cannot_carve_room(self):
        random.seed(1)
        node = BSPNode(Rect(0, 0, 40, 20))
        node.split()
        assert node.carve_room(room_id=0) is None


class TestGetAllCorridors:
    def test_connects_left_and_right_subtree(self):
        random.seed(3)
        node = BSPNode(Rect(0, 0, 40, 20))
        node.split()
        node.left.carve_room(room_id=0)
        node.right.carve_room(room_id=1)

        corridors = node.get_all_corridors()
        assert len(corridors) == 1

    def test_no_corridor_without_rooms_on_both_sides(self):
        random.seed(1)
        node = BSPNode(Rect(0, 0, 40, 20))
        node.split()
        node.left.carve_room(room_id=0)
        # right side has no room

        assert node.get_all_corridors() == []