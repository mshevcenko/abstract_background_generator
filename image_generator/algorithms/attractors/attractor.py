from abc import abstractmethod
from typing import Optional, Tuple, List


class Attractor:

    @abstractmethod
    def generate_points(self,
                        num_points: Optional[int] = None,
                        seed: Optional[int] = None,
                        randomise: bool = True) -> List[Tuple[float, ...]]:
        pass

    @abstractmethod
    def dimensions(self) -> int:
        pass
