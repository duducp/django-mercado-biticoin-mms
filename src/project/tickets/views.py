# Create the request body and response schemas
# https://django-ninja.rest-framework.com/tutorial

from http import HTTPStatus

from ninja import Router

from project.tickets.schemas import TicketsInSchema, TicketsOutSchema

router = Router(tags=['tickets'])


@router.get(
    path='/',
    summary='Tickets',
    description='',
    response={
        HTTPStatus.OK: TicketsOutSchema,
    }
)
async def retrieve_tickets(request, text: str = 'world'):
    data = {
        'message': f'Hello {text}'
    }

    return HTTPStatus.OK, data


@router.post(
    path='/',
    summary='Tickets',
    description='',
    response={
        HTTPStatus.OK: TicketsOutSchema,
    }
)
async def create_tickets(request, payload: TicketsInSchema):
    return HTTPStatus.OK, payload.dict()
