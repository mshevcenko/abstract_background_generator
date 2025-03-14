import json
import matplotlib.pyplot as plt
from image_generator.algorithms.plain_algorithm import PlainAlgorithm
from image_generator.blendings.alpha_blending import AlphaBlending
from image_generator.image_generator import ImageGenerator
from image_generator.algorithms.attractor_algorithm import AttractorAlgorithm
from image_generator.algorithms.attractors.lorenz_attractor import LorenzAttractor


if __name__ == '__main__':
    lorenz_algorithm = AttractorAlgorithm("lorenz_attractor", "Lorenz Attractor", LorenzAttractor())
    plain_algorithm = PlainAlgorithm("plain_algorithm", "Plain Algorithm", "#EAD196")
    alpha_blending = AlphaBlending()
    image_generator = ImageGenerator(generators=[lorenz_algorithm, plain_algorithm, alpha_blending])
    print(image_generator.to_dict())
    with open("example_queries/simple_alpha_blending_1.json", "r") as file:
        query = json.load(file)
    image = image_generator.generate_image(query)
    plt.figure(figsize=(10, 8))
    plt.imshow(image)
    plt.axis('off')
    plt.show()
    # query = {
    #     "width": 1024,
    #     "height": 768,
    #     "layer_query": {
    #         "name": "lorenz_attractor",
    #         "generator_type": "algorithm",
    #         "values": {
    #             "scale": [1.0, 1.0],
    #             "offset_x": [0.0, 0.0],
    #             "offset_y": [0.0, 0.0]
    #         },
    #     }
    # }
    # query = {
    #     "width": 1024,
    #     "height": 768,
    #     "layer_query": {
    #         "name": "alpha_blending",
    #         "generator_type": "blending",
    #         "layers": [
    #             {
    #                 "name": "lorenz_attractor",
    #                 "generator_type": "algorithm",
    #                 "values": {
    #                     "scale": [1.0, 1.0],
    #                     "offset_x": [0.0, 0.0],
    #                     "offset_y": [0.0, 0.0]
    #                 },
    #                 "blending_values": {
    #                     "opacity": 1.0
    #                 }
    #             },
    #             {
    #                 "name": "plain_algorithm",
    #                 "generator_type": "algorithm",
    #                 "values": {
    #                     "colors": ["EAD196"],
    #                 },
    #                 "blending_values": {
    #                     "opacity": 0.5
    #                 }
    #             },
    #             {
    #                 "name": "plain_algorithm",
    #                 "generator_type": "algorithm",
    #                 "values": {
    #                     "colors": ["034C53"],
    #                 },
    #                 "blending_values": {
    #                     "opacity": 0.5
    #                 }
    #             }
    #         ]
    #     }
    # }

