from PIL.Image import Image
from abc import abstractmethod
from typing import List, Optional, Dict, Any
from image_generator.parameter import Parameter
from image_generator.generator import Generator, GeneratorType


class Algorithm(Generator):

    def __init__(self,
                 name: str,
                 visible_name: str,
                 parameters: List[Parameter]):
        super().__init__(GeneratorType.ALGORITHM, name, visible_name, parameters)
        self.parameters_dict: Dict[str, Parameter] = {}
        self.create_parameters_dict()

    @abstractmethod
    def algorithm(self,
                  width: int,
                  height: int,
                  seed: Optional[int] = None,
                  colors: Optional[List[str]] = None,
                  area: Optional[List[List[bool]]] = None,
                  **kwargs) -> Image:
        pass

    def generate(self,
                 width: int,
                 height: int,
                 values: Dict[str, Any] = None) -> Image:
        self.check_values(values)
        filtered_values = self.filter_values(values)
        filled_values = self.fill_default_values(filtered_values)
        return self.algorithm(width, height, **filled_values)

    def check_values(self,
                     values: Dict[str, Any] = None) -> None:
        for parameter_name, value in values.items():
            if parameter_name in self.parameters_dict:
                self.parameters_dict[parameter_name].check_value(value)

    def fill_default_values(self,
                            values: Dict[str, Any] = None) -> Dict[str, Any]:
        filled_values = values.copy()
        for parameter_name, parameter in self.parameters_dict.items():
            if parameter_name not in values:
                filled_values[parameter_name] = parameter.default
        return filled_values

    def filter_values(self,
                      values: Dict[str, Any] = None) -> Dict[str, Any]:
        filtered_values: Dict[str, Any] = {}
        for parameter_name, value in values.items():
            if not value:
                continue
            if parameter_name in self.parameters_dict \
                    or parameter_name == "seed" \
                    or parameter_name == "area" \
                    or parameter_name == "colors":
                filtered_values[parameter_name] = value
        return filtered_values

    def create_parameters_dict(self) -> None:
        for parameter in self.parameters:
            if parameter.name in self.parameters_dict:
                raise ValueError(f"Parameters have same name: \"{parameter.name}\"")
            self.parameters_dict[parameter.name] = parameter
