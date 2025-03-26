import random
from enum import Enum

import PIL
import numpy as np
from PIL.Image import Image
from typing import List, Optional, Dict

import api.image_generator_config
from image_generator.algorithm import Algorithm
from image_generator.algorithms.voronoi_algorithm import VoronoiAlgorithm
from image_generator.algorithms.wfc_algorithm import WFCAlgorithm
from image_generator.layer import Layer
from image_generator.blending import Blending
from image_generator.parameter import Parameter, DataType, VisibleType
from image_generator.utils import extract_color_to_int


class Layer_Uid:
    def __init__(self, uid: int, layer: Layer):
        self.uid = uid
        self.layer = layer


class ZoneInfo:
    def __init__(self, layer: Layer, mask: np.ndarray, width: int, height: int, center_x: float, center_y: float,
                 top_left_x: int, top_left_y: int):
        self.layer = layer
        self.mask = mask
        self.width = width
        self.height = height
        self.center_x = center_x
        self.center_y = center_y
        self.top_left_x = top_left_x
        self.top_left_y = top_left_y


ZONE_WEIGHT_KEY = "zone_weight"


def collect_layers_weights(layers_stuid_l: List[Layer_Uid]) -> Dict[int, float]:
    return {ll.uid: ll.layer.blending_values.get(ZONE_WEIGHT_KEY, 0) for ll in layers_stuid_l}


def distribute_zones(zone_matrix: np.ndarray, layers_stuid_l: List[Layer_Uid]) -> Dict[int, List[int]]:
    layers_weights = collect_layers_weights(layers_stuid_l)
    unique_zones, counts = np.unique(zone_matrix, return_counts=True)

    non_zero_mask = unique_zones != 0
    unique_zones = unique_zones[non_zero_mask]
    counts = counts[non_zero_mask]

    zone_stats = dict(zip(unique_zones, counts))

    total_zone_size = sum(counts)
    sum_of_fun_weight = sum(layers_weights.values())

    weighted_zones = {layer_id: [] for layer_id in layers_weights.keys()}

    for zone_number, zone_size in zone_stats.items():
        effective_weights = [(layer_id, layers_weights[layer_id]) for layer_id in layers_weights]

        total_effective_weight = sum(weight for _, weight in effective_weights)

        if total_effective_weight > 0:
            chosen_function = random.choices(
                effective_weights,
                weights=[weight for _, weight in effective_weights],
                k=1
            )[0][0]

            # Calculate weight delta
            weight_delta = (zone_size / total_zone_size) * sum_of_fun_weight
            layers_weights[chosen_function] -= weight_delta

            if layers_weights[chosen_function] < 0:
                layers_weights[chosen_function] = 0

            weighted_zones[chosen_function].append(zone_number)

    return weighted_zones


def extract_zones(zone_matrix: np.ndarray, layer: Layer, assigned_zones: List[int],
                  separate_mask: bool = False, centralize: bool = False) -> List[ZoneInfo]:
    height, width = zone_matrix.shape
    zone_masks = {}

    # Create masks for each assigned zone
    for zone_number in assigned_zones:
        mask = (zone_matrix == zone_number)
        zone_masks[zone_number] = mask

    if not separate_mask:
        combined_mask = np.any([zone_masks[zone] for zone in assigned_zones], axis=0)
        if not np.any(combined_mask):
            combined_mask = np.full((height, width), False, dtype=bool)
        zone_masks = {0: combined_mask}

    result = []

    for zone_number, mask in zone_masks.items():
        mask_width = width
        mask_height = height
        top_left_x = 0
        top_left_y = 0
        center_y = top_left_y + mask_height / 2
        center_x = top_left_x + mask_width / 2

        if centralize:
            indices = np.argwhere(mask)
            if indices.size == 0:
                continue

            top_left_y, top_left_x = indices.min(axis=0)
            bottom_right_y, bottom_right_x = indices.max(axis=0)

            mask_height = bottom_right_y - top_left_y + 1
            mask_width = bottom_right_x - top_left_x + 1

            total_mass = indices.shape[0]
            center_y = np.sum(indices[:, 0]) / total_mass
            center_x = np.sum(indices[:, 1]) / total_mass
            # center_y = top_left_y + mask_height / 2
            # center_x = top_left_x + mask_width / 2

        result.append(ZoneInfo(layer, mask, mask_width, mask_height, center_x, center_y, top_left_x, top_left_y))

    return result


def generate_zone_info(matrix: np.ndarray, layers: List[Layer]) -> List[ZoneInfo]:
    layers_stuid_l: List[Layer_Uid] = [Layer_Uid(index, layer) for index, layer in enumerate(layers)]
    uid_and_zone_id_lists = distribute_zones(matrix, layers_stuid_l)
    res = []
    for layers_stuid in layers_stuid_l:
        res.extend(extract_zones(matrix, layers_stuid.layer, uid_and_zone_id_lists[layers_stuid.uid],
                                 False, False))
    return res


def combine_images_using_zones(images: List[Image], zones: List[ZoneInfo],
                               width: int, height: int) -> Image:
    result_image = PIL.Image.new("RGBA", (width, height), (0, 0, 0, 0))
    result_np = np.array(result_image)

    for image, zone in zip(images, zones):
        image = image.convert("RGBA")
        image_np = np.array(image)
        mask = zone.mask
        if mask.shape != (height, width):
            raise ValueError(f"Mask size {mask.shape} does not match the expected size ({height}, {width}).")

        result_np[mask] = image_np[mask]

    final_image = PIL.Image.fromarray(result_np)

    return final_image


class ZoneGenFunction(Enum):
    voronoi = 0
    wave_function_collapse = 1


generators = [
    VoronoiAlgorithm("vor", "vor"),
    WFCAlgorithm()
]

zone_patterns = ["RedMaze", "Spirals"]
basic_colors: List[str] = ["#ff0000", "#00ff00"]


def generate_zones_matrix(zgf: int,
                          width: int,
                          height: int,
                          seed: int,
                          area: Optional[List[List[bool]]] = None,
                          **kwargs) -> np.ndarray:
    random.seed(seed)
    img = generators[zgf].algorithm(width=width, height=height,
                                    seed=seed, area=area,
                                    colors=basic_colors,
                                    n_points=random.randint(10, 500),
                                    **kwargs)
    return extract_color_to_int(img)


class ZoneBlending(Blending):
    def __init__(self,
                 name="zone_blending",
                 visible_name="Zone blending"):
        parameters = [
            Parameter(name="zone_gen_fun",
                      visible_name="Zone generation function",
                      data_type=DataType.ENUM_LIST,
                      visible_type=VisibleType.SELECTOR,
                      default=ZoneGenFunction.voronoi.value,
                      possible_values=[
                          {"value": ZoneGenFunction.voronoi.value,
                           "visible_value": "Voronoi"},

                          {"value": ZoneGenFunction.wave_function_collapse.value,
                           "visible_value": "WFC"}
                      ], ),
            Parameter(name="scale",
                      visible_name="Additional scaling",
                      data_type=DataType.FLOAT_TUPLE,
                      visible_type=VisibleType.RANGE_SLIDER,
                      default=(1.0, 2.0),
                      min_value=1.0,
                      max_value=10.0),
            Parameter(name="pattern",
                      visible_name="Pattern",
                      data_type=DataType.ENUM_LIST,
                      visible_type=VisibleType.SELECTOR,
                      default="RedMaze",
                      possible_values=[
                          {"value": "RedMaze", "visible_value": "Red Maze"},
                          {"value": "Spirals", "visible_value": "Spirals"},
                      ], )
        ]
        blending_parameters = [
            Parameter(
                name=ZONE_WEIGHT_KEY,
                visible_name="Zone weight",
                data_type=DataType.FLOAT,
                visible_type=VisibleType.SLIDER,
                default=1.0,
                min_value=1.0,
                max_value=9999.0
            )
        ]
        super().__init__(name, visible_name, parameters, blending_parameters)

    def blending(self,
                 width: int,
                 height: int,
                 layers: List[Layer] = None,
                 seed: int = None,
                 area: Optional[List[List[bool]]] = None,
                 zone_gen_fun: int = ZoneGenFunction.voronoi,
                 **kwargs) -> Image:
        zones_matrix = generate_zones_matrix(zone_gen_fun,
                                             width, height,
                                             seed, area,
                                             **kwargs
                                             )
        zones_info = generate_zone_info(zones_matrix, layers)

        combined_image = combine_images_using_zones(
            [zinfo.layer.generate(width, height, area=zinfo.mask.tolist()) for zinfo in zones_info],
            zones_info, width, height
        )

        return combined_image
