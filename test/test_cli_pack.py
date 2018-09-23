#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import os
import shutil
import subprocess
import tempfile
from unittest import TestCase, skipIf

import sys
sys.path.append('../')
from image_packer import tools


class TestCliPack(TestCase):

    @classmethod
    def setUpClass(cls):
        logging.disable(logging.CRITICAL)

    @classmethod
    def tearDownClass(cls):
        logging.disable(logging.NOTSET)

    @skipIf(shutil.which('impack') is None, 'impack command not found.')
    def test_cli(self):
        command = 'impack -h'
        returncode = subprocess.call(command.split(), stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        self.assertEqual(returncode, 0)

        command = 'impack'
        returncode = subprocess.call(command.split(), stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        self.assertEqual(returncode, 2)

        with tempfile.TemporaryDirectory() as workpath:
            tools.make_random_png32_files(width=(1, 64), height=(1, 64), num_files=4, dirpath=workpath)
            tools.make_random_bmp_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)
            tools.make_random_jpeg_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)

            output_filepath = workpath + '/output.png'

            command = 'impack -i {i} -o {o} -w {w}'.format(
                i=workpath + '/*.*',
                o=output_filepath,
                w=100
            )
            returncode = subprocess.call(command.split(), stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            self.assertEqual(returncode, 0)
            self.assertTrue(os.path.exists(output_filepath))

        with tempfile.TemporaryDirectory() as workpath:
            tools.make_random_png32_files(width=(1, 64), height=(1, 64), num_files=4, dirpath=workpath)
            tools.make_random_bmp_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)
            tools.make_random_jpeg_files(width=(1, 64), height=(1, 64), num_files=3, dirpath=workpath)

            output_filepath = workpath + '/output.png'

            command = 'impack -i {i} -o {o} -w 1 --disable-auto-size'.format(
                i=workpath + '/*.*',
                o=output_filepath,
            )
            returncode = subprocess.call(command.split(), stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            self.assertEqual(returncode, 1)
            self.assertFalse(os.path.exists(output_filepath))
