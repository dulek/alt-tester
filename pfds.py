from lm_pickers.avoid import AvoidLMPicker
from lm_pickers.rand import RandomLMPicker
from lm_pickers.farthest import FarthestLMPicker, FarthestBLMPicker
from lm_pickers.optimized_farthest import OptimizedFarthestLMPicker,\
    OptimizedFarthestBLMPicker
from lm_pickers.optimized_rand import OptimizedRandomLMPicker
from lm_pickers.optimized_planar import OptimizedPlanarLMPicker,\
    OptimizedPlanarBLMPicker
from lm_pickers.planar import PlanarLMPicker, PlanarBLMPicker
from path_finders.dijkstra import Dijkstra
from path_finders.astar import AStar
from path_finders.astar_landmarks import AStarLandmarks

runs = 2

pfds = {
    'Dijkstra': {
        'class': Dijkstra,
        'lm_picker': None,
        'runs': 1,
    },
    'A*': {
        'class': AStar,
        'lm_picker': None,
        'runs': 1,
    },
    'ALT-Random': {
        'class': AStarLandmarks,
        'lm_picker': RandomLMPicker,
        'runs': runs,
    },
    'ALT-Farthest': {
        'class': AStarLandmarks,
        'lm_picker': FarthestLMPicker,
        'runs': runs,
    },
    'ALT-FarthestB': {
        'class': AStarLandmarks,
        'lm_picker': FarthestBLMPicker,
        'runs': runs,
    },
    'ALT-Planar': {
        'class': AStarLandmarks,
        'lm_picker': PlanarLMPicker,
        'runs': 1,
    },
    'ALT-PlanarB': {
        'class': AStarLandmarks,
        'lm_picker': PlanarBLMPicker,
        'runs': 1,
    },
    'ALT-Avoid': {
        'class': AStarLandmarks,
        'lm_picker': AvoidLMPicker,
        'runs': runs,
    },
    'ALT-OptimizedFarthest': {
        'class': AStarLandmarks,
        'lm_picker': OptimizedFarthestLMPicker,
        'runs': runs,
    },
    'ALT-OptimizedFarthestB': {
        'class': AStarLandmarks,
        'lm_picker': OptimizedFarthestBLMPicker,
        'runs': runs,
    },
    'ALT-OptimizedPlanar': {
        'class': AStarLandmarks,
        'lm_picker': OptimizedPlanarLMPicker,
        'runs': runs,
    },
    'ALT-OptimizedPlanarB': {
        'class': AStarLandmarks,
        'lm_picker': OptimizedPlanarBLMPicker,
        'runs': runs,
    },
    'ALT-OptimizedRandom': {
        'class': AStarLandmarks,
        'lm_picker': OptimizedRandomLMPicker,
        'runs': runs,
    },
}
