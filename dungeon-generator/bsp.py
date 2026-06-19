import random
from room import Rect


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