from django.contrib import admin, messages
from django.urls import reverse
from django.utils.safestring import mark_safe

import structlog

from project.tickets.models import Tickets

logger = structlog.get_logger()


@admin.register(Tickets)
class TicketAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'cpf',
        'validated',
        'button_validate',
        'note',
    ]

    search_fields = [
        'name',
        'cpf',
    ]

    list_per_page = 30
    list_max_show_all = 30

    actions = [
        'validate_ticket',
    ]

    # def get_queryset(self, request):
    #     if request.GET or request.POST:
    #         filter_q = request.GET.get('q')
    #         if filter_q != '':
    #             return super(TicketAdmin, self).get_queryset(request)
    #
    #     return self.model.objects.none()

    def get_actions(self, request):
        actions = super(TicketAdmin, self).get_actions(request)

        if not request.user.has_perm('tickets.validate_ticket'):
            del actions['validate_ticket']

        validate = request.GET.get('validate')
        id_ticket = request.GET.get('id')
        cpf = request.GET.get('cpf')
        if validate == 'true' and id_ticket and cpf:
            if not request.user.has_perm('tickets.validate_ticket'):
                self.message_user(
                    request,
                    'Você não tem permissão para realizar esta ação.',
                    level=messages.WARNING,
                )
            else:
                ticket = Tickets.objects.filter(
                    id=id_ticket,
                    cpf=cpf,
                ).first()
                if ticket:
                    if ticket.is_validated():
                        self.message_user(
                            request,
                            'O ingresso já foi validado anteriormente.',
                            level=messages.WARNING,
                        )
                    else:
                        ticket.validate(username=request.user.username)
                        self.message_user(
                            request,
                            'Ingresso validado com sucesso.'
                        )
                else:
                    self.message_user(
                        request,
                        'Falha ao validar o ingresso.',
                        level=messages.ERROR,
                    )

        return actions

    @admin.display(description='AÇÕES')
    def button_validate(self, obj):
        if obj.validated:
            return ''

        url = f"{reverse('admin:tickets_tickets_changelist')}?cpf={obj.cpf}&id={obj.id}&validate=true"  # noqa
        return mark_safe(
            f"<a href='{url}'>Validar</a>"
        )

    @admin.action(description='Validar ingresso selecionado')
    def validate_ticket(self, request, queryset):
        if not request.user.has_perm('tickets.validate_ticket'):
            self.message_user(
                request,
                'Você não tem permissão para realizar esta ação.',
                level=messages.WARNING,
            )
            return

        if len(queryset) > 1:
            self.message_user(
                request,
                'Selecione um ingresso para executar essa ação.',
                level=messages.WARNING,
            )
            return

        ticket = queryset[0]
        username = request.user.username

        try:
            if ticket.is_validated():
                self.message_user(
                    request,
                    'O ingresso já foi validado anteriormente.',
                    level=messages.WARNING,
                )
                return

            ticket.validate(username)

            self.message_user(
                request,
                'Ingresso validado com sucesso.'
            )
        except Exception:
            logger.error(
                '[TICKET][ADMIN] Failed to validate ticket.',
                id=ticket.id,
                cpf=ticket.cpf,
                exc_info=True
            )
            self.message_user(
                request,
                'Falha ao validar o ingresso.',
                level=messages.ERROR,
            )
