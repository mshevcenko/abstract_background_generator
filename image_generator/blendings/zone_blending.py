import copy
import random

import PIL
import numpy as np
from PIL.Image import Image
from typing import List, Optional, Dict

from api.algorithm_instances_config import algorithm_instances_list, AlgorithmInstancesEnum
from image_generator.algorithms.wfc_algorithm import allowed_patterns, wfc_specific_parameters
from image_generator.layer import Layer
from image_generator.blending import Blending
from image_generator.parameter import Parameter, DataType, VisibleType
from image_generator.utils import extract_color_to_int, get_copy_with_appended_visible_name, append_to_visible_name


class LayerUid:
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


def collect_layers_weights(layers_stuid_l: List[LayerUid]) -> Dict[int, float]:
    return {ll.uid: ll.layer.blending_values.get(ZONE_WEIGHT_KEY, 0) for ll in layers_stuid_l}


def distribute_zones(zone_matrix: np.ndarray, layers_stuid_l: List[LayerUid]) -> Dict[int, List[int]]:
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
    layers_stuid_l: List[LayerUid] = [LayerUid(index, layer) for index, layer in enumerate(layers)]
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


basic_colors: List[str] = ["#ff0000", "#00ff00"]


def generate_zones_matrix(zgf: int,
                          width: int,
                          height: int,
                          **kwargs) -> np.ndarray:
    img = algorithm_instances_list[zgf].algorithm(width=width, height=height, **kwargs)
    return extract_color_to_int(img)


def generate_allowed_zone_gen_fun(enum_values: List[AlgorithmInstancesEnum]) -> List[Dict]:
    zone_gen_fun = []
    for enum_value in enum_values:
        zone_gen_fun.append({
            "value": enum_value.value,
            "visible_value": algorithm_instances_list[enum_value.value].visible_name
        })
    return zone_gen_fun


allowed_zone_gen_fun = generate_allowed_zone_gen_fun([
    AlgorithmInstancesEnum.voronoi,
    AlgorithmInstancesEnum.wfc,
    AlgorithmInstancesEnum.smooth_wave,
    AlgorithmInstancesEnum.hex_pattern,
])


def gen_annot_for_algorithm_str(algorithm_index: int, f_part: str = " (if using ", s_part: str = ")") -> str:
    for zone in allowed_zone_gen_fun:
        if zone["value"] == algorithm_index:
            return f"{f_part}{zone['visible_value']}{s_part}"
    return ""


wfc_annot = gen_annot_for_algorithm_str(AlgorithmInstancesEnum.wfc.value)
parameters_for_wfc = copy.deepcopy(wfc_specific_parameters)
append_to_visible_name(parameters_for_wfc, wfc_annot)


voronoi_annot = gen_annot_for_algorithm_str(AlgorithmInstancesEnum.voronoi.value)
parameters_for_voronoi = [
    Parameter(
        name="n_points",
        visible_name="Number of points",
        data_type=DataType.INTEGER,
        visible_type=VisibleType.SLIDER,
        default=100,
        min_value=10,
        max_value=500
    )
]
append_to_visible_name(parameters_for_voronoi, voronoi_annot)


hexes_annot = gen_annot_for_algorithm_str(AlgorithmInstancesEnum.hex_pattern.value)
parameters_for_hexes = [
    Parameter(
        name="hex_size",
        visible_name="Hex Size",
        data_type=DataType.INTEGER,
        visible_type=VisibleType.SLIDER,
        default=80,
        min_value=10,
        max_value=200
    ),
    Parameter(
        name="spacing",
        visible_name="Spacing",
        data_type=DataType.INTEGER,
        visible_type=VisibleType.SLIDER,
        default=0,
        min_value=0,
        max_value=100
    )
]
append_to_visible_name(parameters_for_hexes, hexes_annot)


waves_annot = gen_annot_for_algorithm_str(AlgorithmInstancesEnum.smooth_wave.value)
parameters_for_waves = [
    Parameter(
        name="n_layers",
        visible_name="Number of layers",
        data_type=DataType.INTEGER,
        visible_type=VisibleType.SLIDER,
        default=10,
        min_value=5,
        max_value=20
    )
]
append_to_visible_name(parameters_for_waves, waves_annot)


class ZoneBlending(Blending):
    def __init__(self,
                 name="zone_blending",
                 visible_name="Zone blending"):
        parameters = [
            Parameter(name="zone_gen_fun",
                      visible_name="Zone generation function",
                      data_type=DataType.ENUM_LIST,
                      visible_type=VisibleType.SELECTOR,
                      default=AlgorithmInstancesEnum.voronoi.value,
                      possible_values=allowed_zone_gen_fun),
            Parameter(name="scale",
                      visible_name="Additional scaling (if algorithm allows)",
                      data_type=DataType.FLOAT_TUPLE,
                      visible_type=VisibleType.RANGE_SLIDER,
                      default=(1.0, 2.0),
                      min_value=1.0,
                      max_value=10.0),
            *parameters_for_wfc,
            *parameters_for_voronoi,
            *parameters_for_hexes,

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
                 zone_gen_fun: int = AlgorithmInstancesEnum.voronoi.value,
                 **kwargs) -> Image:
        zones_matrix = generate_zones_matrix(zone_gen_fun,
                                             monochrome=True,
                                             width=width,
                                             height=height,
                                             **kwargs
                                             )
        zones_info = generate_zone_info(zones_matrix, layers)

        combined_image = combine_images_using_zones(
            [zinfo.layer.generate(width, height, area=zinfo.mask.tolist()) for zinfo in zones_info],
            zones_info, width, height
        )

        return combined_image
