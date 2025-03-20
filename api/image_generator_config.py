from image_generator.algorithms.attractor_algorithm import AttractorAlgorithm
from image_generator.algorithms.attractors.lorenz_attractor import LorenzAttractor
from image_generator.algorithms.flow_field_algorithm import FlowFieldGenerator
from image_generator.algorithms.noises import ProceduralBackgroundGenerator
from image_generator.algorithms.plain_algorithm import PlainAlgorithm
from image_generator.blendings.alpha_blending import AlphaBlending
from image_generator.image_generator import ImageGenerator

lorenz_algorithm = AttractorAlgorithm("lorenz_attractor", "Lorenz Attractor", LorenzAttractor())
plain_algorithm = PlainAlgorithm("plain_algorithm", "Plain Algorithm", "#EAD196")
alpha_blending = AlphaBlending()
flow_field_generator = FlowFieldGenerator("flow_field_generator", "Flow Field Generator")
procedural_background_generator = ProceduralBackgroundGenerator("procedural_background_generator", "Procedural Background Generator")
image_generator = ImageGenerator(generators=[lorenz_algorithm,
                                             plain_algorithm,
                                             alpha_blending,
                                             flow_field_generator,
                                             procedural_background_generator])
