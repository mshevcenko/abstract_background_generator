import random

import numpy as np
from PIL import Image
from typing import Tuple, List, Optional, Union

Color = Tuple[int, int, int]  # RGB
ColorAlpha = Tuple[int, int, int, int]  # RGBA
ColorType = Union[Color, ColorAlpha, List[Color], List[ColorAlpha]]  # Accepts single or list of colors


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
                             color_changes: List[Tuple[Union[Color, ColorAlpha], Union[Color, ColorAlpha]]]
                             ) -> Image.Image:
    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    pixels = image.load()
    width, height = image.size

    color_map = {ensure_color_format(old_color, True): ensure_color_format(new_color, True)
                 for old_color, new_color in color_changes}

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


def convert_hex_list_to_rgb(hex_colors: List[str]) -> List[Color]:
    return [hex_to_rgb(hex_color) for hex_color in hex_colors]


def convert_hex_list_to_rgba(hex_colors: List[str]) -> List[ColorAlpha]:
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


def convert_list_of_rgb_to_rgba(rgb_colors: List[Color]) -> List[ColorAlpha]:
    return ensure_color_format(rgb_colors, True)


def ensure_color_format(colors: ColorType, use_alpha: bool) -> ColorType:
    is_single = isinstance(colors, tuple)
    colors = [colors] if is_single else colors

    if use_alpha:
        colors = [(c[0], c[1], c[2], c[3] if len(c) == 4 else 255) for c in colors]
    else:
        colors = [(c[0], c[1], c[2]) for c in colors]

    return colors[0] if is_single else colors


def interpolate_colors(color1, color2, t):
    return (
        int(color1[0] * (1 - t) + color2[0] * t),
        int(color1[1] * (1 - t) + color2[1] * t),
        int(color1[2] * (1 - t) + color2[2] * t)
    )
def apply_color_palette(noise_map, colors, color_variation=0.2):

    colors_array = np.array(colors, dtype=np.float32)
    n_colors = colors_array.shape[0]

    height, width = noise_map.shape

    scaled = noise_map * (n_colors - 1)
    index = np.floor(scaled).astype(int)
    index = np.clip(index, 0, n_colors - 2)
    interp_factor = scaled - index

    color1 = colors_array[index]
    color2 = colors_array[index + 1]

    interpolated_color = color1 * (1 - interp_factor[..., None]) + color2 * interp_factor[..., None]

    variation = np.random.uniform(-color_variation, color_variation, size=(height, width, 3))
    final_color = np.clip(interpolated_color + variation * 255, 0, 255)

    return final_color.astype(np.uint8)


def extract_color_to_int(image: Image.Image) -> np.ndarray:
    img_array = np.array(image)

    color_map = {}
    color_counter = 1

    for i in range(img_array.shape[0]):
        for j in range(img_array.shape[1]):
            color = tuple(img_array[i, j])
            if color not in color_map:
                color_map[color] = color_counter
                color_counter += 1

    int_array = np.zeros((img_array.shape[0], img_array.shape[1]), dtype=int)

    for i in range(img_array.shape[0]):
        for j in range(img_array.shape[1]):
            color = tuple(img_array[i, j])
            int_array[i, j] = color_map[color]

    return int_array


def scale_dimensions_in_ratio(final_width: int, final_height: int,
                              max_size_w: int = 250, max_size_h: int = 250
                              ) -> tuple[int, int]:
    scale_factor = min(max_size_w / final_width, max_size_h / final_height, 1.0)
    new_width = int(final_width * scale_factor)
    new_height = int(final_height * scale_factor)
    return new_width, new_height


def get_unique_colors_rgb(image: Image) -> List[Color]:
    if image.mode != 'RGB':
        image = image.convert('RGB')

    img_array = np.array(image)
    pixels = img_array.reshape(-1, 3)
    unique_colors = np.unique(pixels, axis=0)
    return [tuple(color) for color in unique_colors]


def generate_random_colors(n: int, seed: int, use_alpha: bool = False) -> List[Union[Color, ColorAlpha]]:
    random.seed(seed)

    if use_alpha:
        return [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for _
                in range(n)]
    else:
        return [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for _ in range(n)]


def extend_colors(colors: List[Union[Color, ColorAlpha]],
                  pattern_colors: List[Union[Color, ColorAlpha]],
                  seed: int, use_alpha: bool = False):
    if len(colors) < len(pattern_colors):
        missing_count = len(pattern_colors) - len(colors)
        colors.extend(generate_random_colors(missing_count, seed, use_alpha))
    return ensure_color_format(colors, use_alpha)
