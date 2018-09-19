#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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

    @staticmethod
    def is_power_of_2(x):
        p = math.log2(x)
        return math.ceil(p) == math.floor(p)

    def test_opaque_images(self):
        with tempfile.TemporaryDirectory() as workpath:
            tools.make_random_png24_files(width=(1, 64), height=(1, 64), num_files=4, dirpath=workpath)
            tools.make_random_bmp_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)
            tools.make_random_jpeg_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)

            input_filepaths = [workpath + '/*.*', ]
            output_filepath = workpath + '/output.png'
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

    def test_transparent_images(self):
        with tempfile.TemporaryDirectory() as workpath:
            tools.make_random_png32_files(width=(1, 64), height=(1, 64), num_files=4, dirpath=workpath)
            tools.make_random_bmp_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)
            tools.make_random_jpeg_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)

            input_filepaths = [workpath + '/*.*', ]
            output_filepath = workpath + '/output.png'
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

    def test_collapse_margin(self):
        with tempfile.TemporaryDirectory() as workpath:
            tools.make_random_png32_files(width=(1, 64), height=(1, 64), num_files=4, dirpath=workpath)
            tools.make_random_bmp_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)
            tools.make_random_jpeg_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)

            input_filepaths = [workpath + '/*.*', ]
            output_filepath = workpath + '/output.png'
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

    def test_disable_auto_size(self):
        with tempfile.TemporaryDirectory() as workpath:
            tools.make_random_png32_files(width=(1, 64), height=(1, 64), num_files=4, dirpath=workpath)
            tools.make_random_bmp_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)
            tools.make_random_jpeg_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)

            input_filepaths = [workpath + '/*.*', ]
            output_filepath = workpath + '/output.png'
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

        with tempfile.TemporaryDirectory() as workpath:
            tools.make_random_png32_files(width=(1, 64), height=(1, 64), num_files=4, dirpath=workpath)
            tools.make_random_bmp_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)
            tools.make_random_jpeg_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)

            input_filepaths = [workpath + '/*.*', ]
            output_filepath = workpath + '/output.png'
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

    def test_disable_vertical_flip(self):
        with tempfile.TemporaryDirectory() as workpath:
            tools.make_random_png32_files(width=(1, 64), height=(1, 64), num_files=4, dirpath=workpath)
            tools.make_random_bmp_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)
            tools.make_random_jpeg_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)

            input_filepaths = [workpath + '/*.*', ]
            output_filepath = workpath + '/output.png'
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

    def test_force_pow2(self):
        with tempfile.TemporaryDirectory() as workpath:
            tools.make_random_png32_files(width=(1, 64), height=(1, 64), num_files=4, dirpath=workpath)
            tools.make_random_bmp_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)
            tools.make_random_jpeg_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)

            input_filepaths = [workpath + '/*.*', ]
            output_filepath = workpath + '/output.png'
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

                input_filepaths = [workpath + '/*.*', ]
                output_filepath = workpath + '/output.png'

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
