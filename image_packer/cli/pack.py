#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import logging
import sys
from .. import packer


logger = logging.getLogger(__name__)


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


def main():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-i',
        '--input',
        type=str,
        action='append',
        required=True,
        help='Specifies an input image file path. '
             'The file path provides support for Unix shell-style wildcards.'
    )

    parser.add_argument(
        '-o',
        '--output',
        type=str,
        action='store',
        required=True,
        help='Specifies an output image file path.'
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

    parser.add_argument(
        '--force-absolute-path',
        action='store_true',
        help='Specifies whether to force the paths in a configuration file to absolute paths.'
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
            'force_pow2': args.force_pow2,
            'force_absolute_path': args.force_absolute_path
        }
        if args.bg_color is not None:
            options['bg_color'] = tuple(args.bg_color)

        packer.pack(
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


if __name__ == '__main__':
    main()
