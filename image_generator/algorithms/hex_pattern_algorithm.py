import numpy as np
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
            data_type=DataType.COLORS,
            visible_type=VisibleType.COLORS,
            default=["#FFA500", "#00FF00"]
        ),
        Parameter(
            name="hex_size",
            visible_name="Hex Size",
            data_type=DataType.INTEGER,
            visible_type=VisibleType.SLIDER,
            default=80,
            min_value=10,
            max_value=200
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
        hex_size = kwargs.get("hex_size", 80)

        if colors is not None and len(colors) >= 2:
            base_color = hex_to_rgb(colors[0])
            secondary_color = hex_to_rgb(colors[1])
        else:
            base_color = (randint(50, 150), randint(50, 150), randint(50, 150))
            secondary_color = (randint(100, 200), randint(100, 200), randint(100, 200))

        img = Image.new("RGB", (width, height), (randint(20, 50), randint(20, 50), randint(20, 50)))
        draw = ImageDraw.Draw(img)

        cols = width // hex_size
        rows = height // hex_size

        for i in range(cols + 2):
            for j in range(rows + 2):
                x = i * hex_size * 0.75
                y = j * hex_size * (np.sqrt(3) / 2)
                if i % 2:
                    y += hex_size * (np.sqrt(3) / 4)

                hexagon = [(x + hex_size * np.cos(theta), y + hex_size * np.sin(theta))
                           for theta in np.linspace(0, 2 * np.pi, 7)]
                t = (i + j) / (cols + rows)
                color = interpolate_colors(base_color, secondary_color, t)
                draw.polygon(hexagon, fill=color, outline=(20, 20, 20))
        return img