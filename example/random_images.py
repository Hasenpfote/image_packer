#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import glob
import os
import random
import tempfile
from PIL import Image

import sys
sys.path.append('../')
from image_packer import packer


def make_random_size_image(dirpath, min_size, max_size, n):
    for index, _ in enumerate(range(n)):
        w = random.randint(min_size, max_size)
        h = random.randint(min_size, max_size)
        image = Image.new('RGBA', (w, h), 'white')
        image.save('{}/{}.png'.format(dirpath, index))


def main():

    workpath = tempfile.mkdtemp(dir='.')
    make_random_size_image(dirpath=workpath, min_size=1, max_size=64, n=10)

    input_filepaths = [filepath for filepath in glob.glob(workpath + '/*.png')]
    output_filepath = workpath + '/atlas.png'
    container_width = 128
    padding = (1, 1, 1, 1)

    packer.pack(
        input_filepaths=input_filepaths,
        output_filepath=output_filepath,
        container_width=container_width,
        padding=padding
    )


if __name__ == '__main__':
    main()
