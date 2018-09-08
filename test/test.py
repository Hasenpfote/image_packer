#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import uuid
import random
import glob
from PIL import Image

import sys
sys.path.append('../')
from image_packer import blf


def remove_image_files(dirpath):

    filepath = '{}/{}'.format(dirpath, '*.png')
    for filename in glob.glob(filepath):
        os.remove(filename)


def make_random_size_image(dirpath, n):

    for index, _ in enumerate(range(n)):
        w = random.randint(1, 64)
        h = random.randint(1, 64)
        image = Image.new('RGBA', (w, h), 'white')
        image.save('{}/{}.png'.format(dirpath, index))


def main():

    dataset_size = 50
    dirpath = './temp'
    remove_image_files(dirpath=dirpath)
    make_random_size_image(dirpath=dirpath, n=dataset_size)
    filepath = filepath = '{}/{}'.format(dirpath, '*.png')

    uid_to_filepath = dict()
    pieces = list()

    padding = (1, 1, 1, 1) # top, right, bottom, left

    for filepath in glob.glob(filepath):
        with Image.open(filepath) as im:
            w = im.width + padding[1] + padding[3]
            h = im.height + padding[0] + padding[2]
            uid = uuid.uuid4()
            uid_to_filepath[uid] = filepath
            pieces.append(blf.Piece(uid=uid, width=w, height=h))

    container_width = 256
    container_width, container_height, rects = blf.solve(pieces, container_width)

    blank_image = Image.new('RGBA', (container_width, container_height), 'black')

    for rect in rects:
        x = rect.x + padding[3]
        y = (container_height - rect.top) + padding[0]
        filepath = uid_to_filepath.get(rect.uid)
        with Image.open(filepath) as im:
            blank_image.paste(im, (x, y))

    blank_image.save(dirpath + '/drawn_image.png')
    blank_image.show()


if __name__ == '__main__':
    main()
