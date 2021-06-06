import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

import structlog

from project.indicators.enum import PairEnum
from project.indicators.mms.models import SimpleMovingAverage
from project.indicators.mms.tasks import task_calculate_simple_moving_average

logger = structlog.get_logger()


class Command(BaseCommand):
    help = 'Will do initial load on Simple Moving Average indicator table'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            help='number of days before today that must be processed',
            type=int,
            default=365,
            required=False
        )

    def handle(self, *args, **options):
        days = int(options['days'])
        value = SimpleMovingAverage.objects.first()
        if value:
            logger.error(
                'Cannot proceed as there are already records in the table'
            )
            return

        try:
            precision = '1d'
            pairs = PairEnum.get_values()
            now = timezone.now()
            expires = now + datetime.timedelta(hours=24)
            expires = (expires - now).total_seconds()

            logger.info(
                'Starting initial charge for simple moving average indicator',
                days=days
            )

            for day in range(days):
                datetime_started = now - datetime.timedelta(days=days - day)

                for pair in pairs:
                    print(
                        f'Pair: {pair} - '
                        f'Precision: {precision} - '
                        f'Day: {day + 1} - '
                        f'Started: {datetime_started.isoformat()} - '
                        f'Expires: {expires}'
                    )
                    args = (pair, precision, datetime_started.isoformat())
                    task_calculate_simple_moving_average.apply_async(
                        args=args,
                        expires=expires
                    )

            logger.info(
                'Simple moving average initial load processing request '
                'completed',
                days=days
            )
        except Exception:
            logger.error(
                'An error occurred in the initial load request',
                days=days,
                exc_info=True,
            )
