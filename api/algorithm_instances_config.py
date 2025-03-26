from enum import Enum

from image_generator.algorithms.attractor_algorithm import AttractorAlgorithm
from image_generator.algorithms.attractors.lorenz_attractor import LorenzAttractor
from image_generator.algorithms.gradient_algorithm import GradientAlgorithm
from image_generator.algorithms.hex_pattern_algorithm import HexPatternAlgorithm
from image_generator.algorithms.plain_algorithm import PlainAlgorithm
from image_generator.algorithms.smooth_wave_background_algorithm import SmoothWaveBackgroundAlgorithm
from image_generator.algorithms.voronoi_algorithm import VoronoiAlgorithm
from image_generator.algorithms.wfc_algorithm import WFCAlgorithm
from image_generator.algorithms.flow_field_algorithm import FlowFieldGenerator
from image_generator.algorithms.noises import ProceduralBackgroundGenerator

lorenz_algorithm = AttractorAlgorithm("lorenz_attractor", "Lorenz Attractor", LorenzAttractor())
plain_algorithm = PlainAlgorithm("plain_algorithm", "Plain Algorithm", "#EAD196")
smooth_wave_algorithm = SmoothWaveBackgroundAlgorithm("smooth_wave_background", "Smooth Wave Background")
gradient_algorithm = GradientAlgorithm("gradient_algorithm", "Gradient Algorithm")
voronoi_algorithm = VoronoiAlgorithm("voronoi_algorithm", "Voronoi Algorithm")
hex_pattern_algorithm = HexPatternAlgorithm("hex_pattern_algorithm", "Hex Pattern Algorithm")
wave_function_collapse_algorithm = WFCAlgorithm()
flow_field_generator = FlowFieldGenerator("flow_field_generator", "Flow Field Generator")
procedural_background_generator = ProceduralBackgroundGenerator("procedural_background_generator", "Procedural Background Generator")


class AlgorithmInstancesEnum(Enum):
    lorenz = 0
    plain = 1
    smooth_wave = 2
    gradient = 3
    voronoi = 4
    hex_pattern = 5
    wfc = 6
    flow_field = 7
    noise = 8


algorithm_instances_list = [
    lorenz_algorithm,
    plain_algorithm,
    smooth_wave_algorithm,
    gradient_algorithm,
    voronoi_algorithm,
    hex_pattern_algorithm,
    wave_function_collapse_algorithm,
    flow_field_generator,
    procedural_background_generator
]