import random
import numpy as np
from typing import List, Tuple
from scipy.integrate import odeint
from image_generator.algorithms.attractors.attractor import Attractor


def lorenz(state, t, sigma, beta, rho):
    x, y, z = state
    dx = sigma * (y - x)
    dy = x * (rho - z) - y
    dz = x * y - beta * z
    return [dx, dy, dz]


class LorenzAttractor(Attractor):

    def __init__(self,
                 sigma=10.0,
                 beta=8.0 / 3.0,
                 rho=28.0,
                 initial=(0.1, 0.0, 0.0),
                 t_max=40.0,
                 num_points=10000):
        self.sigma = sigma
        self.beta = beta
        self.rho = rho
        self.initial = initial
        self.num_points = num_points
        self.t = np.linspace(0, t_max, num_points)

    def generate_points(self,
                        num_points=None,
                        seed=None,
                        randomise=True) -> List[Tuple[float, ...]]:
        if seed:
            random.seed(seed)
        sigma = self.sigma
        beta = self.beta
        rho = self.rho
        initial = self.initial
        if randomise:
            sigma = sigma + random.uniform(-1, 1)
            beta = beta + random.uniform(-0.5, 0.5)
            rho = rho + random.uniform(-2, 2)
            initial = (
                initial[0] + random.uniform(-0.1, 0.1),
                initial[1] + random.uniform(-0.1, 0.1),
                initial[2] + random.uniform(-0.1, 0.1)
            )
        t = self.t
        if num_points:
            t = np.linspace(t[0], t[-1], num_points)
        points = odeint(lorenz, initial, t, args=(sigma, beta, rho))
        return points

    def dimensions(self) -> int:
        return 3
