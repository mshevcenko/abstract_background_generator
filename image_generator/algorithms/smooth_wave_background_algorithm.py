import numpy as np
import random
import math
from PIL import Image, ImageDraw
from random import randint, uniform
from typing import Optional, List, Tuple

from image_generator.algorithm import Algorithm
from image_generator.parameter import Parameter, DataType, VisibleType
from image_generator.utils import hex_to_rgb, interpolate_colors


class SmoothWaveBackgroundAlgorithm(Algorithm):
    PARAMETERS = [
        Parameter(
            name="colors",
            visible_name="Colors",
            description="Gradient colors for the wave layers.",
            data_type=DataType.COLORS,
            visible_type=VisibleType.COLORS,
            default=["#FF0000", "#FFFFFF"],
            min_count=2,
            max_count=2,
        ),
        Parameter(
            name="n_layers",
            visible_name="Number of layers",
            description="How many wave layers to generate.",
            data_type=DataType.INTEGER,
            visible_type=VisibleType.SLIDER,
            default=10,
            min_value=5,
            max_value=20
        ),
        Parameter(
            name="monochrome",
            visible_name="Monochrome mode",
            description="If enabled, a monochrome version of the waves will be rendered using only the base color.",
            data_type=DataType.BOOL,
            visible_type=VisibleType.CHECKBOX,
            default=False
        ),
        Parameter(
            name="wave_angle",
            visible_name="Wave Angle",
            description="The tilt angle of the waves in degrees.",
            data_type=DataType.FLOAT,
            visible_type=VisibleType.SLIDER,
            default=0.0,
            min_value=-90.0,
            max_value=90.0
        )
    ]

    def __init__(self, name: str, visible_name: str):
        super().__init__(name, visible_name, "", self.PARAMETERS)

    def generate_wave_points(self, width: int, base_y: float, amplitude: float, n_points: int = 250) -> List[Tuple[float, float]]:
        xs = np.linspace(0, width, n_points)
        ys = np.full_like(xs, base_y, dtype=float)
        harmonics = randint(1, 3)
        for _ in range(harmonics):
            freq = uniform(1, 3)
            phase = uniform(0, 2 * math.pi)
            amp = uniform(amplitude * 0.5, amplitude)
            ys += np.sin(2 * math.pi * freq * xs / width + phase) * amp
        ys[0] = base_y
        ys[-1] = base_y
        return list(zip(xs, ys))

    def rotate_points(self, points: List[Tuple[float, float]], angle_deg: float, center: Tuple[float, float]) -> List[
        Tuple[float, float]]:
        angle_rad = math.radians(angle_deg)
        cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)
        cx, cy = center
        return [
            (
                cos_a * (x - cx) - sin_a * (y - cy) + cx,
                sin_a * (x - cx) + cos_a * (y - cy) + cy
            )
            for x, y in points
        ]

    def algorithm(self,
                  width: int,
                  height: int,
                  seed: Optional[int] = None,
                  area: Optional[List[List[bool]]] = None,
                  colors: Optional[List[str]] = None,
                  n_layers: int = 7,
                  monochrome: bool = False,
                  wave_angle: float = 0.0,
                  **kwargs) -> Image:

        if seed is not None:
            random.seed(seed)

        if colors is not None and len(colors) >= 2:
            base_color = hex_to_rgb(colors[0])
            secondary_color = hex_to_rgb(colors[1])
        elif colors is not None and len(colors) == 1:
            base_color = hex_to_rgb(colors[0])
            secondary_color = base_color
        else:
            base_color = (randint(50, 150), randint(50, 150), randint(50, 150))
            secondary_color = (255, 255, 255)

        extra = max(width, height)
        big_width = width + extra
        big_height = height + extra
        offset_x = (big_width - width) // 2
        offset_y = (big_height - height) // 2

        img = Image.new("RGB", (big_width, big_height), (255, 255, 255))
        draw = ImageDraw.Draw(img)

        n_layers = max(n_layers * 2, 2)
        layer_ys = np.linspace(0, big_height, n_layers)
        amplitude = (height / (n_layers - 1)) * 0.2

        wave_curves = []
        for i, y in enumerate(layer_ys):
            if i == 0 or i == n_layers - 1:
                base_y = y
            else:
                offset = uniform(-amplitude / 2, amplitude / 2)
                base_y = y + offset
            wave = self.generate_wave_points(big_width, base_y, amplitude)
            wave_curves.append(wave)

        center = (big_width / 2, big_height / 2)

        if abs(wave_angle) > 0.01:
            wave_curves = [self.rotate_points(curve, wave_angle, center) for curve in wave_curves]

        def draw_polygon(polygon, fill_color, outline_color=None):
            pts = [(round(x), round(y)) for x, y in polygon]
            draw.polygon(pts, fill=fill_color, outline=outline_color)

        if monochrome:
            def get_monochrome_color(t: float) -> Tuple[int, int, int]:
                factor = 1.0 - 0.2 * t
                r = max(0, min(255, int(base_color[0] * factor)))
                g = max(0, min(255, int(base_color[1] * factor)))
                b = max(0, min(255, int(base_color[2] * factor)))
                return (r, g, b)

        for i in reversed(range(n_layers - 1)):
            upper_wave = wave_curves[i]
            lower_wave = wave_curves[i + 1]

            polygon = upper_wave + list(reversed(lower_wave))
            t = i / (n_layers - 1)
            fill_color = get_monochrome_color(t) if monochrome else interpolate_colors(base_color, secondary_color, t)

            polygon = [
                (x, y + 2) if j >= len(upper_wave) else (x, y)
                for j, (x, y) in enumerate(polygon)
            ]

            draw_polygon(polygon, fill_color)

        top_wave = wave_curves[0]
        top_polygon = [(0, 0)] + top_wave + [(big_width, 0)]
        if abs(wave_angle) > 0.01:
            top_polygon = self.rotate_points(top_polygon, wave_angle, center)
        t = 0.0
        fill_color = get_monochrome_color(t) if monochrome else interpolate_colors(base_color, secondary_color, t)
        draw_polygon(top_polygon, fill_color)

        bottom_wave = wave_curves[-1]
        bottom_polygon = bottom_wave + [(big_width, big_height), (0, big_height)]
        if abs(wave_angle) > 0.01:
            bottom_polygon = self.rotate_points(bottom_polygon, wave_angle, center)
        t = 1.0
        fill_color = get_monochrome_color(t) if monochrome else interpolate_colors(base_color, secondary_color, t)
        draw_polygon(bottom_polygon, fill_color)

        final_img = img.crop((offset_x, offset_y, offset_x + width, offset_y + height))
        return final_img