# BSP tree: splits map regions, carves rooms into leaves, and connects
# rooms across the tree with corridors. This is the core generation algorithm.

import random
from room import Corridor, Rect, Room


MIN_SIZE = 6  # smallest a region's half can be after a split

class BSPNode:
    # One rectangular region of the map. Starts as a leaf (left/right None);
    # once split() succeeds it becomes an internal node with two children.
    def __init__(self, region: Rect):
        self.region = region
        self.left = None    # child node after split, else None
        self.right = None   # child node after split, else None
        self.room = None    # only ever set on leaf nodes, via carve_room()

    @property
    def is_leaf(self):
        return self.left is None and self.right is None

    def split(self, min_size = MIN_SIZE):
        # Already split -> nothing to do.
        if self.is_leaf != True:
            return False

        # min_size * 2 because both halves produced by the cut need to be
        # at least min_size each.
        can_split_horizontally = self.region.rect_height >= min_size * 2
        can_split_vertically = self.region.rect_width >= min_size * 2

        # Too small either way -> this region becomes a permanent leaf.
        if not can_split_horizontally and not can_split_vertically:
            return False

        # Bias toward splitting the longer axis so regions stay closer to
        # square instead of degenerating into thin slivers.
        if can_split_horizontally and can_split_vertically:
           split_horizontally = self.region.rect_height > self.region.rect_width
        else:
            split_horizontally = can_split_horizontally

        if split_horizontally:
            # Cut is a random y-coordinate strictly between the region's top and bottom edges 
            # Kept at least min_size away from each, so neither half ends up too small)
            cut = random.randint(self.region.y_rect_top_left_corner + min_size,
                                 self.region.y_rect_bottom_left_corner - min_size)
            
            # Self.left becomes the top rectangle: same x/width as the parent
            # Starting at the parent's top y, with height = cut - y 
            # Spans from the top down to the cut line
            self.left = BSPNode(Rect(self.region.x_rect_top_left_corner, 
                                     self.region.y_rect_top_left_corner,
                                     self.region.rect_width,
                                     cut - self.region.y_rect_top_left_corner))
            
            # Self.right becomes the bottom rectangle: same x/width
            # Starting at y = cut, with height = y2 - cut 
            # Spans from the cut line down to the parent's original bottom edge
            self.right = BSPNode(Rect(self.region.x_rect_top_left_corner, 
                                     cut,
                                     self.region.rect_width,
                                     self.region.y_rect_bottom_left_corner - cut))
        
        else:
            # Cut is a random x-coordinate strictly between the region's left and right edges 
            # Kept min_size away from each, so neither half is too small

            cut = random.randint(self.region.x_rect_top_left_corner + min_size,
                                 self.region.x_rect_top_right_corner - min_size)
            
            # Self.left becomes the left rectangle: same y/height as the parent
            # Starting at the parent's left x, with width = cut - x 
            # Spans from the left edge over to the cut line
            self.left = BSPNode(Rect(self.region.x_rect_top_left_corner, 
                                     self.region.y_rect_top_left_corner,
                                     cut - self.region.x_rect_top_left_corner,
                                     self.region.rect_height))
             
            # Self.right becomes the right rectangle: same y/height
            # Starting at x = cut, with width = x2 - cut 
            # Spans from the cut line over to the parent's original right edge
            self.right = BSPNode(Rect(cut,
                                     self.region.y_rect_top_left_corner,
                                     self.region.x_rect_top_right_corner - cut,
                                     self.region.rect_height))
        return True

    def carve_room(self, room_id: int, margin=2):
        # Only leaves get rooms.
        if not self.is_leaf:
            return None

        # Shrink the region inward on all sides by margin. This gap is what
        # guarantees a wall between any two adjacent rooms.
        inner_x = self.region.x_rect_top_left_corner + margin
        inner_y = self.region.y_rect_top_left_corner + margin
        inner_width = self.region.rect_width - (margin * 2)
        inner_height = self.region.rect_height - (margin * 2)

        # Margin ate all the usable space -> no room fits here.
        if inner_width < 3 or inner_height < 3:
            return None

        # Room size: somewhere between half the inner area and the full
        # inner area, so rooms vary instead of always filling their leaf.
        room_width = random.randint(max(3, inner_width // 2), inner_width)
        room_height = random.randint(max(3, inner_height // 2), inner_height)

        # Random position within the inner bounds that still fits the room.
        room_x = random.randint(inner_x, inner_x + inner_width - room_width)
        room_y = random.randint(inner_y, inner_y + inner_height - room_height)

        self.room = Room(rect=Rect(room_x, room_y, room_width, room_height), id=room_id)
        return self.room

    def get_room(self):
        """Return any one room from this subtree (random pick if both children have one)."""
        if self.is_leaf:
            return self.room

        left_room = self.left.get_room() if self.left else None
        right_room = self.right.get_room() if self.right else None
        if left_room and right_room:
            return random.choice([left_room, right_room])
        return left_room or right_room

    def get_all_corridors(self):
        # Bottom-up: collect corridors from both subtrees first, then connect
        # one room from the left subtree to one from the right. Every
        # internal node does this, so the whole tree ends up connected --
        # no room can be left isolated.
        corridors = []
        if not self.is_leaf:
            corridors += self.left.get_all_corridors()
            corridors += self.right.get_all_corridors()

            a = self.left.get_room()
            b = self.right.get_room()

            if a and b:
                ax, ay = a.center
                bx, by = b.center

                # Coin flip decides the L-shape's bend: horizontal-then-vertical
                # vs. vertical-then-horizontal, so corridors don't all bend
                # the same way.
                if random.random() < 0.5:
                    bend = (bx, ay)
                else:
                    bend = (ax, by)
                corridors.append(Corridor(center_room_A=(ax, ay), center_room_B=(bx, by),center_L_shaped_corner=bend))
        return corridors