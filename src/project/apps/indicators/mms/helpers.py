from decimal import Decimal
from typing import List, Union

from django.db.models import QuerySet

from asgiref.sync import sync_to_async

from project.apps.indicators.mms.exceptions import (
    CalculateMmsCountCandlesException
)
from project.apps.indicators.mms.models import SimpleMovingAverage
from project.services.candles.clients import get_candles


async def calculate_simple_moving_average_by_candles(
    pair: str,
    precision: str,
    timestamp: int,
    to_timestamp: int,
    from_timestamp: int,
):
    """
    Make the request in the candles api and calculate the simple moving average
    """
    candles = await get_candles(
        pair=pair,
        precision=precision,
        to_timestamp=to_timestamp,
        from_timestamp=from_timestamp
    )
    if len(candles) < 200:
        raise CalculateMmsCountCandlesException(
            'The amount of Candles returned by api is less than two hundred'
        )

    values_close = list(map(lambda candle: candle.close, candles))

    mms_20 = _calculate_simple_moving_average(values_close[:20])
    mms_50 = _calculate_simple_moving_average(values_close[:50])
    mms_200 = _calculate_simple_moving_average(values_close[:200])

    await save_simple_moving_average_database(
        pair=pair,
        precision=precision,
        timestamp=timestamp,
        mms_20=mms_20.quantize(Decimal('.0000000001')),
        mms_50=mms_50.quantize(Decimal('.0000000001')),
        mms_200=mms_200.quantize(Decimal('.0000000001')),
    )


def _calculate_simple_moving_average(values: List[Decimal]) -> Decimal:
    return sum(values) / len(values)


@sync_to_async
def save_simple_moving_average_database(
    pair: str,
    precision: str,
    mms_20: Decimal,
    mms_50: Decimal,
    mms_200: Decimal,
    timestamp: int,
):
    """
    Save simple moving average calculation to database
    """
    SimpleMovingAverage.objects.create(
        pair=pair,
        precision=precision,
        mms_20=mms_20,
        mms_50=mms_50,
        mms_200=mms_200,
        timestamp=timestamp
    )


def get_simple_moving_average_variations(
    pair: str,
    precision: str,
    from_timestamp: int,
    to_timestamp: int,
) -> Union[QuerySet, List[SimpleMovingAverage]]:
    """
    Filters out simple moving average variations in the database
    """
    return SimpleMovingAverage.objects.filter(
        pair=pair,
        precision=precision,
        timestamp__range=(from_timestamp, to_timestamp),
    )
