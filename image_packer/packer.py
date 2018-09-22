#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import glob
import json
import logging
import os
import sys
import uuid
from collections import OrderedDict
from PIL import Image
from . import blf
from . import blf_solver


__all__ = ['pack']

logger = logging.getLogger(__name__)


def extract_filepaths(filepaths, allowed_extensions):
    results = set()
    for filepath in filepaths:
        filepath = os.path.normpath(filepath)
        if '*' in filepath:
            for filepath_ in glob.glob(filepath):
                if os.path.splitext(filepath_)[1] in allowed_extensions:
                    results.add(filepath_)
                else:
                    logger.warning('The `{}` file has been ignored.'.format(filepath_))
        else:
            if os.path.splitext(filepath)[1] in allowed_extensions:
                results.add(filepath)
            else:
                logger.warning('The `{}` file has been ignored.'.format(filepath))

    return results


class Packer(object):
    '''The Packer class packs multiple images of different sizes or formats into one image.

    Args:
        filepaths (list(str)): List of input image file paths.
    '''
    _ALLOWED_EXTENSIONS = {'.png', '.bmp', '.jpg'}

    _DEFAULT_OPTIONS = {
        'bg_color': (0.0, 0.0, 0.0, 1.0),
        'margin': (0, 0, 0, 0),
        'collapse_margin': False,
        # If true, the size will be adjusted automatically.
        'enable_auto_size': True,
        # If true, flips the output upside down.
        'enable_vertical_flip': True,
        # If true, the power-of-two rule is forced.
        'force_pow2': False
    }

    def __init__(self, filepaths):
        # Ensure plugins are fully loaded so that Image.EXTENSION is populated.
        Image.init()

        filepaths_ = extract_filepaths(
            filepaths=filepaths,
            allowed_extensions={ext for ext in self._ALLOWED_EXTENSIONS if ext in Image.EXTENSION}
        )

        self._uid_to_filepath = dict()
        self._pieces = list()
        self._has_alpha = False

        for filepath in filepaths_:
            with Image.open(fp=filepath) as im:
                width = im.width
                height = im.height
                uid = uuid.uuid4()
                self._uid_to_filepath[uid] = filepath
                self._pieces.append(blf.Piece(uid=uid, size=blf.Size(width, height)))
                if im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info):
                    self._has_alpha = True

    def pack(self, filepath, container_width, options=None):
        '''Packs multiple images of different sizes or formats into one image.

        Args:
            filepath (str): An output image file path.
            container_width (int):
            options (dict):
        '''
        if options is None:
            options = self._DEFAULT_OPTIONS
        else:
            options = {
                key: options[key] if key in options else self._DEFAULT_OPTIONS[key]
                for key in self._DEFAULT_OPTIONS.keys()
            }

        margin_ = options['margin']
        assert isinstance(margin_, tuple) and len(margin_) == 4

        if options['enable_vertical_flip']:
            margin = blf.Thickness(top=margin_[2], right=margin_[1], bottom=margin_[0], left=margin_[3])
        else:
            margin = blf.Thickness(top=margin_[0], right=margin_[1], bottom=margin_[2], left=margin_[3])

        blf_options = {
            'margin': margin,
            'collapse_margin': options['collapse_margin'],
            'enable_auto_size': options['enable_auto_size'],
            'force_pow2': options['force_pow2']
        }

        container_width, container_height, regions = blf_solver.solve(
            pieces=self._pieces,
            container_width=container_width,
            options=blf_options
        )

        self._save_image(
            filepath=filepath,
            container_width=container_width,
            container_height=container_height,
            regions=regions,
            options=options
        )

        self._save_configuration(
            filepath=os.path.splitext(filepath)[0],
            image_filepath=os.path.normpath(filepath),
            container_width=container_width,
            container_height=container_height,
            regions=regions,
            options=options
        )

    def _save_image(
        self,
        filepath,
        container_width,
        container_height,
        regions,
        options
    ):
        bg_color_ = options['bg_color']
        assert isinstance(bg_color_, tuple) and (3 <= len(bg_color_) <= 4)
        bg_color = tuple(int(channel * 255.0) for channel in bg_color_)
        if len(bg_color) == 3:
            bg_color += (255,)

        if self._has_alpha:
            blank_image = Image.new(
                mode='RGBA',
                size=(container_width, container_height),
                color=bg_color
            )
        else:
            blank_image = Image.new(
                mode='RGB',
                size=(container_width, container_height),
                color=bg_color[0:3]
            )

        enable_vertical_flip = options['enable_vertical_flip']

        for region in regions:
            x = region.left
            if enable_vertical_flip:
                y = region.bottom
            else:
                y = container_height - region.top

            input_filepath = self._uid_to_filepath.get(region.uid)
            # Open path as file to avoid ResourceWarning.
            # https://github.com/python-pillow/Pillow/issues/835
            with open(input_filepath, 'rb') as fp:
                im = Image.open(fp=fp)
                blank_image.paste(im=im, box=(x, y))

        blank_image.save(fp=filepath, format='PNG')

    def _save_configuration(
        self,
        filepath,
        image_filepath,
        container_width,
        container_height,
        regions,
        options
    ):
        enable_vertical_flip = options['enable_vertical_flip']

        details = OrderedDict()
        details['filepath'] = image_filepath
        details['width'] = container_width
        details['height'] = container_height
        details['regions'] = OrderedDict()
        for i, region in enumerate(regions):
            details['regions'][str(i)] = OrderedDict(
                [
                    ('filepath', self._uid_to_filepath[region.uid]),
                    ('x', region.left),
                    ('y', region.bottom if enable_vertical_flip else container_height - region.top),
                    ('width', region.width),
                    ('height', region.height)
                ]
            )

        with open(filepath + '.json', 'w', encoding='utf-8') as fp:
            json.dump(details, fp, indent=4)


def pack(
    input_filepaths,
    output_filepath,
    container_width,
    options=None
):
    '''Convenience function to create Packer object and call `pack` method.'''
    packer = Packer(filepaths=input_filepaths)
    packer.pack(filepath=output_filepath, container_width=container_width, options=options)


def main():

    def positive_integer(x):
        x = int(x)
        if x <= 0:
            raise argparse.ArgumentTypeError('{} is not a positive integer.'.format(x))
        return x

    def nonnegative_integer(x):
        x = int(x)
        if x < 0:
            raise argparse.ArgumentTypeError('{} is not a nonnegative integer.'.format(x))
        return x

    def nonnegative_normalized_float(x):
        x = float(x)
        if x < 0.0 or x > 1.0:
            raise argparse.ArgumentTypeError('{} is not in range.'.format(x))
        return x

    def required_length(nmin, nmax):
        class RequiredLength(argparse.Action):
            def __call__(self, parser, args, values, option_string=None):
                if not nmin <= len(values) <= nmax:
                    msg = 'argument "{f}" requires between {nmin} and {nmax} arguments'.format(
                        f=self.dest, nmin=nmin, nmax=nmax)
                    raise argparse.ArgumentTypeError(msg)
                setattr(args, self.dest, values)

        return RequiredLength

    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-i',
        '--input',
        type=str,
        action='append',
        required=True,
        help='Specifies a input image file path or directory path. '
             'The file path can also use an asterisk as a wildcard character.'
    )

    parser.add_argument(
        '-o',
        '--output',
        type=str,
        action='store',
        required=True,
        help='Specifies a output image file path.'
    )

    parser.add_argument(
        '-w',
        '--width',
        type=positive_integer,
        action='store',
        required=True,
        help='Specifies a container width.'
    )

    parser.add_argument(
        '--bg-color',
        type=nonnegative_normalized_float,
        nargs='+',
        action=required_length(3, 4),
        help='Specifies a background color as RGB or RGBA. '
             'The range of each channel is 0 to 1.'
    )

    parser.add_argument(
        '-m',
        '--margin',
        type=nonnegative_integer,
        nargs=4,
        default=(0, 0, 0, 0),
        metavar=('top', 'right', 'bottom', 'left'),
        action='store',
        help='Specifies a margin around each input image.'
    )

    parser.add_argument(
        '--collapse-margin',
        action='store_true',
        help='Specifies if the margin between images are collapsed into each other.'
    )

    parser.add_argument(
        '--disable-auto-size',
        action='store_true',
        help='Specifies whether to disable automatic adjustment of container size.'
    )

    parser.add_argument(
        '--disable-vertical-flip',
        action='store_true',
        help='Specifies whether to disable vertical flip.'
    )

    parser.add_argument(
        '--force-pow2',
        action='store_true',
        help='Specifies whether to force the power-of-2 rule.'
    )

    try:
        args = parser.parse_args()
    except SystemExit as e:
        if e.code != 0:
            logger.exception('The command terminated abnormally.')
        raise

    try:
        options = {
            'margin': args.margin,
            'collapse_margin': args.collapse_margin,
            'enable_auto_size': not args.disable_auto_size,
            'enable_vertical_flip': not args.disable_vertical_flip,
            'force_pow2': args.force_pow2
        }
        if args.bg_color is not None:
            options['bg_color'] = tuple(args.bg_color)

        pack(
            input_filepaths=args.input,
            output_filepath=args.output,
            container_width=args.width,
            options=options
        )
        logger.info('The command terminated normally.')
        sys.exit(0)
    except Exception:
        logger.exception('The command terminated abnormally.')
        sys.exit(1)
