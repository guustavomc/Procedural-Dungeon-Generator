from room import Rect, Room

class TestRect:
    def x_rect_top_right_corner(self):
        rect = Rect(x_rect_top_left_corner=5, y_rect_top_left_corner=10, rect_width=20, rect_height=8)
        assert rect.x_rect_top_right_corner == 25

    def y_rect_bottom_left_corner(self):
        rect = Rect(x_rect_top_left_corner=5, y_rect_top_left_corner=10, rect_width=20, rect_height=8)
        assert rect.y_rect_bottom_left_corner == 18