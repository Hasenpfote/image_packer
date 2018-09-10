#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import math
import os
import random
import tempfile
import uuid
from PIL import Image
from unittest import TestCase

import sys
sys.path.append('../')
from image_packer import packer
from image_packer import blf


class TestPacker(TestCase):

    @staticmethod
    def is_power_of_2(x):
        p = math.log2(x)
        return math.ceil(p) == math.floor(p)

    @staticmethod
    def make_png24_files(dirpath, max_width, max_height, n):
        for _ in range(n):
            w = random.randint(1, max_width)
            h = random.randint(1, max_height)
            image = Image.new(mode='RGB', size=(w, h), color=(255, 255, 255))
            image.save(fp='{}/{}.png'.format(dirpath, uuid.uuid4()), format='PNG')

    @staticmethod
    def make_png32_files(dirpath, max_width, max_height, n):
        for _ in range(n):
            w = random.randint(1, max_width)
            h = random.randint(1, max_height)
            image = Image.new(mode='RGBA', size=(w, h), color=(255, 255, 255, 127))
            image.save(fp='{}/{}.png'.format(dirpath, uuid.uuid4()), format='PNG')

    @staticmethod
    def make_bmp_files(dirpath, max_width, max_height, n):
        for _ in range(n):
            w = random.randint(1, max_width)
            h = random.randint(1, max_height)
            image = Image.new(mode='RGB', size=(w, h), color=(255, 255, 255))
            image.save(fp='{}/{}.bmp'.format(dirpath, uuid.uuid4()), format='BMP')

    @staticmethod
    def make_jpg_files(dirpath, max_width, max_height, n):
        for _ in range(n):
            w = random.randint(1, max_width)
            h = random.randint(1, max_height)
            image = Image.new(mode='RGB', size=(w, h), color=(255, 255, 255))
            image.save(fp='{}/{}.jpg'.format(dirpath, uuid.uuid4()), format='JPEG')

    def test_opaque_images(self):
        with tempfile.TemporaryDirectory() as workpath:
            self.make_png24_files(dirpath=workpath, max_width=64, max_height=64, n=4)
            self.make_bmp_files(dirpath=workpath, max_width=64, max_height=64, n=3)
            self.make_jpg_files(dirpath=workpath, max_width=64, max_height=64, n=3)

            input_filepaths = [workpath + '/*.*', ]
            output_filepath = workpath + '/output.png'
            container_width = 128
            padding = (1, 1, 1, 1)

            packer.pack(
                input_filepaths=input_filepaths,
                output_filepath=output_filepath,
                container_width=container_width,
                padding=padding
            )
            self.assertTrue(os.path.exists(output_filepath))

    def test_transparent_images(self):
        with tempfile.TemporaryDirectory() as workpath:
            self.make_png32_files(dirpath=workpath, max_width=64, max_height=64, n=4)
            self.make_bmp_files(dirpath=workpath, max_width=64, max_height=64, n=3)
            self.make_jpg_files(dirpath=workpath, max_width=64, max_height=64, n=3)

            input_filepaths = [workpath + '/*.*', ]
            output_filepath = workpath + '/output.png'
            container_width = 128
            padding = (1, 1, 1, 1)

            packer.pack(
                input_filepaths=input_filepaths,
                output_filepath=output_filepath,
                container_width=container_width,
                padding=padding
            )
            self.assertTrue(os.path.exists(output_filepath))

    def test_disable_auto_size(self):
        with tempfile.TemporaryDirectory() as workpath:
            self.make_png32_files(dirpath=workpath, max_width=64, max_height=64, n=4)
            self.make_bmp_files(dirpath=workpath, max_width=64, max_height=64, n=3)
            self.make_jpg_files(dirpath=workpath, max_width=64, max_height=64, n=3)

            input_filepaths = [workpath + '/*.*', ]
            output_filepath = workpath + '/output.png'
            container_width = 1
            padding = (1, 1, 1, 1)

            with self.assertRaises(blf.LocationNotFoundError):
                packer.pack(
                    input_filepaths=input_filepaths,
                    output_filepath=output_filepath,
                    container_width=container_width,
                    padding=padding,
                    enable_auto_size=False
                )

    def test_disable_vertical_flip(self):
        with tempfile.TemporaryDirectory() as workpath:
            self.make_png32_files(dirpath=workpath, max_width=64, max_height=64, n=4)
            self.make_bmp_files(dirpath=workpath, max_width=64, max_height=64, n=3)
            self.make_jpg_files(dirpath=workpath, max_width=64, max_height=64, n=3)

            input_filepaths = [workpath + '/*.*', ]
            output_filepath = workpath + '/output.png'
            container_width = 128
            padding = (1, 1, 1, 1)

            packer.pack(
                input_filepaths=input_filepaths,
                output_filepath=output_filepath,
                container_width=container_width,
                padding=padding,
                enable_auto_size=True,
                enable_vertical_flip=False,
            )
            self.assertTrue(os.path.exists(output_filepath))

        with tempfile.TemporaryDirectory() as workpath:
            self.make_png32_files(dirpath=workpath, max_width=64, max_height=64, n=4)
            self.make_bmp_files(dirpath=workpath, max_width=64, max_height=64, n=3)
            self.make_jpg_files(dirpath=workpath, max_width=64, max_height=64, n=3)

            input_filepaths = [workpath + '/*.*', ]
            output_filepath = workpath + '/output.png'
            container_width = 128
            padding = (1, 1, 1, 1)

            packer.pack(
                input_filepaths=input_filepaths,
                output_filepath=output_filepath,
                container_width=container_width,
                padding=padding,
                enable_auto_size=False,
                enable_vertical_flip=False,
            )
            self.assertTrue(os.path.exists(output_filepath))

    def test_force_pow2(self):
        with tempfile.TemporaryDirectory() as workpath:
            self.make_png32_files(dirpath=workpath, max_width=64, max_height=64, n=4)
            self.make_bmp_files(dirpath=workpath, max_width=64, max_height=64, n=3)
            self.make_jpg_files(dirpath=workpath, max_width=64, max_height=64, n=3)

            input_filepaths = [workpath + '/*.*', ]
            output_filepath = workpath + '/output.png'
            container_width = 60
            padding = (1, 1, 1, 1)

            packer.pack(
                input_filepaths=input_filepaths,
                output_filepath=output_filepath,
                container_width=container_width,
                padding=padding,
                enable_auto_size=True,
                enable_vertical_flip=True,
                force_pow2=True
            )
            self.assertTrue(os.path.exists(output_filepath))
            with Image.open(fp=output_filepath) as im:
                self.assertTrue(self.is_power_of_2(im.width))
                self.assertTrue(self.is_power_of_2(im.height))

        with tempfile.TemporaryDirectory() as workpath:
            self.make_png32_files(dirpath=workpath, max_width=64, max_height=64, n=4)
            self.make_bmp_files(dirpath=workpath, max_width=64, max_height=64, n=3)
            self.make_jpg_files(dirpath=workpath, max_width=64, max_height=64, n=3)

            input_filepaths = [workpath + '/*.*', ]
            output_filepath = workpath + '/output.png'
            container_width = 60
            padding = (0, 0, 0, 0)

            packer.pack(
                input_filepaths=input_filepaths,
                output_filepath=output_filepath,
                container_width=container_width,
                padding=padding,
                enable_auto_size=False,
                enable_vertical_flip=True,
                force_pow2=True
            )
            self.assertTrue(os.path.exists(output_filepath))
            with Image.open(fp=output_filepath) as im:
                self.assertTrue(self.is_power_of_2(im.width))
                self.assertTrue(self.is_power_of_2(im.height))

        with tempfile.TemporaryDirectory() as workpath:
            self.make_png32_files(dirpath=workpath, max_width=64, max_height=64, n=4)
            self.make_bmp_files(dirpath=workpath, max_width=64, max_height=64, n=3)
            self.make_jpg_files(dirpath=workpath, max_width=64, max_height=64, n=3)

            input_filepaths = [workpath + '/*.*', ]
            output_filepath = workpath + '/output.png'
            container_width = 60
            padding = (1, 1, 1, 1)

            packer.pack(
                input_filepaths=input_filepaths,
                output_filepath=output_filepath,
                container_width=container_width,
                padding=padding,
                enable_auto_size=True,
                enable_vertical_flip=False,
                force_pow2=True
            )
            self.assertTrue(os.path.exists(output_filepath))
            with Image.open(fp=output_filepath) as im:
                self.assertTrue(self.is_power_of_2(im.width))
                self.assertTrue(self.is_power_of_2(im.height))

        with tempfile.TemporaryDirectory() as workpath:
            self.make_png32_files(dirpath=workpath, max_width=64, max_height=64, n=4)
            self.make_bmp_files(dirpath=workpath, max_width=64, max_height=64, n=3)
            self.make_jpg_files(dirpath=workpath, max_width=64, max_height=64, n=3)

            input_filepaths = [workpath + '/*.*', ]
            output_filepath = workpath + '/output.png'
            container_width = 60
            padding = (0, 0, 0, 0)

            packer.pack(
                input_filepaths=input_filepaths,
                output_filepath=output_filepath,
                container_width=container_width,
                padding=padding,
                enable_auto_size=False,
                enable_vertical_flip=False,
                force_pow2=True
            )
            self.assertTrue(os.path.exists(output_filepath))
            with Image.open(fp=output_filepath) as im:
                self.assertTrue(self.is_power_of_2(im.width))
                self.assertTrue(self.is_power_of_2(im.height))
