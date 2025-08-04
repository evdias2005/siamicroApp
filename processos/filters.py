import django_filters
from .models import PessoaFisica, PessoaJuridica, Processo, Parecer, Negociacao, Financeiro

from django.db.models import Q


class PessoaFisicaFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method='my_custom_filter', label="Search")

    class Meta:
        model = PessoaFisica
        fields = ['q']

    @staticmethod
    def my_custom_filter(queryset, name, value):
        return queryset.filter(
            Q(nome__icontains=value) | Q(numcpf__icontains=value) | Q(criado_por__first_name__icontains=value) |
            Q(situacao__descricao__icontains=value)
        )


class PessoaJuridicaFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method='my_custom_filter', label="Search")

    class Meta:
        model = PessoaJuridica
        fields = ['q']

    @staticmethod
    def my_custom_filter(queryset, name, value):
        return queryset.filter(
            Q(razaosocial__icontains=value) | Q(nomefantasia__icontains=value) |
            Q(numcnpj__icontains=value) | Q(criado_por__first_name__icontains=value)
        )

# class ProcessoFilter(django_filters.FilterSet):
#     numprocesso = django_filters.CharFilter(lookup_expr='icontains')
#     # cliente__nome = django_filters.CharFilter(lookup_expr='icontains')
#
#     class Meta:
#         model = Processo
#         fields = ['numprocesso']
#         # fields = ['numprocesso', 'cliente__nome']

class ProcessoFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method='my_custom_filter', label="Search")

    class Meta:
        model = Processo
        fields = ['q']

    @staticmethod
    def my_custom_filter(queryset, name, value):
        return queryset.filter(
            Q(numprocesso__icontains=value) | Q(clientepf__nome__icontains=value) |
            Q(clientepj__razaosocial__icontains=value) | Q(criado_por__first_name__icontains=value) |
            Q(linhacredito__nome__icontains=value)
        )

class ParecerFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method='my_custom_filter', label="Search")

    class Meta:
        model = Parecer
        fields = ['q']

    @staticmethod
    def my_custom_filter(queryset, name, value):
        # return queryset.filter(
        #     Q(numprocesso__icontains=value) | Q(criado_por__first_name__icontains=value)
        # )
        return queryset.filter(
            Q(processo__numprocesso__icontains=value)
        )

class NegociacaoFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method='my_custom_filter', label="Search")

    class Meta:
        model = Negociacao
        fields = ['q']

    @staticmethod
    def my_custom_filter(queryset, name, value):
        # return queryset.filter(
        #     Q(numprocesso__icontains=value) | Q(criado_por__first_name__icontains=value)
        # )
        return queryset.filter(
            Q(processo__numprocesso__icontains=value)
        )

class FinanceiroFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method='my_custom_filter', label="Search")

    class Meta:
        model = Financeiro
        fields = ['q']

    @staticmethod
    def my_custom_filter(queryset, name, value):
        # return queryset.filter(
        #     Q(numprocesso__icontains=value) | Q(criado_por__first_name__icontains=value)
        # )
        return queryset.filter(
            Q(financeiro__processo__numprocesso__icontains=value)
        )




