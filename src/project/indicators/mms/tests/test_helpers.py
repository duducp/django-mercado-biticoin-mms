from decimal import Decimal

import pytest
from asgiref.sync import sync_to_async
from asynctest import patch

from project.indicators.mms.exceptions import CalculateMmsCountCandlesException
from project.indicators.mms.helpers import (
    calculate_simple_moving_average_by_candles
)
from project.indicators.mms.models import SimpleMovingAverage
from project.services.candles.schemas import CandleSchema


@pytest.mark.django_db
class TestCalculateSimpleMovingAverageByCandles:

    @pytest.fixture()
    def mock_return_get_candles(self):
        return [
            CandleSchema(
                timestamp=1622689200,
                open=Decimal('190806.7413400000'),
                close=Decimal('198499.9795800000'),
                high=Decimal('198542.0000000000'),
                low=Decimal('190000.0000000000'),
                volume=Decimal('72.5853810900')
            )
        ]

    @pytest.fixture()
    def mock_get_candles(self, mock_return_get_candles):
        with patch(
            'project.indicators.mms.helpers.get_candles'
        ) as mock_get_candles:
            mock_get_candles.return_value = mock_return_get_candles
            yield mock_get_candles

    @pytest.mark.asyncio
    async def test_should_return_exception_when_the_api_returns_less_than_200_items(  # noqa
        self,
        mock_get_candles
    ):
        with pytest.raises(CalculateMmsCountCandlesException):
            await calculate_simple_moving_average_by_candles(
                pair='BRLBTC',
                precision='1d',
                timestamp=1622743200,
                from_timestamp=1622775600,
                to_timestamp=1622948399,
            )

    @pytest.mark.asyncio
    async def test_shouyd_validate_if_the_item_was_entered_into_the_database(
        self,
        mock_get_candles
    ):
        candles = [
            CandleSchema(
                timestamp=1622746800,
                open=Decimal('190806.7413400000'),
                close=Decimal('198499.9795800000'),
                high=Decimal('198542.0000000000'),
                low=Decimal('190000.0000000000'),
                volume=Decimal('72.5853810900')
            )
            for _ in range(200)
        ]
        mock_get_candles.return_value = candles

        await calculate_simple_moving_average_by_candles(
            pair='BRLBTC',
            precision='1d',
            timestamp=1622743200,
            from_timestamp=1622775600,
            to_timestamp=1622948399,
        )

        mock_get_candles.assert_awaited_once_with(
            pair='BRLBTC',
            precision='1d',
            to_timestamp=1622948399,
            from_timestamp=1622775600
        )

        values = await sync_to_async(SimpleMovingAverage.objects.first)()
        assert values.mms_20 == Decimal('198499.9795800000')
        assert values.mms_50 == Decimal('198499.9795800000')
        assert values.mms_200 == Decimal('198499.9795800000')
        assert values.precision == '1d'
        assert values.pair == 'BRLBTC'
