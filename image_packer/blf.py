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


class CorrectionInfo(object):
    '''The CorrectionInfo class encapsulates the correction information caused by a margin.'''
    def __init__(self, margin, collapse_margin=False):
        self._margin = margin
        self._h_spacing = margin.left + margin.right
        self._v_spacing = margin.bottom + margin.top

        if collapse_margin:
            self._h_overlap = margin.left if margin.left < margin.right else margin.right
            self._v_overlap = margin.bottom if margin.bottom < margin.top else margin.top
        else:
            self._h_overlap, self._v_overlap = 0, 0

        self._offset_x = self._h_spacing - self._h_overlap
        self._offset_y = self._v_spacing - self._v_overlap
        self._offset_w = - self._h_spacing + self._h_overlap * 2
        self._offset_h = - self._v_spacing + self._v_overlap * 2

    @property
    def margin(self):
        return self._margin

    @property
    def horizontal_spacing(self):
        return self._h_spacing

    @property
    def vertical_spacing(self):
        return self._v_spacing

    @property
    def horizontal_overlap(self):
        return self._h_overlap

    @property
    def vertical_overlap(self):
        return self._v_overlap

    @property
    def offset_x(self):
        return self._offset_x

    @property
    def offset_y(self):
        return self._offset_y

    @property
    def offset_width(self):
        return self._offset_w

    @property
    def offset_height(self):
        return self._offset_h


def next_power_of_2(x):
    return 2.0 ** math.ceil(math.log2(x))


def find_point_index(
    stable_points,
    current_size,
    other_regions,
    container_width,
    correction_info
):
    '''Find a BL point index.'''
    margin = correction_info.margin
    h_spacing = correction_info.horizontal_spacing
    v_spacing = correction_info.vertical_spacing
    offset_x = correction_info.offset_x
    offset_y = correction_info.offset_y

    min_x, min_y = sys.maxsize, sys.maxsize
    last_used_id = None

    for i, point in enumerate(stable_points):
        if (current_size.width + h_spacing <= point.gap_width) \
                or (current_size.height + v_spacing <= point.gap_height):
            continue

        if (point.x < 0) or (point.y < 0) \
                or (point.x + current_size.width + margin.right > container_width):
            continue

        # Whether the rectangle on the stable point is in collide with another rectangles.
        is_colliding = False
        for other_region in other_regions:
            if (point.x - offset_x) >= other_region.right:
                continue
            if (point.x + current_size.width + offset_x) <= other_region.left:
                continue
            if (point.y - offset_y) >= other_region.top:
                continue
            if (point.y + current_size.height + offset_y) <= other_region.bottom:
                continue
            is_colliding = True
            break

        if is_colliding:
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
    correction_info
):
    '''Generate stable points.'''
    margin = correction_info.margin
    h_overlap = correction_info.horizontal_overlap
    v_overlap = correction_info.vertical_overlap
    offset_x = correction_info.offset_x
    offset_y = correction_info.offset_y
    offset_w = correction_info.offset_width
    offset_h = correction_info.offset_height

    stable_points = list()

    # Add a candidate for BL stable point.
    # This newly occurred by the current rectangle and the container.
    stable_points.append(
        StablePoint(
            x=current_region.right + offset_x,
            y=0 + margin.bottom,
            gap_width=0,
            gap_height=current_region.bottom - margin.bottom + v_overlap
        )
    )
    stable_points.append(
        StablePoint(
            x=0 + margin.left,
            y=current_region.top + offset_y,
            gap_width=current_region.left - margin.left + h_overlap,
            gap_height=0
        )
    )

    # Add a candidate for BL stable point.
    # This newly occurred by the current rectangle and other rectangles.
    for other_region in other_regions:
        # When the current rectangle is to the left side of the other rectangle.
        if ((current_region.right + offset_x) <= other_region.left) \
                and (current_region.top > other_region.top):
            x = current_region.right + offset_x
            y = other_region.top + offset_y
            w = other_region.left - current_region.right + offset_w
            if (current_region.bottom + offset_h) > other_region.top:
                h = current_region.bottom - other_region.top + offset_h
            else:
                h = 0
            stable_points.append(StablePoint(x=x, y=y, gap_width=w, gap_height=h))
        # When the current rectangle is to the right side of the other rectangle.
        elif ((current_region.left - offset_x) >= other_region.right) \
                and (current_region.top < other_region.top):
            x = other_region.right + offset_x
            y = current_region.top + offset_y
            w = current_region.left - other_region.right + offset_w
            if (current_region.top - offset_h) < other_region.bottom:
                h = other_region.bottom - current_region.top + offset_h
            else:
                h = 0
            stable_points.append(StablePoint(x=x, y=y, gap_width=w, gap_height=h))
        # When the current rectangle is to the lower side of the other rectangle.
        elif ((current_region.top + offset_y) <= other_region.bottom) \
                and (current_region.right > other_region.right):
            x = other_region.right + offset_x
            y = current_region.top + offset_y
            if (current_region.left + offset_w) > other_region.right:
                w = current_region.left - other_region.right + offset_w
            else:
                w = 0
            h = other_region.bottom - current_region.top + offset_h
            stable_points.append(StablePoint(x=x, y=y, gap_width=w, gap_height=h))
        # When the current rectangle is to the upper side of the other rectangle.
        elif ((current_region.bottom - offset_y) >= other_region.top) \
                and (current_region.right < other_region.right):
            x = current_region.right + offset_x
            y = other_region.top + offset_y
            if (current_region.right - offset_w) < other_region.left:
                w = other_region.left - current_region.right + offset_w
            else:
                w = 0
            h = current_region.bottom - other_region.top + offset_h
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

    correction_info = CorrectionInfo(
        margin=margin,
        collapse_margin=options.get('collapse_margin', False)
    )

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
            correction_info=correction_info
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
            correction_info=correction_info
        )
        stable_points.extend(new_stable_points)
        regions.append(new_region)

    return container_width, regions
