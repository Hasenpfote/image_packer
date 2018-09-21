#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import math
import random
import uuid
from unittest import TestCase

import sys
sys.path.append('../')
from image_packer import blf
from image_packer import blf_solver


class TestBlfSolver(TestCase):
    @classmethod
    def setUpClass(cls):
        logging.disable(logging.CRITICAL)

    @classmethod
    def tearDownClass(cls):
        logging.disable(logging.NOTSET)

    @staticmethod
    def next_power_of_2(x):
        return 2.0 ** math.ceil(math.log2(x))

    @staticmethod
    def is_power_of_2(x):
        p = math.log2(x)
        return math.ceil(p) == math.floor(p)

    @staticmethod
    def make_random_pieces(width, height, num_pieces):
        if isinstance(width, tuple):
            min_width, max_width = width
        else:
            min_width, max_width = width, width

        if isinstance(height, tuple):
            min_height, max_height = height
        else:
            min_height, max_height = height, height

        pieces = list()
        for _ in range(num_pieces):
            w = random.randint(min_width, max_width)
            h = random.randint(min_height, max_height)
            pieces.append(blf.Piece(uid=uuid.uuid4(), size=blf.Size(w, h)))

        return pieces

    def test_calc_minimum_container_size(self):
        margin = blf.Thickness(top=1, right=1, bottom=1, left=1)

        regions = list()

        region1 = blf.Region(
            uid=uuid.uuid4(),
            top=margin.bottom + 10,
            right=margin.left + 10,
            bottom=margin.bottom,
            left=margin.left
        )
        regions.append(region1)

        region2 = blf.Region(
            uid=uuid.uuid4(),
            top=margin.bottom + 5,
            right=region1.right + margin.right + margin.left + 5,
            bottom=margin.bottom,
            left=region1.right + margin.right + margin.left
        )
        regions.append(region2)

        size = blf_solver.calc_minimum_container_size(regions, margin)
        self.assertEqual(size.width, region2.right + margin.right)
        self.assertEqual(size.height, region1.top + margin.top)

    def test_calc_container_size(self):
        margin = blf.Thickness(top=1, right=1, bottom=1, left=1)

        regions = list()

        region1 = blf.Region(
            uid=uuid.uuid4(),
            top=margin.bottom + 10,
            right=margin.left + 10,
            bottom=margin.bottom,
            left=margin.left
        )
        regions.append(region1)

        region2 = blf.Region(
            uid=uuid.uuid4(),
            top=margin.bottom + 5,
            right=region1.right + margin.right + margin.left + 5,
            bottom=margin.bottom,
            left=region1.right + margin.right + margin.left
        )
        regions.append(region2)

        container_width = 100
        #
        size = blf_solver.calc_container_size(container_width, regions, margin, False, False)
        self.assertEqual(size.width, container_width)
        self.assertEqual(size.height, region1.top + margin.top)
        #
        size = blf_solver.calc_container_size(container_width, regions, margin, True, False)
        self.assertEqual(size.width, region2.right + margin.right)
        self.assertEqual(size.height, region1.top + margin.top)
        #
        size = blf_solver.calc_container_size(container_width, regions, margin, False, True)
        self.assertEqual(size.width, self.next_power_of_2(container_width))
        self.assertEqual(size.height, self.next_power_of_2(region1.top + margin.top))
        #
        size = blf_solver.calc_container_size(container_width, regions, margin, True, True)
        self.assertEqual(size.width, self.next_power_of_2(region2.right + margin.right))
        self.assertEqual(size.height, self.next_power_of_2(region1.top + margin.top))

    def test_calc_filling_rate(self):
        margin = blf.Thickness(top=1, right=1, bottom=1, left=1)

        regions = list()

        region1 = blf.Region(
            uid=uuid.uuid4(),
            top=margin.bottom + 10,
            right=margin.left + 10,
            bottom=margin.bottom,
            left=margin.left
        )
        regions.append(region1)

        region2 = blf.Region(
            uid=uuid.uuid4(),
            top=margin.bottom + 5,
            right=region1.right + margin.right + margin.left + 5,
            bottom=margin.bottom,
            left=region1.right + margin.right + margin.left
        )
        regions.append(region2)

        container_size = blf.Size(region2.right + margin.right, region1.top + margin.top)

        expected_area = sum(region.area for region in regions) / container_size.area
        area = blf_solver.calc_filling_rate(container_size, regions)
        self.assertAlmostEqual(area, expected_area)

    def test_default(self):
        pieces = self.make_random_pieces(width=(1, 64), height=(1, 64), num_pieces=10)
        result = blf_solver.solve(pieces=pieces, container_width=1)
        self.assertTrue(isinstance(result, tuple))
        self.assertTrue(isinstance(result[0], int))
        self.assertTrue(isinstance(result[1], int))
        self.assertTrue(isinstance(result[2], list))
        self.assertEqual(len(pieces), len(result[2]))

    def test_margin(self):
        pieces = self.make_random_pieces(width=(1, 64), height=(1, 64), num_pieces=10)
        options = {
            'margin': blf.Thickness(top=1, right=1, bottom=1, left=1),
        }
        result = blf_solver.solve(pieces=pieces, container_width=1, options=options)
        self.assertTrue(isinstance(result, tuple))
        self.assertTrue(isinstance(result[0], int))
        self.assertTrue(isinstance(result[1], int))
        self.assertTrue(isinstance(result[2], list))
        self.assertEqual(len(pieces), len(result[2]))

    def test_collapse_margin(self):
        pieces = self.make_random_pieces(width=(1, 64), height=(1, 64), num_pieces=10)
        options = {
            'margin': blf.Thickness(top=1, right=1, bottom=1, left=1),
            'collapse_margin': True
        }
        result = blf_solver.solve(pieces=pieces, container_width=1, options=options)
        self.assertTrue(isinstance(result, tuple))
        self.assertTrue(isinstance(result[0], int))
        self.assertTrue(isinstance(result[1], int))
        self.assertTrue(isinstance(result[2], list))
        self.assertEqual(len(pieces), len(result[2]))

    def test_disable_auto_size(self):
        pieces = self.make_random_pieces(width=64, height=64, num_pieces=10)
        options = {
            'margin': blf.Thickness(top=1, right=1, bottom=1, left=1),
            'enable_auto_size': False
        }
        result = blf_solver.solve(pieces=pieces, container_width=66, options=options)
        self.assertTrue(isinstance(result, tuple))
        self.assertTrue(isinstance(result[0], int))
        self.assertTrue(isinstance(result[1], int))
        self.assertTrue(isinstance(result[2], list))
        self.assertEqual(len(pieces), len(result[2]))
        #
        with self.assertRaises(blf.LocationNotFoundError):
            blf_solver.solve(pieces=pieces, container_width=64, options=options)

    def test_force_pow2(self):
        pieces = self.make_random_pieces(width=(1, 64), height=(1, 64), num_pieces=10)
        options = {
            'margin': blf.Thickness(top=1, right=1, bottom=1, left=1),
            'force_pow2': True
        }
        result = blf_solver.solve(pieces=pieces, container_width=1, options=options)
        self.assertTrue(isinstance(result, tuple))
        self.assertTrue(isinstance(result[0], int))
        self.assertTrue(isinstance(result[1], int))
        self.assertTrue(isinstance(result[2], list))
        self.assertTrue(self.is_power_of_2(result[0]))
        self.assertTrue(self.is_power_of_2(result[1]))
        self.assertEqual(len(pieces), len(result[2]))

    def test_combination(self):
        keys = ('collapse_margin', 'enable_auto_size', 'force_pow2')
        patterns = (
            (True, True, True),
            (True, False, False),
            (True, True, False),
            (True, False, True),
            (False, True, False),
            (False, True, True),
            (False, False, True),
            (False, False, False),
        )

        pieces = self.make_random_pieces(width=(1, 64), height=(1, 64), num_pieces=10)
        margin = blf.Thickness(top=1, right=1, bottom=1, left=1)
        container_width = 66
        for pattern in patterns:
            options = {k: v for k, v in zip(keys, pattern)}
            options['margin'] = margin
            result = blf_solver.solve(pieces=pieces, container_width=container_width, options=options)
            self.assertTrue(isinstance(result, tuple))
            self.assertTrue(isinstance(result[0], int))
            self.assertTrue(isinstance(result[1], int))
            self.assertTrue(isinstance(result[2], list))
            if options['force_pow2']:
                self.assertTrue(self.is_power_of_2(result[0]))
                self.assertTrue(self.is_power_of_2(result[1]))
            self.assertEqual(len(pieces), len(result[2]))

    def test_concurrent_processing(self):
        pieces = self.make_random_pieces(width=64, height=64, num_pieces=100)
        options = {
            'margin': blf.Thickness(top=1, right=1, bottom=1, left=1),
            'enable_auto_size': False
        }
        result = blf_solver.solve(pieces=pieces, container_width=66, options=options)
        self.assertTrue(isinstance(result, tuple))
        self.assertTrue(isinstance(result[0], int))
        self.assertTrue(isinstance(result[1], int))
        self.assertTrue(isinstance(result[2], list))
        self.assertEqual(len(pieces), len(result[2]))
        #
        with self.assertRaises(blf.LocationNotFoundError):
            blf_solver.solve(pieces=pieces, container_width=64, options=options)
