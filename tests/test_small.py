import unittest

import utils


class SmallTest(unittest.TestCase):

    def setUp(self):
        """Every test in this class will do this"""
        utils.wait()
        utils.debug_pid()

    def test_small1(self):
        self.assertTrue(False)

    def test_small2(self):
        self.assertTrue(False)
