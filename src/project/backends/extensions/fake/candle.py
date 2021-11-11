from decimal import Decimal
from typing import List

from project.backends.candle.backend import CandleBackend
from project.backends.candle.schemas import CandleSchema


class FakeCandleBackend(CandleBackend):
    id = 'fake'

    async def _get_candles(
        self,
        pair: str,
        from_timestamp: int,
        to_timestamp: int,
        precision: str
    ) -> List[CandleSchema]:
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
