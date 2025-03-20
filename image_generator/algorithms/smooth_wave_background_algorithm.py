import numpy as np
from PIL import Image, ImageDraw
from random import randint, uniform
from typing import Optional, List, Dict, Any

from image_generator.algorithm import Algorithm
from image_generator.parameter import Parameter, DataType, VisibleType
from image_generator.utils import hex_to_rgb, interpolate_colors


class SmoothWaveBackgroundAlgorithm(Algorithm):
    PARAMETERS = [
        Parameter(
            name="colors",
            visible_name="Colors",
            data_type=DataType.COLORS,
            visible_type=VisibleType.COLORS,
            default=["#FF0000", "#FFFFFF"],
            min_count=2,
            max_count=2,
        ),
        Parameter(
            name="n_layers",
            visible_name="Number of layers",
            data_type=DataType.INTEGER,
            visible_type=VisibleType.SLIDER,
            default=7,
            min_value=1,
            max_value=10
        ),
        Parameter(
            name="monochrome",
            visible_name="Monochrome mode",
            data_type=DataType.BOOL,
            visible_type=VisibleType.CHECKBOX,
            default=True
        )
    ]

    def __init__(self,
                 name: str,
                 visible_name: str):
        super().__init__(name, visible_name, self.PARAMETERS)

    def generate_wave_points(self, width: int, base_y: float, step: float, n_points: int = 250):
        x = np.linspace(0, width, n_points)
        y = np.full_like(x, base_y, dtype=float)
        harmonics = randint(3, 5)
        for _ in range(harmonics):
            freq = uniform(1, 4)
            phase = uniform(0, 2 * np.pi)
            amp = uniform(step * 0.25, step * 0.6)
            y += np.sin((x / width) * np.pi * freq + phase) * amp
        return list(zip(x, y))

    def algorithm(self,
                  width: int,
                  height: int,
                  seed: Optional[int] = None,
                  area: Optional[List[List[bool]]] = None,
                  colors: Optional[List[str]] = None,
                  **kwargs) -> Image:
        if seed is not None:
            np.random.seed(seed)
        n_layers = kwargs.get("n_layers", 7)
        monochrome = kwargs.get("monochrome", True)

        if colors is not None and len(colors) >= 1:
            base_color = hex_to_rgb(colors[0])
        else:
            base_color = (randint(50, 150), randint(50, 150), randint(50, 150))
        secondary_color = (255, 255, 255)

        img = Image.new("RGB", (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        step = height // n_layers
        gradient = Image.new("RGB", (width, height), (255, 255, 255))
        gradient_draw = ImageDraw.Draw(gradient)

        for i in range(n_layers):
            layer_color = base_color if monochrome else (hex_to_rgb(colors[i % len(colors)])
                                                         if colors and len(colors) > 0 else base_color)
            y_offset = i * step + randint(-step // 5, step // 5)
            points = self.generate_wave_points(width, y_offset, step)
            points_full = points + [(width, height), (0, height)]

            shadow_offset = int(step * 0.08)
            shadow_color = tuple(max(0, c - 30) for c in layer_color)
            shadow_points = [(x, y + shadow_offset) for x, y in points]
            shadow_points_full = shadow_points + [(width, height), (0, height)]
            draw.polygon(shadow_points_full, fill=shadow_color)
            draw.polygon(points_full, fill=layer_color)

            grad_color = interpolate_colors(layer_color, secondary_color, 0.3)
            gradient_draw.polygon(points_full, fill=grad_color)

        blended = Image.blend(img, gradient, alpha=0.3)
        return blended