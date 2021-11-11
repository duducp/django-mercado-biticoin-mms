from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, List


@dataclass
class CandleSchema:
    timestamp: int
    open: Decimal
    close: Decimal
    high: Decimal
    low: Decimal
    volume: Decimal

    @classmethod
    def from_dict(cls, data: Dict) -> 'CandleSchema':
        return CandleSchema(
            timestamp=int(data.get('timestamp')),
            open=cls._convert_str_to_decimal(data['open']),
            close=cls._convert_str_to_decimal(data['close']),
            high=cls._convert_str_to_decimal(data['high']),
            low=cls._convert_str_to_decimal(data['low']),
            volume=cls._convert_str_to_decimal(data['volume']),
        )

    @classmethod
    def from_list(cls, items: List[Dict]) -> List['CandleSchema']:
        return [
            CandleSchema.from_dict(item)
            for item in items
        ]

    @staticmethod
    def _convert_str_to_decimal(value: str) -> Decimal:
        return Decimal(value).quantize(Decimal('.0000000001'))
