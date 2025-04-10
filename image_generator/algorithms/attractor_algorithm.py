import io
import math
import cairo
import random
import numpy as np
from PIL.Image import Image
from PIL import Image, ImageFilter
from typing import Optional, List, Tuple
from image_generator.algorithm import Algorithm
from image_generator.algorithms.attractors.attractor import Attractor
from image_generator.parameter import Parameter, DataType, VisibleType
from image_generator.utils import hex_to_rgb_normalized, apply_transparency_mask


def rotation_matrix(rx, ry, rz):
    Rx = np.array([[1, 0, 0],
                   [0, math.cos(rx), -math.sin(rx)],
                   [0, math.sin(rx), math.cos(rx)]])
    Ry = np.array([[math.cos(ry), 0, math.sin(ry)],
                   [0, 1, 0],
                   [-math.sin(ry), 0, math.cos(ry)]])
    Rz = np.array([[math.cos(rz), -math.sin(rz), 0],
                   [math.sin(rz), math.cos(rz), 0],
                   [0, 0, 1]])
    return Rz @ Ry @ Rx


def interpolate_color(color_list, t):
    if len(color_list) == 1:
        return color_list[0]
    if t <= 0:
        return color_list[0]
    if t >= 1:
        return color_list[-1]
    n = len(color_list) - 1
    scaled = t * n
    idx = int(math.floor(scaled))
    frac = scaled - idx
    c0 = np.array(color_list[idx])
    c1 = np.array(color_list[idx + 1])
    return tuple(c0 + frac * (c1 - c0))


def auto_scale_and_center(xs, zs, width, height, scale=1.0, offset_x=0.0, offset_y=0.0):
    x_min, x_max = xs.min(), xs.max()
    z_min, z_max = zs.min(), zs.max()

    x_range = x_max - x_min
    z_range = z_max - z_min

    if x_range < 1e-8:
        x_range = 1e-8
    if z_range < 1e-8:
        z_range = 1e-8

    scale_x = width / x_range
    scale_z = height / z_range

    fit_scale = min(scale_x, scale_z)

    x_center = (x_min + x_max) / 2.0
    z_center = (z_min + z_max) / 2.0

    absolute_offset_x = offset_x * width
    absolute_offset_y = offset_y * height

    xs_centered = (xs - x_center) * fit_scale
    zs_centered = (zs - z_center) * fit_scale
    xs_shifted = xs_centered + absolute_offset_x
    zs_shifted = zs_centered + absolute_offset_y
    xs_centered = (xs_shifted - x_center) * scale
    zs_centered = (zs_shifted - z_center) * scale
    xs_scaled = xs_centered + width / 2
    zs_scaled = zs_centered + height / 2

    return xs_scaled, zs_scaled


# noinspection PyTypeChecker
class AttractorAlgorithm(Algorithm):
    def __init__(self,
                 name: str,
                 visible_name: str,
                 attractor: Attractor):
        parameters = [
            Parameter(name="colors",
                      visible_name="Colors",
                      description="Colors for lines and circles. Applied by gradient. Min 1 color. Max 10 colors.",
                      data_type=DataType.COLORS,
                      visible_type=VisibleType.COLORS,
                      default=["#ff0000", "#00ff00"],
                      min_count=1,
                      max_count=10),
            Parameter(name="scale",
                      visible_name="Scale",
                      description="Scale of all curve. Applied by center. Chooses random scale from range.",
                      data_type=DataType.FLOAT_TUPLE,
                      visible_type=VisibleType.RANGE_SLIDER,
                      default=(1.0, 2.0),
                      min_value=0.5,
                      max_value=10.0),
            Parameter(name="size",
                      visible_name="Size",
                      description="Min and max thickness of lines and size of circles. Lower bound of range is min size. Upper bound of range is max size.",
                      data_type=DataType.FLOAT_TUPLE,
                      visible_type=VisibleType.RANGE_SLIDER,
                      default=(1.0, 2.0),
                      min_value=0.5,
                      max_value=10.0),
            Parameter(name="blur_radius",
                      visible_name="Blur radius",
                      description="Gaussian blur radius. Chooses random value from range.",
                      data_type=DataType.FLOAT_TUPLE,
                      visible_type=VisibleType.RANGE_SLIDER,
                      default=(0.0, 4.0),
                      min_value=0.0,
                      max_value=10.0),
            Parameter(name="num_points",
                      visible_name="Points",
                      description="Number of points in curve. The more points, the smoother the curve. Chooses random value from range.",
                      data_type=DataType.INTEGER_TUPLE,
                      visible_type=VisibleType.RANGE_SLIDER,
                      default=(10000, 10000),
                      min_value=1000,
                      max_value=10000),
            Parameter(name="draw_lines",
                      visible_name="Draw lines",
                      description="Checkbox to draw or not draw lines. If off, only points are drawn in the form of circles.",
                      data_type=DataType.BOOL,
                      visible_type=VisibleType.CHECKBOX,
                      default=True),
            Parameter(name="offset_x",
                      visible_name="Offset x",
                      description="Offset of projected curve by x coord. 1 is offset by all width. 0 is no offset. Chooses random value from range.",
                      data_type=DataType.FLOAT_TUPLE,
                      visible_type=VisibleType.RANGE_SLIDER,
                      default=(0.0, 0.0),
                      min_value=-1.0,
                      max_value=1.0),
            Parameter(name="offset_y",
                      visible_name="Offset y",
                      description="Offset of projected curve by y coord. 1 is offset by all height. 0 is no offset. Chooses random value from range.",
                      data_type=DataType.FLOAT_TUPLE,
                      visible_type=VisibleType.RANGE_SLIDER,
                      default=(0.0, 0.0),
                      min_value=-1.0,
                      max_value=1.0),
            Parameter(name="rotation_x",
                      visible_name="Rotation x",
                      description="Rotation of 3D curve by x axis. Values are in degrees. Chooses random value from range.",
                      data_type=DataType.FLOAT_TUPLE,
                      visible_type=VisibleType.RANGE_SLIDER,
                      default=(-180.0, 180.0),
                      min_value=-180.0,
                      max_value=180.0),
            Parameter(name="rotation_y",
                      visible_name="Rotation y",
                      description="Rotation of 3D curve by y axis. Values are in degrees. Chooses random value from range.",
                      data_type=DataType.FLOAT_TUPLE,
                      visible_type=VisibleType.RANGE_SLIDER,
                      default=(-180.0, 180.0),
                      min_value=-180.0,
                      max_value=180.0),
            Parameter(name="rotation_z",
                      visible_name="Rotation z",
                      description="Rotation of 3D curve by z axis. Values are in degrees. Chooses random value from range.",
                      data_type=DataType.FLOAT_TUPLE,
                      visible_type=VisibleType.RANGE_SLIDER,
                      default=(-180.0, 180.0),
                      min_value=-180.0,
                      max_value=180.0)
        ]
        super().__init__(name, visible_name, "3D semi-random multicolor curve projected on 2D space.", parameters)
        self.attractor = attractor

    def algorithm(self,
                  width: int,
                  height: int,
                  seed: Optional[int] = None,
                  area: Optional[List[List[bool]]] = None,
                  colors: List[str] = ["#ff0000", "#00ff00"],
                  scale: Tuple[float, float] = (1.0, 2.0),
                  size: Tuple[float, float] = (0.5, 2.0),
                  blur_radius: Tuple[float, float] = (0.0, 4.0),
                  num_points: Tuple[int, int] = (10000, 100000),
                  draw_lines: bool = True,
                  offset_x: Tuple[float, float] = (-1.0, 1.0),
                  offset_y: Tuple[float, float] = (-1.0, 1.0),
                  rotation_x: Tuple[float, float] = (0.0, 6.29),
                  rotation_y: Tuple[float, float] = (0.0, 6.29),
                  rotation_z: Tuple[float, float] = (0.0, 6.29),
                  **kwargs) -> Image:
        random.seed(seed)
        scale = random.uniform(*scale)
        min_size = size[0]
        max_size = size[1]
        blur_radius = random.uniform(*blur_radius)
        num_points = int(random.uniform(*num_points))
        offset_x = random.uniform(*offset_x)
        offset_y = random.uniform(*offset_y)
        rotation_x = math.radians(random.uniform(*rotation_x))
        rotation_y = math.radians(random.uniform(*rotation_y))
        rotation_z = math.radians(random.uniform(*rotation_z))
        normalized_colors = [hex_to_rgb_normalized(color) for color in colors]
        points = self.attractor.generate_points(num_points=num_points, seed=seed)
        plane_origin = points[0]
        R = rotation_matrix(rotation_x, rotation_y, rotation_z)
        transformed = (points - plane_origin) @ R.T
        depths = np.abs(transformed[:, 1])
        d_min, d_max = depths.min(), depths.max()
        if d_max - d_min < 1e-5:
            d_max = d_min + 1e-5
        norm_depths = (depths - d_min) / (d_max - d_min)
        xs = transformed[:, 0]
        zs = transformed[:, 2]
        xs, zs = auto_scale_and_center(xs, zs, width, height, scale, offset_x=offset_x, offset_y=offset_y)

        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        ctx = cairo.Context(surface)
        for x, z, norm in zip(xs, zs, norm_depths):
            r, g, b = interpolate_color(normalized_colors, 1 - norm)
            diameter = min_size + (max_size - min_size) * (1 - norm)
            radius = diameter / 2
            ctx.set_source_rgb(r, g, b)
            ctx.arc(x, z, radius, 0, 2 * math.pi)
            ctx.fill()

        if draw_lines:
            for i in range(num_points - 1):
                x1, z1, n1 = xs[i], zs[i], norm_depths[i]
                x2, z2, n2 = xs[i + 1], zs[i + 1], norm_depths[i + 1]

                r1, g1, b1 = interpolate_color(normalized_colors, 1 - n1)
                r2, g2, b2 = interpolate_color(normalized_colors, 1 - n2)

                grad = cairo.LinearGradient(x1, z1, x2, z2)
                grad.add_color_stop_rgb(0.0, r1, g1, b1)
                grad.add_color_stop_rgb(1.0, r2, g2, b2)

                line_width = min_size + (max_size - min_size) * (1 - n1)

                ctx.set_source(grad)
                ctx.set_line_width(line_width)
                ctx.move_to(x1, z1)
                ctx.line_to(x2, z2)
                ctx.stroke()

        buffer = io.BytesIO()
        surface.write_to_png(buffer)
        buffer.seek(0)
        image = Image.open(buffer).convert("RGBA")
        if blur_radius > 0:
            blurred_image = image.filter(ImageFilter.GaussianBlur(radius=blur_radius))
            final_image = Image.new("RGBA", (width, height), (255, 255, 255, 0))
            final_image.paste(blurred_image, (0, 0), blurred_image)
            final_image.paste(image, (0, 0), image)
            image = final_image
        if area:
            image = apply_transparency_mask(image, area)
        return image
