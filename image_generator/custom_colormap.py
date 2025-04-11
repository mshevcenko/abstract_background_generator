from typing import List, Tuple

from scipy.interpolate import interp1d
import numpy as np


class CustomColormap:
    def __init__(self, colors: List[Tuple[int, int, int]], name: str = "custom", interpolation: str = "l"):
        """
        Create a custom colormap.

        Parameters:
        - colors: list of RGB colors (tuples or lists of [r, g, b], values in [0, 1] or [0, 255])
        - name: optional name
        - interpolation: "linear" or "nearest"
        """
        self.name = name
        self.colors = np.array(colors, dtype=np.float32)
        if self.colors.max() > 1.0:
            self.colors /= 255.0  # Normalize if in 0-255 range

        self.interpolation = interpolation
        self._build_interpolators()

    def _build_interpolators(self):
        x = np.linspace(0, 1, len(self.colors))
        kind = "linear" if self.interpolation == "l" else "nearest"
        self.r_interp = interp1d(x, self.colors[:, 0], kind=kind)
        self.g_interp = interp1d(x, self.colors[:, 1], kind=kind)
        self.b_interp = interp1d(x, self.colors[:, 2], kind=kind)

    def __call__(self, values):
        """
        Apply colormap to normalized values in [0, 1].

        Returns: Nx3 RGB array (0-255)
        """
        values = np.clip(values, 0, 1)
        r = self.r_interp(values)
        g = self.g_interp(values)
        b = self.b_interp(values)
        return np.stack([r, g, b], axis=-1) * 255

    def terraced(self, values, terrace_width=0.05):
        """
        Apply terraced color effect.

        `terrace_width` controls the step size in normalized [0,1].
        """
        terraced_values = np.floor(values / terrace_width) * terrace_width
        return self.__call__(terraced_values)
