#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import os
from concurrent import futures
from . import blf


__all__ = ['solve']

logger = logging.getLogger(__name__)


def calc_minimum_container_size(regions, margin):
    '''Calculate a minimum container size from rectangles.'''
    max_width, max_height = 0, 0
    for region in regions:
        if region.right > max_width:
            max_width = region.right
        if region.top > max_height:
            max_height = region.top

    return blf.Size(max_width + margin.right, max_height + margin.top)


def calc_container_size(container_width, regions, margin, enable_auto_size, force_pow2):
    '''Calculate a container size.'''
    size = calc_minimum_container_size(regions, margin)
    if enable_auto_size:
        width, height = size.width, size.height
    else:
        width, height = container_width, size.height

    if force_pow2:
        width = int(blf.next_power_of_2(width))
        height = int(blf.next_power_of_2(height))

    return blf.Size(width, height)


def calc_filling_rate(container_size, regions):
    '''Calculate a filling rate.'''
    area = sum(region.area for region in regions)
    return area / container_size.area


def solver1(pieces, container_width, options):
    '''Inputs are sorted in descending order of height before execution.'''
    pieces.sort(key=lambda piece: -piece.size.height)
    container_width, regions = blf.blf(pieces, container_width, options)
    container_size = calc_container_size(
        container_width=container_width,
        regions=regions,
        margin=options['margin'],
        enable_auto_size=options['enable_auto_size'],
        force_pow2=options['force_pow2']
    )
    filling_rate = calc_filling_rate(container_size, regions)

    return filling_rate, container_size, regions


def solver2(pieces, container_width, options):
    '''Inputs are sorted in descending order of area before execution.'''
    pieces.sort(key=lambda piece: -piece.size.area)
    container_width, regions = blf.blf(pieces, container_width, options)
    container_size = calc_container_size(
        container_width=container_width,
        regions=regions,
        margin=options['margin'],
        enable_auto_size=options['enable_auto_size'],
        force_pow2=options['force_pow2']
    )
    filling_rate = calc_filling_rate(container_size, regions)

    return filling_rate, container_size, regions


def solver3(pieces, container_width, options):
    '''Inputs are sorted in descending order of height and width before execution.'''
    pieces.sort(key=lambda piece: (-piece.size.height, -piece.size.width))
    container_width, regions = blf.blf(pieces, container_width, options)
    container_size = calc_container_size(
        container_width=container_width,
        regions=regions,
        margin=options['margin'],
        enable_auto_size=options['enable_auto_size'],
        force_pow2=options['force_pow2']
    )
    filling_rate = calc_filling_rate(container_size, regions)

    return filling_rate, container_size, regions


def solve(
    pieces,
    container_width,
    options=None
):
    '''Obtain the highest filling rate result.

    Args:
        pieces (list(:class:`Piece`)):
        container_width (int):
        options (dict):

    Returns:
        container_width, container_height, list(:class:`Region`)
    '''
    default_options = {
        'margin': blf.Thickness(0, 0, 0, 0),
        'collapse_margin': False,
        # If true, the size will be adjusted automatically.
        'enable_auto_size': True,
        # If true, the power-of-two rule is forced.
        'force_pow2': False
    }

    if options is None:
        options = default_options
    else:
        options = {key: options[key] if key in options else default_options[key] for key in default_options.keys()}

    solvers = (solver1, solver2, solver3)
    best_filling_rate = -1.0
    result = (0, 0, None)

    if len(pieces) < 100:
        for solver in solvers:
            filling_rate, container_size, regions = solver(
                pieces=pieces,
                container_width=container_width,
                options=options
            )
            logger.debug(
                'Result of {}: fl={}, w={}, h={}'.format(
                    solver.__name__, filling_rate, container_size.width, container_size.height)
            )
            if filling_rate > best_filling_rate:
                best_filling_rate = filling_rate
                result = (container_size.width, container_size.height, regions)
    else:
        max_workers = min(os.cpu_count(), len(solvers))
        with futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
            future_to_name = {
                executor.submit(
                    solver,
                    pieces=pieces,
                    container_width=container_width,
                    options=options
                ): solver.__name__
                for solver in solvers
            }
            for future in futures.as_completed(future_to_name):
                filling_rate, container_size, regions = future.result()
                logger.debug(
                    'Result of {}: fl={}, w={}, h={}'.format(
                        future_to_name[future], filling_rate, container_size.width, container_size.height)
                )
                if filling_rate > best_filling_rate:
                    best_filling_rate = filling_rate
                    result = (container_size.width, container_size.height, regions)

    logger.debug('Final result: fl={}, w={}, h={}'.format(best_filling_rate, result[0], result[1]))

    return result
