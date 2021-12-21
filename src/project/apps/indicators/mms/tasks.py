import asyncio
import datetime
import random

from django.utils import timezone

import structlog

from project.apps.indicators.enum import PairEnum
from project.apps.indicators.mms.helpers import (
    calculate_simple_moving_average_by_candles
)
from project.core.celery import app
from project.core.locks import CacheLock, LockActiveError

logger = structlog.get_logger()


@app.task(
    bind=True,
    queue='indicator-mms-select-pairs',
    max_retries=3,
    retry_backoff=10,
    retry_backoff_max=600,
)
def task_beat_select_pairs_to_mms(self):
    """
    Generate calls to calculate simple moving average per pair.

    The cache lock is active for 24 hours, preventing the task from being
    called more than once.
    """
    datetime_started = timezone.now()
    precision = '1d'

    try:
        pairs = PairEnum.get_values()

        for pair in pairs:
            _process_task_beat_select_pairs_to_mms(
                pair=pair,
                precision=precision,
                datetime_started=datetime_started
            )

        logger.info(
            'Request to calculate the simple moving average of pairs '
            'successfully performed',
            task='task_beat_select_pairs_to_mms',
            datetime_started=datetime_started.isoformat(),
            precision=precision,
        )
    except LockActiveError:
        pass
    except Exception as exc:
        try:
            logger.error(
                'Error selecting pairs for calculate MMS',
                task='task_beat_select_pairs_to_mms',
                datetime_started=datetime_started.isoformat(),
                precision=precision,
                exc_info=True
            )
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            logger.critical(
                'Max retries exceeded when selecting pairs for calculate MMS',
                task='task_beat_select_pairs_to_mms',
                datetime_started=datetime_started.isoformat(),
                precision=precision,
                exc_info=True,
            )


def _process_task_beat_select_pairs_to_mms(
    pair: str,
    precision: str,
    datetime_started: datetime.datetime
):
    cache_lock_key = (
        'task_beat_select_pairs_to_mms:'
        f'{pair}-'
        f'{precision}-'
        f'{datetime_started.date().isoformat()}'
    )
    cache_lock_expire = datetime_started + datetime.timedelta(hours=24)
    cache_lock_expire_seconds = (
        cache_lock_expire - datetime_started
    ).total_seconds()

    with CacheLock(
        key=cache_lock_key,
        cache_alias='lock',
        expire=cache_lock_expire_seconds,
        delete_on_exit=False
    ) as cache_lock:
        try:
            expires_datetime = datetime_started.replace(
                hour=23,
                minute=59,
                second=59,
            )

            task_calculate_simple_moving_average.apply_async(
                args=[pair, precision, datetime_started.isoformat()],
                countdown=random.randint(30, 120),
                expires=(expires_datetime - datetime_started).total_seconds()
            )
        except Exception:
            cache_lock.delete_cache()
            raise


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
