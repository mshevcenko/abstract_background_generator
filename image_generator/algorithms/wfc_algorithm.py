import os
import random

# Installation of wfc is manual and need Cmake on device before install
# pip install .\wfc_whls\wfc_cpp\
import wfc_cpp as wfc_cpp

import xml.etree.ElementTree as ET
from typing import Union, Optional
from PIL import Image
import numpy as np
from typing import Dict, Any, List, Tuple

from PIL.Image import Resampling

from image_generator.algorithm import Algorithm
from image_generator.algorithms.wfc_pattern_data import pattern_data_dict, PatternData, PatternImage
from image_generator.parameter import Parameter, DataType, VisibleType
from image_generator.utils import apply_transparency_mask, crop_image_by_size, convert_list_of_rgb_to_rgba, \
    convert_hex_list_to_rgba, combine_lists_to_tuples, apply_color_changes_rgba, convert_hex_list_to_rgb, \
    scale_down_dimensions_in_ratio, get_unique_colors_rgb, extend_colors, ensure_color_format


def array_to_image(array: np.ndarray) -> Optional[Image.Image]:
    if not isinstance(array, np.ndarray) or array.dtype != np.uint8:
        print("Error: The input must be a numpy array with dtype np.uint8.")
        return None

    try:
        img = Image.fromarray(array)
        return img
    except Exception as e:
        print(f"Error while converting array to image: {e}")
        return None


def run_overlapping(options: wfc_cpp.Options, numpy_pattern_img: wfc_cpp.Array2Duint32_t, seed: int, limit: int) -> (
        bool, np.ndarray):
    wfc = wfc_cpp.OverlappingWFC(options, numpy_pattern_img)
    is_done = wfc.run_overlapping_wfc(seed, limit)
    array2d_vect = wfc.get_output()
    img_numpy = (array2d_vect.to_numpy())
    return is_done, img_numpy


def run_wfc(pattern_data: PatternData,
            width_g: int, height_g: int,
            width_f: int, height_f: int,
            seed: int, gen_attempt_limit: int
            ) -> Image.Image:
    options = pattern_data.to_wfc_options(width_g, height_g, False)
    random.seed(seed)

    is_done = False
    attempts = 0

    while (not is_done) and (attempts < gen_attempt_limit):
        seed_internal = random.randint(0, 2000000000)
        (is_done, numpy_img) = run_overlapping(options, pattern_data.pattern_image.image, seed_internal, pattern_data.limit)
        attempts += 1

    img_t = array_to_image(numpy_img)
    img = img_t.resize((width_f, height_f), Resampling.NEAREST)
    return img


allowed_patterns = [{
    "value": key,
    "visible_value": value.visible_name
} for key, value in pattern_data_dict.items()]

wfc_specific_parameters = [
    Parameter(name="max_gen_dim",
              visible_name="Base max generation dimensions",
              data_type=DataType.INTEGER,
              visible_type=VisibleType.SLIDER,
              default=192,
              min_value=80,
              max_value=250),
    Parameter(name="pattern",
              visible_name="Pattern",
              data_type=DataType.ENUM_LIST,
              visible_type=VisibleType.SELECTOR,
              default="RedMaze",
              possible_values=allowed_patterns,
              ),
    Parameter(name="scale",
              visible_name="Additional scaling",
              data_type=DataType.FLOAT_TUPLE,
              visible_type=VisibleType.RANGE_SLIDER,
              default=(1.0, 2.0),
              min_value=1.0,
              max_value=10.0),
]


class WFCAlgorithm(Algorithm):
    def __init__(self,
                 name: str = "wfc",
                 visible_name: str = "Wave Function Collapse",
                 ):
        parameters = [
            Parameter(name="colors",
                      visible_name="Colors",
                      data_type=DataType.COLORS,
                      visible_type=VisibleType.COLORS,
                      default=[],
                      min_count=0,
                      max_count=10),
            *wfc_specific_parameters
        ]
        super().__init__(name, visible_name, parameters)

    def algorithm(self,
                  width: int,
                  height: int,
                  seed: Optional[int] = None,
                  area: Optional[List[List[bool]]] = None,
                  colors: Optional[List[str]] = None,
                  scale: Tuple[float, float] = (1.0, 2.0),
                  pattern: str = "RedMaze",
                  max_gen_dim: int = 192,
                  **kwargs
                  ) -> Image:

        pattern_data = pattern_data_dict[pattern]
        random.seed(seed)
        scale = random.uniform(*scale)

        g_width, g_height = scale_down_dimensions_in_ratio(width, height, max_gen_dim, max_gen_dim)

        image = run_wfc(pattern_data,
                        g_width, g_height,
                        round(width * scale), round(height * scale),
                        seed, 100)

        image = crop_image_by_size(image, width, height)

        if colors is None:
            colors = []
        to_change_colors = convert_hex_list_to_rgb(colors)
        to_change_colors = extend_colors(to_change_colors, pattern_data.pattern_image.colors, seed, True)
        color_change_rules = combine_lists_to_tuples(pattern_data.pattern_image.colors, to_change_colors)

        image = apply_color_changes_rgba(image, None, color_change_rules)
        if area is not None:
            apply_transparency_mask(image, area)

        return image


if __name__ == '__main__':
    wfc_alg = WFCAlgorithm("wfc", "Wave Function Collapse")
    img = wfc_alg.algorithm(1920, 1080, None, None, ["#000000FF", "#ffffff22", "#0000ffFF", "#00ff00FF"], (1, 1),
                            "RedMaze")
    img.show()
