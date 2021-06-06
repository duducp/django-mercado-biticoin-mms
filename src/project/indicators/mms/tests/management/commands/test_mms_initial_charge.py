from decimal import Decimal
from unittest import mock
from unittest.mock import call

from django.core.management import call_command

import pytest
from freezegun import freeze_time
from model_bakery import baker

from project.indicators.mms.models import SimpleMovingAverage


@pytest.mark.django_db
class TestCommandMmsInitialCharge:

    @pytest.fixture()
    def mock_logger(self):
        with mock.patch(
            'project.indicators.mms.management.commands.'
            'mms_initial_charge.logger'
        ) as mock_logger:
            yield mock_logger

    @pytest.fixture
    def mock_task_calculate_simple_moving_average(self):
        with mock.patch(
            'project.indicators.mms.management.commands.'
            'mms_initial_charge.task_calculate_simple_moving_average'
        ) as task_mock:
            yield task_mock

    @pytest.fixture
    def clean_database(self):
        SimpleMovingAverage.objects.all().delete()

    @freeze_time('2021-6-6 23:00')
    def test_should_validate_that_the_command_was_executed_successfully_when_called(  # noqa
        self,
        mock_logger,
        mock_task_calculate_simple_moving_average,
        clean_database
    ):
        args = []
        opts = {'days': 1}
        call_command('mms_initial_charge', *args, **opts)

        mock_logger.info.assert_has_calls([
            call(
                'Starting initial charge for simple moving average indicator',
                days=1
            ),
            call(
                'Simple moving average initial load processing request completed',  # noqa
                days=1
            ),
        ])
        mock_task_calculate_simple_moving_average.apply_async.assert_has_calls([  # noqa
            call(
                args=('BRLBTC', '1d', '2021-06-05T23:00:00+00:00',),
                expires=86400
            ),
            call(
                args=('BRLETH', '1d', '2021-06-05T23:00:00+00:00',),
                expires=86400
            ),
        ])

    @freeze_time('2021-6-6 23:00')
    def test_should_validate_the_log_message_when_an_exception_occurs(
        self,
        mock_logger,
        mock_task_calculate_simple_moving_average,
        clean_database
    ):
        mock_task_calculate_simple_moving_average.apply_async.side_effect = Exception  # noqa

        args = []
        opts = {'days': 1}
        call_command('mms_initial_charge', *args, **opts)

        mock_logger.assert_has_calls([
            call.info(
                'Starting initial charge for simple moving average indicator',
                days=1
            ),
            call.error(
                'An error occurred in the initial load request',
                days=1,
                exc_info=True
            ),
        ])

    @freeze_time('2021-6-6 23:00')
    def test_should_validate_that_the_script_will_not_run_if_there_is_already_a_record_in_the_table(  # noqa
        self,
        mock_logger,
        mock_task_calculate_simple_moving_average,
        clean_database,
    ):
        baker.make(
            'SimpleMovingAverage',
            precision='1d',
            pair='BRLBTC',
            mms_20=Decimal('201108.2404745000'),
            mms_50=Decimal('258627.0329508000'),
            mms_200=Decimal('229149.8719421000'),
            timestamp=1623034799
        )

        args = []
        opts = {'days': 1}
        call_command('mms_initial_charge', *args, **opts)

        mock_logger.assert_has_calls([
            call.error(
                'Cannot proceed as there are already records in the table'
            ),
        ])
        mock_task_calculate_simple_moving_average.apply_async.assert_not_called()  # noqa
