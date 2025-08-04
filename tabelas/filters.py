import django_filters
from .models import (Banco, Cidade, Feriado, Bairro, EstadoCivil, GrauRelacao, RegimeBens, LinhaCredito, Localizacao,
                     FinalidadeCredito, SetorNegocio, RamoAtividade, Profissao, SituacaoPessoa, TipoFonteRefer, Veiculo,
                     Log)

from django.db.models import Q


class BancoFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method='my_custom_filter', label="Search")

    class Meta:
        model = Banco
        fields = ['q']

    @staticmethod
    def my_custom_filter(queryset, name, value):
        return queryset.filter(
            Q(codigo__icontains=value) | Q(nome__icontains=value)
        )


class CidadeFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method='my_custom_filter', label="Search")

    class Meta:
        model = Cidade
        fields = ['q']

    @staticmethod
    def my_custom_filter(queryset, name, value):
        return queryset.filter(
            Q(codibge__icontains=value) | Q(nome__icontains=value) | Q(uf__icontains=value)
        )


class FeriadoFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method='my_custom_filter', label="Search")

    class Meta:
        model = Feriado
        fields = ['q']

    @staticmethod
    def my_custom_filter(queryset, name, value):
        return queryset.filter(
            Q(dtferiado__icontains=value) | Q(descricao__icontains=value)
        )


class BairroFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method='my_custom_filter', label="Search")

    class Meta:
        model = Bairro
        fields = ['q']

    @staticmethod
    def my_custom_filter(queryset, name, value):
        return queryset.filter(
            Q(nome__icontains=value) | Q(cidade__nome__icontains=value)
        )


class EstadoCivilFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method='my_custom_filter', label="Search")

    class Meta:
        model = EstadoCivil
        fields = ['q']

    @staticmethod
    def my_custom_filter(queryset, name, value):
        return queryset.filter(
            Q(nome__icontains=value)
        )

class GrauRelacaoFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method='my_custom_filter', label="Search")

    class Meta:
        model = GrauRelacao
        fields = ['q']

    @staticmethod
    def my_custom_filter(queryset, name, value):
        return queryset.filter(
            Q(nome__icontains=value)
        )

class RegimeBensFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method='my_custom_filter', label="Search")

    class Meta:
        model = RegimeBens
        fields = ['q']

    @staticmethod
    def my_custom_filter(queryset, name, value):
        return queryset.filter(
            Q(nome__icontains=value)
        )


class LinhaCreditoFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method='my_custom_filter', label="Search")

    class Meta:
        model = LinhaCredito
        fields = ['q']

    @staticmethod
    def my_custom_filter(queryset, name, value):
        return queryset.filter(
            Q(nome__icontains=value)
        )


class FinalidadeCreditoFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method='my_custom_filter', label="Search")

    class Meta:
        model = FinalidadeCredito
        fields = ['q']

    @staticmethod
    def my_custom_filter(queryset, name, value):
        return queryset.filter(
            Q(nome__icontains=value)
        )


class SetorNegocioFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method='my_custom_filter', label="Search")

    class Meta:
        model = SetorNegocio
        fields = ['q']

    @staticmethod
    def my_custom_filter(queryset, name, value):
        return queryset.filter(
            Q(nome__icontains=value)
        )


class RamoAtividadeFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method='my_custom_filter', label="Search")

    class Meta:
        model = RamoAtividade
        fields = ['q']

    @staticmethod
    def my_custom_filter(queryset, name, value):
        return queryset.filter(
            Q(nome__icontains=value)
        )


class ProfissaoFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method='my_custom_filter', label="Search")

    class Meta:
        model = RamoAtividade
        fields = ['q']

    @staticmethod
    def my_custom_filter(queryset, name, value):
        return queryset.filter(
            Q(nome__icontains=value) | Q(cbo__icontains=value)
        )


class VeiculoFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method='my_custom_filter', label="Search")

    class Meta:
        model = Veiculo
        fields = ['q']

    @staticmethod
    def my_custom_filter(queryset, name, value):
        return queryset.filter(
            Q(placa__icontains=value) | Q(marca__icontains=value) | Q(modelo__icontains=value)
        )


class LocalizacaoFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method='my_custom_filter', label="Search")

    class Meta:
        model = Localizacao
        fields = ['q']

    @staticmethod
    def my_custom_filter(queryset, name, value):
        return queryset.filter(
            Q(nome__icontains=value)
        )


class SituacaoPessoaFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method='my_custom_filter', label="Search")

    class Meta:
        model = SituacaoPessoa
        fields = ['q']

    @staticmethod
    def my_custom_filter(queryset, name, value):
        return queryset.filter(
            Q(descricao__icontains=value)
        )


class TipoFonteReferFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method='my_custom_filter', label="Search")

    class Meta:
        model = TipoFonteRefer
        fields = ['q']

    @staticmethod
    def my_custom_filter(queryset, name, value):
        return queryset.filter(
            Q(nome__icontains=value)
        )


class LogFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method='my_custom_filter', label="Search")

    class Meta:
        model = Log
        fields = ['q']

    @staticmethod
    def my_custom_filter(queryset, name, value):
        return queryset.filter(
            Q(username__icontains=value) | Q(tabela__icontains=value) |
            Q(nome__icontains=value) | Q(history_date__icontains=value)
        )
