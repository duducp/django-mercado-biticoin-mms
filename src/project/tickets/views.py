# Create the request body and response schemas
# https://django-ninja.rest-framework.com/tutorial

from http import HTTPStatus
from typing import List

from django.contrib.auth import authenticate
from django.db.models import Q

from ninja import Query, Router
from ninja.errors import HttpError
from ninja.security import HttpBasicAuth

from project.core.exceptions import InternalServerError, NotFoundError
from project.tickets.models import Tickets
from project.tickets.schemas import (
    QueryFilter,
    TicketsInSchema,
    TicketsOutSchema
)

router = Router(tags=['tickets'])


class BasicAuth(HttpBasicAuth):
    def authenticate(self, request, username, password):
        return authenticate(username=username, password=password)


@router.get(
    path='/',
    summary='Tickets',
    description='',
    response={
        HTTPStatus.OK: List[TicketsOutSchema],
    }
)
def retrieve_tickets(request, filters: QueryFilter = Query(None)):
    try:
        filters = filters.dict()
        value = filters['value']

        if not value:
            tickets = Tickets.objects.order_by('name').all()
        else:
            value = str(value).upper()
            tickets = Tickets.objects.filter(
                Q(cpf=value) |
                Q(name__contains=value)
            ).order_by('name').all()

        return HTTPStatus.OK, tickets
    except Exception:
        raise InternalServerError(
            'An internal error occurred while making the request.'
        )


@router.put(
    path='/',
    summary='Tickets',
    description='',
    response={
        HTTPStatus.OK: TicketsInSchema,
    },
    auth=BasicAuth()
)
def update_tickets(request, payload: TicketsInSchema):
    try:
        if not request.user.has_perm('tickets.validate_ticket'):
            raise HttpError(
                HTTPStatus.FORBIDDEN, 'No permission to validate ticket'
            )

        payload = payload.dict()

        ticket = Tickets.objects.get(id=payload['id'])

        if ticket.validated:
            raise HttpError(HTTPStatus.BAD_REQUEST, 'ID validated')

        ticket.validated = True
        ticket.save()

        return HTTPStatus.OK, {'id': ticket.id}

    except HttpError:
        raise

    except Tickets.DoesNotExist:
        raise NotFoundError('Id not found')

    except Exception:
        raise InternalServerError(
            'An internal error occurred while making the request.'
        )
