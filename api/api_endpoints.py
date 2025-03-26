import io
from typing import Optional
from fastapi import Response, APIRouter
from api.store_query_service import QueryIdModel
from api.image_generator_config import image_generator
from api import store_query_service, template_query_service
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
        image_metadata_bytes = image_metadata.model_dump_json().encode("utf-8")
        fields["image"] = ("image.png", image_bytes, "image/png")
        fields["metadata"] = ("metadata.json", image_metadata_bytes, "application/json")
        multipart_encoder = MultipartEncoder(fields=fields)
        return Response(content=multipart_encoder.to_string(), media_type=multipart_encoder.content_type)
    return Response(content=image_bytes, media_type="image/png")

@api_router.post("/store-query/full")
async def store_query_full(query: QueryFull) -> QueryIdModel:
    query_id_model = await store_query_service.store_query_full(query)
    return query_id_model


@api_router.get("/store-query/{query_id}")
async def store_query_id(query_id: str,
                         include_metadata: Optional[bool] = True,
                         include_image: Optional[bool] = True) -> Response:
    stored_query_full, image_bytes = await store_query_service.retrieve_query_and_image(query_id)
    if include_metadata and include_image:
        fields = {}
        image_metadata_bytes = stored_query_full.model_dump_json().encode("utf-8")
        fields["image"] = ("image.png", image_bytes, "image/png")
        fields["metadata"] = ("metadata.json", image_metadata_bytes, "application/json")
        multipart_encoder = MultipartEncoder(fields=fields)
        return Response(content=multipart_encoder.to_string(), media_type=multipart_encoder.content_type)
    elif include_metadata:
        image_metadata_bytes = stored_query_full.model_dump_json().encode("utf-8")
        return Response(content=image_metadata_bytes, media_type="application/json")
    elif include_image:
        return Response(content=image_bytes, media_type="image/png")
    return Response(status_code=200)


@api_router.get("/template-query/all")
async def template_query_all(include_metadata: Optional[bool] = True,
                             include_image: Optional[bool] = True,
                             full_metadata: Optional[bool] = True) -> Response:
    queries_and_images = await template_query_service.retrieve_all_queries_and_images(full_metadata=full_metadata)
    fields = []
    if not include_metadata and not include_image:
        return Response(status_code=200)
    for idx, (metadata, image_bytes) in enumerate(queries_and_images):
        if include_image:
            fields.append((f"image{idx}", ("image.png", image_bytes, "image/png")))
        if include_metadata:
            fields.append((f"metadata{idx}", ("metadata.json", metadata.model_dump_json().encode("utf-8"), "application/json")))
    multipart_encoder = MultipartEncoder(fields=fields)
    return Response(content=multipart_encoder.to_string(), media_type=multipart_encoder.content_type)


@api_router.get("/template-query/{template_query_id}")
async def template_query_id(template_query_id: str,
                            include_metadata: Optional[bool] = True,
                            include_image: Optional[bool] = True) -> Response:
    template_query_full, image_bytes = await template_query_service.retrieve_query_and_image(template_query_id)
    if include_metadata and include_image:
        fields = {}
        image_metadata_bytes = template_query_full.model_dump_json().encode("utf-8")
        fields["image"] = ("image.png", image_bytes, "image/png")
        fields["metadata"] = ("metadata.json", image_metadata_bytes, "application/json")
        multipart_encoder = MultipartEncoder(fields=fields)
        return Response(content=multipart_encoder.to_string(), media_type=multipart_encoder.content_type)
    elif include_metadata:
        image_metadata_bytes = template_query_full.model_dump_json().encode("utf-8")
        return Response(content=image_metadata_bytes, media_type="application/json")
    elif include_image:
        return Response(content=image_bytes, media_type="image/png")
    return Response(status_code=200)


# @api_router.post("/image-generator/query/random")
# async def generate_image_query_random():
#     pass
