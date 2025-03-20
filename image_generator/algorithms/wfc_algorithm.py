import random

import wfc_cpp_dll.wfc_cpp as wfc_cpp #it writes that it cannot find wfc_cpp but it work

import xml.etree.ElementTree as ET
from typing import Union, Optional
from PIL import Image
import numpy as np
from typing import Dict, Any, List, Tuple

from PIL.Image import Resampling


from image_generator.algorithm import Algorithm
from image_generator.parameter import Parameter, DataType, VisibleType
from image_generator.utils import apply_transparency_mask, crop_image_by_size, convert_list_of_rgb_to_rgba, \
    convert_hex_list_to_rgba, combine_lists_to_tuples, apply_color_changes_rgba


def read_xml_file(file_path: str) -> List[Dict[str, Any]]:
    tree = ET.parse(file_path)
    root = tree.getroot()

    def parse_node(node: ET.Element) -> Dict[str, Any]:
        parsed_node = {
            "tag": node.tag,
            "attributes": node.attrib,
            "children": [parse_node(child) for child in node],
            "text": node.text.strip() if node.text else ""
        }
        return parsed_node

    return [parse_node(child) for child in root]


def find_node_by_name(nodes: List[Dict[str, Any]], name: str) -> Optional[Dict[str, Any]]:
    for node in nodes:
        if node.get("attributes", {}).get("name") == name:
            return node

        result = find_node_by_name(node.get("children", []), name)
        if result:
            return result

    return None


def get_attribute(node: Dict[str, Any], attribute_name: str, default_value: Any = None) -> Any:
    return node.get("attributes", {}).get(attribute_name, default_value)


def get_colors_from_node(node: Dict[str, Any]) -> List[Tuple[int, int, int]]:
    colors_node = next((child for child in node.get("children", []) if child["tag"] == "colors"), None)

    if not colors_node:
        return []

    colors = []
    for color_node in colors_node.get("children", []):
        if color_node["tag"] == "color":
            try:
                r, g, b = map(int, color_node["text"].split(","))
                colors.append((r, g, b))
            except ValueError:
                print(f"Invalid color value: {color_node['text']}")

    return colors


def read_image(image_path: str) -> Dict[str, Union[np.ndarray, int]]:
    """Reads an image and converts it to a 2D numpy array of uint32."""
    try:
        with Image.open(image_path) as img:
            img = img.convert("RGB")
            np_image = np.array(img, dtype=np.uint32)  # Convert to uint32 array

            mx, my = img.size
            flattened_img = (np_image[:, :, 0] << 16) + (np_image[:, :, 1] << 8) + np_image[:, :, 2]

            return {"MX": mx, "MY": my, "data": flattened_img}
    except Exception as e:
        print(f"Error while loading {image_path}: {e}")
        return None


def to_heuristic(heuristic_string: str) -> wfc_cpp.Heuristic:
    if heuristic_string == "Scanline":
        return wfc_cpp.Heuristic.Scanline
    elif heuristic_string == "Entropy":
        return wfc_cpp.Heuristic.Entropy
    elif heuristic_string == "MRV":
        return wfc_cpp.Heuristic.MRV
    else:
        raise ValueError(f"Invalid Heuristic: {heuristic_string}")


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


def run_overlapping(node: Dict[str, Any], width: int, height: int, seed: int, limit: int) -> (bool, np.ndarray):
    name = get_attribute(node, "name")
    size = get_attribute(node, "size", "48")
    N = int(get_attribute(node, "N", "3"))

    periodic_output = get_attribute(node, "periodic", "False") == "True"
    periodic_input = get_attribute(node, "periodicInput", "True") == "True"
    ground = get_attribute(node, "ground", "False") == "True"
    symmetry = int(get_attribute(node, "symmetry", "8"))
    heuristic = get_attribute(node, "heuristic", "Entropy")

    print(f"< {name}")

    image_path = f"patterns/{name}.png"
    pattern_img = read_image(image_path)

    if pattern_img is None:
        raise RuntimeError(f"Error while loading {image_path}")

    numpy_pattern_img = wfc_cpp.Array2Duint32_t.from_numpy(pattern_img["data"])

    options = wfc_cpp.Options()
    options.periodic_input = periodic_input
    options.periodic_output = periodic_output
    options.i_W = pattern_img["MX"]
    options.i_H = pattern_img["MY"]
    options.o_W = width
    options.o_H = height
    options.symmetry = (1 << symmetry) - 1
    options.pattern_size = N
    options.heuristic = to_heuristic(heuristic)
    options.ground = ground

    wfc = wfc_cpp.OverlappingWFC(options, numpy_pattern_img)

    is_done = wfc.run(seed, limit)
    print(is_done)

    array2d_vect =(wfc.get_output())
    img_numpy = (array2d_vect.to_numpy())
    return (is_done, img_numpy)


def run_wfc(pattern_name: str,
            width_g: int, height_g: int,
            width_f: int, height_f: int,
            seed: int, gen_attempt_limit: int
            ) -> Image.Image:
    xml_nodes = read_xml_file("patterns.xml")
    node = find_node_by_name(xml_nodes, pattern_name)

    random.seed(seed)

    is_done = False
    attempts = 0

    while((not is_done) and (attempts < gen_attempt_limit)):
        seed_internal = random.randint(0, 10000)
        (is_done, numpy_img) = run_overlapping(node, width_g, height_g, seed_internal, -1)
        attempts += 1

    img_t = array_to_image(numpy_img)
    img = img_t.resize((width_f, height_f), Resampling.NEAREST)
    return img


class WFCAlgorithm(Algorithm):
    def __init__(self,
                 name: str,
                 visible_name: str,
                 ):
        parameters = [
            Parameter(name="colors",
                      visible_name="Colors",
                      data_type=DataType.COLORS,
                      visible_type=VisibleType.COLORS,
                      default=[],
                      min_count=1,
                      max_count=10),
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
                      ]),
        ]
        super().__init__(name, visible_name, parameters)

    def algorithm(self,
                  width: int,
                  height: int,
                  seed: Optional[int] = None,
                  area: Optional[List[List[bool]]] = None,
                  colors=None,
                  scale: Tuple[float, float] = (1.0, 1.0),
                  pattern: str = "RedMaze"
                  ) -> Image:

        if colors is None:
            colors = []
        random.seed(seed)
        scale = random.uniform(*scale)

        image = run_wfc(pattern,
                      192, 108,
                        round(width * scale), round(height * scale),
                        seed, 100)

        image = crop_image_by_size(image, width, height)

        xml_nodes = read_xml_file("patterns.xml")
        node = find_node_by_name(xml_nodes, pattern)
        pattern_colors = convert_list_of_rgb_to_rgba(get_colors_from_node(node))
        to_change_colors = convert_hex_list_to_rgba(colors)
        color_change_rules = combine_lists_to_tuples(pattern_colors, to_change_colors)

        image = apply_color_changes_rgba(image, None, color_change_rules)
        if area is not None:
            apply_transparency_mask(image, area)

        return image


if __name__ == '__main__':
    wfc_alg = WFCAlgorithm("wfc", "Wave Function Collapse")
    img = wfc_alg.algorithm(1920, 1080, None, None, ["#000000FF", "#ffffff22", "#0000ffFF", "#00ff00FF"], (1, 2), "RedMaze")
    img.show()
