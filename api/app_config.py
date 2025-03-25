from fastapi import FastAPI
from api import template_query_service
from api.api_endpoints import api_router
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
app.add_event_handler("startup", template_query_service.init_template_queries_collection)