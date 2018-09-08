#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
        stable_points (list(:class:`StablePoint`)):
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


def solve(pieces, container_width):
    '''Obtain the highest filling rate result.

    Args:
        pieces (list(:class:`Piece`)):
        container_width (int):

    Returns:
        tuple(container_width, container_height, rects)
    '''
    # 指定の幅より大きい長方形がある場合を考慮
    max_width = max(pieces, key=lambda piece: piece.width).width
    if container_width < max_width:
        container_width = max_width

    results = list()

    # 一回目
    pieces.sort(key=lambda piece: -piece.area)
    rects = run(pieces, container_width)

    container_height = 0
    for rect in rects:
        if rect.top > container_height:
            container_height = rect.top

    area = sum(rect.area for rect in rects)
    filling_rate = area / (container_width * container_height)

    results.append((rects, container_height, filling_rate))

    # 二回目
    pieces.sort(key=lambda piece: -piece.height)
    rects = run(pieces, container_width)
    

    container_height = 0
    for rect in rects:
        if rect.top > container_height:
            container_height = rect.top

    area = sum(rect.area for rect in rects)
    filling_rate = area / (container_width * container_height)

    results.append((rects, container_height, filling_rate))

    # 充填率の降順で並び替え
    results.sort(key=lambda result: -result[2])

    return container_width, results[0][1], results[0][0]
