from __future__ import annotations
from PIL import Image
from pydantic import BaseModel
from typing import Optional, List, Dict, Union, Tuple
from image_generator.seed_generator import SeedGenerator
from image_generator.generator import GeneratorType, Generator



class LayerQuery(BaseModel):
    name: str
    generator_type: GeneratorType
    values: Optional[Dict[str, Union[int, float, str, List[str], Tuple[int, int], Tuple[float, float], bool]]] = None
    blending_values: Optional[Dict[str, Union[int, float, str, List[str], Tuple[int, int], Tuple[float, float], bool]]] = None
    layers: Optional[List[LayerQuery]] = None


LayerQuery.model_rebuild()


class Layer:

    def __init__(self,
                 layer_query: LayerQuery,
                 generators_dict: Dict[str, Generator]):
        self.layer_query = layer_query
        self.generators_dict = generators_dict
        self.check()
        self.generator_type = layer_query.generator_type
        self.generator_name = layer_query.name
        self.generator = self.generators_dict[self.generator_name]
        self.values = {}
        self.layers = {}
        self.blending_values = {}
        if self.layer_query.values:
            self.values = self.layer_query.values
        if self.layer_query.blending_values:
            self.blending_values = self.layer_query.blending_values
        if self.layer_query.layers:
            self.layers = [Layer(layer_query=query, generators_dict=self.generators_dict) for query in self.layer_query.layers]

    def check(self) -> None:
        generator_name = self.layer_query.name
        if generator_name not in self.generators_dict:
            raise ValueError(f"Generator with name \"{generator_name}\" does not exist")
        generator_type = self.layer_query.generator_type
        if generator_type != GeneratorType.BLENDING and generator_type != GeneratorType.ALGORITHM:
            raise ValueError(f"Generator type \"{generator_type.value}\" is not supported! Supported generator types: {GeneratorType.BLENDING.value}, {GeneratorType.ALGORITHM.value}")

    def generate(self,
                 width: int,
                 height: int,
                 seed: Optional[int] = None,
                 area: Optional[List[List[bool]]] = None) -> Image:
        values = self.values.copy()
        if seed:
            values["seed"] = seed
        if area:
            values["area"] = area
        if self.generator_type == GeneratorType.ALGORITHM:
            return self.generator.generate(width, height, values=values)
        else:
            return self.generator.generate(width, height, values=values, layers=self.layers)

    def generate_seed(self,
                      seed_generator: SeedGenerator,
                      overwrite: bool = False,
                      recursive: bool = True) -> None:
        seed = seed_generator.generate_seed()
        if overwrite or "seed" not in self.values:
            self.values["seed"] = seed
        if recursive:
            for layer in self.layers:
                layer.generate_seed(seed_generator)
