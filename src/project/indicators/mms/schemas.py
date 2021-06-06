from datetime import datetime, timedelta
from typing import Dict, List

from django.utils import timezone

from ninja import Schema
from pydantic import Field, validator

from project.indicators.mms.enum import RangeDaysEnum


class QueryFilter(Schema):
    from_timestamp: int = Field(alias='from')
    to_timestamp: int = Field(
        alias='to',
        default=int(
            (timezone.now() - timedelta(days=1)).replace(
                hour=23,
                minute=59,
                second=59
            ).timestamp()
        )
    )
    range: RangeDaysEnum
    precision: str = '1d'

    @validator('from_timestamp')
    def validate_from_datetime(cls, value):
        """
        Ensures the start date is not earlier than 365 days
        """

        now = timezone.now().date()
        date = datetime.utcfromtimestamp(value).date()

        diff_days = (now - date).days
        if diff_days > 365:
            raise ValueError('Start date cannot be longer than 365 days')

        return value


class IndicatorMmsResponseSchema(Schema):
    timestamp: int
    mms: float

    @staticmethod
    def from_dict(item: Dict) -> 'IndicatorMmsResponseSchema':
        return IndicatorMmsResponseSchema(
            timestamp=item['timestamp'],
            mms=item['mms']
        )

    @staticmethod
    def from_list(items: List[Dict]) -> List['IndicatorMmsResponseSchema']:
        return [
            IndicatorMmsResponseSchema.from_dict(item)
            for item in items
        ]
