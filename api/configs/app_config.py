from fastapi import FastAPI

from api.configs.middleware_config import TimeoutMiddleware
from api.services import template_query_service, random_images_service
from api.endpoints.api_endpoints import api_router
from starlette.middleware.cors import CORSMiddleware


app = FastAPI()
app.include_router(api_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(TimeoutMiddleware, timeout=60.0)
app.add_event_handler("startup", template_query_service.init_template_queries_collection)
app.add_event_handler("startup", random_images_service.init_random_queries)