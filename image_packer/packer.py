#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import fnmatch
import glob
import json
import logging
import os
import uuid
from collections import OrderedDict
from PIL import Image
from . import blf
from . import blf_solver


__all__ = ['pack']

logger = logging.getLogger(__name__)


def iglob(pathname, allowed_extensions):
    '''This function is equivalent to iglob, except that it considers allowed extensions.'''
    if not any(
        fnmatch.fnmatch(allowed_extension, os.path.splitext(pathname)[1])
        for allowed_extension in allowed_extensions
    ):
        # If the extension is explicit it will be excluded early.
        return

    for path in glob.iglob(pathname):
        if os.path.splitext(path)[1] in allowed_extensions:
            yield path


def distinct_filepaths(filepaths, allowed_extensions):
    '''Iterate distinct file paths'''
    processed_filepaths = set()
    for filepath in filepaths:
        is_abs = os.path.isabs(filepath)
        pathname = os.path.normpath(filepath if is_abs else os.path.abspath(filepath))
        for path in iglob(pathname, allowed_extensions):
            if path in processed_filepaths:
                continue
            processed_filepaths.add(path)

            if is_abs:
                yield path
            else:
                yield os.path.relpath(path)


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
        'force_pow2': False,
        # If true, all paths are forced to absolute path.
        'force_absolute_path': False
    }

    def __init__(self, filepaths):
        # Ensure plugins are fully loaded so that Image.EXTENSION is populated.
        Image.init()

        self._uid_to_filepath = dict()
        self._pieces = list()
        self._has_alpha = False

        allowed_extensions = {ext for ext in self._ALLOWED_EXTENSIONS if ext in Image.EXTENSION}
        for filepath in distinct_filepaths(filepaths=filepaths, allowed_extensions=allowed_extensions):
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
        force_absolute_path = options['force_absolute_path']

        config = OrderedDict()

        if force_absolute_path and not os.path.isabs(image_filepath):
            image_filepath = os.path.abspath(image_filepath)

        config['filepath'] = image_filepath
        config['width'] = container_width
        config['height'] = container_height

        config['regions'] = OrderedDict()
        for i, region in enumerate(regions):
            region_filepath = self._uid_to_filepath[region.uid]
            if force_absolute_path and not os.path.isabs(region_filepath):
                region_filepath = os.path.abspath(region_filepath)

            config['regions'][str(i)] = OrderedDict(
                [
                    ('filepath', region_filepath),
                    ('x', region.left),
                    ('y', region.bottom if enable_vertical_flip else container_height - region.top),
                    ('width', region.width),
                    ('height', region.height)
                ]
            )

        with open(filepath + '.json', 'w', encoding='utf-8') as fp:
            json.dump(config, fp, indent=4)


def pack(
    input_filepaths,
    output_filepath,
    container_width,
    options=None
):
    '''Convenience function to create Packer object and call `pack` method.'''
    packer = Packer(filepaths=input_filepaths)
    packer.pack(filepath=output_filepath, container_width=container_width, options=options)
