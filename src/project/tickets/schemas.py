# Create the request body and response schemas
# https://django-ninja.rest-framework.com/tutorial/body
# https://django-ninja.rest-framework.com/tutorial/response-schema
# https://django-ninja.rest-framework.com/tutorial/django-pydantic/
from datetime import datetime

from ninja import Schema


class TicketsOutSchema(Schema):
    id: int
    active: bool
    name: str
    cpf: str
    promoter: str = None
    note: str = None
    validated: bool
    created_at: datetime
    updated_at: datetime


class TicketsInSchema(Schema):
    id: int


class QueryFilter(Schema):
    value: str = ''
