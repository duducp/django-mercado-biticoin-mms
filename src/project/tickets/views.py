# Create the request body and response schemas
# https://django-ninja.rest-framework.com/tutorial

from http import HTTPStatus
from typing import List

import structlog
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
logger = structlog.get_logger()


class BasicAuth(HttpBasicAuth):
    def authenticate(self, request, username, password):
        return authenticate(username=username, password=password)


@router.get(
    path='/login/',
    summary='Tickets',
    description='',
    auth=BasicAuth()
)
def login_tickets(request):
    return HTTPStatus.OK, {}


@router.get(
    path='/',
    summary='Tickets',
    description='',
    response={
        HTTPStatus.OK: List[TicketsOutSchema],
    },
    auth=BasicAuth()
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
        logger.error(
            'Erro nao tratado ao atualiza o ingresso',
            user=request.auth.username,
            filters=filters.dict(),
            exc_info=True
        )
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
        if not request.auth.has_perm('tickets.validate_ticket'):
            logger.error(
                'Usuario sem permissao para validar o ingresso',
                user=request.auth.username
            )
            raise HttpError(
                HTTPStatus.FORBIDDEN, 'No permission to validate ticket'
            )

        payload = payload.dict()

        ticket = Tickets.objects.get(id=payload['id'])

        if ticket.validated:
            logger.error(
                'Ingresso ja foi validado',
                cpf=ticket.cpf,
                user=request.auth.username
            )
            raise HttpError(HTTPStatus.BAD_REQUEST, 'ID validated')

        ticket.validated = True
        ticket.save()

        return HTTPStatus.OK, {'id': ticket.id}

    except HttpError:
        raise

    except Tickets.DoesNotExist:
        logger.error(
            'Ingresso nao encontrado',
            id=payload['id'],
            user=request.auth.username
        )
        raise NotFoundError('Id not found')

    except Exception:
        logger.error(
            'Erro nao tratado ao atualiza o ingresso',
            user=request.auth.username,
            payload=payload.dict(),
            exc_info=True
        )
        raise InternalServerError(
            'An internal error occurred while making the request.'
        )
