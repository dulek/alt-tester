import unittest

from lib import utils

class UtilsTests(unittest.TestCase):
    def test_all_bfs(self):
        G = {
            1: {
                2: 3,
                3: 5,
            },
            2: {
                1: 3,
            },
            3: {
                1: 5
            }
        }

        result = utils.all_bfs(1, G)
        self.assertDictEqual(result, {1: 0, 2: 1, 3: 1})

        result = utils.all_bfs(2, G)
        self.assertDictEqual(result, {1: 1, 2: 0, 3: 2})

        result = utils.all_bfs(3, G)
        self.assertDictEqual(result, {1: 1, 2: 2, 3: 0})
