import numpy as np
import math
import random
from PIL import Image, ImageDraw
from random import randint
from typing import Optional, List, Dict, Any

from image_generator.algorithm import Algorithm
from image_generator.parameter import Parameter, DataType, VisibleType
from image_generator.utils import hex_to_rgb, interpolate_colors


class HexPatternAlgorithm(Algorithm):
    PARAMETERS = [
        Parameter(
            name="colors",
            visible_name="Colors",
            description="Colors used to fill the hexagons in the pattern.",
            data_type=DataType.COLORS,
            visible_type=VisibleType.COLORS,
            default=["#FFA500", "#00FF00"],
            min_count=2,
            max_count=2,
        ),
        Parameter(
            name="hex_size",
            visible_name="Hex Size",
            description="Size of each individual hexagon.",
            data_type=DataType.INTEGER,
            visible_type=VisibleType.SLIDER,
            default=80,
            min_value=10,
            max_value=200
        ),
        Parameter(
            name="spacing",
            visible_name="Spacing",
            description="Distance between adjacent hexagons.",
            data_type=DataType.INTEGER,
            visible_type=VisibleType.SLIDER,
            default=0,
            min_value=0,
            max_value=100
        )
    ]

    def __init__(self, name: str, visible_name: str):
        super().__init__(name, visible_name, "Create image using hexagon tiling.", self.PARAMETERS)

    def algorithm(self,
                  width: int,
                  height: int,
                  seed: Optional[int] = None,
                  area: Optional[List[List[bool]]] = None,
                  colors: Optional[List[str]] = None,
                  hex_size: int = 80,
                  spacing: int = 0,
                  **kwargs) -> Image:
        if seed is not None:
            random.seed(seed)

        if colors is not None and len(colors) >= 2:
            base_color = hex_to_rgb(colors[0])
            secondary_color = hex_to_rgb(colors[1])
        else:
            base_color = (randint(50, 150), randint(50, 150), randint(50, 150))
            secondary_color = (randint(100, 200), randint(100, 200), randint(100, 200))

        img = Image.new("RGB", (width, height), (randint(20, 50), randint(20, 50), randint(20, 50)))
        draw = ImageDraw.Draw(img)

        horizontal_step = hex_size * 0.75 + spacing
        vertical_step = hex_size * (math.sqrt(3) / 2) + spacing

        cols = int(np.ceil(width / horizontal_step)) + 1
        rows = int(np.ceil(height / vertical_step)) + 1

        for i in range(cols):
            for j in range(rows):
                x_center = i * horizontal_step
                y_center = j * vertical_step
                if i % 2 == 1:
                    y_center += vertical_step / 2
                hexagon = [
                    (x_center + hex_size * math.cos(theta), y_center + hex_size * math.sin(theta))
                    for theta in np.linspace(0, 2 * math.pi, 7)
                ]
                t = (i + j) / (cols + rows)
                color = interpolate_colors(base_color, secondary_color, t)
                draw.polygon(hexagon, fill=color, outline=(20, 20, 20))
        return img

if __name__ == '__main__':
    wfc_alg = HexPatternAlgorithm("gradient_algorithm", "Gradient Algorithm")
    img = wfc_alg.algorithm(1920, 1080, None, None, ["#ffffff20"], 10, 0)
    img.show()