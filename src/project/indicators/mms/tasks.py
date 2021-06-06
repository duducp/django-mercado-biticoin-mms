import asyncio
import datetime

from django.utils import timezone

import structlog

from project.core.celery import app
from project.core.locks import CacheLock, LockActiveError
from project.indicators.mms.helpers import (
    calculate_simple_moving_average_by_candles
)

logger = structlog.get_logger()


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
    """
    Calculate simple moving average per pair.

    The cache lock is only valid at runtime to prevent the same pair from
    being processed at the same time.
    """
    datetime_started = datetime.datetime.fromisoformat(datetime_started)

    try:
        last_day = datetime_started - datetime.timedelta(days=1)
        last_two_hundred_days = datetime_started - datetime.timedelta(days=200)
        from_timestamp = last_two_hundred_days.replace(
            hour=0,
            minute=0,
            second=0,
        ).timestamp()
        to_timestamp = last_day.replace(
            hour=23,
            minute=59,
            second=59,
        ).timestamp()

        cache_lock_key = (
            'task_calculate_simple_moving_average:'
            f'{pair}-'
            f'{precision}-'
            f'{datetime_started.date().isoformat()}'
        )

        with CacheLock(
            key=cache_lock_key,
            cache_alias='lock',
            expire=300,
            delete_on_exit=True,
        ):
            logger.info(
                'Starting simple moving average indicator calculation',
                pair=pair,
                precision=precision,
                datetime_started=datetime_started.isoformat(),
                task='task_calculate_simple_moving_average',
            )

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

            logger.info(
                'Successfully calculated simple moving average',
                pair=pair,
                precision=precision,
                datetime_started=datetime_started.isoformat(),
                task='task_calculate_simple_moving_average',
            )
    except LockActiveError:
        logger.info(
            'Processing not completed as there is already '
            'another one being processed',
            pair=pair,
            precision=precision,
            datetime_started=datetime_started.isoformat(),
            task='task_calculate_simple_moving_average',
        )
    except Exception as exc:
        now = timezone.now()
        eta = now + datetime.timedelta(minutes=30)

        if eta.date() != datetime_started.date():
            logger.critical(
                'Could not calculate simple moving average',
                pair=pair,
                precision=precision,
                datetime_started=datetime_started.isoformat(),
                task='task_calculate_simple_moving_average',
                eta=eta.isoformat(),
                exc_info=True,
            )
            return

        logger.error(
            'Error calculating simple moving average',
            pair=pair,
            precision=precision,
            datetime_started=datetime_started.isoformat(),
            task='task_calculate_simple_moving_average',
            eta=eta.isoformat(),
            exc_info=True,
        )
        raise self.retry(
            args=[pair, precision, datetime_started.isoformat()],
            eta=eta,
            exc=exc
        )
