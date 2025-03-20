import numpy as np
from PIL import Image, ImageDraw
from random import randint
from scipy.spatial import Voronoi
from typing import Optional, List, Dict, Any

from image_generator.algorithm import Algorithm
from image_generator.parameter import Parameter, DataType, VisibleType
from image_generator.utils import hex_to_rgb, interpolate_colors  # функції для роботи з кольорами


class VoronoiAlgorithm(Algorithm):
    PARAMETERS = [
        Parameter(
            name="colors",
            visible_name="Colors",
            data_type=DataType.COLORS,
            visible_type=VisibleType.COLORS,
            default=["#FF5733", "#33FF57"]
        ),
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

    def __init__(self,
                 name: str,
                 visible_name: str):
        super().__init__(name, visible_name, self.PARAMETERS)

    def algorithm(self,
                  width: int,
                  height: int,
                  seed: Optional[int] = None,
                  area: Optional[List[List[bool]]] = None,
                  colors: Optional[List[str]] = None,
                  **kwargs) -> Image:
        if seed is not None:
            np.random.seed(seed)
        n_points = kwargs.get("n_points", 100)
        points = np.random.rand(n_points, 2) * [width, height]
        vor = Voronoi(points)

        if colors is not None and len(colors) >= 2:
            base_color = hex_to_rgb(colors[0])
            secondary_color = hex_to_rgb(colors[1])
        else:
            base_color = (randint(50, 200), randint(50, 200), randint(50, 200))
            secondary_color = (randint(150, 255), randint(150, 255), randint(150, 255))

        img = Image.new("RGB", (width, height), (randint(50, 100), randint(50, 100), randint(50, 100)))
        draw = ImageDraw.Draw(img)

        regions = [region for region in vor.regions if region and -1 not in region]
        for i, region in enumerate(regions):
            polygon = [tuple(vor.vertices[j]) for j in region]
            t = i / len(regions)
            color = interpolate_colors(base_color, secondary_color, t)
            draw.polygon(polygon, fill=color)
        return img