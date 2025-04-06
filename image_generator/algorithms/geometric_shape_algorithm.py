from PIL import Image, ImageDraw, ImageFilter
import math
import random
from typing import Optional, List, Tuple
from random import randrange

from image_generator.algorithm import Algorithm
from image_generator.parameter import Parameter, DataType, VisibleType
from image_generator.utils import hex_to_rgb, interpolate_colors


class GeometricShapesAlgorithm(Algorithm):
    PARAMETERS = [
        Parameter(
            name="shape_type",
            visible_name="Shape Type",
            data_type=DataType.ENUM_LIST,
            visible_type=VisibleType.SELECTOR,
            default="triangle",
            possible_values=[
                {"value": "triangle", "visible_value": "Triangle"},
                {"value": "circle", "visible_value": "Circle"},
                {"value": "rectangle", "visible_value": "Rectangle"},
            ]
        ),
        Parameter(
            name="size",
            visible_name="Size",
            data_type=DataType.INTEGER,
            visible_type=VisibleType.SLIDER,
            default=40,
            min_value=10,
            max_value=200
        ),
        Parameter(
            name="colors",
            visible_name="Fill Color",
            data_type=DataType.COLORS,
            visible_type=VisibleType.COLORS,
            default=["#FF0000"],
            min_count=1,
            max_count=2
        ),
        Parameter(
            name="angle",
            visible_name="Rotation Angle",
            data_type=DataType.FLOAT,
            visible_type=VisibleType.SLIDER,
            default=0.0,
            min_value=0.0,
            max_value=360.0
        ),
        Parameter(
            name="blur_radius",
            visible_name="Blur Radius",
            data_type=DataType.FLOAT,
            visible_type=VisibleType.SLIDER,
            default=0.0,
            min_value=0.0,
            max_value=10.0
        ),
        Parameter(
            name="border_thickness",
            visible_name="Border Thickness",
            data_type=DataType.INTEGER,
            visible_type=VisibleType.SLIDER,
            default=2,
            min_value=0,
            max_value=10
        ),
        # Parameter(
        #     name="border_color",
        #     visible_name="Border Color",
        #     data_type=DataType.COLORS,
        #     visible_type=VisibleType.COLORS,
        #     default=["#000000"],
        #     min_count=1,
        #     max_count=1
        # ),
        Parameter(
            name="num_shapes",
            visible_name="Number of Shapes",
            data_type=DataType.INTEGER,
            visible_type=VisibleType.SLIDER,
            default=12,
            min_value=1,
            max_value=100
        ),
        Parameter(
            name="arrangement",
            visible_name="Arrangement",
            data_type=DataType.ENUM_LIST,
            visible_type=VisibleType.SELECTOR,
            default="random",
            possible_values=[
                {"value": "random", "visible_value": "Random"},
                {"value": "grid", "visible_value": "Grid"},
                {"value": "spiral", "visible_value": "Spiral"}
            ]
        )
    ]

    def __init__(self, name: str, visible_name: str):
        super().__init__(name, visible_name, self.PARAMETERS)

    def generate_shape(self,
                       shape_type: str = 'triangle',
                       size: int = 40,
                       color: Tuple or List = (255, 0, 0, 200),
                       angle: float = 0.0,
                       blur_radius: float = 0.0,
                       border_thickness: int = 2,
                       border_color: Tuple[int, int, int, int] = (0, 0, 0, 255)) -> Image:

        canvas_size = (size * 3, size * 3)
        base_img = Image.new('RGBA', canvas_size, (0, 0, 0, 0))
        mask = Image.new('L', canvas_size, 0)
        draw_mask = ImageDraw.Draw(mask)
        draw = ImageDraw.Draw(base_img)
        center = (canvas_size[0] // 2, canvas_size[1] // 2)
        shape_coords = None

        if shape_type == 'triangle':
            point1 = (center[0], center[1] - size)
            point2 = (center[0] - int(size * math.sin(math.radians(60))),
                      center[1] + int(size * math.cos(math.radians(60))))
            point3 = (center[0] + int(size * math.sin(math.radians(60))),
                      center[1] + int(size * math.cos(math.radians(60))))
            shape_coords = [point1, point2, point3]
            draw_mask.polygon(shape_coords, fill=255)
        elif shape_type == 'circle':
            bbox = [center[0] - size, center[1] - size, center[0] + size, center[1] + size]
            shape_coords = bbox
            draw_mask.ellipse(bbox, fill=255)
        elif shape_type == 'rectangle':
            bbox = [center[0] - size, center[1] - size, center[0] + size, center[1] + size]
            shape_coords = bbox
            draw_mask.rectangle(bbox, fill=255)

        if isinstance(color, (list, tuple)) and len(color) == 2 and isinstance(color[0], tuple):
            grad = Image.new('RGBA', canvas_size)
            grad_draw = ImageDraw.Draw(grad)

            for y in range(canvas_size[1]):
                t = y / canvas_size[1]
                col = interpolate_colors(color[0], color[1], t)
                grad_draw.line([(0, y), (canvas_size[0], y)], fill=col)
            shape_filled = Image.composite(grad, Image.new('RGBA', canvas_size, (0, 0, 0, 0)), mask)
        else:
            shape_filled = Image.new('RGBA', canvas_size, color)

            shape_filled.putalpha(mask)

        if border_thickness > 0 and shape_coords is not None:
            border_img = Image.new('RGBA', canvas_size, (0, 0, 0, 0))
            border_draw = ImageDraw.Draw(border_img)
            if shape_type == 'triangle':
                border_draw.polygon(shape_coords, outline=border_color, fill=None)
            elif shape_type == 'circle':
                border_draw.ellipse(shape_coords, outline=border_color, width=border_thickness)
            elif shape_type == 'rectangle':
                border_draw.rectangle(shape_coords, outline=border_color, width=border_thickness)

            shape_filled = Image.alpha_composite(shape_filled, border_img)

        if angle != 0:
            shape_filled = shape_filled.rotate(angle, expand=1)
        if blur_radius > 0:
            shape_filled = shape_filled.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        return shape_filled

    def arrange_shapes_randomly(self,
                                background: Image,
                                num_shapes: int,
                                shape_type: str,
                                size: int,
                                color: Tuple or List,
                                angle: float,
                                blur_radius: float,
                                border_thickness: int,
                                border_color: Tuple[int, int, int, int]) -> None:
        bg_width, bg_height = background.size
        for _ in range(num_shapes):
            shape_img = self.generate_shape(shape_type, size, color, angle,
                                            blur_radius, border_thickness, border_color)
            pos_x = randrange(0, bg_width - shape_img.width)
            pos_y = randrange(0, bg_height - shape_img.height)
            background.paste(shape_img, (pos_x, pos_y), shape_img)

    def arrange_shapes_in_grid(self,
                               background: Image,
                               num_shapes: int,
                               shape_type: str,
                               size: int,
                               color: Tuple or List,
                               angle: float,
                               blur_radius: float,
                               border_thickness: int,
                               border_color: Tuple[int, int, int, int]) -> None:
        bg_width, bg_height = background.size
        cols = int(math.sqrt(num_shapes))
        rows = int(math.ceil(num_shapes / cols))
        cell_width = bg_width / cols
        cell_height = bg_height / rows
        shape_count = 0
        for row in range(rows):
            for col in range(cols):
                if shape_count >= num_shapes:
                    break
                shape_img = self.generate_shape(shape_type, size, color, angle,
                                                blur_radius, border_thickness, border_color)
                center_x = int(col * cell_width + cell_width / 2)
                center_y = int(row * cell_height + cell_height / 2)
                pos = (center_x - shape_img.width // 2, center_y - shape_img.height // 2)
                background.paste(shape_img, pos, shape_img)
                shape_count += 1

    def arrange_shapes_in_spiral(self,
                                 background: Image,
                                 num_shapes: int,
                                 shape_type: str,
                                 size: int,
                                 color: Tuple or List,
                                 angle: float,
                                 blur_radius: float,
                                 border_thickness: int,
                                 border_color: Tuple[int, int, int, int]) -> None:
        bg_width, bg_height = background.size
        center = (bg_width // 2, bg_height // 2)
        b = min(bg_width, bg_height) / (4 * num_shapes)
        for i in range(num_shapes):
            theta = i * 0.5
            r = b * theta
            pos_x = int(center[0] + r * math.cos(theta))
            pos_y = int(center[1] + r * math.sin(theta))
            shape_angle = math.degrees(math.atan2(pos_y - center[1], pos_x - center[0])) + 90
            shape_img = self.generate_shape(shape_type, size, color, shape_angle,
                                            blur_radius, border_thickness, border_color)
            pos = (pos_x - shape_img.width // 2, pos_y - shape_img.height // 2)
            background.paste(shape_img, pos, shape_img)

    def algorithm(self,
                  width: int,
                  height: int,
                  seed: Optional[int] = None,
                  area: Optional[List[List[bool]]] = None,
                  colors: Optional[List[str]] = None,
                  shape_type: str = "triangle",
                  size: int = 40,
                  angle: float = 0.0,
                  blur_radius: float = 0.0,
                  border_thickness: int = 2,
                  num_shapes: int = 12,
                  arrangement: str = "spiral",
                  **kwargs) -> Image:

        if seed is not None:
            random.seed(seed)

        if colors is not None and len(colors) > 0:
            if len(colors) == 1:
                fill_color = hex_to_rgb(colors[0])
            else:
                fill_color = (hex_to_rgb(colors[0]), hex_to_rgb(colors[1]))
        else:
            fill_color = (255, 0, 0, 200)
        if colors is not None and len(colors) > 1:
            b_color = hex_to_rgb(colors[1])
        else:
            b_color = (0, 0, 0, 255)

        background = Image.new('RGBA', (width, height), (255, 255, 255, 0))

        if arrangement == "random":
            self.arrange_shapes_randomly(background, num_shapes, shape_type, size,
                                         fill_color, angle, blur_radius, border_thickness, b_color)
        elif arrangement == "grid":
            self.arrange_shapes_in_grid(background, num_shapes, shape_type, size,
                                        fill_color, angle, blur_radius, border_thickness, b_color)
        elif arrangement == "spiral":
            self.arrange_shapes_in_spiral(background, num_shapes, shape_type, size,
                                          fill_color, angle, blur_radius, border_thickness, b_color)
        else:
            self.arrange_shapes_randomly(background, num_shapes, shape_type, size,
                                         fill_color, angle, blur_radius, border_thickness, b_color)
        return background

if __name__ == '__main__':
    geo_alg = GeometricShapesAlgorithm("geometric", "Geometric Shapes")
    img = geo_alg.algorithm(
        width=1920,
        height=1080,
        seed=42,
        area=None,
        colors=["#FF0066", "#0066FF"],
        shape_type="circle",
        size=80,
        angle=15.0,
        blur_radius=0.2,
        border_thickness=0,
        num_shapes=80,
        arrangement="random"
    )
    img.show()