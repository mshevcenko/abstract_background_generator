import os
import random
from enum import Enum

import matplotlib

from typing import Union, Optional
from PIL import Image, ImageDraw
import numpy as np
from typing import Dict, Any, List, Tuple

import matplotlib.pyplot as plt
from image_generator.custom_colormap import CustomColormap
from image_generator.algorithm import Algorithm
from image_generator.parameter import Parameter, DataType, VisibleType
import image_generator.utils as utils
from matplotlib.colors import ListedColormap

all_colormaps = plt.colormaps()


def generate_spirograph_image(width: int,
                              height: int,
                              RR: float = 50,
                              rr: float = 10,
                              dd: float = 5,
                              center_x_coord_delta: int = 0,
                              center_y_coord_delta: int = 0,
                              num_points: int = 5000,
                              thickness: float = 2,
                              colormap: CustomColormap = matplotlib.colormaps['plasma']) -> Image.Image:
    if RR < rr:
        RR, rr = rr, RR

    RR_int = int(RR)
    rr_int = int(rr)

    center = ((width // 2) + center_x_coord_delta,
              (height // 2) + center_y_coord_delta)

    lcm = np.lcm(RR_int, rr_int)
    theta = np.linspace(0, 2 * np.pi * (lcm // rr_int), num_points)

    xx = (RR - rr) * np.cos(theta) + dd * np.cos(((RR - rr) / rr) * theta)
    yy = (RR - rr) * np.sin(theta) - dd * np.sin(((RR - rr) / rr) * theta)

    xx = xx + center[0]
    yy = yy + center[1]

    coords = list(zip(xx.astype(int), yy.astype(int)))

    colors = (colormap(np.linspace(0, 1, num_points))[:, :3] * 255).astype(int)

    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    for i in range(1, len(coords)):
        color = tuple(colors[i])
        draw.line([coords[i - 1], coords[i]], fill=color, width=int(thickness))

    return image


mandelbrot_blending_parameters = [
    Parameter(name="RR",
              visible_name="Radius of the outer circle",
              description="Radius of the outer circle",
              data_type=DataType.FLOAT_TUPLE,
              visible_type=VisibleType.RANGE_SLIDER,
              default=(100.0, 1500.0),
              min_value=1.0,
              max_value=10000.0),

    Parameter(name="rr",
              visible_name="Radius of the inner circle",
              description="Radius of the inner circle",
              data_type=DataType.FLOAT_TUPLE,
              visible_type=VisibleType.RANGE_SLIDER,
              default=(50.0, 400.0),
              min_value=1.0,
              max_value=10000.0),

    Parameter(name="dd",
              visible_name="Distance",
              description="Distance from center of inner circle to drawing point",
              data_type=DataType.FLOAT_TUPLE,
              visible_type=VisibleType.RANGE_SLIDER,
              default=(200.0, 500.0),
              min_value=1.0,
              max_value=10000.0),

    Parameter(name="thickness",
              visible_name="Line thickness",
              description="Line thickness",
              data_type=DataType.FLOAT_TUPLE,
              visible_type=VisibleType.RANGE_SLIDER,
              default=(1.0, 3.0),
              min_value=1.0,
              max_value=10.0),

    Parameter(name="num_points",
              visible_name="Number of points",
              description="Number of points in the drawing, affects smoothness",
              data_type=DataType.INTEGER_TUPLE,
              visible_type=VisibleType.RANGE_SLIDER,
              default=(1000, 5000),
              min_value=100,
              max_value=10000),

    Parameter(name="center_x_coord_delta",
              visible_name="delta X of center",
              description="delta of X coord of center",
              data_type=DataType.INTEGER_TUPLE,
              visible_type=VisibleType.RANGE_SLIDER,
              default=(0, 0),
              min_value=-10000,
              max_value=10000),

    Parameter(name="center_y_coord_delta",
              visible_name="delta Y of center",
              description="delta of Y coord of center",
              data_type=DataType.INTEGER_TUPLE,
              visible_type=VisibleType.RANGE_SLIDER,
              default=(0, 0),
              min_value=-10000,
              max_value=10000),

]

allowed_pallets = [{
    "value": index,
    "visible_value": val
} for index, val in enumerate(all_colormaps)]

mandelbrot_non_blending_parameters = [
    Parameter(name="use_coloring_pallets",
              visible_name="Use color pallets",
              description="Enables use of preset color pallets instead of provided colors",
              data_type=DataType.BOOL,
              visible_type=VisibleType.CHECKBOX,
              default=False),

    Parameter(name="coloring_pallet",
              visible_name="Color pallet",
              description="This pallet can be used instead of provided colors",
              data_type=DataType.ENUM_LIST,
              visible_type=VisibleType.SELECTOR,
              default=0,
              possible_values=allowed_pallets,
              ),
]


class SpirographAlgorithm(Algorithm):
    def __init__(self,
                 name: str = "spirograph",
                 visible_name: str = "Spirograph",
                 ):
        parameters = [
            Parameter(name="colors",
                      visible_name="Colors",
                      description="Colors that will be used in custom pallet",
                      data_type=DataType.COLORS,
                      visible_type=VisibleType.COLORS,
                      default=["#00FF00"],
                      min_count=1,
                      max_count=10),
            *mandelbrot_non_blending_parameters,
            *mandelbrot_blending_parameters,
        ]
        super().__init__(name, visible_name, "Create image using spirograph",
                         parameters)

    def algorithm(self,
                  width: int,
                  height: int,

                  seed: Optional[int] = None,
                  area: Optional[List[List[bool]]] = None,

                  colors: Optional[List[str]] = ["#ff0000", "#00ff00", "#0000ff", "#aa0000", "#00aa00"],

                  RR: Tuple[float, float] = (100, 10000),
                  rr: Tuple[float, float] = (50, 1000),
                  dd: Tuple[float, float] = (5, 100),

                  num_points: Tuple[int, int] = (1000, 5000),

                  thickness: Tuple[float, float] = (1, 3),

                  center_x_coord_delta: Tuple[int, int] = (0, 0),
                  center_y_coord_delta: Tuple[int, int] = (0, 0),

                  use_coloring_pallets: bool = False,
                  coloring_pallet: int = 0,
                  **kwargs
                  ) -> Image:

        random.seed(seed)

        RR = random.uniform(*RR)
        rr = random.uniform(*rr)
        dd = random.uniform(*dd)

        num_points = random.randint(*num_points)

        thickness = random.uniform(*thickness)

        center_x_coord_delta = random.randint(*center_x_coord_delta)
        center_y_coord_delta = random.randint(*center_y_coord_delta)

        if use_coloring_pallets or colors is None:
            color_map = matplotlib.colormaps[all_colormaps[coloring_pallet]]
        else:
            color_map = ListedColormap(colors, name="my_colormap")

        image = generate_spirograph_image(width,
                                          height,
                                          RR=RR,
                                          rr=rr,
                                          dd=dd,
                                          center_x_coord_delta=center_x_coord_delta,
                                          center_y_coord_delta=center_y_coord_delta,
                                          num_points=num_points,
                                          thickness=thickness,
                                          colormap=color_map)
        # colored_array_uint8 = (image * 255).astype(np.uint8)
        # image = Image.fromarray(colored_array_uint8)

        if area is not None:
            utils.apply_transparency_mask(image, area)

        return image


if __name__ == '__main__':
    wfc_alg = SpirographAlgorithm("wfc", "Wave Function Collapse")
    img = wfc_alg.algorithm(1920, 1080)
    img.show()
