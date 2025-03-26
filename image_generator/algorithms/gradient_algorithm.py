import numpy as np
import math
import random
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
            default=["#123456", "#654321"],
            min_count=2,
            max_count=2,
        ),
        Parameter(
            name="angle",
            visible_name="Angle",
            data_type=DataType.FLOAT,
            visible_type=VisibleType.SLIDER,
            default=0.0,
            min_value=0.0,
            max_value=360.0,
        )
    ]

    def __init__(self, name: str, visible_name: str):
        super().__init__(name, visible_name, self.PARAMETERS)

    def algorithm(self,
                  width: int,
                  height: int,
                  seed: Optional[int] = None,
                  area: Optional[List[List[bool]]] = None,
                  colors: Optional[List[str]] = None,
                  angle: float = 0.0) -> Image:
        if seed is not None:
            random.seed(seed)

        if colors is not None and len(colors) >= 2:
            base_color = hex_to_rgb(colors[0])
            secondary_color = hex_to_rgb(colors[1])
        else:
            base_color = (randint(50, 150), randint(50, 150), randint(50, 150))
            secondary_color = (randint(100, 255), randint(100, 255), randint(100, 255))

        theta = math.radians(angle)
        direction = (math.cos(theta), math.sin(theta))

        corners = np.array([[0, 0], [width, 0], [0, height], [width, height]])
        dots = corners[:, 0] * direction[0] + corners[:, 1] * direction[1]
        min_dot = dots.min()
        max_dot = dots.max()

        x_coords, y_coords = np.meshgrid(np.arange(width), np.arange(height))
        dots_pixels = x_coords * direction[0] + y_coords * direction[1]
        t = (dots_pixels - min_dot) / (max_dot - min_dot)

        base_arr = np.array(base_color, dtype=np.float32).reshape(1, 1, 3)
        sec_arr = np.array(secondary_color, dtype=np.float32).reshape(1, 1, 3)
        gradient_arr = (base_arr * (1 - t[..., None]) + sec_arr * t[..., None]).astype(np.uint8)

        img = Image.fromarray(gradient_arr, "RGB")
        return img