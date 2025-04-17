from PIL import Image, ImageDraw
from typing import List
import math
import random
import math
from typing import Optional, List
from image_generator.algorithm import Algorithm
from image_generator.parameter import Parameter, DataType, VisibleType
from image_generator.utils import apply_transparency_mask



class DragonCurveGenerator(Algorithm):
    def __init__(self,
                 name: str,
                 visible_name: str,):
        parameters = [
            Parameter(name="colors",
                      visible_name="Colors",
                      description="Defines the colors used for the curves. Can include multiple colors",
                      data_type=DataType.COLORS,
                      visible_type=VisibleType.COLORS,
                      default=["#ff0000", "#00ff00"],
                      min_count=1,
                      max_count=10),
            Parameter(name="scale",
                      visible_name="Scale",
                      description="Controls the scaling factor for the image. Larger values increase size.",
                      data_type=DataType.FLOAT,
                      visible_type=VisibleType.SLIDER,
                      default=1.0,
                      min_value=0.5,
                      max_value=100.0),
            Parameter(name="iterations",
                      visible_name="Iterations",
                      description="Specifies the number of iterations for generating the dragon curve complexity",
                      data_type=DataType.INTEGER,
                      visible_type=VisibleType.SLIDER,
                      default=12,
                      min_value=1,
                      max_value=25),
            Parameter(name="matrix",
                      visible_name="Matrix",
                      description="Determines the number of curves arranged in a grid-like matrix",
                      data_type=DataType.INTEGER,
                      visible_type=VisibleType.SLIDER,
                      default=2,
                      min_value=2,
                      max_value=6),
            Parameter(name="offset_x",
                      visible_name="Offset_x",
                      description="Sets the horizontal spacing between curves in the matrix",
                      data_type=DataType.INTEGER,
                      visible_type=VisibleType.SLIDER,
                      default=0,
                      min_value=0,
                      max_value=2000),
            Parameter(name="offset_y",
                      visible_name="Offset_y",
                      description="Sets the vertical spacing between curves in the matrix",
                      data_type=DataType.INTEGER,
                      visible_type=VisibleType.SLIDER,
                      default=0,
                      min_value=0,
                      max_value=2000),
            Parameter(name="line_width",
                      visible_name="Line width",
                      description="Defines the thickness of the curve lines",
                      data_type=DataType.INTEGER,
                      visible_type=VisibleType.SLIDER,
                      default=1,
                      min_value=1,
                      max_value=40),
            Parameter(name="matrix_offset_x",
                      visible_name="Matrix offset x",
                      description="Applies an additional horizontal offset to the entire matrix",
                      data_type=DataType.INTEGER,
                      visible_type=VisibleType.SLIDER,
                      default=0,
                      min_value=0,
                      max_value=2000),
            Parameter(name="matrix_offset_y",
                      visible_name="Matrix offset y",
                      description="Applies an additional vertical offset to the entire matrix",
                      data_type=DataType.INTEGER,
                      visible_type=VisibleType.SLIDER,
                      default=0,
                      min_value=0,
                      max_value=2000),

        ]
        super().__init__(name, visible_name, "Create image using multiple dragon curves algorithm", parameters)
    
    def algorithm(self,
                  width: int,
                  height: int,
                  seed: Optional[int] = None,
                  area: Optional[List[List[bool]]] = None,
                  matrix: int = 2,
                  offset_x: int = 100,
                  offset_y: int = 100,
                  colors: List[str] = ["#ff0000", "#00ff00"],
                  scale: float = 100.0,
                  iterations: int = 12,
                  line_width: int = 1,
                  matrix_offset_x: int = 0,
                  matrix_offset_y: int = 0,
                  **kwargs) -> Image.Image:
       img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
       draw = ImageDraw.Draw(img)
       if area:
            img = apply_transparency_mask(img, area)
       sequence = dragon_curve_sequence(iterations)
       base_points = calculate_dragon_curve_points(sequence)

       min_x = min(x for x, y in base_points)
       max_x = max(x for x, y in base_points)
       min_y = min(y for x, y in base_points)
       max_y = max(y for x, y in base_points)
       cx = (min_x + max_x) / 2
       cy = (min_y + max_y) / 2
       centered_points = [(x - cx, y - cy) for x, y in base_points]
       scaled_points = [(x * scale, y * scale) for x, y in centered_points]
       def draw_rounded_polyline(draw_obj, pts, r, fill_color, width_px):
        def unit_vector(vx, vy):
            mag = math.hypot(vx, vy)
            return (vx / mag, vy / mag) if mag != 0 else (0, 0)

        def angle_from_center(cx, cy, px, py):
            return math.degrees(math.atan2(py - cy, px - cx))

        def compute_corner(prev_pt, corner_pt, next_pt, radius):
            in_vec = (corner_pt[0] - prev_pt[0], corner_pt[1] - prev_pt[1])
            out_vec = (next_pt[0] - corner_pt[0], next_pt[1] - corner_pt[1])
            d_in = unit_vector(in_vec[0], in_vec[1])
            d_out = unit_vector(out_vec[0], out_vec[1])
            cross = in_vec[0]*out_vec[1] - in_vec[1]*out_vec[0]
            T1 = (corner_pt[0] - d_in[0]*radius, corner_pt[1] - d_in[1]*radius)
            T2 = (corner_pt[0] + d_out[0]*radius, corner_pt[1] + d_out[1]*radius)
            cx_arc = corner_pt[0] - d_in[0]*radius + d_out[0]*radius
            cy_arc = corner_pt[1] - d_in[1]*radius + d_out[1]*radius
            start_angle = angle_from_center(cx_arc, cy_arc, T1[0], T1[1])
            end_angle  = angle_from_center(cx_arc, cy_arc, T2[0], T2[1])
            if cross < 0:
                start_angle, end_angle = end_angle, start_angle
            if end_angle < start_angle:
                end_angle += 360
            bbox = (cx_arc - radius, cy_arc - radius, cx_arc + radius, cy_arc + radius)
            return T1, T2, bbox, start_angle, end_angle

        if len(pts) < 2:
            return
        current_pt = pts[0]
        for i in range(1, len(pts) - 1):
            p0 = pts[i - 1]
            p1 = pts[i]
            p2 = pts[i + 1]
            T1, T2, arc_box, a1, a2 = compute_corner(p0, p1, p2, r)
            draw_obj.line([current_pt, T1], fill=fill_color, width=width_px)
            draw_obj.arc(arc_box, start=a1, end=a2, fill=fill_color, width=width_px)
            current_pt = T2
        if len(pts) > 1:
            draw_obj.line([current_pt, pts[-1]], fill=fill_color, width=width_px)
       corner_radius = scale / 4
       center_x = width // 2
       center_y = height // 2

       for i in range(matrix):
        for j in range(matrix):
            pos_x = center_x + (i - matrix // 2) * offset_x + matrix_offset_x
            pos_y = center_y + (j - matrix // 2) * offset_y + matrix_offset_y 
            color = colors[(i + j) % len(colors)]
            final_points = [(x + pos_x, y + pos_y) for x, y in scaled_points]
            draw_rounded_polyline(draw, final_points, corner_radius, fill_color=color, width_px=line_width)

       return img
    
def dragon_curve_sequence(n: int) -> List[int]:
        sequence = []
        for _ in range(n):
            old = sequence[:]
            sequence.append(1)
            sequence.extend([-x for x in reversed(old)])
        return sequence
    
    
def calculate_dragon_curve_points(sequence: List[int]) -> List[tuple]:
        points = [(0, 0), (1, 0)]
        direction = 0
        for turn in sequence:
            x, y = points[-1]
            direction = (direction + turn) % 4
            if direction == 0:
                points.append((x + 1, y))
            elif direction == 1:
                points.append((x, y + 1))
            elif direction == 2:
                points.append((x - 1, y))
            else:
                points.append((x, y - 1))
        return points