from PIL.Image import Image
from abc import abstractmethod
from image_generator.layer import Layer
from typing import List, Any, Dict, Optional
from image_generator.generator import Generator, GeneratorType, GeneratorModel
from image_generator.parameter import Parameter, check_parameters_unique_names, check_values, filter_values, \
    fill_default_values, ParameterModel


class BlendingModel(GeneratorModel):
    blending_parameters: List[ParameterModel]


class Blending(Generator):

    def __init__(self,
                 name: str,
                 visible_name: str,
                 parameters: List[Parameter],
                 blending_parameters: List[Parameter]):
        super().__init__(GeneratorType.BLENDING, name, visible_name, parameters)
        self.blending_parameters = blending_parameters
        check_parameters_unique_names(self.blending_parameters)
        self.model = BlendingModel(
            **self.model.dict(),
            blending_parameters=[blending_parameter.model for blending_parameter in self.blending_parameters]
        )

    @abstractmethod
    def blending(self,
                 width: int,
                 height: int,
                 layers: List[Layer] = None,
                 seed: int = None,
                 area: Optional[List[List[bool]]] = None,
                 **kwargs) -> Image:
        pass

    def generate(self,
                 width: int,
                 height: int,
                 values: Dict[str, Any] = None,
                 layers: List[Layer] = None) -> Image:
        if not values:
            values = {}
        check_values(self.parameters, values)
        filtered_values = filter_values(self.parameters, values, allow_list=["seed", "area"])
        filled_values = fill_default_values(self.parameters, filtered_values)
        for layer in layers:
            check_values(self.blending_parameters, layer.blending_values)
            layer.blending_values = filter_values(self.blending_parameters, layer.blending_values)
            layer.blending_values = fill_default_values(self.blending_parameters, layer.blending_values)
        return self.blending(width, height, layers, **filled_values)
