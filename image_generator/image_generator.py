import random
from PIL.Image import Image
from pydantic import BaseModel
from typing import List, Optional, Tuple
from image_generator.layer import Layer, LayerQuery
from image_generator.seed_generator import SeedGenerator
from image_generator.blending import BlendingModel, Blending
from image_generator.generator import Generator, GeneratorType
from image_generator.algorithm import AlgorithmModel, Algorithm


class ImageGeneratorModel(BaseModel):
    blendings: List[BlendingModel]
    algorithms: List[AlgorithmModel]


class QueryFull(BaseModel):
    layer_query: LayerQuery
    width: int
    height: int
    seed: Optional[int] = None


class QueryRandom(BaseModel):
    width: int
    height: int
    count: int
    min_layers_count: Optional[int] = None
    max_layers_count: Optional[int] = None


class ImageMetadataFull(BaseModel):
    width: int
    height: int
    seed: int
    layer_query: LayerQuery


class ImageGenerator:

    def __init__(self,
                 generators: List[Generator]):
        self.generators = generators
        #self.seed_generator = SeedGenerator()
        self.generators_dict = {}
        self.create_generators_dict()
        self.blendings = [blending for blending in self.generators if blending.generator_type == GeneratorType.BLENDING]
        self.algorithms = [algorithm for algorithm in self.generators if algorithm.generator_type == GeneratorType.ALGORITHM]
        self.model = ImageGeneratorModel(
            blendings=[blending.model for blending in self.generators if blending.generator_type == GeneratorType.BLENDING],
            algorithms=[algorithm.model for algorithm in self.generators if algorithm.generator_type == GeneratorType.ALGORITHM],
        )

    def generate_image_query_full(self,
                                  query: QueryFull) -> Tuple[Image, ImageMetadataFull]:
        width = query.width
        height = query.height
        layer_query = query.layer_query
        seed = query.seed
        layer = Layer(layer_query, self.generators_dict)
        if not seed:
            seed = SeedGenerator().generate_seed()
        layers_seed_generator = SeedGenerator(seed=seed)
        layer.generate_seed(layers_seed_generator)
        image = layer.generate(width, height)
        metadata = ImageMetadataFull(
            width=width,
            height=height,
            seed=seed,
            layer_query=layer_query
        )
        return image, metadata

    def __random_algorithm_query(self) -> LayerQuery:
        algorithms = [algorithm for algorithm in self.algorithms if algorithm.name != "geometric_shape_algorithm"]
        algorithm: Algorithm = random.choice(algorithms)
        values = {parameter.name: parameter.random_value() for parameter in algorithm.parameters}
        return LayerQuery(name=algorithm.name,
                          generator_type=algorithm.generator_type,
                          values=values)

    def __random_blending_query(self,
                                layers_count: int) -> LayerQuery:
        blending: Blending = random.choice(self.blendings)
        values = {parameter.name: parameter.random_value() for parameter in blending.parameters}
        #blending_values = {parameter.name: parameter.random_value() for parameter in blending.blending_parameters}
        layers = []
        i = 1
        while i <= layers_count:
            is_next_blending: bool = False
            if layers_count - i > 0:
                is_next_blending = random.uniform(0.0, 1.0) < 0.3
            if is_next_blending:
                inner_blending_layers_count = random.randint(1, layers_count - i)
                inner_layer_query = self.__random_blending_query(layers_count=inner_blending_layers_count)
                i += inner_blending_layers_count
            else:
                inner_layer_query = self.__random_algorithm_query()
            layers.append(inner_layer_query)
            i += 1
        for layer in layers:
            layer.blending_values = {parameter.name: parameter.random_value() for parameter in blending.blending_parameters}
        return LayerQuery(name=blending.name,
                          generator_type=blending.generator_type,
                          values=values,
                          layers=layers)

    def random_query(self,
                     width: int,
                     height: int,
                     min_layers_count: int = 2,
                     max_layers_count: int = 7) -> QueryFull:
        if min_layers_count < 2:
            min_layers_count = 2
        if min_layers_count > max_layers_count:
            max_layers_count = min_layers_count
        layers_count = random.randint(min_layers_count, max_layers_count)
        layer_query = self.__random_blending_query(layers_count=layers_count - 1)
        layer = Layer(layer_query, self.generators_dict)
        seed = SeedGenerator().generate_seed()
        layers_seed_generator = SeedGenerator(seed=seed)
        layer.generate_seed(layers_seed_generator)
        return QueryFull(width=width,
                         height=height,
                         layer_query=layer_query,
                         seed=seed)

    def generate_random_images(self,
                               query_random: QueryRandom) -> List[Tuple[Image, ImageMetadataFull]]:
        images_metadatas = []
        width = query_random.width
        height = query_random.height
        count = query_random.count
        min_layers_count = query_random.min_layers_count
        max_layers_count = query_random.max_layers_count
        if min_layers_count is None:
            min_layers_count = 2
        if max_layers_count is None:
            max_layers_count = min_layers_count
        for _ in range(count):
            query = self.random_query(width=width,
                                      height=height,
                                      min_layers_count=min_layers_count,
                                      max_layers_count=max_layers_count)
            image_metadata = self.generate_image_query_full(query)
            images_metadatas.append(image_metadata)
        return images_metadatas

    def create_generators_dict(self) -> None:
        for generator in self.generators:
            if generator.name in self.generators_dict:
                raise ValueError(f"Generators have same name: \"{generator.name}\"")
            self.generators_dict[generator.name] = generator
