#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import math
import sys


__all__ = [
    'Size',
    'Thickness',
    'Piece',
    'Region',
    'next_power_of_2',
    'blf',
    'LocationNotFoundError'
]


class Size(object):
    '''The Size class encapsulates the width and height of a component in a single object.'''
    def __init__(self, width, height):
        self._width = width
        self._height = height

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def area(self):
        return self._width * self._height


class Thickness(object):
    '''This class represents the thickness of a frame around a rectangle.'''
    def __init__(self, top, right, bottom, left):
        self._top = top
        self._right = right
        self._bottom = bottom
        self._left = left

    @property
    def top(self):
        return self._top

    @property
    def right(self):
        return self._right

    @property
    def bottom(self):
        return self._bottom

    @property
    def left(self):
        return self._left


class Piece(object):
    '''This class represents input information.'''
    def __init__(self, uid, size):
        self._uid = uid
        self._size = size

    @property
    def uid(self):
        return self._uid

    @property
    def size(self):
        return self._size


class StablePoint(object):
    '''This class represents a BL stable point.'''
    def __init__(self, x=0, y=0, gap_width=0, gap_height=0):
        self._x = x
        self._y = y
        self._gap_width = gap_width
        self._gap_height = gap_height

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def gap_width(self):
        return self._gap_width

    @property
    def gap_height(self):
        return self._gap_height


class Region(object):
    '''This class represents a rectangle in an integer coordinate system.'''
    def __init__(self, uid, top, right, bottom, left):
        self._uid = uid
        self._top = top
        self._right = right
        self._bottom = bottom
        self._left = left

    @property
    def uid(self):
        return self._uid

    @property
    def top(self):
        return self._top

    @property
    def right(self):
        return self._right

    @property
    def bottom(self):
        return self._bottom

    @property
    def left(self):
        return self._left

    @property
    def width(self):
        return self._right - self._left

    @property
    def height(self):
        return self._top - self._bottom

    @property
    def area(self):
        return self.width * self.height

    @classmethod
    def from_position_and_size(cls, uid, x, y, width, height):
        return cls(uid=uid, top=y + height, right=x + width, bottom=y, left=x)


class LocationNotFoundError(Exception):
    '''Raised when a location is not found.'''
    pass


def next_power_of_2(x):
    return 2.0 ** math.ceil(math.log2(x))


def is_colliding(
    stable_point,
    current_size,
    other_regions,
    margin
):
    '''Whether the rectangle on the stable point is in collide with another rectangles.

    Args:
        stable_point (:class:`StablePoint`):
        current_size (:class:`Size`):
        other_regions (list(:class:`Region`)):

    Returns:
        True if colliding, False otherwise.
    '''
    h_spacing = margin.left + margin.right
    v_spacing = margin.bottom + margin.top

    for other_region in other_regions:
        if (stable_point.x - h_spacing) >= other_region.right:
            continue
        if (stable_point.x + current_size.width + h_spacing) <= other_region.left:
            continue
        if (stable_point.y - v_spacing) >= other_region.top:
            continue
        if (stable_point.y + current_size.height + v_spacing) <= other_region.bottom:
            continue

        return True

    return False


def find_point_index(
    stable_points,
    current_size,
    other_regions,
    container_width,
    margin
):
    '''Find a BL point index.'''
    h_spacing = margin.left + margin.right
    v_spacing = margin.bottom + margin.top

    min_x, min_y = sys.maxsize, sys.maxsize
    last_used_id = None

    for i, point in enumerate(stable_points):
        if (current_size.width + h_spacing <= point.gap_width) \
                or (current_size.height + v_spacing <= point.gap_height):
            continue

        if (point.x < 0) or (point.y < 0) \
                or (point.x + current_size.width + margin.right > container_width):
            continue

        if is_colliding(
                stable_point=point,
                current_size=current_size,
                other_regions=other_regions,
                margin=margin
        ):
            continue

        # Update the location.
        if (point.y < min_y) or (point.y == min_y and point.x < min_x):
            min_x = point.x
            min_y = point.y
            last_used_id = i

    if last_used_id is None:
        raise LocationNotFoundError

    return last_used_id


def generate_stable_points(
    current_region,
    other_regions,
    margin
):
    '''Generate stable points.'''
    h_spacing = margin.left + margin.right
    v_spacing = margin.bottom + margin.top

    stable_points = list()

    # Add a candidate for BL stable point.
    # This newly occurred by the current rectangle and the container.
    stable_points.append(
        StablePoint(
            x=current_region.right + h_spacing,
            y=0 + margin.bottom,
            gap_width=0,
            gap_height=current_region.bottom - margin.bottom
        )
    )
    stable_points.append(
        StablePoint(
            x=0 + margin.left,
            y=current_region.top + v_spacing,
            gap_width=current_region.left - margin.left,
            gap_height=0
        )
    )

    # Add a candidate for BL stable point.
    # This newly occurred by the current rectangle and other rectangles.
    for other_region in other_regions:
        # When the current rectangle is to the left side of the other rectangle.
        if ((current_region.right + h_spacing) <= other_region.left) \
                and (current_region.top > other_region.top):
            x = current_region.right + h_spacing
            y = other_region.top + v_spacing
            w = other_region.left - current_region.right - h_spacing
            if (current_region.bottom - v_spacing) > other_region.top:
                h = current_region.bottom - other_region.top - v_spacing
            else:
                h = 0
            stable_points.append(StablePoint(x=x, y=y, gap_width=w, gap_height=h))
        # When the current rectangle is to the right side of the other rectangle.
        if ((current_region.left - h_spacing) >= other_region.right) \
                and (current_region.top < other_region.top):
            x = other_region.right + h_spacing
            y = current_region.top + v_spacing
            w = current_region.left - other_region.right - h_spacing
            if other_region.bottom > (current_region.top + v_spacing):
                h = other_region.bottom - current_region.top - v_spacing
            else:
                h = 0
            stable_points.append(StablePoint(x=x, y=y, gap_width=w, gap_height=h))
        # When the current rectangle is to the lower side of the other rectangle.
        if ((current_region.top + v_spacing) <= other_region.bottom) \
                and (current_region.right > other_region.right):
            x = other_region.right + h_spacing
            y = current_region.top + v_spacing
            if (current_region.left - h_spacing) > other_region.right:
                w = current_region.left - other_region.right - h_spacing
            else:
                w = 0
            h = other_region.bottom - current_region.top - v_spacing
            stable_points.append(StablePoint(x=x, y=y, gap_width=w, gap_height=h))
        # When the current rectangle is to the upper side of the other rectangle.
        if ((current_region.bottom - v_spacing) >= other_region.top) \
                and (current_region.right < other_region.right):
            x = current_region.right + h_spacing
            y = other_region.top + v_spacing
            if other_region.left > (current_region.right + h_spacing):
                w = other_region.left - current_region.right - h_spacing
            else:
                w = 0
            h = current_region.bottom - other_region.top - v_spacing
            stable_points.append(StablePoint(x=x, y=y, gap_width=w, gap_height=h))

    return stable_points


def blf(pieces, container_width, options=None):
    '''Run all iterations.

    Args:
        pieces (list(:class:`Piece`)):
        container_width (int):
        options (dict):

    Returns:
        container_width, list(:class:`Region`)
    '''
    if options is None:
        options = dict()

    margin = options.get('margin', Thickness(0, 0, 0, 0))
    collapse_margin = options.get('collapse_margin', False)

    if options.get('enable_auto_size', True):
        max_width = max(pieces, key=lambda piece: piece.size.width).size.width
        max_width += margin.left + margin.right
        if container_width < max_width:
            container_width = max_width

    if options.get('force_pow2', False):
        container_width = int(next_power_of_2(container_width))

    regions = list()
    stable_points = list()
    stable_points.append(
        StablePoint(
            x=margin.left,
            y=margin.bottom,
            gap_width=0,
            gap_height=0
        )
    )

    for piece in pieces:
        index = find_point_index(
            stable_points=stable_points,
            current_size=piece.size,
            other_regions=regions,
            container_width=container_width,
            margin=margin
        )
        point = stable_points.pop(index)

        new_region = Region.from_position_and_size(
            uid=piece.uid,
            x=point.x,
            y=point.y,
            width=piece.size.width,
            height=piece.size.height
        )
        new_stable_points = generate_stable_points(
            current_region=new_region,
            other_regions=regions,
            margin=margin
        )
        stable_points.extend(new_stable_points)
        regions.append(new_region)

    return container_width, regions
