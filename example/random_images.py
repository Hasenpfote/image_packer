#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import tempfile

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
