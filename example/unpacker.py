#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
import tempfile
from PIL import Image

import sys
sys.path.append('../')
from image_packer import packer
from image_packer import tools


class Unpacker(object):

    def __init__(self, image_filepath, configuration_filepath):
        self._image_filepath = image_filepath
        with open(configuration_filepath, 'r', encoding='utf-8') as fp:
            self._configuration = json.load(fp)

        self._filename_to_multiplicity = dict()
        for v in self._configuration['regions'].values():
            filename = os.path.splitext(os.path.basename(v['filepath']))[0]
            if self._filename_to_multiplicity.get(filename) is None:
                self._filename_to_multiplicity[filename] = 1
            else:
                self._filename_to_multiplicity[filename] += 1

    def unpack(self, dirpath):
        filename_to_counter = dict()
        with open(self._image_filepath, 'rb') as fp:
            im = Image.open(fp=fp)
            for k, v in self._configuration['regions'].items():
                src_filename = os.path.splitext(os.path.basename(v['filepath']))[0]
                if self._filename_to_multiplicity[src_filename] > 1:
                    if filename_to_counter.get(src_filename) is None:
                        filename_to_counter[src_filename] = 0
                    else:
                        filename_to_counter[src_filename] += 1
                    suffix = '_' + str(filename_to_counter[src_filename])
                else:
                    suffix = ''

                dst_basename = src_filename + suffix + '.png'
                dst_filepath = os.path.join(dirpath, dst_basename)

                left = v['x']
                top = v['y']
                right = left + v['width']
                bottom = top + v['height']
                cropped_image = im.crop(box=(left, top, right, bottom))
                cropped_image.save(fp=dst_filepath, format='PNG')


def main():
    workpath = tempfile.mkdtemp(dir='.')

    # 1. Make random images.
    tools.make_random_png24_files(width=(1, 64), height=(1, 64), num_files=4, dirpath=workpath)
    tools.make_random_bmp_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)
    tools.make_random_jpeg_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)

    # 2. Pack multiple images of different sizes or formats into one image.
    input_filepaths = [
        os.path.join(workpath, '*.*'),
    ]
    output_filepath = os.path.join(workpath, 'atlas.png')
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

    # 3. Unpack it.
    unpacker = Unpacker(
        image_filepath=output_filepath,
        configuration_filepath=os.path.splitext(output_filepath)[0] + '.json'
    )
    unpacker.unpack(dirpath=tempfile.mkdtemp(dir=workpath))


if __name__ == '__main__':
    main()
