import os
from typing import List, Dict, Optional, Union

import numpy as np
import wfc_cpp
from PIL import Image

from image_generator.utils import get_unique_colors_rgb

current_folder = os.path.dirname(os.path.abspath(__file__))
image_folder = os.path.join(current_folder, "patterns/")


class PatternImage:
    def __init__(self,
                 image: np.ndarray,
                 mx: int,
                 my: int
                 ):
        self.image = wfc_cpp.Array2Duint32_t.from_numpy(image)
        self.mx = mx
        self.my = my
        self.colors = []


def read_image(image_path: str) -> PatternImage:
    """Reads an image and converts it to a 2D numpy array of uint32."""
    try:
        with Image.open(image_path) as img:
            img = img.convert("RGB")
            np_image = np.array(img, dtype=np.uint32)  # Convert to uint32 array

            mx, my = img.size
            flattened_img = (np_image[:, :, 0] << 16) + (np_image[:, :, 1] << 8) + np_image[:, :, 2]

            return PatternImage(flattened_img, mx, my)

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


pattern_data_dict = {}


class PatternData:

    def __init__(self,
                 name: str,
                 visible_name: str,
                 image_name: str,
                 nn: int = 3,
                 periodic: bool = False,
                 symmetry: int = 8,
                 ground: bool = False,
                 periodic_input: bool = True,
                 heuristic: wfc_cpp.Heuristic = wfc_cpp.Heuristic.Entropy,
                 size: Optional[int] = None,
                 limit: int = -1
                 ):
        self.name = name
        self.nn = nn
        self.periodic = periodic
        self.symmetry = symmetry
        self.ground = ground
        self.periodic_input = periodic_input
        self.heuristic = heuristic
        self.size = size
        self.limit = limit
        image_path = os.path.join(image_folder, f"{image_name}.png")
        self.pattern_image = read_image(image_path)
        self.pattern_image.colors = get_unique_colors_rgb(Image.open(image_path))
        self.visible_name = f"{visible_name} ({len(self.pattern_image.colors)} colors)"
        pattern_data_dict[self.name] = self

    def to_wfc_options(self,
                       g_width=192,
                       g_height=108,
                       overwrite_size: bool = False,
                       ) -> wfc_cpp.Options:
        options = wfc_cpp.Options()
        options.periodic_input = self.periodic_input
        options.periodic_output = self.periodic

        options.i_W = self.pattern_image.mx
        options.i_H = self.pattern_image.my

        if overwrite_size or self.size is None:
            options.o_W = g_width
            options.o_H = g_height
        else:
            options.o_W = self.size
            options.o_H = self.size

        options.symmetry = (1 << self.symmetry) - 1
        options.pattern_size = self.nn

        options.heuristic = self.heuristic
        options.ground = self.ground
        return options


PatternDataList = [
    PatternData(name="some_lines", visible_name="Some lines", image_name="some_lines", nn=2, periodic=True),
    PatternData(name="chess", visible_name="Chess", image_name="chess", nn=2, periodic=True),
    PatternData(name="Skyline", visible_name="Skyline", image_name="Skyline", nn=3, symmetry=2, ground=True,
                periodic=True),
    PatternData(name="Flowers", visible_name="Flowers", image_name="Flowers", nn=3, symmetry=2, ground=True,
                periodic=True),
    PatternData(name="Hogs_1", visible_name="Hogs 1", image_name="Hogs", nn=3, periodic=True),
    PatternData(name="Hogs_2", visible_name="Hogs 2", image_name="Hogs", nn=2, periodic=True),
    PatternData(name="Knot", visible_name="Knot", image_name="Knot", nn=3, periodic=True),
    PatternData(name="LessRooms", visible_name="LessRooms", image_name="LessRooms", nn=3, periodic=True),
    PatternData(name="Mountains", visible_name="Mountains", image_name="Mountains", nn=3, symmetry=2, periodic=True),
    PatternData(name="Office", visible_name="Office", image_name="Office", nn=3, periodic=True),
    PatternData(name="Paths", visible_name="Paths", image_name="Paths", nn=3, periodic=True),
    PatternData(name="RedMaze", visible_name="Red Maze", image_name="RedMaze", nn=2),
    PatternData(name="Rooms", visible_name="Rooms", image_name="Rooms", nn=3, periodic=True),
    PatternData(name="Rule126", visible_name="Rule 126", image_name="Rule126", nn=3, symmetry=2, periodic_input=False,
                periodic=False),
    PatternData(name="SimpleKnot", visible_name="Simple Knot", image_name="SimpleKnot", nn=3, periodic=True),
    PatternData(name="SimpleMaze", visible_name="Simple Maze", image_name="SimpleMaze", nn=2),
    PatternData(name="SimpleWall_1", visible_name="Simple Wall 1", image_name="SimpleWall", nn=3, symmetry=2,
                periodic=True),
    PatternData(name="SimpleWall_2", visible_name="Simple Wall 2", image_name="SimpleWall", nn=3, periodic=True),
    PatternData(name="SimpleWall_3", visible_name="Simple Wall 3", image_name="SimpleWall", nn=2, symmetry=2,
                periodic=True),
    PatternData(name="SimpleWall_4", visible_name="Simple Wall 4", image_name="SimpleWall", nn=2, periodic=True),
    PatternData(name="TrickKnot", visible_name="Trick Knot", image_name="TrickKnot", nn=3, periodic=True),
    PatternData(name="Water", visible_name="Water", image_name="Water", nn=3, symmetry=1, periodic=True),
    PatternData(name="Skyline2", visible_name="Skyline 2", image_name="Skyline2", nn=3, symmetry=2, ground=True,
                periodic=True),
    PatternData(name="Angular", visible_name="Angular", image_name="Angular", nn=3, periodic=True),
    PatternData(name="City", visible_name="City", image_name="City", nn=3, periodic=True),
    PatternData(name="ColoredCity", visible_name="Colored City", image_name="ColoredCity", nn=3, periodic=True),
    PatternData(name="Dungeon", visible_name="Dungeon", image_name="Dungeon", nn=3, periodic=True),
    PatternData(name="Lake", visible_name="Lake", image_name="Lake", nn=3, periodic=True),
    PatternData(name="Mazelike", visible_name="Mazelike", image_name="Mazelike", nn=3, periodic=True),
    PatternData(name="Nested", visible_name="Nested", image_name="Nested", nn=3, periodic=True),
    PatternData(name="MagicOffice", visible_name="Magic Office", image_name="MagicOffice", nn=3, periodic=True),
    PatternData(name="Office2", visible_name="Office 2", image_name="Office2", nn=3, periodic=True),
    PatternData(name="Qud", visible_name="Qud", image_name="Qud", nn=3, periodic=True),
    PatternData(name="ScaledMaze", visible_name="Scaled Maze", image_name="ScaledMaze", nn=2, periodic=True),
    PatternData(name="Sewers", visible_name="Sewers", image_name="Sewers", nn=3, periodic=True),
    PatternData(name="SmileCity", visible_name="Smile City", image_name="SmileCity", nn=3, periodic=True),
    PatternData(name="Spirals", visible_name="Spirals", image_name="Spirals", nn=3, periodic=True),
    PatternData(name="Town", visible_name="Town", image_name="Town", nn=3, periodic=True),
    PatternData(name="Wall_1", visible_name="Wall 1", image_name="Wall", nn=2, symmetry=1),
    PatternData(name="Wall_2", visible_name="Wall 2", image_name="Wall", nn=3, symmetry=2),
    PatternData(name="Lines", visible_name="Lines", image_name="Lines", nn=3),
    PatternData(name="WalledDot", visible_name="Walled Dot", image_name="WalledDot", nn=3),
    PatternData(name="NotKnot", visible_name="Not Knot", image_name="NotKnot", nn=3, periodic=True,
                periodic_input=False),
    PatternData(name="Sand", visible_name="Sand", image_name="Sand", nn=3, periodic=True, periodic_input=False),
    PatternData(name="Wrinkles", visible_name="Wrinkles", image_name="Wrinkles", nn=3, periodic=True,
                heuristic=wfc_cpp.Heuristic.MRV),
    PatternData(name="3Bricks", visible_name="3 Bricks", image_name="3Bricks", nn=3, symmetry=1, periodic=True),
    PatternData(name="Circle_1", visible_name="Circle 1", image_name="Circle", nn=3, symmetry=1, periodic=True,
                heuristic=wfc_cpp.Heuristic.MRV, size=90),
    PatternData(name="Circle_2", visible_name="Circle 2", image_name="Circle", nn=4, symmetry=1, periodic=True,
                heuristic=wfc_cpp.Heuristic.MRV, size=90),
    PatternData(name="Disk_1", visible_name="Disk 1", image_name="Disk", nn=3, symmetry=1, periodic=True,
                heuristic=wfc_cpp.Heuristic.MRV, size=90),
    PatternData(name="Disk_2", visible_name="Disk 2", image_name="Disk", nn=3, periodic=True,
                heuristic=wfc_cpp.Heuristic.MRV, size=90),
    PatternData(name="Disk_3", visible_name="Disk 3", image_name="Disk", nn=4, periodic=True,
                heuristic=wfc_cpp.Heuristic.MRV, size=90),
    PatternData(name="Font", visible_name="Font", image_name="Font", nn=5, symmetry=2, periodic=True,
                heuristic=wfc_cpp.Heuristic.MRV, size=90),

]
