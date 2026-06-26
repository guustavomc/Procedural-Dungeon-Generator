import random
from room import Corridor, Rect, Room


MIN_SIZE = 6

class BSPNode:
    def __init__(self, region: Rect):
        self.region = region
        self.left = None
        self.right = None
        self.room = None

    @property
    def is_leaf(self):
        return self.left is None and self.right is None
    
    def split(self, min_size = MIN_SIZE):
        if self.is_leaf != True:
            return False
        
        can_split_horizontally = self.region.rect_height >= min_size * 2
        can_split_vertically = self.region.rect_width >= min_size * 2

        if not can_split_horizontally and not can_split_vertically:
            return False
        
        if can_split_horizontally and can_split_vertically:
           split_horizontally = self.region.rect_height > self.region.rect_width
        else:
            split_horizontally = can_split_horizontally

        if split_horizontally:
            cut = random.randint(self.region.y_rect_top_left_corner + min_size,
                                 self.region.y_rect_bottom_left_corner - min_size)
            
            self.left = BSPNode(Rect(self.region.x_rect_top_left_corner, 
                                     self.region.y_rect_top_left_corner,
                                     self.region.rect_width,
                                     cut - self.region.y_rect_top_left_corner))
            
            self.right = BSPNode(Rect(self.region.x_rect_top_left_corner, 
                                     cut,
                                     self.region.rect_width,
                                     self.region.y_rect_bottom_left_corner - cut))
        
        else:
            cut = random.randint(self.region.x_rect_top_left_corner + min_size,
                                 self.region.x_rect_top_right_corner - min_size)
            
            self.left = BSPNode(Rect(self.region.x_rect_top_left_corner, 
                                     self.region.y_rect_top_left_corner,
                                     cut - self.region.x_rect_top_left_corner,
                                     self.region.rect_height))
            
            self.right = BSPNode(Rect(cut, 
                                     self.region.y_rect_top_left_corner,
                                     self.region.x_rect_top_right_corner - cut,
                                     self.region.rect_height))
        return True
    
    def carve_room(self, room_id: int, margin=2):
        if not self.is_leaf:
            return None
        
        inner_x = self.region.x_rect_top_left_corner + margin
        inner_y = self.region.y_rect_top_left_corner + margin
        inner_width = self.region.rect_width - (margin * 2)
        inner_height = self.region.rect_height - (margin * 2)

        if inner_width < 3 or inner_height < 3:
            return None
        
        room_width = random.randint(max(3, inner_width // 2), inner_width)
        room_height = random.randint(max(3, inner_height // 2), inner_height)

        room_x = random.randint(inner_x, inner_x + inner_width - room_width)
        room_y = random.randint(inner_y, inner_y + inner_height - room_height)

        self.room = Room(rect=Rect(room_x, room_y, room_width, room_height), id=room_id)
        return self.room
    
    def get_room(self):
        """Return any one room from this subtree."""
        if self.is_leaf:
            return self.room
        
        left_room = self.left.get_room() if self.left else None
        right_room = self.right.get_room() if self.right else None
        if left_room and right_room:
            return random.choice([left_room, right_room])
        return left_room or right_room
    
    def get_all_corridors(self):
        corridors = []
        if not self.is_leaf:
            corridors += self.left.get_all_corridors()
            corridors += self.right.get_all_corridors()

            a = self.left.get_room()
            b = self.right.get_room()

            if a and b:
                ax, ay = a.center
                bx, by = b.center

                if random.random() < 0.5:
                    bend = (bx, ay)
                else:
                    bend = (ax, by)
                corridors.append(Corridor(start=(ax, ay), end=(bx, by), ben=bend))
        return corridors