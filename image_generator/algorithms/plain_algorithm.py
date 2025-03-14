import PIL
from PIL.Image import Image
from typing import Optional, List, Tuple
from image_generator.algorithm import Algorithm
from image_generator.parameter import Parameter, DataType, VisibleType


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        raise ValueError(f"Hex color must be 6 characters long {hex_color}")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return r, g, b


class PlainAlgorithm(Algorithm):

    def __init__(self,
                 name: str,
                 visible_name: str,
                 color: str):
        parameters = [
            Parameter(
                name="colors",
                visible_name="Colors",
                data_type=DataType.COLORS,
                visible_type=VisibleType.COLORS,
                default=[color],
                min_count=1,
                max_count=1
            )
        ]
        super().__init__(name, visible_name, parameters)

    def algorithm(self,
                  width: int,
                  height: int,
                  seed: Optional[int] = None,
                  area: Optional[List[List[bool]]] = None,
                  colors: Optional[List[str]] = None,
                  **kwargs) -> Image:
        r, g, b = hex_to_rgb(colors[0])
        return PIL.Image.new("RGBA", (width, height), (r, g, b, 255))

