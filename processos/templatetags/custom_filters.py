from django import template

register = template.Library()

# FIltro utilizado no Relatório de Inadimplentes da Dívida Ativa
@register.filter
def to_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0