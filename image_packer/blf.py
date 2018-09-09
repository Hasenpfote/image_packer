#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import math
import sys


__all__ = ['Piece', 'Rect', 'solve', 'LocationNotFoundError']


class Piece(object):
    '''This class represents input information.'''
    def __init__(self, uid, width, height):
        self._uid = uid
        self._width = width
        self._height = height

    @property
    def uid(self):
        return self._uid

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def area(self):
        return self._width * self._height


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


class Rect(object):
    '''This class represents a rectangle in an integer coordinate system.'''
    def __init__(self, uid, x, y, width, height):
        self.uid = uid
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    @property
    def area(self):
        return self.width * self.height

    @property
    def top(self):
        return self.y + self.height

    @property
    def bottom(self):
        return self.y

    @property
    def left(self):
        return self.x

    @property
    def right(self):
        return self.x + self.width


def is_colliding(stable_point, current, others):
    '''Whether the rectangle on the stable point is in collide with another rectangles.

    Args:
        stable_point (:class:`StablePoint`):
        current (:class:`Rect`):
        others (list(:class:`Rect`)):

    Returns:
        True if colliding, False otherwise.
    '''
    for other in others:
        if stable_point.x >= other.right:
            continue
        if (stable_point.x + current.width) <= other.left:
            continue
        if stable_point.y >= other.top:
            continue
        if (stable_point.y + current.height) <= other.bottom:
            continue

        return True

    return False


class LocationNotFoundError(Exception):
    '''Raised when a location is not found.'''
    pass


def run_step(stable_points, current, others, container_width):
    '''Run one iteration.

    Args:
        stable_points (list(:class:`StablePoint`)):
        current (:class:`Rect`):
        others (list(:class:`Rect`)):
        container_width (int):
    '''
    min_x, min_y = sys.maxsize, sys.maxsize
    last_used_id = None
   
    for i, point in enumerate(stable_points):
        if (current.width <= point.gap_width) or (current.height <= point.gap_height):
            continue

        if (point.x < 0) or (point.y < 0) or (point.x + current.width > container_width):
            continue

        if is_colliding(point, current, others):
            continue

        # Update the location.
        if (point.y < min_y) or (point.y == min_y and point.x < min_x):
            last_used_id = i
            min_x = point.x
            min_y = point.y

    # Is it possible to place the current rectangle?
    if (min_x < sys.maxsize) and (min_y < sys.maxsize):
        current.x = min_x
        current.y = min_y
    else:
        raise LocationNotFoundError

    # Remove the applied point from the list.
    if last_used_id is not None:
        del stable_points[last_used_id]

    # Add a candidate for BL stable point.
    # This newly occurred by the current rectangle and the container.
    stable_points.append(
        StablePoint(x=current.right, y=0, gap_width=0, gap_height=current.bottom)
    )
    stable_points.append(
        StablePoint(x=0, y=current.top, gap_width=current.left, gap_height=0)
    )

    # Add a candidate for BL stable point.
    # This newly occurred by the current rectangle and other rectangles.
    for other in others:
        # When the current rectangle is to the left side of the other rectangle.
        if (current.right <= other.left) and (current.top > other.top):
            x = current.right
            y = other.top
            w = other.left - current.right
            if current.bottom > other.top:
                h = current.bottom - other.top
            else:
                h = 0
            stable_points.append(StablePoint(x=x, y=y, gap_width=w, gap_height=h))
        # When the current rectangle is to the right side of the other rectangle.
        if (current.left >= other.right) and (current.top < other.top):
            x = other.right
            y = current.top
            w = current.left - other.right
            if other.bottom > current.top:
                h = other.bottom - current.top
            else:
                h = 0
            stable_points.append(StablePoint(x=x, y=y, gap_width=w, gap_height=h))
        # When the current rectangle is to the lower side of the other rectangle.
        if (current.top <= other.bottom) and (current.right > other.right):
            x = other.right
            y = current.top
            if current.left > other.right:
                w = current.left - other.right
            else:
                w = 0
            h = other.bottom - current.top
            stable_points.append(StablePoint(x=x, y=y, gap_width=w, gap_height=h))
        # When the current rectangle is to the upper side of the other rectangle.
        if (current.bottom >= other.top) and (current.right < other.right):
            x = current.right
            y = other.top
            if other.left > current.right:
                w = other.left - current.right
            else:
                w = 0
            h = current.bottom - other.top
            stable_points.append(StablePoint(x=x, y=y, gap_width=w, gap_height=h))


def run(pieces, container_width):
    '''Run all iterations.

    Args:
        pieces (list(:class:`Piece`)):
        container_width (int):

    Returns:
        list(:class:`Rect`)
    '''
    stable_points = list()
    stable_points.append(StablePoint())

    rects = [Rect(uid=piece.uid, x=0, y=0, width=piece.width, height=piece.height) for piece in pieces]

    for i, current in enumerate(rects):
        run_step(stable_points, current, rects[0:i], container_width)

    return rects


def next_power_of_2(x):
    return 2.0 ** math.ceil(math.log2(x))


def calc_minimum_container_size(rects):
    '''Calculate a minimum container size from rectangles.'''
    width = 0
    height = 0
    for rect in rects:
        if rect.right > width:
            width = rect.right
        if rect.top > height:
            height = rect.top

    return width, height


def calc_container_size(container_width, rects, enable_auto_size, force_pow2):
    '''Calculate a container size.'''
    if enable_auto_size:
        width, height = calc_minimum_container_size(rects)
    else:
        width = container_width
        _, height = calc_minimum_container_size(rects)

    if force_pow2:
        width = int(next_power_of_2(width))
        height = int(next_power_of_2(height))

    return width, height


def calc_filling_rate(container_width, container_height, rects):
    '''Calculate a filling rate.'''
    area = sum(rect.area for rect in rects)
    return area / (container_width * container_height)


def solver1(pieces, container_width, enable_auto_size, force_pow2):
    '''Inputs are sorted in descending order of height before execution.'''
    pieces.sort(key=lambda piece: -piece.height)
    rects = run(pieces, container_width)
    width, height = calc_container_size(
        container_width=container_width,
        rects=rects,
        enable_auto_size=enable_auto_size,
        force_pow2=force_pow2
    )
    filling_rate = calc_filling_rate(width, height, rects)

    return filling_rate, width, height, rects


def solver2(pieces, container_width, enable_auto_size, force_pow2):
    '''Inputs are sorted in descending order of area before execution.'''
    pieces.sort(key=lambda piece: -piece.area)
    rects = run(pieces, container_width)
    width, height = calc_container_size(
        container_width=container_width,
        rects=rects,
        enable_auto_size=enable_auto_size,
        force_pow2=force_pow2
    )
    filling_rate = calc_filling_rate(width, height, rects)

    return filling_rate, width, height, rects


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
        tuple(container_width, container_height, rects)
    '''
    if enable_auto_size:
        max_width = max(pieces, key=lambda piece: piece.width).width
        if container_width < max_width:
            container_width = max_width

    if force_pow2:
        container_width = int(next_power_of_2(container_width))

    best_filling_rate = -1.0
    result = (0, 0, None)
    for solver in (solver1, solver2):
        filling_rate, width, height, rects = solver(
            pieces=pieces,
            container_width=container_width,
            enable_auto_size=enable_auto_size,
            force_pow2=force_pow2
        )
        if filling_rate > best_filling_rate:
            best_filling_rate = filling_rate
            result = (width, height, rects)

    return result
