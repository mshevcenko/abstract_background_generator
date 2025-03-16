import io
from typing import Optional
from fastapi import APIRouter, Response
from api.image_generator_config import image_generator
from requests_toolbelt.multipart.encoder import MultipartEncoder
from image_generator.image_generator import ImageGeneratorModel, QueryFull


api_router = APIRouter(prefix="/api")


@api_router.get("/image-generator/model")
async def image_generator_model() -> ImageGeneratorModel:
    return image_generator.model


@api_router.post("/image-generator/query/full")
async def generate_image_query_full(include_metadata: Optional[bool],
                                    query: QueryFull) -> Response:
    image, image_metadata = image_generator.generate_image_query_full(query)
    fields = {}
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    buf.seek(0)
    image_bytes = buf.read()
    if include_metadata:
        image_metadata_bytes = image_metadata.json().encode("utf-8")
        fields["image"] = ("image.png", image_bytes, "image/png")
        fields["metadata"] = ("metadata.json", image_metadata_bytes, "application/json")
        multipart_encoder = MultipartEncoder(fields=fields)
        return Response(content=multipart_encoder.to_string(), media_type=multipart_encoder.content_type)
    return Response(content=image_bytes, media_type="image/png")


@api_router.post("/image-generator/query/short")
async def generate_image_query_short():
    pass


@api_router.post("/image-generator/query/random")
async def generate_image_query_random():
    pass
