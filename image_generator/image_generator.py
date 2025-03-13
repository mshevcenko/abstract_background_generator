from typing import List, Dict

from PIL.Image import Image

from image_generator.generator import Generator
from image_generator.layer import Layer


def check_query(query: Dict) -> None:
    if "width" not in query:
        raise ValueError(f"No query parameter \"width\" in {str(query)}")
    if "height" not in query:
        raise ValueError(f"No query parameter \"height\" in {str(query)}")
    if "layer_query" not in query:
        raise ValueError(f"No query parameter \"layer_query\" in {str(query)}")


class ImageGenerator:

    def __init__(self,
                 generators: List[Generator]):
        self.generators = generators
        self.generators_dict = {}
        self.create_generators_dict()

    def generate_image(self,
                       query: Dict) -> Image:
        check_query(query)
        width = query["width"]
        height = query["height"]
        layer_query = query["layer_query"]
        seed = None
        if "seed" in query:
            seed = query["seed"]
        layer = Layer(layer_query, self.generators_dict)
        return layer.generate(width, height, seed=seed)

    def to_dict(self) -> Dict:
        return [generator.to_dict() for generator in self.generators]

    def create_generators_dict(self) -> None:
        for generator in self.generators:
            if generator.name in self.generators_dict:
                raise ValueError(f"Parameters have same name: \"{generator.name}\"")
            self.generators_dict[generator.name] = generator
