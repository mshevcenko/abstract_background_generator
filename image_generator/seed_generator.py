import numpy as np
from typing import Optional

int64_info = np.iinfo(np.int64)
int32_info = np.iinfo(np.int32)
low = 0
high = int32_info.max #int64_info.max


class SeedGenerator:

    def __init__(self,
                 seed: Optional[int] = None):
        if seed:
            self.rng = np.random.default_rng(seed)
        else:
            self.rng = np.random.default_rng()

    def generate_seed(self) -> int:
        return self.rng.integers(low=low, high=high, endpoint=True).item()
