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
from image_packer import tools


def main():

    workpath = tempfile.mkdtemp(dir='.')

    tools.make_random_png32_files(width=(1, 64), height=(1, 64), num_files=10, dirpath=workpath)

    input_filepaths = [
        workpath + '/*.png',
    ]
    output_filepath = workpath + '/atlas.png'
    container_width = 100
    padding = (1, 1, 1, 1)

    packer.pack(
        input_filepaths=input_filepaths,
        output_filepath=output_filepath,
        container_width=container_width,
        padding=padding,
        enable_auto_size=True,
        enable_vertical_flip=True,
        force_pow2=False
    )


if __name__ == '__main__':
    main()
