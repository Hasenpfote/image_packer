#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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

    options = {
        'margin': (1, 1, 1, 1),
        'collapse_margin': False,
        'enable_auto_size': True,
        'enable_vertical_flip': True,
        'force_pow2': False
    }

    packer.pack(
        input_filepaths=input_filepaths,
        output_filepath=output_filepath,
        container_width=container_width,
        options=options
    )


if __name__ == '__main__':
    main()
