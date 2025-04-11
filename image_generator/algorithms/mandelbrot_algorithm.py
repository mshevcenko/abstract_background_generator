import os
import random
from enum import Enum

import matplotlib
# Installation of wfc is manual and need Cmake on device before install
# pip install .\wfc_whls\wfc_cpp\
import wfc_cpp as wfc_cpp

import xml.etree.ElementTree as ET
from typing import Union, Optional
from PIL import Image
import numpy as np
from typing import Dict, Any, List, Tuple

import matplotlib.pyplot as plt
from image_generator.custom_colormap import CustomColormap
from image_generator.algorithm import Algorithm
from image_generator.parameter import Parameter, DataType, VisibleType
import image_generator.utils as utils
from matplotlib.colors import ListedColormap

# The original Mandelbrot set's bounds in the complex plane
mandelbrot_x_min = -2.5
mandelbrot_x_max = 1.0
mandelbrot_y_min = -1.0
mandelbrot_y_max = 1.0

# Calculate the original aspect ratio of the Mandelbrot set
mandelbrot_base_width = (mandelbrot_x_max - mandelbrot_x_min)
mandelbrot_x_center = (mandelbrot_x_max + mandelbrot_x_min) / 2
mandelbrot_base_height = (mandelbrot_y_max - mandelbrot_y_min)
mandelbrot_y_center = (mandelbrot_y_max + mandelbrot_y_min) / 2

all_colormaps = plt.colormaps()


def calculate_mandelbrot_window(width: int = 1920,
                                height: int = 1080,
                                scale: float = 1,
                                center_x: float = mandelbrot_x_center,
                                center_y: float = mandelbrot_y_center):
    true_scale = 1 / scale
    new_width, new_height = utils.scale_down_dimensions_in_ratio_float(width, height, mandelbrot_base_width,
                                                                       mandelbrot_base_width)

    new_x_min = center_x - (new_width / 2) * true_scale
    new_x_max = center_x + (new_width / 2) * true_scale
    new_y_min = center_y - (new_height / 2) * true_scale
    new_y_max = center_y + (new_height / 2) * true_scale

    return new_x_min, new_x_max, new_y_min, new_y_max


def mandelbrot(width: int,
               height: int,
               xmin: float, xmax: float,
               ymin: float, ymax: float,
               max_iter: int = 1000,
               bailout_radius_squared: float = 1 << 16):
    # Generate pixel grid
    x_pixels = np.linspace(xmin, xmax, width)
    y_pixels = np.linspace(ymax, ymin, height)
    X, Y = np.meshgrid(x_pixels, y_pixels)
    C = X + 1j * Y
    Z = np.zeros_like(C)
    M = np.zeros(C.shape)

    # Iteration counts with smoothing
    for i in range(max_iter):
        # mask = np.abs(Z)**2 <= bailout_radius_squared
        mask = (Z.real ** 2 + Z.imag ** 2) <= bailout_radius_squared
        Z[mask] = Z[mask] ** 2 + C[mask]
        M[mask] += 1

    return Z, M, max_iter


def color_mandelbrot(Z: np.ndarray,
                     M: np.ndarray,
                     max_iter: int = 1000,
                     colormap: CustomColormap = matplotlib.colormaps['plasma'],
                     terrace_width: float = 0):
    with np.errstate(divide='ignore', invalid='ignore'):
        abs_z = np.abs(Z)
        log_zn = np.log(abs_z)
        nu = np.log(log_zn / np.log(2)) / np.log(2)

        M_smooth = M + 1 - nu
        M_smooth[np.isnan(M_smooth)] = 0

    norm = np.clip(M_smooth / max_iter, 0, 1)

    if terrace_width <= 0:
        # colormap = matplotlib.colormaps[palette_name]
        colored = colormap(norm)
    else:
        colored = colormap.terraced(norm, terrace_width)  # don't use with matplotlib colormap

    return colored[:, :, :3]


mandelbrot_blending_parameters = [
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
              default=(1.0, 2000.0),
              min_value=1.0,
              max_value=10000.0),

    Parameter(name="center_x_base",
              visible_name="X coord of center",
              description="Value of X coord of center excluded E^",
              data_type=DataType.INTEGER_TUPLE,
              visible_type=VisibleType.RANGE_SLIDER,
              default=(-7455, -7455),
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
              default=(1025, 1025),
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
]


class AvailableColoringTypesEnum(Enum):
    smooth = 0
    wavy = 1


available_coloring_types = [
    "Smooth",
    "Wavy"
]



allowed_available_coloring_types = [{
    "value": index,
    "visible_value": val
} for index, val in enumerate(available_coloring_types)]

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

    Parameter(name="bailout_radius_squared",
              visible_name="Smoothing",
              description="Determine how smooth is color potentially can change",
              data_type=DataType.FLOAT_TUPLE,
              visible_type=VisibleType.RANGE_SLIDER,
              default=(4.0, float(1 << 16)),
              min_value=1.0,
              max_value=float(1 << 16)),

    Parameter(name="coloring_type",
              visible_name="Coloring type",
              description="Controls which coloring method will be used (for now only used with custom pallet)",
              data_type=DataType.ENUM_LIST,
              visible_type=VisibleType.SELECTOR,
              possible_values=allowed_available_coloring_types,
              default=AvailableColoringTypesEnum.smooth.value),
]


class MandelbrotAlgorithm(Algorithm):
    def __init__(self,
                 name: str = "mandelbrot_fractal",
                 visible_name: str = "Mandelbrot fractal",
                 ):
        parameters = [
            Parameter(name="colors",
                      visible_name="Colors",
                      description="Colors that will be used in pallet for representing mandelbrot fractal",
                      data_type=DataType.COLORS,
                      visible_type=VisibleType.COLORS,
                      default=["#000000", "#0000FF", "#00FFFF", "#FFFF00", "#FF0000", "#FFFFFF"],
                      min_count=2,
                      max_count=10),
            *mandelbrot_non_blending_parameters,
            *mandelbrot_blending_parameters,
        ]
        super().__init__(name, visible_name, "Create image using escape time algorithm for Mandelbrot set", parameters)

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

                  use_coloring_pallets: bool = False,
                  coloring_pallet: int = 0,
                  coloring_type: int = 0,

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

        if use_coloring_pallets:
            color_map = matplotlib.colormaps[all_colormaps[coloring_pallet]]
        else:
            if coloring_type == AvailableColoringTypesEnum.smooth.value:
                color_map = ListedColormap(colors, name="my_colormap")
            else:
                if colors is None:
                    colors = []
                colors = utils.convert_hex_list_to_rgb(colors)
                interpol = 'l' if is_linear_color_interpolation else 'n'
                color_map = CustomColormap(colors, interpolation=interpol)

        xmin, xmax, ymin, ymax = calculate_mandelbrot_window(width, height, scale, xc, yc)
        Z, M, max_iter = mandelbrot(width, height, xmin, xmax, ymin, ymax,
                                    max_iter=max_iterations,
                                    bailout_radius_squared=bailout_radius_squared
                                    )
        # matplotlib.colormaps['viridis'] can be used

        image = color_mandelbrot(Z, M, max_iter,
                                 colormap=color_map  # matplotlib.colormaps['viridis']
                                 )
        colored_array_uint8 = (image * 255).astype(np.uint8)
        image = Image.fromarray(colored_array_uint8)

        if area is not None:
            utils.apply_transparency_mask(image, area)

        return image
