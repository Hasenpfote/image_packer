#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import uuid
from PIL import Image
from . import blf


def pack(input_filepaths, output_filepath, container_width, padding=None):
    '''make a atlas.

    Args:
        input_filepaths (list(str)):
        output_filepath (str):
        container_width (int):
        padding (tuple):
    '''
    if padding is None:
        padding = (0, 0, 0, 0)

    uid_to_filepath = dict()
    pieces = list()

    for filepath in input_filepaths:
        with Image.open(filepath) as im:
            width = im.width + padding[1] + padding[3]
            height = im.height + padding[0] + padding[2]
            uid = uuid.uuid4()
            uid_to_filepath[uid] = filepath
            pieces.append(blf.Piece(uid=uid, width=width, height=height))

    container_width, container_height, rects = blf.solve(pieces, container_width)

    blank_image = Image.new('RGBA', (container_width, container_height), 'black')

    for rect in rects:
        x = rect.x + padding[3]
        y = (container_height - rect.top) + padding[0]
        filepath = uid_to_filepath.get(rect.uid)
        with Image.open(filepath) as im:
            blank_image.paste(im, (x, y))

    blank_image.save(output_filepath)


def main():
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-i',
        '--input',
        type=str,
        action='append',
        required=True,
        help='Setting the input file-path.'
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
        '-p',
        '--padding',
        type=int,
        nargs=4,
        default=(0, 0, 0, 0),
        metavar=('top', 'right', 'bottom', 'left'),
        action='store',
        help='Setting the padding for each side of an image.'
    )

    parser.add_argument(
        '-v', 
        '--verbose', 
        action='store_true', 
        help=''
    )

    args = parser.parse_args()

    pack(
        input_filepaths=args.input,
        output_filepath=args.output,
        container_width=args.width,
        padding=args.padding
    )


if __name__ == '__main__':
    main()
