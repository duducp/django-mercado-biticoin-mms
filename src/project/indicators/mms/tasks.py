import asyncio
import datetime

from django.utils import timezone

import structlog

from project.core.celery import app
from project.indicators.mms.helpers import (
    calculate_simple_moving_average_by_candles
)

logger = structlog.get_logger(__name__)


@app.task(
    bind=True,
    queue='indicator-mms-calculate',
    max_retries=None,
)
def task_calculate_simple_moving_average(
    self,
    pair,
    precision,
    datetime_started
):
    try:
        datetime_started = datetime.datetime.fromisoformat(datetime_started)
        last_day = datetime_started - datetime.timedelta(days=1)
        last_two_hundred_days = datetime_started - datetime.timedelta(days=200)

        from_timestamp = datetime.datetime(
            year=last_two_hundred_days.year,
            month=last_two_hundred_days.month,
            day=last_two_hundred_days.day,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
            tzinfo=last_two_hundred_days.tzinfo
        ).timestamp()
        to_timestamp = datetime.datetime(
            year=last_day.year,
            month=last_day.month,
            day=last_day.day,
            hour=23,
            minute=59,
            second=59,
            microsecond=59,
            tzinfo=last_day.tzinfo
        ).timestamp()

        logger.bind(
            pair=pair,
            precision=precision,
            from_timestamp=from_timestamp,
            to_timestamp=to_timestamp,
            datetime_started=datetime_started.isoformat(),
            task='task_calculate_simple_moving_average',
        )
        logger.info('Starting simple moving average indicator calculation')

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            calculate_simple_moving_average_by_candles(
                pair=pair,
                precision=precision,
                timestamp=int(to_timestamp),
                from_timestamp=int(from_timestamp),
                to_timestamp=int(to_timestamp),
            )
        )

        logger.info('Successfully calculated simple moving average')
    except Exception as exc:
        now = timezone.now()
        eta = now + datetime.timedelta(minutes=30)

        if eta.date() != now.date():
            logger.critical(
                'Could not calculate simple moving average',
                exc_info=True,
            )
            return

        logger.error('Error calculating simple moving average', exc_info=True)
        self.retry(args=(pair, precision, datetime_started), eta=eta, exc=exc)
