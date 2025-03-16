from enum import Enum
from typing import List
from PIL.Image import Image
from abc import abstractmethod
from pydantic import BaseModel
from image_generator.parameter import Parameter, check_parameters_unique_names, ParameterModel


class GeneratorType(str, Enum):
    BLENDING = "blending"
    ALGORITHM = "algorithm"


class GeneratorModel(BaseModel):
    generator_type: GeneratorType
    name: str
    visible_name: str
    parameters: List[ParameterModel]


class Generator:

    def __init__(self,
                 generator_type:  GeneratorType,
                 name: str,
                 visible_name: str,
                 parameters: List[Parameter]):
        self.generator_type = generator_type
        self.name = name
        self.visible_name = visible_name
        self.parameters = parameters
        check_parameters_unique_names(self.parameters)
        self.model = GeneratorModel(
            generator_type=self.generator_type,
            name=self.name,
            visible_name=self.visible_name,
            parameters=[parameter.model for parameter in self.parameters],
        )

    @abstractmethod
    def generate(self,
                 width: int,
                 height: int,
                 **kwargs) -> Image:
        pass
