from PIL import Image, ImageDraw
import random
from typing import List, Optional
import numpy as np

from image_generator.algorithm import Algorithm
from image_generator.parameter import Parameter, DataType, VisibleType
from image_generator.utils import apply_transparency_mask, hex_to_rgb_normalized, hex_to_rgb

class DiamondGenerator(Algorithm):
    def __init__(self,
                 name: str,
                 visible_name: str,):
        parameters = [
            Parameter(name="colors",
                      visible_name="Colors",
                      description="Specifies the set of colors used to draw",
                      data_type=DataType.COLORS,
                      visible_type=VisibleType.COLORS,
                      default=["#ff0000", "#00ff00"],
                      min_count=2,
                      max_count=10),
            Parameter(name="scale",
                      visible_name="Scale",
                      description="Controls the size",
                      data_type=DataType.FLOAT,
                      visible_type=VisibleType.SLIDER,
                      default=1.0,
                      min_value=0.5,
                      max_value=100.0),
            Parameter(name="roughness",
                      visible_name="Roughness",
                      description="Controls the roughness",
                      data_type=DataType.FLOAT,
                      visible_type=VisibleType.SLIDER,
                      default=0.5,
                      min_value=0.5,
                      max_value=10.0),
            Parameter(name="min_height",
                      visible_name="Min height",
                      description="Controls the height that affect colors",
                      data_type=DataType.FLOAT,
                      visible_type=VisibleType.SLIDER,
                      default=0.0,
                      min_value=0.0,
                      max_value=2.0),
            Parameter(name="max_height",
                      visible_name="Max height",
                      description="Controls the height that affect colors",
                      data_type=DataType.FLOAT,
                      visible_type=VisibleType.SLIDER,
                      default=1.0,
                      min_value=1.0,
                      max_value=3.0),
        ]
        super().__init__(name, visible_name, "Create image using diamond-square algorithm", parameters)
    

    def algorithm(
            self,
            width: int,
            height: int,
            seed: Optional[int] = None,
            area: Optional[List[List[bool]]] = None,
            roughness: float = 0.5,
            min_height: float = 0.0,
            max_height: float = 1.0,
            colors: List[str] = ['#42aaff', '#4ccc4c', '#ccaa66'],
            scale: float = 1.0) -> Image.Image:
        
        rgb_colors = [hex_to_rgb(color) for color in colors]
        
        size = max(width, height)
        n = 1
        while 2**n + 1 <= size/scale:
            n += 1
        size = 2**n + 1
        
        if seed is not None:
            random.seed(seed)
        
        heightmap = np.zeros((size, size))
        
        heightmap[0, 0] = random.uniform(min_height, max_height)
        heightmap[0, size-1] = random.uniform(min_height, max_height)
        heightmap[size-1, 0] = random.uniform(min_height, max_height)
        heightmap[size-1, size-1] = random.uniform(min_height, max_height)
        
        step = size - 1
        
        while step > 1:
            half = step // 2

            for y in range(0, size-1, step):
                for x in range(0, size-1, step):
                    avg = (heightmap[y, x] + 
                        heightmap[y+step, x] +
                        heightmap[y, x+step] +
                        heightmap[y+step, x+step]) / 4.0
                    heightmap[y+half, x+half] = avg + random.uniform(-roughness, roughness)
            
            for y in range(0, size, half):
                for x in range((y + half) % step, size, step):
                    count = 0
                    avg = 0
                    
                    if y >= half:
                        avg += heightmap[y-half, x]
                        count += 1
                    if y + half < size:
                        avg += heightmap[y+half, x]
                        count += 1
                    if x >= half:
                        avg += heightmap[y, x-half]
                        count += 1
                    if x + half < size:
                        avg += heightmap[y, x+half]
                        count += 1
                    
                    if count > 0:
                        heightmap[y, x] = avg/count + random.uniform(-roughness, roughness)
            
            roughness *= 0.5
            step = half
        
        heightmap = np.clip(heightmap, 0, 1)
        
        img = Image.new('RGB', (width, height))
        pixels = img.load()
        
        thresholds = [i / len(rgb_colors) for i in range(1, len(rgb_colors))]

        for y in range(height):
            for x in range(width):
                sample_y = int((y / height) * (size-1))
                sample_x = int((x / width) * (size-1))
                height_val = heightmap[sample_y, sample_x]
                
                color_index = 0
                for i, threshold in enumerate(thresholds):
                    if height_val >= threshold:
                        color_index = i + 1
                
                pixels[x, y] = rgb_colors[color_index]
        
        if area:
            img = apply_transparency_mask(img, area)

        return img