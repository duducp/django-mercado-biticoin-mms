from http import HTTPStatus
from typing import List

from django.core.cache import cache
from ninja import Query, Router
from simple_settings import settings

from project.core.exceptions import InternalServerError
from project.indicators.mms.schemas import (
    IndicatorMmsResponseSchema,
    QueryFilter
)

from .helpers import get_simple_moving_average_variations

router = Router()


@router.get(
    path='/{pair}/mms',
    summary='Simple Moving Average',
    description='Service that delivers the 20, 50, and 200 day simple moving '
                'average variations of Bitcoin and Etherium currencies that '
                'are listed on the Mercado Bitcoin.',
    response={
        HTTPStatus.OK: List[IndicatorMmsResponseSchema],
    }
)
def retrieve(
    request,
    pair: str,
    filters: QueryFilter = Query(None)
):
    try:
        filters = filters.dict()
        precision = filters['precision']
        from_timestamp = filters['from_timestamp']
        to_timestamp = filters['to_timestamp']
        range_days = filters['range'].value

        cache_key = (
            'mms_retrieve_'
            f'{pair}_{precision}_{range_days}_{from_timestamp}_{to_timestamp}'
        )
        data = cache.get(cache_key)
        if not data:
            items = get_simple_moving_average_variations(
                pair=pair,
                precision=precision,
                from_timestamp=from_timestamp,
                to_timestamp=to_timestamp
            )

            data = [
                {
                    'mms': getattr(item, f'mms_{filters["range"].value}'),
                    'timestamp': item.timestamp
                }
                for item in items
            ]

            cache.set(
                key=cache_key,
                value=data,
                timeout=settings.CACHE_LIFETIME['mms_retrieve']
            )

        return HTTPStatus.OK, IndicatorMmsResponseSchema.from_list(data)
    except Exception:
        raise InternalServerError(
            'An internal error occurred while making the request.'
        )
