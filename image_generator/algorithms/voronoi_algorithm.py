import numpy as np
import random
from PIL import Image, ImageDraw
from random import randint
from scipy.spatial import Voronoi
from typing import Optional, List, Dict, Any

from image_generator.algorithm import Algorithm
from image_generator.parameter import Parameter, DataType, VisibleType
from image_generator.utils import hex_to_rgb, interpolate_colors


class VoronoiAlgorithm(Algorithm):
    PARAMETERS = [
        Parameter(
            name="colors",
            visible_name="Colors",
            data_type=DataType.COLORS,
            visible_type=VisibleType.COLORS,
            default=["#FF5733", "#33FF57"],
            min_count=2,
            max_count=2,
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

    def __init__(self, name: str, visible_name: str):
        super().__init__(name, visible_name, self.PARAMETERS)

    def algorithm(self,
                  width: int,
                  height: int,
                  seed: Optional[int] = None,
                  area: Optional[List[List[bool]]] = None,
                  colors: Optional[List[str]] = None,
                  n_points: int = 100,
                  **kwargs) -> Image:
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

        margin = max(width, height) * 0.1
        points = np.random.rand(n_points, 2)
        points[:, 0] = points[:, 0] * (width + 2 * margin) - margin
        points[:, 1] = points[:, 1] * (height + 2 * margin) - margin

        from scipy.spatial import Voronoi
        vor = Voronoi(points)

        if colors is not None and len(colors) >= 2:
            base_color = hex_to_rgb(colors[0])
            secondary_color = hex_to_rgb(colors[1])
        else:
            base_color = (randint(50, 200), randint(50, 200), randint(50, 200))
            secondary_color = (randint(150, 255), randint(150, 255), randint(150, 255))

        img = Image.new("RGB", (width, height), (randint(50, 100), randint(50, 100), randint(50, 100)))
        draw = ImageDraw.Draw(img)

        def voronoi_finite_polygons_2d(vor, radius=None):
            if vor.points.shape[1] != 2:
                raise ValueError("Requires 2D input")
            new_regions = []
            new_vertices = vor.vertices.tolist()
            center = vor.points.mean(axis=0)
            if radius is None:
                radius = np.max(np.ptp(vor.points, axis=0)) * 2

            all_ridges = {}
            for (p1, p2), (v1, v2) in zip(vor.ridge_points, vor.ridge_vertices):
                all_ridges.setdefault(p1, []).append((p2, v1, v2))
                all_ridges.setdefault(p2, []).append((p1, v1, v2))

            for p1, region in enumerate(vor.point_region):
                vertices = vor.regions[region]
                if all(v >= 0 for v in vertices):
                    new_regions.append(vertices)
                    continue
                ridges = all_ridges[p1]
                new_region = [v for v in vertices if v >= 0]
                for p2, v1, v2 in ridges:
                    if v2 < 0:
                        v1, v2 = v2, v1
                    if v1 >= 0:
                        continue
                    t = vor.points[p2] - vor.points[p1]
                    t /= np.linalg.norm(t)
                    n = np.array([-t[1], t[0]])
                    midpoint = vor.points[[p1, p2]].mean(axis=0)
                    direction = np.sign(np.dot(midpoint - center, n)) * n
                    far_point = vor.vertices[v2] + direction * radius
                    new_region.append(len(new_vertices))
                    new_vertices.append(far_point.tolist())
                new_regions.append(new_region)
            return new_regions, np.array(new_vertices)

        regions, vertices = voronoi_finite_polygons_2d(vor)

        def clip_polygon(polygon, bbox):
            xmin, ymin, xmax, ymax = bbox
            clipped = []
            for x, y in polygon:
                clipped.append((max(xmin, min(x, xmax)), max(ymin, min(y, ymax))))
            return clipped

        bbox = (0, 0, width, height)
        for i, region in enumerate(regions):
            polygon = vertices[region].tolist()
            polygon = clip_polygon(polygon, bbox)
            if len(polygon) < 3:
                continue
            t = i / len(regions)
            color = interpolate_colors(base_color, secondary_color, t)
            draw.polygon(polygon, fill=color)

        return img

if __name__ == '__main__':
    wfc_alg = VoronoiAlgorithm("gradient_algorithm", "Gradient Algorithm")
    img = wfc_alg.algorithm(1920, 1080, None, None, ["#ffffff20", "#ffffff20"], 100)
    img.show()