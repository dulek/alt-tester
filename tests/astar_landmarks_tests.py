import unittest
from mock import Mock

from astar_landmarks import AStarLandmarks

class AStarLandmarksTests(unittest.TestCase):
    def setUp(self):
        self.finder = AStarLandmarks({}, Mock())

    def test_lm_dijkstra(self):
        self.finder.G = {
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

        result = self.finder._dijkstra(1)
        self.assertDictEqual(result, {1: 0, 2: 3, 3: 5})

        result = self.finder._dijkstra(2)
        self.assertDictEqual(result, {1: 3, 2: 0, 3: 8})

        result = self.finder._dijkstra(3)
        self.assertDictEqual(result, {1: 5, 2: 8, 3: 0})
