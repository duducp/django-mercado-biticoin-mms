import datetime
from decimal import Decimal
from unittest import mock
from unittest.mock import call

import asynctest
import pytest
from celery.exceptions import Retry
from freezegun import freeze_time

from project.core.locks import LockActiveError
from project.indicators.mms.tasks import task_calculate_simple_moving_average
from project.services.candles.schemas import CandleSchema


class TestTaskCalculateSimpleMovingAverage:

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
            for _ in range(200)
        ]

    @pytest.fixture()
    def mock_get_candles(self, mock_return_get_candles):
        with asynctest.patch(
            'project.indicators.mms.tasks.'
            'calculate_simple_moving_average_by_candles'
        ) as mock_get_candles:
            mock_get_candles.return_value = mock_return_get_candles
            yield mock_get_candles

    @pytest.fixture()
    def mock_logger(self, mock_return_get_candles):
        with mock.patch('project.indicators.mms.tasks.logger') as mock_logger:
            yield mock_logger

    @pytest.fixture
    def mock_cache_lock(self):
        with mock.patch('project.indicators.mms.tasks.CacheLock') as lock:
            yield lock

    def test_should_validate_if_a_task_was_successfully_executed(
        self,
        mock_logger,
        mock_get_candles,
        mock_cache_lock,
    ):
        pair = 'BRLBTC'
        precision = '1d'
        datetime_started = datetime.datetime(2021, 6, 6, 23, 59).isoformat()

        task_calculate_simple_moving_average(
            pair, precision, datetime_started
        )

        mock_get_candles.assert_awaited_once_with(
            pair='BRLBTC',
            precision='1d',
            timestamp=1622937599,
            from_timestamp=1605657600,
            to_timestamp=1622937599,
        )
        mock_cache_lock.assert_called_once_with(
            key='task_calculate_simple_moving_average:BRLBTC-1d-2021-06-06',
            cache_alias='lock',
            expire=300,
            delete_on_exit=True
        )
        mock_logger.assert_has_calls([
            call.info(
                'Starting simple moving average indicator calculation',
                pair='BRLBTC',
                precision='1d',
                datetime_started='2021-06-06T23:59:00',
                task='task_calculate_simple_moving_average'
            ),
            call.info(
                'Successfully calculated simple moving average',
                pair='BRLBTC',
                precision='1d',
                datetime_started='2021-06-06T23:59:00',
                task='task_calculate_simple_moving_average'
            ),
        ])

    def test_should_validate_cache_locked_exception(
        self,
        mock_logger,
        mock_get_candles,
        mock_cache_lock,
    ):
        pair = 'BRLBTC'
        precision = '1d'
        datetime_started = datetime.datetime(2021, 6, 6, 23, 59).isoformat()
        mock_cache_lock.side_effect = LockActiveError

        task_calculate_simple_moving_average(
            pair, precision, datetime_started
        )

        mock_logger.assert_has_calls([
            call.info(
                'Processing not completed as there is already another one '
                'being processed',
                pair='BRLBTC',
                precision='1d',
                datetime_started='2021-06-06T23:59:00',
                task='task_calculate_simple_moving_average'
            )
        ])

    @mock.patch(
        'project.indicators.mms.tasks.'
        'task_calculate_simple_moving_average.retry'
    )
    @freeze_time('2021-6-6 23:00')
    def test_should_validate_the_retry_when_an_exception_occurs(
        self,
        task_retry,
        mock_logger,
        mock_get_candles,
        mock_cache_lock,
    ):
        task_retry.side_effect = Retry()
        mock_cache_lock.side_effect = Exception

        pair = 'BRLBTC'
        precision = '1d'
        datetime_started = datetime.datetime(2021, 6, 6, 23, 59).isoformat()

        with pytest.raises(Retry):
            task_calculate_simple_moving_average(
                pair, precision, datetime_started
            )

        mock_logger.assert_has_calls([
            call.error(
                'Error calculating simple moving average',
                pair='BRLBTC',
                precision='1d',
                datetime_started='2021-06-06T23:59:00',
                task='task_calculate_simple_moving_average',
                eta='2021-06-06T23:30:00+00:00',
                exc_info=True
            )
        ])

    @freeze_time('2021-6-6 23:55')
    def test_should_validate_that_it_will_no_longer_retry_when_the_date_is_the_next_day(  # noqa
        self,
        mock_logger,
        mock_get_candles,
        mock_cache_lock,
    ):
        mock_cache_lock.side_effect = Exception

        pair = 'BRLBTC'
        precision = '1d'
        datetime_started = datetime.datetime(2021, 6, 6, 23, 59).isoformat()

        task_calculate_simple_moving_average(
            pair, precision, datetime_started
        )

        mock_logger.assert_has_calls([
            call.critical(
                'Could not calculate simple moving average',
                pair='BRLBTC',
                precision='1d',
                datetime_started='2021-06-06T23:59:00',
                task='task_calculate_simple_moving_average',
                eta='2021-06-07T00:25:00+00:00',
                exc_info=True
            )
        ])
