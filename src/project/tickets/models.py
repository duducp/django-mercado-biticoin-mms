from django.core.validators import MinLengthValidator
from django.db import models, transaction

import structlog

from project.core.models import UpperCaseCharField, Validators

logger = structlog.get_logger()


class Tickets(models.Model):
    active = models.BooleanField(
        verbose_name='Ativado',
        default=True,
    )
    name = UpperCaseCharField(
        verbose_name='Nome',
        null=False,
        max_length=255,
        validators=[
            Validators().only_letters_and_space,
        ],
        help_text='Informe o nome completo do cliente.'
    )
    cpf = models.CharField(
        verbose_name='CPF',
        unique=True,
        null=False,
        max_length=11,
        validators=[
            Validators().only_numbers,
            MinLengthValidator(11)
        ],
        help_text='Informe o CPF do cliente. Somente números.'
    )
    promoter = models.CharField(
        verbose_name='Promotor',
        null=True,
        blank=True,
        max_length=50,
        validators=[
            Validators().only_letters_and_space,
        ],
        help_text='Opcional: Informe o nome da pessoa que vendeu o ingresso.'
    )
    note = models.TextField(
        verbose_name='Observação',
        null=True,
        blank=True,
        help_text='Opcional: Informe alguma observação sobre o ingresso.'
    )
    validated = models.BooleanField(
        verbose_name='Validado',
        default=False,
        help_text='Se preenchido o ingresso já foi validado.'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Adicionado em',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em',
    )

    def is_validated(self):
        return self.validated

    @transaction.atomic
    def validate(self, username):
        self.validated = True
        self.save()
        logger.info(
            f'Ticket {self.id} successfully activated by {username}.'
        )

    class Meta:
        app_label = 'tickets'
        verbose_name = 'Ingresso'
        verbose_name_plural = 'Ingressos'
        ordering = ['-created_at']
