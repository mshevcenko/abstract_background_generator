from enum import Enum

from image_generator.algorithms.attractor_algorithm import AttractorAlgorithm
from image_generator.algorithms.attractors.lorenz_attractor import LorenzAttractor
from image_generator.algorithms.diamond_square import DiamondGenerator
from image_generator.algorithms.geometric_shape_algorithm import GeometricShapesAlgorithm
from image_generator.algorithms.gradient_algorithm import GradientAlgorithm
from image_generator.algorithms.hex_pattern_algorithm import HexPatternAlgorithm
from image_generator.algorithms.julia_algorithm import JuliaMandelbrotAlgorithm
from image_generator.algorithms.mandelbrot_algorithm import MandelbrotAlgorithm
from image_generator.algorithms.plain_algorithm import PlainAlgorithm
from image_generator.algorithms.smooth_wave_background_algorithm import SmoothWaveBackgroundAlgorithm
from image_generator.algorithms.spirograph_algorithm import SpirographAlgorithm
from image_generator.algorithms.voronoi_algorithm import VoronoiAlgorithm
from image_generator.algorithms.wfc_algorithm import WFCAlgorithm
from image_generator.algorithms.flow_field_algorithm import FlowFieldGenerator
from image_generator.algorithms.noises import ProceduralBackgroundGenerator
from image_generator.algorithms.dragon_curve_algorithm import DragonCurveGenerator

lorenz_algorithm = AttractorAlgorithm("lorenz_attractor", "Cosmic flow", LorenzAttractor())
plain_algorithm = PlainAlgorithm("plain_algorithm", "Color", "#EAD196")
smooth_wave_algorithm = SmoothWaveBackgroundAlgorithm("smooth_wave_background", "Waves")
gradient_algorithm = GradientAlgorithm("gradient_algorithm", "Gradient")
voronoi_algorithm = VoronoiAlgorithm("voronoi_algorithm", "Cellular pattern")  # to rename
hex_pattern_algorithm = HexPatternAlgorithm("hex_pattern_algorithm", "Hex grid")
wave_function_collapse_algorithm = WFCAlgorithm(visible_name="Pattern replicator")
flow_field_generator = FlowFieldGenerator("flow_field_generator", "Fluid")
procedural_background_generator = ProceduralBackgroundGenerator("procedural_background_generator", "Noises")
geometric_shape_algorithm = GeometricShapesAlgorithm("geometric_shape_algorithm", "Geometric shapes")
dragon_algorithm = DragonCurveGenerator("dragon_curve_algorithm", "Dragon shapes")
mandelbrot_algorithm = MandelbrotAlgorithm()
diamond_square = DiamondGenerator("diamond_square", "Diamond terrain")
julia_mandelbrot_algorithm = JuliaMandelbrotAlgorithm()
spirograph_algorithm = SpirographAlgorithm()


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
    geometric_shape = 9
    dragon_algorithm = 10
    mandelbrot = 11
    diamond = 12
    julia_mandelbrot = 13
    spirograph_algorithm = 14


algorithm_instances_list = [
    lorenz_algorithm,
    plain_algorithm,
    smooth_wave_algorithm,
    gradient_algorithm,
    voronoi_algorithm,
    hex_pattern_algorithm,
    wave_function_collapse_algorithm,
    flow_field_generator,
    procedural_background_generator,
    geometric_shape_algorithm,
    dragon_algorithm,
    mandelbrot_algorithm,
    diamond_square,
    julia_mandelbrot_algorithm,
    spirograph_algorithm,
]
