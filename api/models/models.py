from typing import List

from pydantic import BaseModel


class QueryIdModel(BaseModel):
    query_id: str


class TemplateIdModel(BaseModel):
    template_query_id: str


class PopularTotalModel(BaseModel):
    total: int


class QueryIdsModel(BaseModel):
    query_ids: List[str]