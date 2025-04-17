import random
import numpy as np
from typing import List, Tuple
from scipy.integrate import odeint
from image_generator.algorithms.attractors.attractor import Attractor


def qi_chen(state, t, a, b, c, d, f):
    x, y, z = state
    dx = a * (y - x) + d * x * z
    dy = c * x - x * z + f * y
    dz = x * y - b * z
    return [dx, dy, dz]


class QiChenAttractor(Attractor):
    def __init__(self,
                 a: float = 35.0,
                 b: float = 3.0,
                 c: float = 28.0,
                 d: float = 1.0,
                 f: float = 3.0,
                 initial: Tuple[float, float, float] = (0.1, 0.0, 0.0),
                 t_max: float = 40.0,
                 num_points: int = 10000):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.f = f
        self.initial = initial
        self.num_points = num_points
        self.t = np.linspace(0, t_max, num_points)

    def generate_points(self,
                        num_points: int = None,
                        seed: int = None,
                        randomise: bool = True) -> List[Tuple[float, ...]]:
        if seed is not None:
            random.seed(seed)
        a = self.a
        b = self.b
        c = self.c
        d = self.d
        f = self.f
        initial = self.initial
        if randomise:
            a += random.uniform(-1, 1)
            b += random.uniform(-0.5, 0.5)
            c += random.uniform(-2, 2)
            d += random.uniform(-0.1, 0.1)
            f += random.uniform(-0.1, 0.1)
            initial = (
                initial[0] + random.uniform(-0.1, 0.1),
                initial[1] + random.uniform(-0.1, 0.1),
                initial[2] + random.uniform(-0.1, 0.1)
            )
        t = self.t
        if num_points is not None:
            t = np.linspace(t[0], t[-1], num_points)
        points = odeint(qi_chen, initial, t, args=(a, b, c, d, f), rtol=1e-8, atol=1e-8)
        return points

    def dimensions(self) -> int:
        return 3