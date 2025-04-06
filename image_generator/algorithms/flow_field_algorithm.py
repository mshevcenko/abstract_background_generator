import numpy as np
import noise
from PIL import Image, ImageFilter, ImageDraw
import random
import math
from typing import Optional, List
from image_generator.algorithm import Algorithm
from image_generator.parameter import Parameter, DataType, VisibleType
from image_generator.utils import apply_transparency_mask, hex_to_rgb_normalized, hex_to_rgb


class FlowFieldGenerator(Algorithm):
    def __init__(self,
                 name: str,
                 visible_name: str,):
        parameters = [
            Parameter(name="colors",
                      visible_name="Colors",
                      description="",
                      data_type=DataType.COLORS,
                      visible_type=VisibleType.COLORS,
                      default=["#ff0000", "#00ff00"],
                      min_count=2,
                      max_count=10),
            Parameter(name="scale",
                      visible_name="Scale",
                      description="",
                      data_type=DataType.FLOAT,
                      visible_type=VisibleType.SLIDER,
                      default=1.0,
                      min_value=0.5,
                      max_value=100.0),
            Parameter(name="blur_radius",
                      visible_name="Blur radius",
                      description="",
                      data_type=DataType.FLOAT,
                      visible_type=VisibleType.SLIDER,
                      default=1.0,
                      min_value=0.0,
                      max_value=10.0),
            Parameter(name="octaves",
                      visible_name="Octaves",
                      description="",
                      data_type=DataType.INTEGER,
                      visible_type=VisibleType.SLIDER,
                      default=6,
                      min_value=2,
                      max_value=32),
            Parameter(name="line_count",
                      visible_name="line_count",
                      description="",
                      data_type=DataType.INTEGER,
                      visible_type=VisibleType.SLIDER,
                      default=1000,
                      min_value=1,
                      max_value=10000),
            Parameter(name="line_length",
                      visible_name="Line_length",
                      description="",
                      data_type=DataType.INTEGER,
                      visible_type=VisibleType.SLIDER,
                      default=100,
                      min_value=1,
                      max_value=10000),
            Parameter(name="line_width",
                      visible_name="line_width",
                      description="",
                      data_type=DataType.INTEGER,
                      visible_type=VisibleType.SLIDER,
                      default=1,
                      min_value=1,
                      max_value=100),
        ]
        super().__init__(name, visible_name, "", parameters)

    def algorithm(self,
                  width: int,
                  height: int,
                  seed: Optional[int] = None,
                  area: Optional[List[List[bool]]] = None,
                  colors: List[str] = ["#ff0000", "#00ff00"],
                  scale: float = 100.0,
                  blur_radius: float = 1.0,
                  octaves: int = 6,
                  line_count: int = 1000,
                  line_length: int = 100,
                  line_width: int = 1,
                  **kwargs) -> Image.Image:
        random.seed(seed)
        colors = [hex_to_rgb(color) for color in colors]
        flow_field_image = self._generate_flow_field(width, height, colors, scale, octaves,
                                                   line_count, line_length, line_width)

        img = Image.fromarray(flow_field_image)
        if blur_radius > 0:
            img = img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        if area:
            img = apply_transparency_mask(img, area)
        return img

    def _generate_flow_field(self, width, height, colors, scale=100.0, octaves=1, line_count=1000,
                            line_length=100, line_width=1):
        angle_map = np.zeros((height, width))
        for y in range(height):
            for x in range(width):
                angle_map[y, x] = noise.pnoise2(
                    x/scale,
                    y/scale,
                    octaves=octaves
                ) * math.pi * 2

        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)


        for _ in range(line_count):
            x, y = random.randint(0, width-1), random.randint(0, height-1)

            color_index = random.randint(0, len(colors)-1)
            line_color = colors[color_index]

            for i in range(line_length):
                if x < 0 or x >= width or y < 0 or y >= height:
                    break

                angle = angle_map[int(y), int(x)]
                dx = math.cos(angle)
                dy = math.sin(angle)

                new_x, new_y = x + dx, y + dy

                if 0 <= new_x < width and 0 <= new_y < height:
                    draw.line([(x, y), (new_x, new_y)], fill=line_color, width=line_width)

                x, y = new_x, new_y

        return np.array(img)
