import numpy as np
import noise
from PIL import Image, ImageFilter, ImageDraw
import random
from typing import Optional, List
from image_generator.algorithm import Algorithm
from image_generator.parameter import Parameter, DataType, VisibleType
from image_generator.utils import apply_transparency_mask, hex_to_rgb_normalized, apply_color_palette

class ProceduralBackgroundGenerator(Algorithm):
    def __init__(self,
                 name: str,
                 visible_name: str,):
        parameters = [
            Parameter(name="colors",
                      visible_name="Colors",
                      data_type=DataType.COLORS,
                      visible_type=VisibleType.COLORS,
                      default=["#ff0000", "#00ff00"],
                      min_count=2,
                      max_count=10),
            Parameter(name="noise_type",
                      visible_name="Noise type",
                      data_type=DataType.ENUM_LIST,
                      visible_type=VisibleType.SELECTOR,
                      default=0,
                      possible_values=[{"value": 0, "visible_value": "Perlin"},
                                       {"value": 1, "visible_value": "Simplex"},
                                       {"value": 2, "visible_value": "Worley"},
                                       {"value": 3, "visible_value": "Brownian Motion Fractal"},
                                       {"value": 4, "visible_value": "Turbulence"}]
                      ),
            Parameter(name="scale",
                      visible_name="Scale",
                      data_type=DataType.FLOAT,
                      visible_type=VisibleType.SLIDER,
                      default=1.0,
                      min_value=0.5,
                      max_value=100.0),
            Parameter(name="blur_radius",
                      visible_name="Blur radius",
                      data_type=DataType.FLOAT,
                      visible_type=VisibleType.SLIDER,
                      default=1.0,
                      min_value=0.0,
                      max_value=10.0),
            Parameter(name="octaves",
                      visible_name="Octaves",
                      data_type=DataType.INTEGER,
                      visible_type=VisibleType.SLIDER,
                      default=6,
                      min_value=2,
                      max_value=32),
            Parameter(name="persistence",
                      visible_name="Persistence",
                      data_type=DataType.FLOAT,
                      visible_type=VisibleType.SLIDER,
                      default=0.5,
                      min_value=0.1,
                      max_value=3.0),
            Parameter(name="lacunarity",
                      visible_name="Lacunarity",
                      data_type=DataType.FLOAT,
                      visible_type=VisibleType.SLIDER,
                      default=2.0,
                      min_value=0.5,
                      max_value=6.0),
            Parameter(name="island_type",
                      visible_name="Island Type",
                      data_type=DataType.BOOL,
                      visible_type=VisibleType.CHECKBOX,
                      default=False),
        ]
        super().__init__(name, visible_name, parameters)
        

    def algorithm(self,
                  width: int,
                  height: int,
                  seed: Optional[int] = None,
                  area: Optional[List[List[bool]]] = None,
                  colors: List[str] = ["#ff0000", "#00ff00"],
                  scale: float = 100.0,
                  blur_radius: float = 1.0,
                  noise_type: int = 0,
                  octaves: int =6,
                  persistence:float =0.5,
                  lacunarity: float =2.0,
                  island_type: bool = False)-> Image.Image:
        random.seed(seed)
        if noise_type == 0:
            noise_map= self._generate_perlin_noise(width, height, scale, octaves, persistence, lacunarity)
        elif noise_type == 1:
            noise_map= self._generate_simplex_noise(width, height, scale, octaves, persistence, lacunarity)
        elif noise_type == 2:
            noise_map=  self._generate_worley_noise(width, height, scale)
        elif noise_type == 3:
            noise_map=  self._generate_fractal_brownian_motion(width, height, scale, octaves)
        elif noise_type == 4:
            noise_map= self._generate_turbulence(width, height, scale, octaves)
        else:
            raise ValueError("Invalid noise type")
        
        normalized_colors = [hex_to_rgb_normalized(color) for color in colors]
        if island_type:
          center_x, center_y = width / 2, height / 2
          max_distance = np.sqrt(center_x**2 + center_y**2)

          for y in range(height):
              for x in range(width):
                  distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
                  falloff = 1 - (distance / max_distance)
                  falloff = falloff**2
                  noise_map[y, x] *= falloff

          if (noise_map.min() != 0 or noise_map.max() != 1):
                noise_map = (noise_map - noise_map.min()) / (noise_map.max() - noise_map.min())
                
        color_image = apply_color_palette(noise_map, normalized_colors)        



        img = Image.fromarray(color_image)
        if blur_radius > 0:
            img = img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        if area:
            img = apply_transparency_mask(img, area)
        #filename = f"{noise_type}_background_.png"
        #img.save(filename)
        #print(f"Background saved as {filename}")
        return img

    def _generate_perlin_noise(self, width, height, scale=100.0, octaves=6, persistence=0.5, lacunarity=2.0):
        noise_map = np.zeros((height, width))
        for i in range(height):
            for j in range(width):
                noise_map[i][j] = noise.pnoise2(
                    i/scale,
                    j/scale,
                    octaves=octaves,
                    persistence=persistence,
                    lacunarity=lacunarity,
                    repeatx=width,
                    repeaty=height,
                    base=0
                )

        noise_map = (noise_map - noise_map.min()) / (noise_map.max() - noise_map.min())
        return noise_map

    def _generate_simplex_noise(self, width, height, scale=100.0, octaves=6, persistence=0.5, lacunarity=2.0):
        noise_map = np.zeros((height, width))
        for i in range(height):
            for j in range(width):
                noise_map[i][j] = noise.snoise2(
                    i/scale,
                    j/scale,
                    octaves=octaves,
                    persistence=persistence,
                    lacunarity=lacunarity
                )

        noise_map = (noise_map - noise_map.min()) / (noise_map.max() - noise_map.min())
        return noise_map

    def _generate_worley_noise(self, width, height, scale=100.0, points=5):
        feature_points = [(random.randint(0, width-1), random.randint(0, height-1)) for _ in range(points)]

        noise_map = np.zeros((height, width))
        for i in range(height):
            for j in range(width):
                distances = [np.sqrt((i - fp[0])**2 + (j - fp[1])**2) for fp in feature_points]
                noise_map[i][j] = min(distances) / scale

        noise_map = (noise_map - noise_map.min()) / (noise_map.max() - noise_map.min())
        return noise_map

    def _generate_fractal_brownian_motion(self, width, height, scale=100.0, octaves=6):
        noise_map = np.zeros((height, width))
        for i in range(height):
            for j in range(width):
                noise_map[i][j] = 0
                frequency = 1
                amplitude = 1
                max_value = 0
                for _ in range(octaves):
                    sample_x = i / scale * frequency
                    sample_y = j / scale * frequency

                    perlin_value = noise.pnoise2(sample_x, sample_y)
                    noise_map[i][j] += perlin_value * amplitude

                    max_value += amplitude
                    amplitude *= 0.5
                    frequency *= 2

                noise_map[i][j] /= max_value

        noise_map = (noise_map - noise_map.min()) / (noise_map.max() - noise_map.min())
        return noise_map

    def _generate_turbulence(self, width, height, scale=100.0, octaves=6):
        noise_map = np.zeros((height, width))
        for i in range(height):
            for j in range(width):
                noise_map[i][j] = abs(noise.pnoise2(
                    i/scale,
                    j/scale,
                    octaves=octaves
                ))

        noise_map = (noise_map - noise_map.min()) / (noise_map.max() - noise_map.min())
        return noise_map

    
    

    ''' def generate_background(self, width, height, noise_type='perlin',
                            palette='ocean',
                            scale=100.0, octaves=6,
                            persistence=0.5, lacunarity=2.0,
                            color_variation=0.2):


        noise_map = self.generate_noise(width, height, noise_type, scale, octaves, persistence, lacunarity)

        color_image = self.apply_color_palette(noise_map, palette, color_variation)

        img = Image.fromarray(color_image)

        img = img.filter(ImageFilter.GaussianBlur(radius=1))

        filename = f"{noise_type}_{palette}_background_.png"
        img.save(filename)
        print(f"Background saved as {filename}")
        return filename'''

