from abc import abstractmethod
from typing import List, Any, Dict

from PIL.Image import Image

from image_generator.generator import Generator, GeneratorType
from image_generator.layer import Layer
from image_generator.parameter import Parameter


class Blending(Generator):

    def __init__(self,
                 name: str,
                 visible_name: str,
                 parameters: List[Parameter],
                 blending_parameters: List[Parameter],
                 min_layers_count: int,
                 max_layers_count: int):
        super().__init__(GeneratorType.BLENDING, name, visible_name, parameters)
        self.min_layers_count = min_layers_count
        self.max_layers_count = max_layers_count
        self.blending_parameters = blending_parameters
        self.check()

    @abstractmethod
    def image(self,
              width: int,
              height: int,
              seed: int = None,
              layers: List[Layer] = None,
              **kwargs):
        pass

    def generate(self,
                 width: int,
                 height: int,
                 values: Dict[str, Any] = None,
                 layers: List[Layer] = None) -> Image:
        pass

    def check(self):
        pass

    def create_parameters_dict(self):
        pass

    def create_algorithms_blending_parameters_dict(self):
        pass
