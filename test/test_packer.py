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
            container_width = 128

            options = {
                'padding': (1, 1, 1, 1)
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
            container_width = 128

            options = {
                'padding': (1, 1, 1, 1)
            }

            packer.pack(
                input_filepaths=input_filepaths,
                output_filepath=output_filepath,
                container_width=container_width,
                options=options
            )
            self.assertTrue(os.path.exists(output_filepath))

    def test_disable_auto_size(self):
        with tempfile.TemporaryDirectory() as workpath:
            tools.make_random_png32_files(width=(1, 64), height=(1, 64), num_files=4, dirpath=workpath)
            tools.make_random_bmp_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)
            tools.make_random_jpeg_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)

            input_filepaths = [workpath + '/*.*', ]
            output_filepath = workpath + '/output.png'
            container_width = 1

            options = {
                'padding': (1, 1, 1, 1),
                'enable_auto_size': False
            }

            with self.assertRaises(blf.LocationNotFoundError):
                packer.pack(
                    input_filepaths=input_filepaths,
                    output_filepath=output_filepath,
                    container_width=container_width,
                    options=options,
                )

    def test_disable_vertical_flip(self):
        with tempfile.TemporaryDirectory() as workpath:
            tools.make_random_png32_files(width=(1, 64), height=(1, 64), num_files=4, dirpath=workpath)
            tools.make_random_bmp_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)
            tools.make_random_jpeg_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)

            input_filepaths = [workpath + '/*.*', ]
            output_filepath = workpath + '/output.png'
            container_width = 128

            options = {
                'padding': (1, 1, 1, 1),
                'enable_auto_size': True,
                'enable_vertical_flip': False
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
            container_width = 128

            options = {
                'padding': (1, 1, 1, 1),
                'enable_auto_size': False,
            }

            packer.pack(
                input_filepaths=input_filepaths,
                output_filepath=output_filepath,
                container_width=container_width,
                options=options
            )
            self.assertTrue(os.path.exists(output_filepath))

    def test_force_pow2(self):
        with tempfile.TemporaryDirectory() as workpath:
            tools.make_random_png32_files(width=(1, 64), height=(1, 64), num_files=4, dirpath=workpath)
            tools.make_random_bmp_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)
            tools.make_random_jpeg_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)

            input_filepaths = [workpath + '/*.*', ]
            output_filepath = workpath + '/output.png'
            container_width = 60

            options = {
                'padding': (1, 1, 1, 1),
                'enable_auto_size': True,
                'enable_vertical_flip': True,
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

        with tempfile.TemporaryDirectory() as workpath:
            tools.make_random_png32_files(width=(1, 64), height=(1, 64), num_files=4, dirpath=workpath)
            tools.make_random_bmp_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)
            tools.make_random_jpeg_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)

            input_filepaths = [workpath + '/*.*', ]
            output_filepath = workpath + '/output.png'
            container_width = 60

            options = {
                'padding': (0, 0, 0, 0),
                'enable_auto_size': False,
                'enable_vertical_flip': True,
                'force_pow2': True
            }

            packer.pack(
                input_filepaths=input_filepaths,
                output_filepath=output_filepath,
                container_width=container_width,
                options=options
            )
            self.assertTrue(os.path.exists(output_filepath))
            with Image.open(fp=output_filepath) as im:
                self.assertTrue(self.is_power_of_2(im.width))
                self.assertTrue(self.is_power_of_2(im.height))

        with tempfile.TemporaryDirectory() as workpath:
            tools.make_random_png32_files(width=(1, 64), height=(1, 64), num_files=4, dirpath=workpath)
            tools.make_random_bmp_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)
            tools.make_random_jpeg_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)

            input_filepaths = [workpath + '/*.*', ]
            output_filepath = workpath + '/output.png'
            container_width = 60

            options = {
                'padding': (1, 1, 1, 1),
                'enable_auto_size': True,
                'enable_vertical_flip': False,
                'force_pow2': True
            }

            packer.pack(
                input_filepaths=input_filepaths,
                output_filepath=output_filepath,
                container_width=container_width,
                options=options
            )
            self.assertTrue(os.path.exists(output_filepath))
            with Image.open(fp=output_filepath) as im:
                self.assertTrue(self.is_power_of_2(im.width))
                self.assertTrue(self.is_power_of_2(im.height))

        with tempfile.TemporaryDirectory() as workpath:
            tools.make_random_png32_files(width=(1, 64), height=(1, 64), num_files=4, dirpath=workpath)
            tools.make_random_bmp_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)
            tools.make_random_jpeg_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)

            input_filepaths = [workpath + '/*.*', ]
            output_filepath = workpath + '/output.png'
            container_width = 60

            options = {
                'padding': (0, 0, 0, 0),
                'enable_auto_size': False,
                'enable_vertical_flip': False,
                'force_pow2': True
            }

            packer.pack(
                input_filepaths=input_filepaths,
                output_filepath=output_filepath,
                container_width=container_width,
                options=options
            )
            self.assertTrue(os.path.exists(output_filepath))
            with Image.open(fp=output_filepath) as im:
                self.assertTrue(self.is_power_of_2(im.width))
                self.assertTrue(self.is_power_of_2(im.height))
