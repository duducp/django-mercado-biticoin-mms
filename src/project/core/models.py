import uuid

from django.core.validators import RegexValidator
from django.db import models


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created at',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated at',
    )

    class Meta:
        abstract = True


class UpperCaseCharField(models.CharField):
    def __init__(self, *args, **kwargs):
        super(UpperCaseCharField, self).__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname, None)
        if value:
            value = value.upper()
            setattr(model_instance, self.attname, value)
            return value
        else:
            return super(UpperCaseCharField, self).pre_save(
                model_instance,
                add
            )


class Validators:
    @property
    def only_numbers(self):
        return RegexValidator(
            regex=r'^[0-9]*$',
            message='This field must contain only numbers.'
        )

    @property
    def only_letters_and_space(self):
        return RegexValidator(
            regex=r'^[a-z A-Z]*$',
            message='This field must contain only letters and spaces.'
        )
