#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import collections
import json
import logging
import math
import os
import tempfile
from PIL import Image
from unittest import TestCase

import sys
sys.path.append('../')
from image_packer import packer
from image_packer import blf
from image_packer import tools


class TestPacker(TestCase):

    @classmethod
    def setUpClass(cls):
        logging.disable(logging.CRITICAL)

    @classmethod
    def tearDownClass(cls):
        logging.disable(logging.NOTSET)

    @staticmethod
    def is_power_of_2(x):
        p = math.log2(x)
        return math.ceil(p) == math.floor(p)

    def test_opaque_images(self):
        with tempfile.TemporaryDirectory() as workpath:
            tools.make_random_png24_files(width=(1, 64), height=(1, 64), num_files=4, dirpath=workpath)
            tools.make_random_bmp_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)
            tools.make_random_jpeg_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)

            input_filepaths = [os.path.join(workpath, '*.*'), ]
            output_filepath = os.path.join(workpath, 'output.png')
            container_width = 100

            options = {
                'margin': (1, 1, 1, 1)
            }

            packer.pack(
                input_filepaths=input_filepaths,
                output_filepath=output_filepath,
                container_width=container_width,
                options=options
            )
            self.assertTrue(os.path.exists(output_filepath))
            self.assertTrue(os.path.exists(os.path.splitext(output_filepath)[0] + '.json'))

    def test_transparent_images(self):
        with tempfile.TemporaryDirectory() as workpath:
            tools.make_random_png32_files(width=(1, 64), height=(1, 64), num_files=4, dirpath=workpath)
            tools.make_random_bmp_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)
            tools.make_random_jpeg_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)

            input_filepaths = [os.path.join(workpath, '*.*'), ]
            output_filepath = os.path.join(workpath, 'output.png')
            container_width = 100

            options = {
                'margin': (1, 1, 1, 1)
            }

            packer.pack(
                input_filepaths=input_filepaths,
                output_filepath=output_filepath,
                container_width=container_width,
                options=options
            )
            self.assertTrue(os.path.exists(output_filepath))
            self.assertTrue(os.path.exists(os.path.splitext(output_filepath)[0] + '.json'))

    def test_collapse_margin(self):
        with tempfile.TemporaryDirectory() as workpath:
            tools.make_random_png32_files(width=(1, 64), height=(1, 64), num_files=4, dirpath=workpath)
            tools.make_random_bmp_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)
            tools.make_random_jpeg_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)

            input_filepaths = [os.path.join(workpath, '*.*'), ]
            output_filepath = os.path.join(workpath, 'output.png')
            container_width = 66

            options = {
                'margin': (1, 1, 1, 1),
                'collapse_margin': True
            }

            packer.pack(
                input_filepaths=input_filepaths,
                output_filepath=output_filepath,
                container_width=container_width,
                options=options,
            )
            self.assertTrue(os.path.exists(output_filepath))
            self.assertTrue(os.path.exists(os.path.splitext(output_filepath)[0] + '.json'))

    def test_disable_auto_size(self):
        with tempfile.TemporaryDirectory() as workpath:
            tools.make_random_png32_files(width=(1, 64), height=(1, 64), num_files=4, dirpath=workpath)
            tools.make_random_bmp_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)
            tools.make_random_jpeg_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)

            input_filepaths = [os.path.join(workpath, '*.*'), ]
            output_filepath = os.path.join(workpath, 'output.png')
            container_width = 66

            options = {
                'margin': (1, 1, 1, 1),
                'enable_auto_size': False
            }

            packer.pack(
                input_filepaths=input_filepaths,
                output_filepath=output_filepath,
                container_width=container_width,
                options=options,
            )
            self.assertTrue(os.path.exists(output_filepath))
            self.assertTrue(os.path.exists(os.path.splitext(output_filepath)[0] + '.json'))

        with tempfile.TemporaryDirectory() as workpath:
            tools.make_random_png32_files(width=(1, 64), height=(1, 64), num_files=4, dirpath=workpath)
            tools.make_random_bmp_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)
            tools.make_random_jpeg_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)

            input_filepaths = [os.path.join(workpath, '*.*'), ]
            output_filepath = os.path.join(workpath, 'output.png')
            container_width = 1

            options = {
                'margin': (1, 1, 1, 1),
                'enable_auto_size': False
            }

            with self.assertRaises(blf.LocationNotFoundError):
                packer.pack(
                    input_filepaths=input_filepaths,
                    output_filepath=output_filepath,
                    container_width=container_width,
                    options=options,
                )
            self.assertFalse(os.path.exists(output_filepath))
            self.assertFalse(os.path.exists(os.path.splitext(output_filepath)[0] + '.json'))

    def test_disable_vertical_flip(self):
        with tempfile.TemporaryDirectory() as workpath:
            tools.make_random_png32_files(width=(1, 64), height=(1, 64), num_files=4, dirpath=workpath)
            tools.make_random_bmp_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)
            tools.make_random_jpeg_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)

            input_filepaths = [os.path.join(workpath, '*.*'), ]
            output_filepath = os.path.join(workpath, 'output.png')
            container_width = 100

            options = {
                'margin': (1, 1, 1, 1),
                'enable_vertical_flip': False
            }

            packer.pack(
                input_filepaths=input_filepaths,
                output_filepath=output_filepath,
                container_width=container_width,
                options=options,
            )
            self.assertTrue(os.path.exists(output_filepath))
            self.assertTrue(os.path.exists(os.path.splitext(output_filepath)[0] + '.json'))

    def test_force_pow2(self):
        with tempfile.TemporaryDirectory() as workpath:
            tools.make_random_png32_files(width=(1, 64), height=(1, 64), num_files=4, dirpath=workpath)
            tools.make_random_bmp_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)
            tools.make_random_jpeg_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)

            input_filepaths = [os.path.join(workpath, '*.*'), ]
            output_filepath = os.path.join(workpath, 'output.png')
            container_width = 66

            options = {
                'margin': (1, 1, 1, 1),
                'force_pow2': True
            }

            packer.pack(
                input_filepaths=input_filepaths,
                output_filepath=output_filepath,
                container_width=container_width,
                options=options,
            )
            self.assertTrue(os.path.exists(output_filepath))
            with Image.open(fp=output_filepath) as im:
                self.assertTrue(self.is_power_of_2(im.width))
                self.assertTrue(self.is_power_of_2(im.height))

            self.assertTrue(os.path.exists(os.path.splitext(output_filepath)[0] + '.json'))

    def test_combination(self):
        keys = ('collapse_margin', 'enable_auto_size', 'enable_vertical_flip', 'force_pow2')
        patterns = (
            (True, True, True, True),
            (True, False, False, False),
            (True, True, False, False),
            (True, False, True, False),
            (True, False, False, True),
            (True, True, True, False),
            (True, True, False, True),
            (True, False, True, True),
            (False, True, False, False),
            (False, True, True, False),
            (False, True, False, True),
            (False, True, True, True),
            (False, False, True, False),
            (False, False, True, True),
            (False, False, False, True),
            (False, False, False, False),
        )

        container_width = 66
        for pattern in patterns:
            options = {k: v for k, v in zip(keys, pattern)}
            options['margin'] = (1, 1, 1, 1)
            with tempfile.TemporaryDirectory() as workpath:
                tools.make_random_png32_files(width=(1, 64), height=(1, 64), num_files=4, dirpath=workpath)
                tools.make_random_bmp_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)
                tools.make_random_jpeg_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)

                input_filepaths = [os.path.join(workpath, '*.*'), ]
                output_filepath = os.path.join(workpath, 'output.png')

                packer.pack(
                    input_filepaths=input_filepaths,
                    output_filepath=output_filepath,
                    container_width=container_width,
                    options=options
                )
                self.assertTrue(os.path.exists(output_filepath))
                if options['force_pow2']:
                    with Image.open(fp=output_filepath) as im:
                        self.assertTrue(self.is_power_of_2(im.width))
                        self.assertTrue(self.is_power_of_2(im.height))

                self.assertTrue(os.path.exists(os.path.splitext(output_filepath)[0] + '.json'))

    def test_configuration(self):
        with tempfile.TemporaryDirectory(dir='.') as workpath:
            tools.make_random_png24_files(width=(1, 64), height=(1, 64), num_files=4, dirpath=workpath)
            tools.make_random_bmp_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)
            tools.make_random_jpeg_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)

            input_filepaths = [os.path.join(workpath, '*.*'), ]
            output_filepath = os.path.join(workpath, 'output.png')
            container_width = 100

            options = {
                'margin': (1, 1, 1, 1),
                'force_absolute_path': False
            }

            packer.pack(
                input_filepaths=input_filepaths,
                output_filepath=output_filepath,
                container_width=container_width,
                options=options
            )
            self.assertTrue(os.path.exists(output_filepath))

            config_filepath = os.path.splitext(output_filepath)[0] + '.json'
            self.assertTrue(os.path.exists(config_filepath))
            with open(config_filepath, 'r', encoding='utf-8') as fp:
                config = json.load(fp)

                filepath = config.get('filepath')
                self.assertTrue(filepath is not None and isinstance(filepath, str))
                self.assertFalse(os.path.isabs(filepath))

                width = config.get('width')
                self.assertTrue(width is not None and isinstance(width, int))

                height = config.get('height')
                self.assertTrue(height is not None and isinstance(height, int))

                regions = config.get('regions')
                self.assertTrue(regions is not None)
                for region in regions.values():
                    filepath = region.get('filepath')
                    self.assertTrue(filepath is not None and isinstance(filepath, str))
                    self.assertFalse(os.path.isabs(filepath))

                    x = region.get('x')
                    self.assertTrue(x is not None and isinstance(x, int))

                    y = region.get('y')
                    self.assertTrue(y is not None and isinstance(y, int))

                    width = region.get('width')
                    self.assertTrue(width is not None and isinstance(width, int))

                    height = region.get('height')
                    self.assertTrue(height is not None and isinstance(height, int))

        with tempfile.TemporaryDirectory(dir='.') as workpath:
            tools.make_random_png24_files(width=(1, 64), height=(1, 64), num_files=4, dirpath=workpath)
            tools.make_random_bmp_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)
            tools.make_random_jpeg_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)

            input_filepaths = [os.path.join(workpath, '*.*'), ]
            output_filepath = os.path.join(workpath, 'output.png')
            container_width = 100

            options = {
                'margin': (1, 1, 1, 1),
                'force_absolute_path': True
            }

            packer.pack(
                input_filepaths=input_filepaths,
                output_filepath=output_filepath,
                container_width=container_width,
                options=options
            )
            self.assertTrue(os.path.exists(output_filepath))

            config_filepath = os.path.splitext(output_filepath)[0] + '.json'
            self.assertTrue(os.path.exists(config_filepath))
            with open(config_filepath, 'r', encoding='utf-8') as fp:
                config = json.load(fp)

                filepath = config.get('filepath')
                self.assertTrue(filepath is not None and isinstance(filepath, str))
                self.assertTrue(os.path.isabs(filepath))

                width = config.get('width')
                self.assertTrue(width is not None and isinstance(width, int))

                height = config.get('height')
                self.assertTrue(height is not None and isinstance(height, int))

                regions = config.get('regions')
                self.assertTrue(regions is not None)
                for region in regions.values():
                    filepath = region.get('filepath')
                    self.assertTrue(filepath is not None and isinstance(filepath, str))
                    self.assertTrue(os.path.isabs(filepath))

                    x = region.get('x')
                    self.assertTrue(x is not None and isinstance(x, int))

                    y = region.get('y')
                    self.assertTrue(y is not None and isinstance(y, int))

                    width = region.get('width')
                    self.assertTrue(width is not None and isinstance(width, int))

                    height = region.get('height')
                    self.assertTrue(height is not None and isinstance(height, int))

    def test_distinct_filepaths(self):
        with tempfile.TemporaryDirectory(dir='.') as workpath:
            num_files = 10
            tools.make_random_png24_files(width=(1, 64), height=(1, 64), num_files=num_files, dirpath=workpath)

            filepaths = [
                os.path.join(workpath, '*.png'),
                os.path.join(workpath, '..', workpath, '*.png'),
                os.path.join(os.path.abspath(workpath), '*.png'),
                os.path.join(os.path.abspath(workpath), '..', workpath, '*.png'),
                os.path.join(os.path.abspath(workpath), '*.p?g'),
                os.path.join(os.path.abspath(workpath), '*.*'),
            ]

            iter = packer.distinct_filepaths(filepaths=filepaths, allowed_extensions={'.png', })
            self.assertTrue(isinstance(iter, collections.Iterable))
            self.assertEqual(sum(1 for _ in iter), num_files)
