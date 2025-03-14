import enum
from typing import List
from PIL.Image import Image
from abc import abstractmethod
from image_generator.parameter import Parameter, check_parameters_unique_names


class GeneratorType(enum.Enum):
    BLENDING = "blending"
    ALGORITHM = "algorithm"


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

    @abstractmethod
    def generate(self,
                 width: int,
                 height: int,
                 **kwargs) -> Image:
        pass

    def to_dict(self) -> dict:
        return {"generator_type": self.generator_type.value,
                "name": self.name,
                "visible_name": self.visible_name,
                "parameters": [parameter.to_dict() for parameter in self.parameters]}
