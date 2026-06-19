from dataclasses import dataclass

@dataclass
class Rect:
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
    
@dataclass
class Room:
    rect: Rect
    id: int
    
    @property
    def center(self):
        return self.rect.center
    
@dataclass
class Corridor:
    center_room_A: tuple[int, int]
    center_room_B: tuple[int, int]
    center_L_shaped_corner: tuple[int, int]