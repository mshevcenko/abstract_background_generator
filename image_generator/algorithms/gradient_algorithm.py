import numpy as np
from PIL import Image, ImageDraw
from random import randint
from typing import Optional, List, Dict, Any

from image_generator.algorithm import Algorithm
from image_generator.parameter import Parameter, DataType, VisibleType
from image_generator.utils import hex_to_rgb, interpolate_colors


class GradientAlgorithm(Algorithm):
    PARAMETERS = [
        Parameter(
            name="colors",
            visible_name="Colors",
            data_type=DataType.COLORS,
            visible_type=VisibleType.COLORS,
            default=["#123456", "#654321"]
        )
    ]

    def __init__(self,
                 name: str,
                 visible_name: str):
        super().__init__(name, visible_name, self.PARAMETERS)

    def algorithm(self,
                  width: int,
                  height: int,
                  seed: Optional[int] = None,
                  area: Optional[List[List[bool]]] = None,
                  colors: Optional[List[str]] = None,
                  **kwargs) -> Image:
        if seed is not None:
            np.random.seed(seed)
        if colors is not None and len(colors) >= 2:
            base_color = hex_to_rgb(colors[0])
            secondary_color = hex_to_rgb(colors[1])
        else:
            base_color = (randint(50, 150), randint(50, 150), randint(50, 150))
            secondary_color = (randint(100, 255), randint(100, 255), randint(100, 255))

        img = Image.new("RGB", (width, height), (0, 0, 0))
        draw = ImageDraw.Draw(img)

        for i in range(height):
            t = i / height
            color = interpolate_colors(base_color, secondary_color, t)
            draw.line([(0, i), (width, i)], fill=color)
        return img