#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import glob
import os
import random
from PIL import Image
from unittest import TestCase

import sys
sys.path.append('../')
from image_packer import packer


class TestPacker(TestCase):

    WORKPATH = './temp'

    @classmethod
    def setUpClass(cls):
        if not os.path.exists(cls.WORKPATH):
            os.mkdir(cls.WORKPATH)

        for index, _ in enumerate(range(10)):
            w = random.randint(1, 64)
            h = random.randint(1, 64)
            image = Image.new('RGBA', (w, h), 'white')
            image.save('{}/{}.png'.format(cls.WORKPATH, index))

    @classmethod
    def tearDownClass(cls):
        filepath = '{}/{}'.format(cls.WORKPATH, '*.png')
        for filename in glob.glob(filepath):
            os.remove(filename)

    def test(self):
        input_filepaths = [filepath for filepath in glob.glob(self.WORKPATH + '/*.png')]
        output_filepath = self.WORKPATH + '/output.png'
        container_width = 128
        padding = (1, 1, 1, 1)

        packer.pack(
            input_filepaths=input_filepaths,
            output_filepath=output_filepath,
            container_width=container_width,
            padding=padding
        )
        self.assertTrue(os.path.exists(output_filepath))
