#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import glob
import os
import sys
import uuid
import warnings
from PIL import Image
from . import blf


ALLOWED_EXTENSIONS = {'.png', '.bmp', '.jpg'}


def extract_filepaths(filepaths, allowed_extensions):
    results = set()
    for filepath in filepaths:
        filepath = os.path.normpath(filepath)
        if '*' in filepath:
            for filepath_ in glob.glob(filepath):
                if os.path.splitext(filepath_)[1] in allowed_extensions:
                    results.add(filepath_)
                else:
                    warnings.warn('The `{}` file has been ignored'.format(filepath_), stacklevel=2)
        else:
            if os.path.splitext(filepath)[1] in allowed_extensions:
                results.add(filepath)
            else:
                warnings.warn('The `{}` file has been ignored'.format(filepath), stacklevel=2)

    return results


def pack(
    input_filepaths,
    output_filepath,
    container_width,
    options=None
):
    '''make a atlas.

    Args:
        input_filepaths (list(str)):
        output_filepath (str):
        container_width (int):
        options (dict):
    '''
    default_options = {
        'margin': (0, 0, 0, 0),
        'collapse_margin': False,
        # If true, the size will be adjusted automatically.
        'enable_auto_size': True,
        # If true, flips the output upside down.
        'enable_vertical_flip': True,
        # If true, the power-of-two rule is forced.
        'force_pow2': False
    }
    if options is None:
        options = default_options
    else:
        options = {key: options[key] if key in options else default_options[key] for key in default_options.keys()}

    # Ensure plugins are fully loaded so that Image.EXTENSION is populated.
    Image.init()

    with warnings.catch_warnings():
        warnings.simplefilter('always')
        input_filepaths = extract_filepaths(
            filepaths=input_filepaths,
            allowed_extensions={ext for ext in ALLOWED_EXTENSIONS if ext in Image.EXTENSION}
        )

    uid_to_filepath = dict()
    pieces = list()
    has_alpha = False

    for filepath in input_filepaths:
        with Image.open(fp=filepath) as im:
            width = im.width
            height = im.height
            uid = uuid.uuid4()
            uid_to_filepath[uid] = filepath
            pieces.append(blf.Piece(uid=uid, size=blf.Size(width, height)))

            if im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info):
                has_alpha = True

    enable_vertical_flip = options['enable_vertical_flip']

    margin_ = options['margin']
    if enable_vertical_flip:
        margin = blf.Thickness(top=margin_[2], right=margin_[1], bottom=margin_[0], left=margin_[3])
    else:
        margin = blf.Thickness(top=margin_[0], right=margin_[1], bottom=margin_[2], left=margin_[3])

    blf_options = {
        'margin': margin,
        'collapse_margin': options['collapse_margin'],
        'enable_auto_size': options['enable_auto_size'],
        'force_pow2': options['force_pow2']
    }

    container_width, container_height, regions = blf.solve(
        pieces=pieces,
        container_width=container_width,
        options=blf_options
    )

    if has_alpha:
        blank_image = Image.new(
            mode='RGBA',
            size=(container_width, container_height),
            color=(0, 0, 0, 255)
        )
    else:
        blank_image = Image.new(
            mode='RGB',
            size=(container_width, container_height),
            color=(0, 0, 0)
        )

    for region in regions:
        x = region.left
        if enable_vertical_flip:
            y = region.bottom
        else:
            y = container_height - region.top
        filepath = uid_to_filepath.get(region.uid)
        with Image.open(filepath) as im:
            blank_image.paste(im=im, box=(x, y))

    blank_image.save(fp=output_filepath, format='PNG')


def main():
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-i',
        '--input',
        type=str,
        action='append',
        required=True,
        help='Setting the input file-path. An asterisk(*) wildcard can also be used.'
    )

    parser.add_argument(
        '-o',
        '--output',
        type=str,
        action='store',
        required=True,
        help='Setting the output file-path.'
    )

    parser.add_argument(
        '-w',
        '--width',
        type=int,
        action='store',
        required=True,
        help='Setting the width of the container.'
    )

    parser.add_argument(
        '-m',
        '--margin',
        type=int,
        nargs=4,
        default=(0, 0, 0, 0),
        metavar=('top', 'right', 'bottom', 'left'),
        action='store',
        help='Setting the margin for each side of an image.'
    )

    parser.add_argument(
        '--collapse-margin',
        action='store_true',
        help='This specifies if the margin between images are collapsed into each other.'
    )

    parser.add_argument(
        '--disable-auto-size',
        action='store_true',
        help='Disable automatic size adjustment.'
    )

    parser.add_argument(
        '--disable-vertical-flip',
        action='store_true',
        help='Disable vertical flip.'
    )

    parser.add_argument(
        '--force-pow2',
        action='store_true',
        help='Force the power-of-two rule.'
    )

    args = parser.parse_args()

    try:
        options = {
            'margin': args.margin,
            'collapse_margin': args.collapse_margin,
            'enable_auto_size': not args.disable_auto_size,
            'enable_vertical_flip': not args.disable_vertical_flip,
            'force_pow2': args.force_pow2
        }

        pack(
            input_filepaths=args.input,
            output_filepath=args.output,
            container_width=args.width,
            options=options
        )
        sys.exit(0)
    except Exception as e:
        print(e)
        sys.exit(1)
