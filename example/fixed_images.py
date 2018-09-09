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


def main():

    workpath = './image'

    input_filepaths = [
        workpath + '/*.png',
        workpath + '/*.jpg',
        workpath + '/*.bmp',
    ]
    output_filepath = workpath + '/atlas.png'
    container_width = 128
    padding = (1, 1, 1, 1)

    packer.pack(
        input_filepaths=input_filepaths,
        output_filepath=output_filepath,
        container_width=container_width,
        padding=padding,
        enable_auto_size=True,
        force_pow2=False
    )


if __name__ == '__main__':
    main()
