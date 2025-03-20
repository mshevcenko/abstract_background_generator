import numpy as np
from PIL import Image
from typing import Tuple, List


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

def apply_color_palette(self, noise_map, colors, color_variation=0.2):
      
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
