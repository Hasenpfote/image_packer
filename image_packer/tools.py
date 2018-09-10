#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import colorsys
import random
from PIL import Image


__all__ = [
    'make_random_png24_files',
    'make_random_png32_files',
    'make_random_bmp_files',
    'make_random_jpeg_files',
]


def gen_distinct_colors(num_colors):
    '''Generate distinct colors.'''
    def hsv_to_rgb(h, s, v):
        (r, g, b) = colorsys.hsv_to_rgb(h, s, v)
        return int(r * 255), int(g * 255), int(b * 255)

    hue_partition = 1.0 / (num_colors + 1)
    return (hsv_to_rgb(value * hue_partition, 1.0, 1.0) for value in range(0, num_colors))


def make_random_image_files(
    extension,
    mode,
    width,
    height,
    num_files,
    dirpath
):
    '''Make random image files.'''
    # Ensure plugins are fully loaded so that Image.EXTENSION is populated.
    Image.init()

    format_ = Image.EXTENSION[extension]

    if isinstance(width, tuple):
        min_width, max_width = width
    else:
        min_width, max_width = width, width

    if isinstance(height, tuple):
        min_height, max_height = height
    else:
        min_height, max_height = height, height

    for color in gen_distinct_colors(num_files):
        w = random.randint(min_width, max_width)
        h = random.randint(min_height, max_height)
        image = Image.new(mode=mode, size=(w, h), color=color)
        filename = '{r:02x}{g:02x}{b:02x}_{suffix}{extension}'.format(
            r=color[0],
            g=color[1],
            b=color[2],
            suffix=mode.lower(),
            extension=extension
        )
        image.save(fp=dirpath + '/' + filename, format=format_)


def make_random_png24_files(width, height, num_files, dirpath):
    make_random_image_files(
        extension='.png',
        mode='RGB',
        width=width,
        height=height,
        num_files=num_files,
        dirpath=dirpath
    )


def make_random_png32_files(width, height, num_files, dirpath):
    make_random_image_files(
        extension='.png',
        mode='RGBA',
        width=width,
        height=height,
        num_files=num_files,
        dirpath=dirpath
    )


def make_random_bmp_files(width, height, num_files, dirpath):
    make_random_image_files(
        extension='.bmp',
        mode='RGB',
        width=width,
        height=height,
        num_files=num_files,
        dirpath=dirpath
    )


def make_random_jpeg_files(width, height, num_files, dirpath):
    make_random_image_files(
        extension='.jpg',
        mode='RGB',
        width=width,
        height=height,
        num_files=num_files,
        dirpath=dirpath
    )
