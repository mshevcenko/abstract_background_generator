import matplotlib.pyplot as plt
from image_generator.image_generator import ImageGenerator
from image_generator.algorithms.attractor_algorithm import AttractorAlgorithm
from image_generator.algorithms.attractors.lorenz_attractor import LorenzAttractor


if __name__ == '__main__':
    generator = AttractorAlgorithm("lorenz_attractor", "Lorenz Attractor", LorenzAttractor())
    print(generator.to_dict())
    image_generator = ImageGenerator(generators=[generator])
    query = {
        "width": 1024,
        "height": 768,
        "layer_query": {
            "name": "lorenz_attractor",
            "generator_type": "algorithm",
            "values": {
                "scale": [1.0, 1.0],
                "offset_x": [0.0, 0.0],
                "offset_y": [0.0, 0.0]
            },
        }
    }
    image = image_generator.generate_image(query)
    plt.figure(figsize=(10, 8))
    plt.imshow(image)
    plt.axis('off')
    plt.show()
