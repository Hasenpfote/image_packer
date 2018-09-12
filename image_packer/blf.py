#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import math
import sys


__all__ = ['Size', 'Piece', 'BLRect', 'solve', 'LocationNotFoundError']


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


class BLRect(object):
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


def is_colliding(stable_point, current_size, other_rects):
    '''Whether the rectangle on the stable point is in collide with another rectangles.

    Args:
        stable_point (:class:`StablePoint`):
        current_size (:class:`Size`):
        other_rects (list(:class:`BLRect`)):

    Returns:
        True if colliding, False otherwise.
    '''
    for other_rect in other_rects:
        if stable_point.x >= other_rect.right:
            continue
        if (stable_point.x + current_size.width) <= other_rect.left:
            continue
        if stable_point.y >= other_rect.top:
            continue
        if (stable_point.y + current_size.height) <= other_rect.bottom:
            continue

        return True

    return False


def find_point_index(
    stable_points,
    current_size,
    other_rects,
    container_width
):
    '''Find a BL point index.'''
    min_x, min_y = sys.maxsize, sys.maxsize
    last_used_id = None

    for i, point in enumerate(stable_points):
        if (current_size.width <= point.gap_width) or (current_size.height <= point.gap_height):
            continue

        if (point.x < 0) or (point.y < 0) or (point.x + current_size.width > container_width):
            continue

        if is_colliding(stable_point=point, current_size=current_size, other_rects=other_rects):
            continue

        # Update the location.
        if (point.y < min_y) or (point.y == min_y and point.x < min_x):
            min_x = point.x
            min_y = point.y
            last_used_id = i

    if last_used_id is None:
        raise LocationNotFoundError

    return last_used_id


def generate_stable_points(current_rect, other_rects):
    '''Generate stable points.'''
    stable_points = list()

    # Add a candidate for BL stable point.
    # This newly occurred by the current rectangle and the container.
    stable_points.append(
        StablePoint(x=current_rect.right, y=0, gap_width=0, gap_height=current_rect.bottom)
    )
    stable_points.append(
        StablePoint(x=0, y=current_rect.top, gap_width=current_rect.left, gap_height=0)
    )

    # Add a candidate for BL stable point.
    # This newly occurred by the current rectangle and other rectangles.
    for other_rect in other_rects:
        # When the current rectangle is to the left side of the other rectangle.
        if (current_rect.right <= other_rect.left) and (current_rect.top > other_rect.top):
            x = current_rect.right
            y = other_rect.top
            w = other_rect.left - current_rect.right
            if current_rect.bottom > other_rect.top:
                h = current_rect.bottom - other_rect.top
            else:
                h = 0
            stable_points.append(StablePoint(x=x, y=y, gap_width=w, gap_height=h))
        # When the current rectangle is to the right side of the other rectangle.
        if (current_rect.left >= other_rect.right) and (current_rect.top < other_rect.top):
            x = other_rect.right
            y = current_rect.top
            w = current_rect.left - other_rect.right
            if other_rect.bottom > current_rect.top:
                h = other_rect.bottom - current_rect.top
            else:
                h = 0
            stable_points.append(StablePoint(x=x, y=y, gap_width=w, gap_height=h))
        # When the current rectangle is to the lower side of the other rectangle.
        if (current_rect.top <= other_rect.bottom) and (current_rect.right > other_rect.right):
            x = other_rect.right
            y = current_rect.top
            if current_rect.left > other_rect.right:
                w = current_rect.left - other_rect.right
            else:
                w = 0
            h = other_rect.bottom - current_rect.top
            stable_points.append(StablePoint(x=x, y=y, gap_width=w, gap_height=h))
        # When the current rectangle is to the upper side of the other rectangle.
        if (current_rect.bottom >= other_rect.top) and (current_rect.right < other_rect.right):
            x = current_rect.right
            y = other_rect.top
            if other_rect.left > current_rect.right:
                w = other_rect.left - current_rect.right
            else:
                w = 0
            h = current_rect.bottom - other_rect.top
            stable_points.append(StablePoint(x=x, y=y, gap_width=w, gap_height=h))

    return stable_points


def run(pieces, container_width):
    '''Run all iterations.

    Args:
        pieces (list(:class:`Piece`)):
        container_width (int):

    Returns:
        list(:class:`BLRect`)
    '''
    rects = list()
    stable_points = list()
    stable_points.append(StablePoint())

    for piece in pieces:
        current_size = piece.size
        index = find_point_index(
            stable_points=stable_points,
            current_size=current_size,
            other_rects=rects,
            container_width=container_width
        )
        point = stable_points.pop(index)
        rect = BLRect.from_position_and_size(
            uid=piece.uid,
            x=point.x,
            y=point.y,
            width=current_size.width,
            height=current_size.height
        )
        new_stable_points = generate_stable_points(
            current_rect=rect,
            other_rects=rects
        )
        stable_points.extend(new_stable_points)
        rects.append(rect)

    return rects


def next_power_of_2(x):
    return 2.0 ** math.ceil(math.log2(x))


def calc_minimum_container_size(rects):
    '''Calculate a minimum container size from rectangles.'''
    max_width, max_height = 0, 0
    for rect in rects:
        if rect.right > max_width:
            max_width = rect.right
        if rect.top > max_height:
            max_height = rect.top

    return Size(max_width, max_height)


def calc_container_size(container_width, rects, enable_auto_size, force_pow2):
    '''Calculate a container size.'''
    size = calc_minimum_container_size(rects)
    if enable_auto_size:
        width, height = size.width, size.height
    else:
        width, height = container_width, size.height

    if force_pow2:
        width = int(next_power_of_2(width))
        height = int(next_power_of_2(height))

    return Size(width, height)


def calc_filling_rate(container_size, rects):
    '''Calculate a filling rate.'''
    area = sum(rect.area for rect in rects)
    return area / container_size.area


def solver1(pieces, container_width, enable_auto_size, force_pow2):
    '''Inputs are sorted in descending order of height before execution.'''
    pieces.sort(key=lambda piece: -piece.size.height)
    rects = run(pieces, container_width)
    container_size = calc_container_size(
        container_width=container_width,
        rects=rects,
        enable_auto_size=enable_auto_size,
        force_pow2=force_pow2
    )
    filling_rate = calc_filling_rate(container_size, rects)

    return filling_rate, container_size, rects


def solver2(pieces, container_width, enable_auto_size, force_pow2):
    '''Inputs are sorted in descending order of area before execution.'''
    pieces.sort(key=lambda piece: -piece.size.area)
    rects = run(pieces, container_width)
    container_size = calc_container_size(
        container_width=container_width,
        rects=rects,
        enable_auto_size=enable_auto_size,
        force_pow2=force_pow2
    )
    filling_rate = calc_filling_rate(container_size, rects)

    return filling_rate, container_size, rects


def solver3(pieces, container_width, enable_auto_size, force_pow2):
    '''Inputs are sorted in descending order of height and width before execution.'''
    pieces.sort(key=lambda piece: (-piece.size.height, -piece.size.width))
    rects = run(pieces, container_width)
    container_size = calc_container_size(
        container_width=container_width,
        rects=rects,
        enable_auto_size=enable_auto_size,
        force_pow2=force_pow2
    )
    filling_rate = calc_filling_rate(container_size, rects)

    return filling_rate, container_size, rects


def solve(
    pieces,
    container_width,
    enable_auto_size=True,
    force_pow2=False
):
    '''Obtain the highest filling rate result.

    Args:
        pieces (list(:class:`Piece`)):
        container_width (int):
        enable_auto_size (bool): If true, the size will be adjusted automatically.
        force_pow2 (bool): If true, the power-of-two rule is forced.

    Returns:
        tuple(container_width, container_height, list(:class:`BLRect`))
    '''
    if enable_auto_size:
        max_width = max(pieces, key=lambda piece: piece.size.width).size.width
        if container_width < max_width:
            container_width = max_width

    if force_pow2:
        container_width = int(next_power_of_2(container_width))

    best_filling_rate = -1.0
    result = (0, 0, None)
    for solver in (solver1, solver2, solver3):
        filling_rate, container_size, rects = solver(
            pieces=pieces,
            container_width=container_width,
            enable_auto_size=enable_auto_size,
            force_pow2=force_pow2
        )
        if filling_rate > best_filling_rate:
            best_filling_rate = filling_rate
            result = (container_size.width, container_size.height, rects)

    return result
