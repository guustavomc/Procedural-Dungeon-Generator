from room import Rect, Room

class TestRect:
    def test_x_rect_top_right_corner(self):
        rect = Rect(x_rect_top_left_corner=5, y_rect_top_left_corner=10, rect_width=20, rect_height=8)
        assert rect.x_rect_top_right_corner == 25

    def test_y_rect_bottom_left_corner(self):
        rect = Rect(x_rect_top_left_corner=5, y_rect_top_left_corner=10, rect_width=20, rect_height=8)
        assert rect.y_rect_bottom_left_corner == 18

    def test_center(self):
        rect = Rect(x_rect_top_left_corner=0, y_rect_top_left_corner=0, rect_width=10, rect_height=6)
        assert rect.center == (5,3)
