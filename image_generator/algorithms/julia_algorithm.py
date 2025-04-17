import random

import matplotlib
from matplotlib.colors import ListedColormap

from typing import Union, Optional
from PIL import Image
import numpy as np
from typing import Dict, Any, List, Tuple

import matplotlib.pyplot as plt

from image_generator.algorithms import mandelbrot_algorithm
from image_generator.algorithms.mandelbrot_algorithm import allowed_available_fractals_types, AvailableFractalTypesEnum
from image_generator.custom_colormap import CustomColormap
from image_generator.algorithm import Algorithm
from image_generator.parameter import Parameter, DataType, VisibleType
import image_generator.utils as utils


def mandelbrot_julia(width: int,
                     height: int,
                     xmin: float, xmax: float,
                     ymin: float, ymax: float,
                     cc: complex = complex(0, 0),
                     max_iter: int = 1000,
                     bailout_radius_squared: float = 1 << 16):
    x_pixels = np.linspace(xmin, xmax, width)
    y_pixels = np.linspace(ymax, ymin, height)
    X, Y = np.meshgrid(x_pixels, y_pixels)
    Z = X + 1j * Y
    M = np.zeros(Z.shape)

    for i in range(max_iter):
        mask = np.abs(Z) <= bailout_radius_squared
        # mask = (Z.real ** 2 + Z.imag ** 2) <= bailout_radius_squared

        Z[mask] = Z[mask] ** 2 + cc
        M[mask] += 1

    return Z, M, max_iter


def burning_ship_julia(width: int,
                       height: int,
                       xmin: float, xmax: float,
                       ymin: float, ymax: float,
                       cc: complex = complex(0, 0),
                       max_iter: int = 1000,
                       bailout_radius_squared: float = 1 << 16):
    # Create pixel grid
    x_pixels = np.linspace(xmin, xmax, width)
    y_pixels = np.linspace(ymin, ymax, height)
    X, Y = np.meshgrid(x_pixels, y_pixels)
    Z = X + 1j * Y  # Z varies per pixel
    M = np.zeros(Z.shape)

    for i in range(max_iter):
        mask = np.abs(Z) <= bailout_radius_squared
        # mask = (Z.real ** 2 + Z.imag ** 2) <= bailout_radius_squared

        Z_real = np.abs(Z.real[mask])
        Z_imag = np.abs(Z.imag[mask])
        Z[mask] = (Z_real + 1j * Z_imag) ** 2 + cc

        M[mask] += 1

    return Z, M, max_iter


fractal_functions_julia = [mandelbrot_julia, burning_ship_julia]

julia_blending_parameters = [
    Parameter(name="fractal_type",
              visible_name="Fractal type",
              description="Selector to choose fractal type to generate (default values are specified for mandelbrot)",
              data_type=DataType.ENUM_LIST,
              visible_type=VisibleType.SELECTOR,
              possible_values=allowed_available_fractals_types,
              default=AvailableFractalTypesEnum.mandelbrot.value),

    Parameter(name="max_iterations",
              visible_name="Maximum iterations",
              description="Maximum iterations calculation of escape time",  # TODO write more "normal" explanation
              data_type=DataType.INTEGER_TUPLE,
              visible_type=VisibleType.RANGE_SLIDER,
              default=(100, 1000),
              min_value=1,
              max_value=2000),

    Parameter(name="scale",
              visible_name="Zoom",
              description="Determine the zoom level relative to the center coordinates",
              data_type=DataType.FLOAT_TUPLE,
              visible_type=VisibleType.RANGE_SLIDER,
              default=(1.0, 1.0),
              min_value=1.0,
              max_value=2000.0),

    Parameter(name="center_x_base",
              visible_name="X coord of center",
              description="Value of X coord of center excluded E^",
              data_type=DataType.INTEGER_TUPLE,
              visible_type=VisibleType.RANGE_SLIDER,
              default=(0, 0),
              min_value=-10000,
              max_value=10000),

    Parameter(name="center_ex",
              visible_name="E^ value for X center coord",
              description="Value of E^ for x coord",
              data_type=DataType.INTEGER_TUPLE,
              visible_type=VisibleType.RANGE_SLIDER,
              default=(-4, -4),
              min_value=-30,
              max_value=1),

    Parameter(name="center_y_base",
              visible_name="Y coord of center",
              description="Value of Y coord of center excluded E^",
              data_type=DataType.INTEGER_TUPLE,
              visible_type=VisibleType.RANGE_SLIDER,
              default=(0, 0),
              min_value=-10000,
              max_value=10000),

    Parameter(name="center_ey",
              visible_name="E^ value for Y center coord",
              description="Value of E^ for y coord",
              data_type=DataType.INTEGER_TUPLE,
              visible_type=VisibleType.RANGE_SLIDER,
              default=(-4, -4),
              min_value=-30,
              max_value=1),

    Parameter(name="julia_center_x_base",
              visible_name="X coord of julia center",
              description="Value of X coord of julia center excluded E^",
              data_type=DataType.INTEGER_TUPLE,
              visible_type=VisibleType.RANGE_SLIDER,
              default=(-7455, -7455),
              min_value=-10000,
              max_value=10000),

    Parameter(name="julia_center_ex",
              visible_name="E^ value for X julia center coord",
              description="Value of E^ for x coord",
              data_type=DataType.INTEGER_TUPLE,
              visible_type=VisibleType.RANGE_SLIDER,
              default=(-4, -4),
              min_value=-30,
              max_value=1),

    Parameter(name="julia_center_y_base",
              visible_name="Y coord of julia center",
              description="Value of Y coord of julia center excluded E^",
              data_type=DataType.INTEGER_TUPLE,
              visible_type=VisibleType.RANGE_SLIDER,
              default=(1025, 1025),
              min_value=-10000,
              max_value=10000),

    Parameter(name="julia_center_ey",
              visible_name="E^ value for Y julia center coord",
              description="Value of E^ for y coord",
              data_type=DataType.INTEGER_TUPLE,
              visible_type=VisibleType.RANGE_SLIDER,
              default=(-4, -4),
              min_value=-30,
              max_value=1),
]

julia_non_blending_parameters = [

]


class JuliaMandelbrotAlgorithm(Algorithm):
    def __init__(self,
                 name: str = "julia_mandelbrot_fractal",
                 visible_name: str = "Julia over fractal",
                 ):
        parameters = [
            Parameter(name="colors",
                      visible_name="Colors",
                      description="Colors that will be used in pallet for representing chosen julia modification of "
                                  "fractal",
                      data_type=DataType.COLORS,
                      visible_type=VisibleType.COLORS,
                      default=["#000000", "#0000FF", "#00FFFF", "#FFFF00", "#FF0000", "#FFFFFF"],
                      min_count=2,
                      max_count=10),
            *mandelbrot_algorithm.mandelbrot_non_blending_parameters,
            # *mandelbrot_algorithm.mandelbrot_blending_parameters,
            *julia_non_blending_parameters,
            *julia_blending_parameters
        ]
        super().__init__(name, visible_name, "Create image using escape time algorithm for Julia modification of "
                                             "chosen fractal set", parameters)

    def algorithm(self,
                  width: int,
                  height: int,

                  seed: Optional[int] = None,
                  area: Optional[List[List[bool]]] = None,

                  colors: Optional[List[str]] = None,
                  is_linear_color_interpolation: bool = True,  # maybe will be removed
                  scale: Tuple[float, float] = (1.0, 2000.0),
                  max_iterations: Tuple[int, int] = (100, 1000),
                  bailout_radius_squared: Tuple[float, float] = (4.0, 1 << 16),

                  center_x_base: Tuple[int, int] = (-7455, -7455),
                  center_ex: Tuple[int, int] = (-4, -4),
                  center_y_base: Tuple[int, int] = (1025, 1025),
                  center_ey: Tuple[int, int] = (-4, -4),

                  julia_center_x_base: Tuple[int, int] = (0, -0),
                  julia_center_ex: Tuple[int, int] = (-4, -4),
                  julia_center_y_base: Tuple[int, int] = (0, 0),
                  julia_center_ey: Tuple[int, int] = (-4, -4),

                  use_coloring_pallets: bool = False,
                  coloring_pallet: int = 0,
                  coloring_type: int = 0,

                  fractal_type: int = 0,
                  **kwargs
                  ) -> Image:

        random.seed(seed)
        scale = random.uniform(*scale)
        bailout_radius_squared = random.uniform(*bailout_radius_squared)
        max_iterations = random.randint(*max_iterations)

        center_x_base = random.randint(*center_x_base)
        center_ex = random.randint(*center_ex)
        xc = center_x_base * (10 ** center_ex)

        center_y_base = random.randint(*center_y_base)
        center_ey = random.randint(*center_ey)
        yc = center_y_base * (10 ** center_ey)

        julia_center_x_base = random.randint(*julia_center_x_base)
        julia_center_ex = random.randint(*julia_center_ex)
        jxc = julia_center_x_base * (10 ** julia_center_ex)

        julia_center_y_base = random.randint(*julia_center_y_base)
        julia_center_ey = random.randint(*julia_center_ey)
        jyc = julia_center_y_base * (10 ** julia_center_ey)

        cc = complex(jxc, jyc)

        if use_coloring_pallets:
            color_map = matplotlib.colormaps[mandelbrot_algorithm.all_colormaps[coloring_pallet]]
        else:
            if coloring_type == mandelbrot_algorithm.AvailableColoringTypesEnum.smooth.value:
                color_map = ListedColormap(colors, name="my_colormap")
            else:
                if colors is None:
                    colors = []
                colors = utils.convert_hex_list_to_rgb(colors)
                interpol = 'l' if is_linear_color_interpolation else 'n'
                color_map = CustomColormap(colors, interpolation=interpol)

        xmin, xmax, ymin, ymax = mandelbrot_algorithm.calculate_mandelbrot_window(width, height, scale, xc, yc)
        Z, M, max_iter = fractal_functions_julia[fractal_type](width, height, xmin, xmax, ymin, ymax,
                                                               cc=cc,
                                                               max_iter=max_iterations,
                                                               bailout_radius_squared=bailout_radius_squared
                                                               )

        image = mandelbrot_algorithm.color_mandelbrot(Z, M, max_iter,
                                                      colormap=color_map  # matplotlib.colormaps['viridis']
                                                      )
        colored_array_uint8 = (image * 255).astype(np.uint8)
        image = Image.fromarray(colored_array_uint8)

        if area is not None:
            utils.apply_transparency_mask(image, area)

        return image
