[![License](https://img.shields.io/badge/license-MIT-brightgreen.svg)](https://github.com/Hasenpfote/image_packer/blob/master/LICENSE)
[![Build Status](https://travis-ci.com/Hasenpfote/image_packer.svg?branch=master)](https://travis-ci.com/Hasenpfote/image_packer)
[![PyPI version](https://badge.fury.io/py/image-packer.svg)](https://badge.fury.io/py/image-packer)
[![Pyversions](https://img.shields.io/pypi/pyversions/image-packer.svg?style=flat)](https://img.shields.io/pypi/pyversions/image-packer.svg?style=flat)

image_packer
============

## About
Pack multiple images of different sizes or formats into one image.
- Supported image input formats:
  - png, bmp, jpg
- Supported image output formats:
  - png(24 or 32bits)

![atlas](https://raw.githubusercontent.com/Hasenpfote/image_packer/master/example/image/atlas.png)

## Compatibility
image_packer works with Python 3.4 or higher.

## Dependencies
* Pillow

## Installation
```
pip install image-packer
```

## Usage
```python
from image_packer import packer

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
```

## Command-line Tool
```
$ impack -i "./image/*.png" -i "./image/*.jpg" -i "./image/*.bmp" -o "./image/atlas.png" -w 128 -m 1 1 1 1
```

## License
This software is released under the MIT License, see LICENSE.
