import PIL
from PIL.Image import Image
from typing import List, Optional
from image_generator.layer import Layer
from image_generator.blending import Blending
from image_generator.parameter import Parameter, DataType, VisibleType


class AlphaBlending(Blending):

    def __init__(self,
                 name="alpha_blending",
                 visible_name="Alpha blending"):
        blending_parameters = [
            Parameter(
                name="opacity",
                visible_name="Opacity",
                description="Blending parameter. Controls opacity of full layer. 1 for a fully opaque result layer, 0 for a fully transparent one.",
                data_type=DataType.FLOAT,
                visible_type=VisibleType.SLIDER,
                default=1.0,
                min_value=0.0,
                max_value=1.0
            )
        ]
        super().__init__(name, visible_name, "Blending of layers by transparency (opacity). Mixes layers in one image by alpha color value. Have blending parameter Opacity for each inner layer to control alpha.", [], blending_parameters)

    def blending(self,
                 width: int,
                 height: int,
                 layers: List[Layer] = None,
                 seed: int = None,
                 area: Optional[List[List[bool]]] = None,
                 **kwargs) -> Image:
        combined_image = PIL.Image.new("RGBA", (width, height), (255, 255, 255, 0))
        for layer in reversed(layers):
            layer_image = layer.generate(width, height, area=area)
            if layer_image.mode != "RGBA":
                layer_image = layer_image.convert("RGBA")
            desired_alpha = int(layer.blending_values["opacity"] * 255)
            r, g, b, a = layer_image.split()
            a = a.point(lambda p: p if p <= desired_alpha else desired_alpha)
            layer_image = PIL.Image.merge("RGBA", (r, g, b, a))
            combined_image.paste(layer_image, mask=layer_image)
        return combined_image

