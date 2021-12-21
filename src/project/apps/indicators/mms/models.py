from django.db import models

from project.core.models import BaseModel, UpperCaseCharField


class SimpleMovingAverage(BaseModel):
    timestamp = models.IntegerField(
        verbose_name='Timestamp',
    )
    pair = UpperCaseCharField(
        verbose_name='Pair',
        max_length=10
    )
    precision = models.CharField(
        verbose_name='Precision',
        max_length=10
    )
    mms_20 = models.DecimalField(
        verbose_name='Simple Moving Average of 20',
        max_digits=20,
        decimal_places=10,
    )
    mms_50 = models.DecimalField(
        verbose_name='Simple Moving Average of 50',
        max_digits=20,
        decimal_places=10,
    )
    mms_200 = models.DecimalField(
        verbose_name='Simple Moving Average of 200',
        max_digits=20,
        decimal_places=10,
    )

    class Meta:
        app_label = 'mms'
        verbose_name = 'Simple Moving Average'
        verbose_name_plural = 'Simple Moving Average'

        db_table = 'ind_simplemovingaverage'
        unique_together = ('timestamp', 'pair', 'precision')
