from PIL.Image import Image
from abc import abstractmethod
from typing import List, Optional, Dict, Any
from image_generator.parameter import Parameter, check_values, fill_default_values, filter_values
from image_generator.generator import Generator, GeneratorType, GeneratorModel


class AlgorithmModel(GeneratorModel):
    pass


class Algorithm(Generator):

    def __init__(self,
                 name: str,
                 visible_name: str,
                 parameters: List[Parameter]):
        super().__init__(GeneratorType.ALGORITHM, name, visible_name, parameters)
        self.model = AlgorithmModel(**self.model.dict())

    @abstractmethod
    def algorithm(self,
                  width: int,
                  height: int,
                  seed: Optional[int] = None,
                  area: Optional[List[List[bool]]] = None,
                  colors: Optional[List[str]] = None,
                  **kwargs) -> Image:
        pass

    def generate(self,
                 width: int,
                 height: int,
                 values: Dict[str, Any] = None) -> Image:
        if not values:
            values = {}
        check_values(self.parameters, values)
        filtered_values = filter_values(self.parameters, values, allow_list=["seed", "colors", "area"])
        filled_values = fill_default_values(self.parameters, filtered_values)
        return self.algorithm(width, height, **filled_values)
