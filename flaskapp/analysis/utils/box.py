"""Utility class to interact with sections of an image as a box."""

from typing import List, Sequence
from itertools import combinations


class Box(object):
    """
    Box object that represent portions of text found
    in an image
    """

    def __init__(self,
                 x: int,
                 y: int,
                 width: int,
                 height: int):
        """
        initialise Box object with (x,y) being the coordinates
        of its top left corner, and its width/height
        """
        self.top_left_x = x
        self.top_left_y = y
        self.width = width
        self.height = height

    @property
    def area(self):
        return self.width * self.height

    @property
    def top_right_x(self):
        return self.top_left_x + self.width

    @property
    def top_right_y(self):
        return self.top_left_y

    @property
    def bottom_left_x(self):
        return self.top_left_x

    @property
    def bottom_left_y(self):
        return self.top_left_y + self.height

    @property
    def bottom_right_x(self):
        return self.top_right_x

    @property
    def bottom_right_y(self):
        return self.bottom_left_y

    @property
    def top_left(self):
        return self.top_left_x, self.top_left_y

    @property
    def bottom_left(self):
        return self.bottom_left_x, self.bottom_left_y

    @property
    def top_right(self):
        return self.top_right_x, self.top_right_y

    @property
    def bottom_right(self):
        return self.bottom_right_x, self.bottom_right_y

    @property
    def aspect_ratio(self):
        return self.width / self.height

    @property
    def is_mrz(self):
        # TODO: have better way of guessing?
        return self.aspect_ratio > 5

    def scale(self,
              fx: float,
              fy: float,
              max_width: int,
              max_height: int):
        """
        Function to expand the box by a certain scale.
        Limit the expansion of the box to be within the image border
        """
        width = round(self.width * fx)
        height = round(self.height * fy)
        x = round(self.top_left_x + (self.width - width) / 2)
        y = round(self.top_left_y + (self.height - height) / 2)

        return Box(x=max(x, 0),
                   y=max(y, 0),
                   width=min(width, max_width),
                   height=min(height, max_height)
                   )

    def overlap(self, other) -> bool:
        """
        Function to determine whether two boxes overlap
        """
        # coordinates of intersecting area, if there is an overlap
        top_left_x = max(self.top_left_x, other.top_left_x)
        top_left_y = max(self.top_left_y, other.top_left_y)
        bottom_right_x = min(self.bottom_right_x, other.bottom_right_x)
        bottom_right_y = min(self.bottom_right_y, other.bottom_right_y)

        # height/width of intersecting area, if there is an overlap
        width = bottom_right_x - top_left_x
        height = bottom_right_y - top_left_y

        return width > 0 and height > 0

    def contains(self, other) -> bool:
        return self.overlap(other) and self.merge(other).area == max(self.area, other.area)

    def near(self,
             other,
             v_thresh: int,
             h_thresh: int) -> bool:
        """
        Function to determine whether two boxes are
        close enough either vertically or horizontally
        to be merged together, where close enough depends
        on whether the distance between two boxes
        are less than the vertical/horizontal thresholds

        Case 1:
        -------------  -----------          --------------------------
        |           |  |         |  -->     |                        |
        -------------  -----------          --------------------------

        Case 2:
        -------------       -------------
        |           |       |           |
        -------------       |           |
                       -->  |           |
        -------------       |           |
        |           |       |           |
        -------------       _____________

        Case 3:
        ---------
        |       |
        ---------       --> not near
              ---------
              |       |
              ---------

        """
        return ((abs(self.bottom_left_y - other.bottom_left_y) < h_thresh and  # Case 1
                 abs(self.top_left_y - other.top_left_y) < h_thresh and
                 (max(self.bottom_right_x, other.bottom_right_x) -
                  min(self.bottom_left_x, other.bottom_left_x) <
                  self.width + other.width + h_thresh)
                 )
                or
                (abs(self.bottom_left_x - other.bottom_left_x) < v_thresh and  # Case 2
                 abs(self.bottom_right_x - other.bottom_right_x) < v_thresh and
                 (max(self.bottom_left_y, other.bottom_left_y) -
                  min(self.top_left_y, other.top_left_y) <
                  self.height + other.height + v_thresh)
                 )
                )

    def merge(self, other):
        return Box(x=min(self.bottom_left_x, other.bottom_left_x),
                   y=min(self.top_left_y, other.top_left_y),
                   width=max(self.bottom_right_x, other.bottom_right_x) - min(self.bottom_left_x, other.bottom_left_x),
                   height=max(self.bottom_left_y, other.bottom_left_y) - min(self.top_left_y, other.top_left_y)
                   )


def merge_boxes(boxes: List[Box],
                v_thresh: int,
                h_thresh: int) -> Sequence[Box]:
    """
    Iterate through a sequence of boxes and merge boxes
    that lie within one another, or are close enough to one another.
    """
    contains = [(box1, box2) for (box1, box2) in combinations(boxes, 2) if box1.contains(box2)]

    while contains:
        for (b1, b2) in contains:
            if b1 in boxes and b2 in boxes:
                boxes.append(b1.merge(b2))
                boxes.remove(b1)
                boxes.remove(b2)
        contains = [(box1, box2) for (box1, box2) in combinations(boxes, 2) if box1.contains(box2)]

    near = [(box1, box2) for (box1, box2) in combinations(boxes, 2)
            if box1.near(box2, v_thresh=v_thresh, h_thresh=h_thresh)]

    while near:
        for (b1, b2) in near:
            if b1 in boxes and b2 in boxes:
                boxes.append(b1.merge(b2))
                boxes.remove(b1)
                boxes.remove(b2)
        near = [(box1, box2) for (box1, box2) in combinations(boxes, 2)
                if box1.near(box2, v_thresh=v_thresh, h_thresh=h_thresh)]
    return boxes
