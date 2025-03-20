import numpy as np
from PIL import Image
from typing import Tuple, List, Optional


def apply_transparency_mask(image: Image.Image,
                            mask: List[List[bool]]) -> Image.Image:
    if image.mode != "RGBA":
        image = image.convert("RGBA")
    width, height = image.size
    if len(mask) != height or any(len(row) != width for row in mask):
        raise ValueError("Mask dimensions must match the image dimensions (height x width)")
    pixels = np.array(image)
    mask_np = np.array(mask, dtype=bool)
    pixels[~mask_np] = [0, 0, 0, 0]
    return Image.fromarray(pixels, "RGBA")


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6 and len(hex_color) != 8:
        raise ValueError(f"Hex color must be 6 or 8 characters long {hex_color}")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return r, g, b


def hex_to_rgba(hex_color: str) -> Tuple[int, int, int, int]:
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 8:
        raise ValueError(f"Hex color must be 8 characters long {hex_color}")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    a = int(hex_color[6:8], 16)
    return r, g, b, a


def hex_to_rgb_normalized(hex_color: str) -> Tuple[float, float, float]:
    r, g, b = hex_to_rgb(hex_color)
    r /= 255.0
    g /= 255.0
    b /= 255.0
    return r, g, b


def hex_to_rgba_normalized(hex_color: str) -> Tuple[float, float, float, float]:
    r, g, b, a = hex_to_rgba(hex_color)
    r /= 255.0
    g /= 255.0
    b /= 255.0
    a /= 255.0
    return r, g, b, a


def apply_color_changes_rgba(image: Image.Image, mask: Optional[np.ndarray],
                             color_changes: List[Tuple[Tuple[int, int, int, int], Tuple[int, int, int, int]]]
                             ) -> Image.Image:
    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    pixels = image.load()
    width, height = image.size

    color_map = {old_color: new_color for old_color, new_color in color_changes}

    if mask is None or not np.any(mask):
        for y in range(height):
            for x in range(width):
                current_color = pixels[x, y]
                if current_color in color_map:
                    pixels[x, y] = color_map[current_color]
    else:
        for y in range(height):
            for x in range(width):
                if mask[y, x]:
                    current_color = pixels[x, y]
                    if current_color in color_map:
                        pixels[x, y] = color_map[current_color]

    return image


def convert_hex_list_to_rgb(hex_colors: List[str]) -> List[Tuple[int, int, int]]:
    return [hex_to_rgb(hex_color) for hex_color in hex_colors]


def convert_hex_list_to_rgba(hex_colors: List[str]) -> List[Tuple[int, int, int, int]]:
    return [hex_to_rgba(hex_color) for hex_color in hex_colors]


def combine_lists_to_tuples(list1: List, list2: List) -> List[Tuple]:
    min_length = min(len(list1), len(list2))
    return [(list1[i], list2[i]) for i in range(min_length)]


def crop_image_by_size(image: Image.Image, width: int, height: int, left: int=0, upper: int=0) -> Image.Image:
    right = left + width
    lower = upper + height
    box = (left, upper, right, lower)
    cropped_image = image.crop(box)
    return cropped_image


def convert_list_of_rgb_to_rgba(rgb_colors: List[Tuple[int, int, int]]) -> List[Tuple[int, int, int, int]]:
    return [(r, g, b, 255) for r, g, b in rgb_colors]


def interpolate_colors(color1, color2, t):
    return (
        int(color1[0] * (1 - t) + color2[0] * t),
        int(color1[1] * (1 - t) + color2[1] * t),
        int(color1[2] * (1 - t) + color2[2] * t)
    )