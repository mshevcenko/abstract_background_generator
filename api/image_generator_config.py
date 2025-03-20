from image_generator.algorithms.attractor_algorithm import AttractorAlgorithm
from image_generator.algorithms.attractors.lorenz_attractor import LorenzAttractor
from image_generator.algorithms.gradient_algorithm import GradientAlgorithm
from image_generator.algorithms.hex_pattern_algorithm import HexPatternAlgorithm
from image_generator.algorithms.plain_algorithm import PlainAlgorithm
from image_generator.algorithms.smooth_wave_background_algorithm import SmoothWaveBackgroundAlgorithm
from image_generator.algorithms.voronoi_algorithm import VoronoiAlgorithm
from image_generator.blendings.alpha_blending import AlphaBlending
from image_generator.image_generator import ImageGenerator

lorenz_algorithm = AttractorAlgorithm("lorenz_attractor", "Lorenz Attractor", LorenzAttractor())
plain_algorithm = PlainAlgorithm("plain_algorithm", "Plain Algorithm", "#EAD196")
alpha_blending = AlphaBlending()
smooth_wave_algorithm = SmoothWaveBackgroundAlgorithm("smooth_wave_background", "Smooth Wave Background")
gradient_algorithm = GradientAlgorithm("gradient_algorithm", "Gradient Algorithm")
voronoi_algorithm = VoronoiAlgorithm("voronoi_algorithm", "Voronoi Algorithm")
hex_pattern_algorithm = HexPatternAlgorithm("hex_pattern_algorithm", "Hex Pattern Algorithm")
image_generator = ImageGenerator(generators=[lorenz_algorithm, plain_algorithm, alpha_blending, smooth_wave_algorithm, gradient_algorithm, voronoi_algorithm, hex_pattern_algorithm])
