from typing import Optional
from fastapi import Response, APIRouter
from api.models.models import QueryIdModel, TemplateIdModel, PopularTotalModel, QueryIdsModel
from api.configs.image_generator_config import image_generator
from api.services import store_query_service, template_query_service, image_generation_service, random_images_service, \
    popular_images_service
from requests_toolbelt.multipart.encoder import MultipartEncoder
from image_generator.image_generator import ImageGeneratorModel, QueryFull, QueryRandom

api_router = APIRouter(prefix="/api")


@api_router.get("/image-generator/model")
async def image_generator_model() -> ImageGeneratorModel:
    return image_generator.model


@api_router.post("/image-generator/query/full")
async def generate_image_query_full(include_metadata: Optional[bool],
                                    query: QueryFull) -> Response:
    image_bytes, image_metadata = await image_generation_service.generate_image_bytes(query_full=query)
    if include_metadata:
        image_metadata_bytes = image_metadata.model_dump_json().encode("utf-8")
        fields = {"image": ("image.png", image_bytes, "image/png"),
                  "metadata": ("metadata.json", image_metadata_bytes, "application/json")}
        multipart_encoder = MultipartEncoder(fields=fields)
        return Response(content=multipart_encoder.to_string(), media_type=multipart_encoder.content_type)
    return Response(content=image_bytes, media_type="image/png")

@api_router.post("/store-query/full")
async def store_query_full(query: QueryFull) -> QueryIdModel:
    query_id = await store_query_service.store_query_full(query)
    return QueryIdModel(query_id=query_id)


@api_router.get("/store-query/{query_id}")
async def store_query_id(query_id: str,
                         include_metadata: Optional[bool] = True,
                         include_image: Optional[bool] = True) -> Response:
    stored_query_full_info, image_bytes = await store_query_service.retrieve_query_full_info_and_image_bytes(query_id=query_id)
    stored_query_full = stored_query_full_info.query_full
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
    queries_and_images_ids = await template_query_service.retrieve_all_templates_and_images_bytes()
    fields = []
    if not include_metadata and not include_image:
        return Response(status_code=200)
    for idx, (metadata, image_bytes, query_id) in enumerate(queries_and_images_ids):
        if include_image:
            fields.append((f"image{idx}", ("image.png", image_bytes, "image/png")))
        if include_metadata:
            if full_metadata:
                fields.append((f"metadata{idx}", ("metadata.json", metadata.query_full.model_dump_json().encode("utf-8"), "application/json")))
            else:
                query_id_model = TemplateIdModel(template_query_id=query_id)
                fields.append((f"metadata{idx}", ("metadata.json", query_id_model.model_dump_json().encode("utf-8"), "application/json")))
    multipart_encoder = MultipartEncoder(fields=fields)
    return Response(content=multipart_encoder.to_string(), media_type=multipart_encoder.content_type)


@api_router.get("/template-query/{template_query_id}")
async def template_query_id(template_query_id: str,
                            include_metadata: Optional[bool] = True,
                            include_image: Optional[bool] = True) -> Response:
    template_query_full, image_bytes = await template_query_service.retrieve_template_and_image_bytes(template_query_id)
    if include_metadata and include_image:
        fields = {}
        image_metadata_bytes = template_query_full.query_full.model_dump_json().encode("utf-8")
        fields["image"] = ("image.png", image_bytes, "image/png")
        fields["metadata"] = ("metadata.json", image_metadata_bytes, "application/json")
        multipart_encoder = MultipartEncoder(fields=fields)
        return Response(content=multipart_encoder.to_string(), media_type=multipart_encoder.content_type)
    elif include_metadata:
        image_metadata_bytes = template_query_full.query_full.model_dump_json().encode("utf-8")
        return Response(content=image_metadata_bytes, media_type="application/json")
    elif include_image:
        return Response(content=image_bytes, media_type="image/png")
    return Response(status_code=200)


@api_router.post("/image-generator/query/random")
async def generate_images_query_random(query_random: QueryRandom,
                                      include_metadata: Optional[bool] = True,
                                      include_image: Optional[bool] = True) -> Response:
    metadatas_images_bytes = await random_images_service.retrieve_random_images_bytes(query_random.count)
    fields = []
    if not include_metadata and not include_image:
        return Response(status_code=200)
    for idx, (metadata, image_bytes) in enumerate(metadatas_images_bytes):
        if include_image:
            fields.append((f"image{idx}", ("image.png", image_bytes, "image/png")))
        if include_metadata:
            fields.append((f"metadata{idx}", ("metadata.json", metadata.model_dump_json().encode("utf-8"), "application/json")))
    multipart_encoder = MultipartEncoder(fields=fields)
    return Response(content=multipart_encoder.to_string(), media_type=multipart_encoder.content_type)


@api_router.post("/image-generator/query/random/image")
async def generate_image_query_random() -> Response:
    metadatas_images_bytes = await random_images_service.retrieve_random_images_bytes(1)
    image_bytes = metadatas_images_bytes[0][0]
    return Response(content=image_bytes, media_type="image/png")


@api_router.put("/like/query-full")
async def like_query_full(query_full: QueryFull,
                          include_metadata: Optional[bool] = True,
                          full_metadata: Optional[bool] = True) -> Response:
    metadata = await popular_images_service.like_query_full(query_full)
    if metadata is None:
        return Response(status_code=500)
    elif not include_metadata:
        return Response(status_code=200)
    if not full_metadata:
        metadata = QueryIdModel(query_id=metadata.query_id)
    image_metadata_bytes = metadata.model_dump_json().encode("utf-8")
    return Response(content=image_metadata_bytes, media_type="application/json")


@api_router.put("/like/query-id/{query_id}")
async def like_query_id(query_id: str,
                        include_metadata: Optional[bool] = True,
                        full_metadata: Optional[bool] = True) -> Response:
    metadata = await popular_images_service.like_query_id(query_id)
    if metadata is None:
        return Response(status_code=404)
    elif not include_metadata:
        return Response(status_code=200)
    if not full_metadata:
        metadata = QueryIdModel(query_id=metadata.query_id)
    image_metadata_bytes = metadata.model_dump_json().encode("utf-8")
    return Response(content=image_metadata_bytes, media_type="application/json")


@api_router.put("/dislike/query-full")
async def dislike_query_full(query_full: QueryFull,
                             include_metadata: Optional[bool] = True,
                             full_metadata: Optional[bool] = True) -> Response:
    metadata = await popular_images_service.dislike_query_full(query_full)
    if metadata is None:
        return Response(status_code=500)
    elif not include_metadata:
        return Response(status_code=200)
    if not full_metadata:
        metadata = QueryIdModel(query_id=metadata.query_id)
    image_metadata_bytes = metadata.model_dump_json().encode("utf-8")
    return Response(content=image_metadata_bytes, media_type="application/json")


@api_router.put("/dislike/query-id/{query_id}")
async def dislike_query_id(query_id: str,
                           include_metadata: Optional[bool] = True,
                           full_metadata: Optional[bool] = True) -> Response:
    metadata = await popular_images_service.dislike_query_id(query_id)
    if metadata is None:
        return Response(status_code=404)
    elif not include_metadata:
        return Response(status_code=200)
    if not full_metadata:
        metadata = QueryIdModel(query_id=metadata.query_id)
    image_metadata_bytes = metadata.model_dump_json().encode("utf-8")
    return Response(content=image_metadata_bytes, media_type="application/json")

@api_router.get("/popular/total")
async def get_popular_total() -> PopularTotalModel:
    total = await popular_images_service.get_total()
    return PopularTotalModel(total=total)


@api_router.get("/popular/image/{query_id}")
async def get_popular_image(query_id: str,
                            include_metadata: Optional[bool] = True,
                            include_image: Optional[bool] = True,
                            full_metadata: Optional[bool] = True) -> Response:
    image_bytes_metadata = await popular_images_service.get_popular_image_by_id(query_id)
    if image_bytes_metadata is None:
        return Response(status_code=404)
    image_bytes, metadata = image_bytes_metadata
    if not include_metadata and not include_image:
        return Response(status_code=200)
    if not full_metadata:
        metadata = QueryIdModel(query_id=query_id)
    if include_image and include_metadata:
        fields = [(f"image", ("image.png", image_bytes, "image/png")), (
        f"metadata", ("metadata.json", metadata.query_full.model_dump_json().encode("utf-8"), "application/json"))]
        multipart_encoder = MultipartEncoder(fields=fields)
        return Response(content=multipart_encoder.to_string(), media_type=multipart_encoder.content_type)
    elif include_image:
        return Response(content=image_bytes, media_type="image/png")
    elif include_metadata:
        image_metadata_bytes = metadata.model_dump_json().encode("utf-8")
        return Response(content=image_metadata_bytes, media_type="application/json")
    return Response(status_code=500)


@api_router.get("/popular/images")
async def get_popular_image(page: Optional[int] = None,
                            page_size: Optional[int] = None,
                            include_metadata: Optional[bool] = True,
                            include_image: Optional[bool] = True,
                            full_metadata: Optional[bool] = True) -> Response:
    images_bytes_metadatas = await popular_images_service.get_popular_images(page=page, page_size=page_size)
    if not include_metadata and not include_image:
        return Response(status_code=200)
    fields = []
    for idx, (image_bytes, metadata) in enumerate(images_bytes_metadatas):
        if include_image:
            fields.append((f"image{idx}", ("image.png", image_bytes, "image/png")))
        if not full_metadata:
            metadata = QueryIdModel(query_id=metadata.query_id)
        if include_metadata:
            fields.append((f"metadata{idx}", ("metadata.json", metadata.model_dump_json().encode("utf-8"), "application/json")))
    multipart_encoder = MultipartEncoder(fields=fields)
    return Response(content=multipart_encoder.to_string(), media_type=multipart_encoder.content_type)


@api_router.post("/popular/images-by-ids")
async def get_popular_image(query_ids: QueryIdsModel,
                            include_metadata: Optional[bool] = True,
                            include_image: Optional[bool] = True,
                            full_metadata: Optional[bool] = True) -> Response:
    images_bytes_metadatas = await popular_images_service.get_popular_images_by_ids(query_ids=query_ids.query_ids)
    if not include_metadata and not include_image:
        return Response(status_code=200)
    fields = []
    for idx, (image_bytes, metadata) in enumerate(images_bytes_metadatas):
        if include_image:
            fields.append((f"image{idx}", ("image.png", image_bytes, "image/png")))
        if not full_metadata:
            metadata = QueryIdModel(query_id=metadata.query_id)
        if include_metadata:
            fields.append((f"metadata{idx}", ("metadata.json", metadata.model_dump_json().encode("utf-8"), "application/json")))
    multipart_encoder = MultipartEncoder(fields=fields)
    return Response(content=multipart_encoder.to_string(), media_type=multipart_encoder.content_type)