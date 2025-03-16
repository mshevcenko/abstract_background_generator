from typing import List, Dict, Union, Optional, Tuple
from PIL.Image import Image
from pydantic import BaseModel
from image_generator.algorithm import AlgorithmModel
from image_generator.blending import BlendingModel
from image_generator.layer import Layer, LayerQuery
from image_generator.generator import Generator
from image_generator.seed_generator import SeedGenerator


class ImageGeneratorModel(BaseModel):
    generators: List[Union[BlendingModel, AlgorithmModel]]


class QueryFull(BaseModel):
    layer_query: LayerQuery
    width: int
    height: int
    seed: Optional[int] = None
    full_metadata: Optional[bool] = True


class QueryShort(BaseModel):
    layer_query_seed: int
    width: int
    height: int
    seed: Optional[int]
    full_metadata: Optional[bool]


class QueryRandom(BaseModel):
    width: int
    height: int
    full_metadata: Optional[bool]


class ImageMetadataFull(BaseModel):
    width: int
    height: int
    seed: int
    layer_query: LayerQuery


class ImageMetadataShort(BaseModel):
    seed: int


class ImageMetadataRandomShort(BaseModel):
    seed: int
    layer_query_seed: int


class ImageGenerator:

    def __init__(self,
                 generators: List[Generator]):
        self.generators = generators
        self.seed_generator = SeedGenerator()
        self.generators_dict = {}
        self.create_generators_dict()
        self.model = ImageGeneratorModel(
            generators=[generator.model for generator in self.generators]
        )

    def generate_image_query_full(self,
                                  query: QueryFull) -> Tuple[Image, Union[ImageMetadataFull, ImageMetadataShort]]:
        width = query.width
        height = query.height
        layer_query = query.layer_query
        seed = query.seed
        full_metadata = query.full_metadata
        layer = Layer(layer_query, self.generators_dict)
        if not seed:
            seed = self.seed_generator.generate_seed()
        layers_seed_generator = SeedGenerator(seed=seed)
        layer.generate_seed(layers_seed_generator)
        image = layer.generate(width, height)
        if full_metadata is None or full_metadata:
            metadata = ImageMetadataFull(
                width=width,
                height=height,
                seed=seed,
                layer_query=layer_query
            )
        else:
            metadata = ImageMetadataShort(
                seed=seed
            )
        return image, metadata

    def create_generators_dict(self) -> None:
        for generator in self.generators:
            if generator.name in self.generators_dict:
                raise ValueError(f"Generators have same name: \"{generator.name}\"")
            self.generators_dict[generator.name] = generator
