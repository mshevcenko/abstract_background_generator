import PIL
from PIL.Image import Image
from typing import Optional, List
from image_generator.algorithm import Algorithm
from image_generator.parameter import Parameter, DataType, VisibleType
from image_generator.utils import apply_transparency_mask, hex_to_rgb


class PlainAlgorithm(Algorithm):

    def __init__(self,
                 name: str,
                 visible_name: str,
                 color: str):
        parameters = [
            Parameter(
                name="colors",
                visible_name="Colors",
                description="Color of full layer. Only one color is possible.",
                data_type=DataType.COLORS,
                visible_type=VisibleType.COLORS,
                default=[color],
                min_count=1,
                max_count=1
            )
        ]
        super().__init__(name, visible_name, "Just plain color.", parameters)

    def algorithm(self,
                  width: int,
                  height: int,
                  seed: Optional[int] = None,
                  area: Optional[List[List[bool]]] = None,
                  colors: Optional[List[str]] = None,
                  **kwargs) -> Image:
        r, g, b = hex_to_rgb(colors[0])
        image =  PIL.Image.new("RGBA", (width, height), (r, g, b, 255))
        if area:
            image = apply_transparency_mask(image, area)
        return image
