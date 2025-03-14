from PIL import Image
from typing import Optional, List, Dict
from image_generator.generator import GeneratorType, Generator


class Layer:

    def __init__(self,
                 layer_query: Dict,
                 generators_dict: Dict[str, Generator]):
        self.layer_query = layer_query
        self.generators_dict = generators_dict
        self.check()
        self.generator_type = self.layer_query["generator_type"]
        self.generator_name = self.layer_query["name"]
        self.generator = self.generators_dict[self.generator_name]
        self.values = {}
        self.layers = {}
        self.blending_values = {}
        if "values" in self.layer_query:
            self.values = self.layer_query["values"]
        if "blending_values" in self.layer_query:
            self.blending_values = self.layer_query["blending_values"]
        if "layers" in self.layer_query:
            self.layers = [Layer(layer_query=query, generators_dict=self.generators_dict) for query in self.layer_query["layers"]]

    def check(self) -> None:
        if "generator_type" not in self.layer_query:
            raise ValueError(f"No layer query parameter \"generator_type\" in {str(self.layer_query)}")
        if "name" not in self.layer_query:
            raise ValueError(f"No layer query parameter \"name\" in {str(self.layer_query)}")
        generator_name = self.layer_query["name"]
        if generator_name not in self.generators_dict:
            raise ValueError(f"Generator with name \"{generator_name}\" does not exist")
        generator_type = self.layer_query["generator_type"]
        if generator_type != GeneratorType.BLENDING.value and generator_type != GeneratorType.ALGORITHM.value:
            raise ValueError(f"Generator type \"{generator_type}\" is not supported! Supported generator types: {GeneratorType.BLENDING.value}, {GeneratorType.ALGORITHM.value}")

    def generate(self,
                 width: int,
                 height: int,
                 seed: Optional[int] = None,
                 colors: Optional[List[str]] = None,
                 area: Optional[List[List[bool]]] = None) -> Image:
        values = self.values.copy()
        if seed:
            values["seed"] = seed
        if colors:
            values["colors"] = colors
        if area:
            values["area"] = area
        if self.generator_type == GeneratorType.ALGORITHM.value:
            return self.generator.generate(width, height, values=values)
        else:
            return self.generator.generate(width, height, values=values, layers=self.layers)
