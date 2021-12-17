# Create the request body and response schemas
# https://django-ninja.rest-framework.com/tutorial/body
# https://django-ninja.rest-framework.com/tutorial/response-schema
# https://django-ninja.rest-framework.com/tutorial/django-pydantic/

from ninja import Schema


class TicketsOutSchema(Schema):
    message: str


class TicketsInSchema(Schema):
    message: str
