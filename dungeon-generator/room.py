# Pure data structures used by the generator. No generation logic lives here.

from dataclasses import dataclass

@dataclass
class Rect:
    # Defined by a top-left corner + size. Opposite corner and center are
    # computed properties so they can never drift out of sync with width/height.
    x_rect_top_left_corner: int
    y_rect_top_left_corner: int
    rect_width: int
    rect_height: int

    @property
    def x_rect_top_right_corner(self):
        return self.x_rect_top_left_corner + self.rect_width

    @property
    def y_rect_bottom_left_corner(self):
        return self.y_rect_top_left_corner + self.rect_height

    @property
    def center(self):
        return (self.x_rect_top_left_corner+ self.rect_width // 2), (self.y_rect_top_left_corner+ self.rect_height // 2)

    @property
    def room_type(self):
        return 

@dataclass
class Room:
    # A Rect with an identity. Carved into BSP leaf nodes by BSPNode.carve_room().
    rect: Rect
    id: int

    @property
    def center(self):
        return self.rect.center

@dataclass
class Corridor:
    # An L-shaped path between two room centers, routed through one corner
    # point (center_L_shaped_corner) instead of a straight line, so the path
    # bends around walls rather than cutting through them.
    center_room_A: tuple[int, int]
    center_room_B: tuple[int, int]
    center_L_shaped_corner: tuple[int, int]