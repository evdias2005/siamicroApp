# Realizar o processo de refatoração da classe abaixo levando em consideração as melhores práticas
# de programação, fluxo e lógica, bem como dando mais nitidez e documentação ao código, faciltando assim o seu entendimento
# e manutenção por outros desenvolvedores da equipe. Segue abaixo a(s) classe(s):
#
#

import os
import requests
from requests.structures import CaseInsensitiveDict

from django.conf import settings

from django.urls import reverse
from django.urls import reverse_lazy

import xlsxwriter
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core import serializers

from django.db import connection, transaction
import time

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (View, CreateView, UpdateView, ListView, TemplateView, FormView)

from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.detail import SingleObjectMixin

from django.contrib import messages
from processos.models import *
from tabelas.models import Config, LinhaCredito, Feriado, Operador, Operador_Local
from processos.forms import *

from django_filters.views import FilterView
from .filters import *

# *** Utilizando as funções presentes em utils.py ***
from .utils import render_to_pdf, showmessages_error, valor_por_extenso, load_bairros, consultar_cep, consultar_cnpj, \
    numero_para_ordinal, consultar_geolocalizacao

from datetime import date, datetime, timedelta
from django.utils.timezone import now

from django.db.models import Q, Sum, Count, OuterRef, Exists

from num2words import num2words

from decimal import Decimal

import hashlib


def tabela_existe(nome):
    return nome in connection.introspection.table_names()


# config = Config.objects.filter(is_deleted=False).last()
# if config:
#     mostra_excluidos = config.mostraregcancelados
#     mostra_cancelados = config.mostratitcancelados

mostra_excluidos = True
mostra_cancelados = True

def handler404(request, exception):
    return render(request, '404.html', status=404)


def handler500(request):
    return render(request, '500.html', status=500)


def atualizar_outros_dados_processo(request, pk):
    processo = get_object_or_404(Processo, pk=pk)
    if request.method == 'POST':
        form = OutrosDadosProcessoForm(request.POST, instance=processo)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors})
    return JsonResponse({'status': 'invalid request'})


def cancelar_processo(request, pk):
    processo = get_object_or_404(Processo, pk=pk)
    if request.method == 'POST':
        try:
            processo.status = 'C'
            processo.save()
            messages.success(request, f'Processo {processo.numprocesso} cancelado com sucesso.')
        except Exception as e:
            messages.error(request, f'Ocorreu um erro ao cancelar o processo {processo.numprocesso}: código do erro {str(e)}')
    return redirect('processos-list')


def apagar_processo(request, pk):
    processo = get_object_or_404(Processo, pk=pk)
    if request.method == 'POST':
        try:
            processo.is_deleted = True
            processo.save()
            messages.success(request, f'Processo {processo.numprocesso} excluído com sucesso.')
        except Exception as e:
            messages.error(request, f'Ocorreu um erro ao excluir o processo {processo.numprocesso}: código do erro {str(e)}')
    return redirect('processos-list')


def apagar_movimentacao(request, pk):
    if request.method == 'POST':
        with transaction.atomic():
            # Marca a movimentação como deletada
            processomovimentacao = get_object_or_404(Movimentacao, pk=pk)
            processomovimentacao.is_deleted = True
            processomovimentacao.data_edicao = now()
            processomovimentacao.save()

            # Busca a última movimentação não deletada
            ultimalocalizacao = Movimentacao.objects.filter(is_deleted=False, processo_id=processomovimentacao.processo_id
                                                            ).last().destino

            # Busca o processo associado ou retorna 404
            processo = get_object_or_404(Processo, pk=processomovimentacao.processo_id)

            # Atualiza a localização do processo
            processo.localizacao = ultimalocalizacao or processomovimentacao.destino
            processo.save()

            messages.success(request, f"Movimentação {processomovimentacao.origem} -> {processomovimentacao.destino}"
                                           f" do Processo {processo.numprocesso} excluída com sucesso.")
    return redirect('processomovimentacoes-list', processomovimentacao.processo_id)


def checar_movimentacao(request, pk):
    if request.method == 'POST':
        with transaction.atomic():
            # Marca a movimentação como recebida
            processomovimentacao = get_object_or_404(Movimentacao, pk=pk)
            processomovimentacao.is_recebido = True
            processomovimentacao.data_edicao = now()
            processomovimentacao.save()

            # Busca a última movimentação não deletada
            ultimalocalizacao = Movimentacao.objects.filter(is_deleted=False, processo_id=processomovimentacao.processo_id
                                                            ).last().destino

            # Busca o processo associado ou retorna 404
            processo = get_object_or_404(Processo, pk=processomovimentacao.processo_id)

            # Atualiza a localização do processo
            processo.localizacao = ultimalocalizacao or processomovimentacao.destino
            processo.save()

            messages.success(request, f"Movimentação {processomovimentacao.origem} -> {processomovimentacao.destino}"
                                           f" do Processo {processo.numprocesso} recebida com sucesso.")
    return redirect('processomovimentacoes-list', processomovimentacao.processo_id)


def get_logo_images():
    """
    Retorna as últimas informações de logo configuradas no sistema.
    """
    config = Config.objects.filter(is_deleted=False).last()
    if config:
        return {
            "linhalogo1": config.linhalogo1,
            "linhalogo2": config.linhalogo2,
            "linhalogo3": config.linhalogo3,
        }
    return {"linhalogo1": "", "linhalogo2": "", "linhalogo3": ""}

def handle_form_submission(request, form, template_name_pdf, context_data, include_valortotal=False,
                           include_totalsolicitado=False, include_totaldebitonegociado=False,
                           include_totalliberado=False):
    """
    Processa o envio do formulário, gera o PDF e, opcionalmente, calcula o total.

    Parâmetros:
    - request: Objeto HttpRequest.
    - form: Instância do formulário a ser processado.
    - template_name_pdf: Nome do template para geração do PDF.
    - context_data: Dicionário adicional de contexto.
    - include_total (bool): Se True, calcula e adiciona o 'valortotal' ao contexto.

    Retorna:
    - Resposta PDF renderizada ou None se o formulário for inválido.
    """
    if form.is_valid():
        qs = form.processar()

        # Adiciona o valor total ao contexto, se necessário
        additional_context = get_logo_images()
        additional_context.update(context_data)

        # Totalizador para o relatório de movimentação financeira
        if include_valortotal:
            valortotal = form.calcular_total() if hasattr(form, 'calcular_total') else 0.0
            additional_context.update({"valortotal": valortotal})

        # Totalizador para o relatório de processos
        if include_totalsolicitado:
            totalsolicitado = form.calcular_total() if hasattr(form, 'calcular_total') else 0.0
            additional_context.update({"totalsolicitado": totalsolicitado})

        # Totalizador para o relatório de renegociações
        if include_totaldebitonegociado:
            totaldebitonegociado = form.calcular_total() if hasattr(form, 'calcular_total') else 0.0
            additional_context.update({"totaldebitonegociado": totaldebitonegociado})

        # Totalizador para o relatório de renegociações
        if include_totalliberado:
            totalliberado = form.calcular_total() if hasattr(form, 'calcular_total') else 0.0
            additional_context.update({"totalliberado": totalliberado})

        return render_to_pdf(
            template_name_pdf,
            {**additional_context, "qs": qs, "user": request.user, "emissao": now()}
        )
    else:
        messages.warning(request, str(form.errors.as_data())[31:-5])
        return None


# class BaseProcessoListView(ListView):
    # """
    # Classe base para listagens de processos.
    # """
    # model = Processo
    # # filterset_class = ProcessoFilter
    # ordering = '-id'
    # template_name = None
    #
    # def get_queryset(self):
    #     """
    #     Verificação de filtragem de processos excluíodos ou não.
    #     """
    #     if mostra_excluidos:
    #         return super().get_queryset().values_list('id', 'is_devedor')
    #     else:
    #         return super().get_queryset().filter(is_deleted=False).values_list('id', 'is_devedor')


class BaseProcessoListView(ListView):
    """
    Classe base para listagens de processos.
    """
    model = Processo
    ordering = '-id'
    template_name = None

    def get_queryset(self):
        """
        Verificação de filtragem de processos excluídos ou não.
        """

        # Subquery para verificar se existe um financeiro em aberto e vencido
        financeiro_devedor_subquery = Financeiro.objects.filter(
            processo_id=OuterRef('id'),
            status='A',
            dtvencimento__lt=date.today()
        )

        # Subquery para verificar se existe algum financeiro em aberto
        financeiro_quitado_subquery = Financeiro.objects.filter(
            processo_id=OuterRef('id'),
            status='A'
        )

        queryset = super().get_queryset().annotate(
            is_devedor=Exists(financeiro_devedor_subquery),  # True se houver débito vencido
            is_quitado=~Exists(financeiro_quitado_subquery)  # True se NÃO houver registros em aberto
        ).values_list('id', 'is_devedor', 'is_quitado', 'numprocesso', 'localizacao__nome', 'linhacredito__nome',
                      'clientepf__nome', 'clientepj__razaosocial', 'dtprocesso', 'numprotocolo', 'criado_por__first_name',
                      'status')

        if not mostra_excluidos:
            queryset = queryset.filter(is_deleted=False)

        return queryset


class PessoaFisicaListView(ListView):
    template_name = "pessoasfisicas/pessoasfisicas_list.html"

    def get_queryset(self):
        if not mostra_excluidos:
            queryset = PessoaFisica.objects.filter(is_deleted=False).values_list('id', 'nome', 'numcpf', 'tipo', 'situacao__descricao', 'situacao__blq_processo', 'is_deleted')
        else:
            queryset = PessoaFisica.objects.all().values_list('id', 'nome', 'numcpf', 'tipo', 'situacao__descricao', 'situacao__blq_processo', 'is_deleted')
        return queryset


class PessoaFisicaCreateView(SuccessMessageMixin, CreateView):
    """
    Cria um novo registro de Pessoa Física.
    """
    model = PessoaFisica
    form_class = PessoaFisicaForm
    success_url = '/processos/pessoasfisicas'
    template_name = "pessoasfisicas/edit_pessoafisica.html"
    # success_message = "Pessoa Física criada com sucesso."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "title": "Nova Pessoa Física",
            "savebtn": "Adicionar"
        })
        return context

    def form_valid(self, form):
        form.instance.criado_por = self.request.user
        form.instance.data_criacao = datetime.today()
        form.instance.data_edicao = datetime.today()
        # Mensagem de sucesso dinâmica
        success_message = f"Dados do cliente/avalista {form.instance.nome} inseridos com sucesso."
        messages.success(self.request, success_message)  # Exibe a mensagem de sucesso
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())


class PessoaFisicaUpdateView(SuccessMessageMixin, UpdateView):
    """
    Altera um registro de pessoa física
    """
    model = PessoaFisica
    form_class = PessoaFisicaForm
    success_url = '/processos/pessoasfisicas'
    template_name = "pessoasfisicas/edit_pessoafisica.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Edita Pessoa Física'
        context["savebtn"] = 'Salva'
        context["delbtn"] = 'Apaga'

        # Querysets relacionados
        qsprocessos = Processo.objects.filter(is_deleted=False, clientepf=self.kwargs['pk'])
        context["qsprocessos"] = qsprocessos

        qsprocessosava = Avalista.objects.filter(is_deleted=False, avalista_id=self.kwargs['pk'])
        context["qsprocessosava"] = qsprocessosava

        # Cálculo de totais financeiros
        qstitulosT = Financeiro.objects.filter(is_deleted=False, processo__in=qsprocessos)

        def calculate_total(queryset, field, filter_status=None):
            if filter_status:
                queryset = queryset.filter(status=filter_status)
            return queryset.aggregate(total=Sum(field))['total'] or 0

        context["qstitulos"] = qstitulosT
        context["valor_total"] = calculate_total(qstitulosT, 'valorparcela')
        context["valor_pago"] = calculate_total(qstitulosT, 'valorpago', filter_status='P')
        context["valor_aberto"] = calculate_total(qstitulosT, 'valorparcela', filter_status='A')

        return context

    def form_valid(self, form):
        form.instance.data_edicao = datetime.today()
        success_message = f"Dados do cliente/avalista {form.instance.nome} atualizados com sucesso."
        messages.success(self.request, success_message)
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())


class PessoaFisicaDeleteView(View):
    """
    Exclui um registro de pessoa física
    """
    template_name = "pessoasfisicas/delete_pessoafisica.html"

    def get(self, request, pk):
        pessoafisica = get_object_or_404(PessoaFisica, pk=pk)
        return render(request, self.template_name, {'object': pessoafisica})

    def post(self, request, pk):
        pessoafisica = get_object_or_404(PessoaFisica, pk=pk)
        pessoafisica.is_deleted = True
        pessoafisica.data_edicao = datetime.today()
        pessoafisica.save()
        success_message = f"Cliente/avalista {pessoafisica.nome} excluído com sucesso."
        messages.success(request, success_message)
        return redirect('pessoasfisicas-list')


class PessoaJuridicaListView(FilterView):
    """
    Lista todas as pessoas jurídicas, excluindo registros marcados como deletados.
    """
    filterset_class = PessoaFisicaFilter
    template_name = "pessoasjuridicas/pessoasjuridicas_list.html"

    def get_queryset(self):
        queryset = PessoaJuridica.objects.filter(is_deleted=False) if not mostra_excluidos else PessoaJuridica.objects.all()
        return queryset.values_list('id', 'razaosocial', 'numcnpj', 'porteempresa', 'setornegocio__nome',
                                    'ramoatividade__nome', 'situacao__descricao', 'situacao__blq_processo',
                                    'is_deleted', 'bairro__nome')


class PessoaJuridicaCreateView(SuccessMessageMixin, CreateView):
    """
    Cria um novo registro de Pessoa Jurídica.
    """
    model = PessoaJuridica
    form_class = PessoaJuridicaForm
    success_url = '/processos/pessoasjuridicas'
    template_name = "pessoasjuridicas/edit_pessoajuridica.html"

    def get_context_data(self, **kwargs):
        """
        Insere informações adicionais no contexto.
        """
        context = super().get_context_data(**kwargs)
        context.update({
            "title": "Nova Pessoa Jurídica",
            "savebtn": "Adiciona",
            "formset_socios": self._initialize_formset(),
        })
        return context

    def form_valid(self, form):
        """
        Processa a criação da Pessoa Jurídica e seus sócios.
        """
        form.instance.criado_por = self.request.user
        form.instance.data_criacao = now()
        form.instance.data_edicao = now()
        self.object = form.save()

        if not self._process_formset():
            return self.form_invalid(form)

        messages.success(
            self.request,
            f"Dados da empresa {form.instance.razaosocial} inseridos com sucesso."
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Exibe mensagens de erro quando o formulário principal é inválido.
        """
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())

    def _initialize_formset(self):
        """
        Inicializa o formset de sócios com ou sem dados POST.
        """
        if self.request.POST:
            return SocioFormSet(self.request.POST)
        return SocioFormSet()

    def _process_formset(self):
        """
        Processa o formset de sócios para validar e salvar.
        Retorna `False` se o formset for inválido, caso contrário, `True`.
        """
        formset = SocioFormSet(self.request.POST, instance=self.object)
        if not formset.is_valid():
            return False

        for form in formset:
            if form.cleaned_data:  # Ignora formulários vazios
                socio = form.save(commit=False)
                socio.criado_por = self.request.user
                socio.data_criacao = now()
                socio.data_edicao = now()
                socio.save()
        return True


class PessoaJuridicaUpdateView(SuccessMessageMixin, UpdateView):
    """
    Atualiza um registro existente de Pessoa Jurídica.
    """
    model = PessoaJuridica
    form_class = PessoaJuridicaForm
    success_url = '/processos/pessoasjuridicas'
    template_name = "pessoasjuridicas/edit_pessoajuridica.html"

    def get_context_data(self, **kwargs):
        """
        Insere informações adicionais no contexto.
        """
        context = super().get_context_data(**kwargs)
        context.update({
            "title": "Edita Pessoa Jurídica",
            "savebtn": "Salva",
            "delbtn": "Apaga",
            "qsprocessos": self._get_processos(),
            **self._get_financeiro_totais(),
            "formset_socios": self._initialize_formset(),
        })
        return context

    def form_valid(self, form):
        """
        Processa a atualização da Pessoa Jurídica e seus sócios.
        """
        context = self.get_context_data()
        form.instance.data_edicao = now()
        self.object = form.save()

        if not self._process_formset(context["formset_socios"]):
            return self.form_invalid(form)

        messages.success(
            self.request,
            f"Dados da empresa {form.instance.razaosocial} atualizados com sucesso."
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Exibe mensagens de erro quando o formulário principal é inválido.
        """
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())

    def _initialize_formset(self):
        """
        Inicializa o formset de sócios com ou sem dados POST.
        """
        pessoajuridica = self.object
        queryset = PJuridicaSocio.objects.filter(
            pessoajuridica=pessoajuridica, is_deleted=False
        )
        if self.request.POST:
            return SocioFormSet(self.request.POST, instance=pessoajuridica, queryset=queryset)
        return SocioFormSet(instance=pessoajuridica, queryset=queryset)

    def _process_formset(self, formset):
        """
        Processa o formset de sócios, incluindo exclusões e atualizações.
        Retorna `False` se o formset for inválido, caso contrário, `True`.
        """
        if not formset.is_valid():
            return False

        for socio_form in formset.deleted_forms:
            socio = socio_form.instance
            socio.is_deleted = True
            socio.save()

        for socio in formset.save(commit=False):
            socio.processo = self.object
            socio.criado_por = self.request.user
            socio.save()

        return True

    def _get_processos(self):
        """
        Retorna os processos associados à Pessoa Jurídica.
        """
        return Processo.objects.filter(is_deleted=False, clientepj=self.kwargs['pk'])

    def _get_financeiro_totais(self):
        """
        Calcula os totais financeiros para os processos da Pessoa Jurídica.
        """
        qsprocessos = self._get_processos()
        qstitulos = Financeiro.objects.filter(
            is_deleted=False, processo_id__in=qsprocessos.values_list("id", flat=True)
        )

        totais = {
            "valor_total": qstitulos.aggregate(total=Sum("valorparcela"))["total"] or 0,
            "valor_pago": qstitulos.filter(status="P").aggregate(total=Sum("valorpago"))["total"] or 0,
            "valor_aberto": qstitulos.filter(status="A").aggregate(total=Sum("valorparcela"))["total"] or 0,
        }

        return {"qstitulos": qstitulos, **totais}


class PessoaJuridicaDeleteView(View):
    """
    Exclui uma Pessoa Jurídica marcando-a como deletada.
    """
    template_name = "pessoasjuridicas/delete_pessoajuridica.html"

    def get(self, request, pk):
        """
        Exibe a página de confirmação de exclusão.
        """
        pessoajuridica = self._get_pessoajuridica_or_404(pk)
        return render(request, self.template_name, {'object': pessoajuridica})

    def post(self, request, pk):
        """
        Realiza a exclusão lógica de uma Pessoa Jurídica.
        """
        pessoajuridica = self._get_pessoajuridica_or_404(pk)
        self._mark_as_deleted(pessoajuridica)
        messages.success(request, f"Empresa {pessoajuridica.razaosocial} excluída com sucesso.")
        return redirect('pessoasjuridicas-list')

    @staticmethod
    def _get_pessoajuridica_or_404(self, pk):
        """
        Recupera a Pessoa Jurídica ou retorna 404 caso não exista.
        """
        return get_object_or_404(PessoaJuridica, pk=pk)

    @staticmethod
    def _mark_as_deleted(self, pessoajuridica):
        """
        Marca a Pessoa Jurídica como deletada e atualiza o campo de edição.
        """
        pessoajuridica.is_deleted = True
        pessoajuridica.data_edicao = now()  # Usa timezone.now() em vez de datetime.today()
        pessoajuridica.save()


class ProcessoListView(BaseProcessoListView):
    """
    View para listar processos, com suporte a controle de exibição de registros excluídos.
    """

    template_name = "processos/processos_list.html"

    def get_queryset(self):
        """
        Retorna o conjunto de processos a ser exibido.
        Filtra registros excluídos com base na variável global `mostra_excluidos`.
        """

        queryset = super().get_queryset()  # Chama o método da classe base

        return queryset

    def get_context_data(self, **kwargs):
        """
        Adiciona informações adicionais ao contexto da template, como o título da lista.
        """
        context = super().get_context_data(**kwargs)  # Chama o método da classe base
        context["titlerel"] = "Lista de Processos"  # Título da lista
        context["mostra_excluidos"] = mostra_excluidos  # Flag para o template
        return context


class ProcessosPendentesListView(BaseProcessoListView):
    """
    View para listar processos pendentes com base em critérios de prazo e status.
    """
    template_name = "processos/processospendentes_list.html"

    def get_tmpconclusao(self):
        """
        Recupera o prazo de conclusão do processo a partir das configurações.
        """
        config = Config.objects.filter(is_deleted=False).last()
        return config.tmpconclusaoprocesso if config else 0

    def get_datalimite(self):
        """
        Calcula a data limite para considerar processos como pendentes.
        """
        tmpconclusao = self.get_tmpconclusao()
        return datetime.today() - timedelta(days=tmpconclusao)

    def get_queryset(self):
        """
        Filtra processos pendentes com base nos critérios definidos.
        """
        datalimite = self.get_datalimite()
        queryset = (super().get_queryset().filter(~Q(status='F') & ~Q(status='N') & Q(dtprocesso__lte=datalimite))
                    .values_list("id", "numprocesso", "localizacao__nome", "linhacredito__nome", "clientepf__nome",
                                 "clientepj__razaosocial", "dtprocesso", "numprotocolo"))
        return queryset

    def get_context_data(self, **kwargs):
        """
        Adiciona informações adicionais ao contexto da template.
        """
        context = super().get_context_data(**kwargs)
        context["queryset"] = self.get_queryset()  # Passando explicitamente como queryset
        context["titlerel"] = "Pendentes"
        return context

# usado para adicionar um novo registro de processo de PF
# ----------------------------------------------------------------
# class ProcessoPFCreateView(SuccessMessageMixin, CreateView):
#     model = Processo
#     form_class = ProcessoPFForm
#     # success_url = '/processos/processos'
#     template_name = "processos/edit_processopf.html"
#
#     def __init__(self):
#         self.object = None
#
#     def get_context_data(self, **kwargs):
#         data = super().get_context_data(**kwargs)
#         data["title"] = 'Novo Processo PF'
#         data["savebtn"] = 'Adiciona'
#         data["cancelbtn"] = 'Cancela'
#         if self.request.POST:
#             data['formset_avalistas'] = AvalistaFormSet(self.request.POST)
#             data['formset_referencias'] = ReferenciaInsertFormSet(self.request.POST)
#         else:
#             data['formset_avalistas'] = AvalistaFormSet()
#             data['formset_referencias'] = ReferenciaInsertFormSet()
#         return data
#
#     @transaction.atomic
#     def form_valid(self, form):
#         context = self.get_context_data()
#         form.instance.criado_por = self.request.user
#         form.instance.data_criacao = datetime.today()
#         form.instance.data_edicao = datetime.today()
#         form.instance.localizacao_id = Localizacao.objects.values('id').filter(is_deleted=False, is_default=True)
#         # form.instance.status = 'R'
#         form.instance.status = 'A'
#         # qsparametro = Config.objects.filter(is_deleted=False).last()
#         # exercicioatual = qsparametro.exercicio
#
#         exercicioatual = Config.objects.filter(is_deleted=False).last().exercicio
#
#         qsprocesso = Processo.objects.filter(dtprocesso__year=exercicioatual).last()
#
#         if qsprocesso:
#             ultprocesso = qsprocesso.numprocesso
#         else:
#             ultprocesso = '0000/' + str(exercicioatual)
#         seqprocesso = int(ultprocesso[0:4]) + 1
#
#         form.instance.numprocesso = str(seqprocesso).zfill(4) + '/' + str(exercicioatual)
#         self.object = form.save()
#
#         # inicia aqui a gravação dos avalistas e das referências
#         processo = get_object_or_404(Processo, pk=self.object.pk)
#
#         formset_avalistas = context['formset_avalistas']
#         if not formset_avalistas.is_valid():
#             pass
#         else:
#             formset_avalistas = AvalistaFormSet(self.request.POST, instance=processo)
#             avalistas = formset_avalistas
#             for avalista in avalistas:
#                 avalista.criado_por = self.request.user
#                 avalista.data_criacao = datetime.today()
#                 avalista.data_edicao = datetime.today()
#                 avalista.save()
#
#         formset_referencias = context['formset_referencias']
#         if not formset_referencias.is_valid():
#             pass
#         else:
#             formset_referencias = ReferenciaInsertFormSet(self.request.POST, instance=processo)
#             referencias = formset_referencias
#             for referencia in referencias:
#                 referencia.criado_por = self.request.user
#                 referencia.save()
#
#         messages.success(self.request, "Dados do processo " + form.instance.numprocesso + " inseridos com sucesso.")
#         return super().form_valid(form)
#
#     def get_success_url(self):
#         # Redireciona para a página de edição do processo recém-criado
#         return reverse('edit-processopf', kwargs={'pk': self.object.pk})
#
#     def form_invalid(self, form):
#         messages.warning(self.request, showmessages_error(form))
#         return self.render_to_response(self.get_context_data())
#
#
#
# # usado para adicionar um novo registro de processo de PJ
# # ----------------------------------------------------------------
# class ProcessoPJCreateView(SuccessMessageMixin, CreateView):
#     model = Processo
#     form_class = ProcessoPJForm
#     # success_url = '/processos/processos'
#     template_name = "processos/edit_processopj.html"
#
#     def __init__(self):
#         self.object = None
#
#     def get_context_data(self, **kwargs):
#         data = super().get_context_data(**kwargs)
#         data["title"] = 'Novo Processo PJ'
#         data["savebtn"] = 'Adiciona'
#         data["cancelbtn"] = 'Cancela'
#         if self.request.POST:
#             data['formset_avalistas'] = AvalistaFormSet(self.request.POST)
#             data['formset_referencias'] = ReferenciaInsertFormSet(self.request.POST)
#         else:
#             data['formset_avalistas'] = AvalistaFormSet()
#             data['formset_referencias'] = ReferenciaInsertFormSet()
#         return data
#
#     @transaction.atomic
#     def form_valid(self, form):
#         context = self.get_context_data()
#         form.instance.criado_por = self.request.user
#         form.instance.data_criacao = datetime.today()
#         form.instance.data_edicao = datetime.today()
#         form.instance.localizacao_id = Localizacao.objects.values('id').filter(is_deleted=False, is_default=True)
#         # form.instance.status = 'P'
#         # form.instance.status = 'R'
#         form.instance.status = 'A'
#
#         # qsparametro = Config.objects.filter(is_deleted=False).last()
#         # exercicioatual = qsparametro.exercicio
#
#         exercicioatual = Config.objects.filter(is_deleted=False).last().exercicio
#
#         qsprocesso = Processo.objects.filter(dtprocesso__year=exercicioatual).last()
#
#         if qsprocesso:
#             ultprocesso = qsprocesso.numprocesso
#         else:
#             ultprocesso = '0000/' + str(exercicioatual)
#         seqprocesso = int(ultprocesso[0:4]) + 1
#
#         form.instance.numprocesso = str(seqprocesso).zfill(4) + '/' + str(exercicioatual)
#         self.object = form.save()
#
#         # inicia aqui a gravação dos avalistas e das referências
#         processo = get_object_or_404(Processo, pk=self.object.pk)
#
#         formset_avalistas = context['formset_avalistas']
#         if not formset_avalistas.is_valid():
#             pass
#         else:
#             formset_avalistas = AvalistaFormSet(self.request.POST, instance=processo)
#             avalistas = formset_avalistas
#             for avalista in avalistas:
#                 avalista.criado_por = self.request.user
#                 avalista.data_criacao = datetime.today()
#                 avalista.data_edicao = datetime.today()
#                 avalista.save()
#
#         formset_referencias = context['formset_referencias']
#         if not formset_referencias.is_valid():
#             pass
#         else:
#             formset_referencias = ReferenciaInsertFormSet(self.request.POST, instance=processo)
#             referencias = formset_referencias
#             for referencia in referencias:
#                 referencia.criado_por = self.request.user
#                 referencia.save()
#
#         messages.success(self.request, "Dados do processo " + form.instance.numprocesso + " inseridos com sucesso.")
#         return super().form_valid(form)
#
#     def get_success_url(self):
#         # Redireciona para a página de edição do processo recém-criado
#         return reverse('edit-processopj', kwargs={'pk': self.object.pk})
#
#     def form_invalid(self, form):
#         messages.warning(self.request, showmessages_error(form))
#         return self.render_to_response(self.get_context_data())


class BaseProcessoCreateView(SuccessMessageMixin, CreateView):
    """
    Classe base para criação de processos (PF e PJ).
    Gerencia lógica comum para formsets de avalistas, referências e atribuição de dados ao processo.
    """
    model = Processo

    def __init__(self):
        self.object = None

    def get_context_data(self, **kwargs):
        """Adiciona dados de contexto compartilhados entre PF e PJ."""
        data = super().get_context_data(**kwargs)
        data["savebtn"] = "Adiciona"
        data["cancelbtn"] = "Cancela"
        if self.request.POST:
            data["formset_avalistas"] = AvalistaFormSet(self.request.POST)
            data["formset_referencias"] = ReferenciaInsertFormSet(self.request.POST)
        else:
            data["formset_avalistas"] = AvalistaFormSet()
            data["formset_referencias"] = ReferenciaInsertFormSet()
        return data

    def _get_exercicio_atual(self):
        """Obtém o exercício atual a partir das configurações."""
        return Config.objects.filter(is_deleted=False).last().exercicio

    def _gerar_numprocesso(self, exercicio_atual):
        """Gera o número do processo baseado no exercício atual."""
        ultimo_processo = Processo.objects.filter(dtprocesso__year=exercicio_atual).last()
        ult_num = ultimo_processo.numprocesso if ultimo_processo else f"0000/{exercicio_atual}"
        seq_num = int(ult_num.split('/')[0]) + 1
        return f"{str(seq_num).zfill(4)}/{exercicio_atual}"

    @transaction.atomic
    def form_valid(self, form):
        """Processa e salva os dados do formulário e formsets associados."""
        context = self.get_context_data()
        form.instance.criado_por = self.request.user
        form.instance.data_criacao = datetime.today()
        form.instance.data_edicao = datetime.today()
        form.instance.localizacao_id = (Localizacao.objects.filter(is_deleted=False, is_default=True)
                                        .values_list("id",flat=True).first())
        form.instance.status = "A"
        form.instance.numprocesso = self._gerar_numprocesso(self._get_exercicio_atual())

        self.object = form.save()

        linhacredito = get_object_or_404(LinhaCredito, nome=form.instance.linhacredito)
        if linhacredito.is_garantia:
            form.instance.veiculo_id = (Veiculo.objects.filter(is_deleted=False, is_vendido=False,
                                                               clientepf=form.instance.clientepf)
                                        .values_list("id",flat=True).first())

            veiculo = get_object_or_404(Veiculo, pk=form.instance.veiculo_id)
            veiculo.is_vendido = True
            veiculo.save()

        processo = get_object_or_404(Processo, pk=self.object.pk)

        self._salvar_formset(context["formset_avalistas"], processo, "avalista")
        self._salvar_formset(context["formset_referencias"], processo, "referencia")

        messages.success(self.request, f"Dados do processo {form.instance.numprocesso} inseridos com sucesso.")
        return super().form_valid(form)

    def _salvar_formset(self, formset, processo, tipo):
        """Valida e salva os dados do formset associado."""
        formset.instance = processo  # Define a instância pai do formset
        if formset.is_valid():
            # Salva os objetos do formset sem enviar diretamente ao banco
            forms = formset.save(commit=False)
            for form in forms:
                form.criado_por = self.request.user
                form.data_criacao = datetime.today()
                form.data_edicao = datetime.today()
                form.save()  # Agora pode salvar no banco com o objeto pai associado
        else:
            # Adiciona mensagens de erro se o formset for inválido
            messages.warning(self.request, f"Erros ao salvar {tipo}s: {formset.errors}")

    def form_invalid(self, form):
        """Trata formulários inválidos."""
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())


class ProcessoPFCreateView(BaseProcessoCreateView):
    """
    View para criar processos do tipo Pessoa Física (PF).
    """
    form_class = ProcessoPFForm
    template_name = "processos/edit_processopf.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["title"] = "Novo Processo PF"
        return data

    def get_success_url(self):
        return reverse("edit-processopf", kwargs={"pk": self.object.pk})


class ProcessoPJCreateView(BaseProcessoCreateView):
    """
    View para criar processos do tipo Pessoa Jurídica (PJ).
    """
    form_class = ProcessoPJForm
    template_name = "processos/edit_processopj.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["title"] = "Novo Processo PJ"
        return data

    def get_success_url(self):
        return reverse("edit-processopj", kwargs={"pk": self.object.pk})


# usado para atualizar as informações de um processo PF
# ----------------------------------------------------------------
class ProcessoPFUpdateView(SuccessMessageMixin, UpdateView):
    model = Processo
    form_class = ProcessoPFForm
    # success_url = '/processos/processos'
    template_name = "processos/edit_processopf.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Edita Processo PF'
        context["savebtn"] = 'Salva'
        context["delbtn"] = 'Apaga'
        context["cancelbtn"] = 'Cancela'

        # Carrega o processo e as referências associadas
        processo = self.object
        if self.request.POST:
            context['formset_avalistas'] = AvalistaFormSet(self.request.POST, instance=processo,
                                                           queryset=Avalista.objects.filter(processo=processo, is_deleted=False))
            context['formset_referencias'] = ReferenciaUpdateFormSet(self.request.POST, instance=processo,
                                                                     queryset=Referencia.objects.filter(processo=processo, is_deleted=False))
        else:
            context['formset_avalistas'] = AvalistaFormSet(instance=processo,
                                                           queryset = Avalista.objects.filter(processo=processo, is_deleted=False))
            context['formset_referencias'] = ReferenciaUpdateFormSet(instance=processo,
                                                                     queryset=Referencia.objects.filter(processo=processo, is_deleted=False))

        # Adiciona informações do cliente PF e PJ ao contexto
        clientepf = get_object_or_404(PessoaFisica, pk=processo.clientepf_id)
        context["nome"] = clientepf.nome
        context["numrg"] = clientepf.numrg
        context["orgexpedrg"] = clientepf.orgexpedrg
        context["sexo"] = clientepf.sexo
        context["numcpf"] = clientepf.numcpf
        context["nomemae"] = clientepf.nomemae
        context["nomepai"] = clientepf.nomepai
        context["conjuge"] = clientepf.conjuge
        context["cpfconjuge"] = clientepf.cpfconjuge
        context["dtnascimento"] = clientepf.dtnascimento
        context["logradouro"] = clientepf.logradouro
        context["numimovel"] = clientepf.numimovel
        context["bairro"] = clientepf.bairro
        context["cep"] = clientepf.cep
        context["telefones"] = clientepf.telfixo + ' | ' + clientepf.telcelular1 + ' | ' + clientepf.telcelular2
        context["rendaempresa"] = clientepf.rendaempresa
        context["rendaliqempresa"] = clientepf.rendaliqempresa
        context["observacao"] = clientepf.observacao

        if processo.empresa_id:
            clientepj = get_object_or_404(PessoaJuridica, pk=processo.empresa_id)
            context["razaosocial"] = clientepj.razaosocial
            context["dtiniatividade"] = clientepj.dtiniatividade
            context["numcnpj"] = clientepj.numcnpj
            context["porteempresa"] = clientepj.porteempresa
            context["telefonespj"] = clientepj.telfixo + ' | ' + clientepj.telcelular1 + ' | ' + clientepj.telcelular2
            qssocios = PJuridicaSocio.objects.filter(pessoajuridica_id=clientepj.id,is_deleted=False)
            context["socios"] = qssocios
            context["setornegocio"] = clientepj.setornegocio
            context["ramoatividade"] = clientepj.ramoatividade
            context["observacao"] = clientepj.observacao

        movimentacao = Movimentacao.objects.filter(processo_id=processo.pk).order_by('dtmovimento')
        context["movimentacao"] = movimentacao

        return context

    @transaction.atomic
    def form_valid(self, form):
        context = self.get_context_data()
        form.instance.data_edicao = datetime.today()
        form.instance.veiculo_id = (Veiculo.objects.filter(is_deleted=False, is_vendido=False, clientepf=form.instance.clientepf)
                                        .values_list("id",flat=True).first())
        self.object = form.save()

        contaval = 0
        formset_avalistas = context['formset_avalistas']
        if formset_avalistas.is_valid():
            avalistas = formset_avalistas.save(commit=False)  # Não salva imediatamente
            # Lida com formulários marcados para exclusão
            for avalista_form in formset_avalistas.deleted_forms:
                avalista = avalista_form.instance
                avalista.is_deleted = True
                avalista.save()
            for avalista in avalistas:
                avalista.processo = self.object  # Assegura que o processo correto está associado
                avalista.save()  # Salva a referência
            for x in formset_avalistas:
                avalista = x.cleaned_data.get('avalista')
                if avalista:
                    contaval = contaval + 1
            # if contaval < 2:
            #     messages.warning(self.request,
            #                      f"A quantidade mínima é de 2 (dois) avalistas para esta linha de crédito. Atualize os dados.")
            #     return self.form_invalid(form)
        else:
            for error in formset_avalistas.errors:
                print(error)
            return self.form_invalid(form)

        formset_referencias = context['formset_referencias']
        if formset_referencias.is_valid():
            referencias = formset_referencias.save(commit=False)  # Não salva imediatamente
            # Lida com formulários marcados para exclusão
            for referencia_form in formset_referencias.deleted_forms:
                referencia = referencia_form.instance
                referencia.is_deleted = True
                referencia.save()
            for referencia in referencias:
                referencia.processo = self.object  # Assegura que o processo correto está associado
                referencia.save()  # Salva a referência
        else:
            for error in formset_referencias.errors:
                print(error)
            return self.form_invalid(form)

        messages.success(self.request, f"Dados do processo {form.instance.numprocesso} atualizados com sucesso.")
        return super().form_valid(form)

    def get_success_url(self):
        return self.request.path_info  # Redireciona para a própria página de edição

    def form_invalid(self, form):
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())

# usado para atualizar as informações de um processo PJ
# ----------------------------------------------------------------
class ProcessoPJUpdateView(SuccessMessageMixin, UpdateView):
    model = Processo
    form_class = ProcessoPJForm
    # success_url = '/processos/processos'
    template_name = "processos/edit_processopj.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Edita Processo PJ'
        context["savebtn"] = 'Salva'
        context["delbtn"] = 'Apaga'
        context["cancelbtn"] = 'Cancela'

        # Carrega o processo e as referências associadas
        processo = self.object
        if self.request.POST:
            context['formset_avalistas'] = AvalistaFormSet(self.request.POST, instance=processo,
                                                           queryset=Avalista.objects.filter(processo=processo, is_deleted=False))
            context['formset_referencias'] = ReferenciaUpdateFormSet(self.request.POST, instance=processo,
                                                                     queryset=Referencia.objects.filter(processo=processo, is_deleted=False))
        else:
            context['formset_avalistas'] = AvalistaFormSet(instance=processo,
                                                           queryset = Avalista.objects.filter(processo=processo, is_deleted=False))
            context['formset_referencias'] = ReferenciaUpdateFormSet(instance=processo,
                                                                     queryset=Referencia.objects.filter(processo=processo, is_deleted=False))

        # Adiciona informações do cliente PJ ao contexto
        clientepj = get_object_or_404(PessoaJuridica, pk=processo.empresa_id)
        context["razaosocial"] = clientepj.razaosocial
        context["dtiniatividade"] = clientepj.dtiniatividade
        context["numcnpj"] = clientepj.numcnpj
        context["porteempresa"] = clientepj.porteempresa
        context["telefones"] = clientepj.telfixo + ' | ' + clientepj.telcelular1 + ' | ' + clientepj.telcelular2
        qssocios = PJuridicaSocio.objects.filter(pessoajuridica_id=clientepj.id, is_deleted=False)
        context["socios"] = qssocios
        context["setornegocio"] = clientepj.setornegocio
        context["ramoatividade"] = clientepj.ramoatividade
        context["observacao"] = clientepj.observacao

        return context

    @transaction.atomic
    def form_valid(self, form):
        context = self.get_context_data()
        form.instance.data_edicao = datetime.today()
        self.object = form.save()

        formset_avalistas = context['formset_avalistas']
        if formset_avalistas.is_valid():
            avalistas = formset_avalistas.save(commit=False)  # Não salva imediatamente
            # Lida com formulários marcados para exclusão
            for avalista_form in formset_avalistas.deleted_forms:
                avalista = avalista_form.instance
                avalista.is_deleted = True
                avalista.save()
            for avalista in avalistas:
                avalista.processo = self.object  # Assegura que o processo correto está associado
                avalista.save()  # Salva a referência
        else:
            for error in formset_avalistas.errors:
                print(error)
            return self.form_invalid(form)

        formset_referencias = context['formset_referencias']
        if formset_referencias.is_valid():
            referencias = formset_referencias.save(commit=False)  # Não salva imediatamente
            # Lida com formulários marcados para exclusão
            for referencia_form in formset_referencias.deleted_forms:
                referencia = referencia_form.instance
                referencia.is_deleted = True
                referencia.save()
            for referencia in referencias:
                referencia.processo = self.object  # Assegura que o processo correto está associado
                referencia.save()  # Salva a referência
        else:
            for error in formset_referencias.errors:
                print(error)
            return self.form_invalid(form)

        messages.success(self.request, f"Dados do processo {form.instance.numprocesso} atualizados com sucesso.")
        return super().form_valid(form)

    def get_success_url(self):
        return self.request.path_info  # Redireciona para a própria página de edição

    def form_invalid(self, form):
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())


class BaseProcessoActionView(View):
    """
    Classe base para ações em processos (exclusão, cancelamento, etc.).
    """
    template_name = None
    success_message = None
    action = None  # Metodo para aplicar a alteração específica ao processo

    def get(self, request, pk):
        """
        Renderiza a página de confirmação com os detalhes do processo.
        """
        processo = get_object_or_404(Processo, pk=pk)
        return render(request, self.template_name, {'object': processo})

    def post(self, request, pk):
        """
        Aplica a ação especificada no processo e redireciona.
        """
        processo = get_object_or_404(Processo, pk=pk)
        self.apply_action(processo)
        processo.numprotocolo = f"{processo.numprotocolo[:18]}XX"
        processo.data_edicao = datetime.today()
        processo.save()
        messages.success(request, self.success_message.format(numprocesso=processo.numprocesso))
        return redirect('processos-list')

    def apply_action(self, processo):
        """
        Define a ação específica a ser realizada no processo.
        Deve ser implementada em subclasses.
        """
        raise NotImplementedError("Subclasses devem implementar o método `apply_action`.")


# class ProcessoDeleteView(BaseProcessoActionView):
#     """
#     View para excluir um processo (soft delete).
#     """
#     template_name = "processos/delete_processo.html"
#     success_message = "Processo {numprocesso} excluído com sucesso."
#
#     def apply_action(self, processo):
#         """
#         Marca o processo como excluído.
#         """
#         processo.is_deleted = True
#
#
# class ProcessoCancelView(BaseProcessoActionView):
#     """
#     View para cancelar um processo (alterar status para 'C').
#     """
#     template_name = "processos/cancel_processo.html"
#     success_message = "Processo {numprocesso} cancelado com sucesso."
#
#     def apply_action(self, processo):
#         """
#         Altera o status do processo para cancelado.
#         """
#         processo.status = 'C'


# # usado para listar todos os registros da tabela de Avalistas
# # ----------------------------------------------------------------
# class AvalistaListView(ListView):
#     model = Avalista
#     template_name = "processoavalistas/processoavalistas_list.html"
#
#     def get_queryset(self, **kwargs):
#         qs = super().get_queryset(**kwargs).filter(is_deleted=False)
#         return qs.filter(processo_id=self.kwargs['pk'])
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         processo = get_object_or_404(Processo, pk=self.kwargs['pk'])
#         context["idprocesso"] = processo.id
#         context["numprocesso"] = processo.numprocesso
#         context["statusprocesso"] = processo.texto_status
#         if processo.clientepf:
#             context["clienteprocesso"] = processo.clientepf.nome
#         else:
#             context["clienteprocesso"] = processo.clientepj.razaosocial
#         return context
#

# # usado para adicionar um novo registro na tabela de Avalistas
# # ----------------------------------------------------------------
# class AvalistaCreateView(SuccessMessageMixin, CreateView):
#     model = Avalista
#     form_class = AvalistaForm
#     success_url = '/processos/processos'
#     template_name = "processoavalistas/edit_processoavalista.html"
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["title"] = 'Novo Avalista'
#         context["savebtn"] = 'Adiciona'
#
#         processo = get_object_or_404(Processo, pk=self.kwargs['pk'])
#         context["numprocesso"] = processo.numprocesso
#         context["statusprocesso"] = processo.texto_status
#         context["flagstatus"] = processo.status
#         if processo.clientepf:
#             context["clienteprocesso"] = processo.clientepf.nome
#         else:
#             context["clienteprocesso"] = processo.clientepj.razaosocial
#
#         return context
#
#     def form_valid(self, form):
#         processo = get_object_or_404(Processo, pk=self.kwargs['pk'])
#         if not processo.status == 'N':
#             processo.status = 'A'
#             processo.save()
#
#         form.instance.processo_id = self.kwargs['pk']
#         form.instance.criado_por = self.request.user
#         form.instance.data_criacao = datetime.today()
#         form.instance.data_edicao = datetime.today()
#         messages.success(self.request, "Dados do avalista " + form.instance.avalista.nome + " do Processo " + processo.numprocesso + " inseridos com sucesso.")
#         return super().form_valid(form)
#
#     def form_invalid(self, form):
#         # Adds errors to Django messaging framework in the case of an invalid form and redirects to the page
#         # messages.warning(self.request, str(form.errors.as_data())[31:-5])
#         messages.warning(self.request, dict(form.errors.items()))
#         return self.render_to_response(self.get_context_data())
#
#
# # usado para atualizar as informações de um Avalista em um Processo
# # ----------------------------------------------------------------
# class AvalistaUpdateView(SuccessMessageMixin, UpdateView):
#     model = Avalista
#     form_class = AvalistaForm
#     success_url = '/processos/processos'
#     template_name = "processoavalistas/edit_processoavalista.html"
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["title"] = 'Edita Avalista'
#         context["savebtn"] = 'Salva'
#         context["delbtn"] = 'Apaga'
#
#         avalista = get_object_or_404(Avalista, pk=self.kwargs['pk'])
#
#         processo = get_object_or_404(Processo, pk=avalista.processo_id)
#
#         context["numprocesso"] = processo.numprocesso
#         context["statusprocesso"] = processo.texto_status
#         context["flagstatus"] = processo.status
#         if processo.clientepf:
#             context["clienteprocesso"] = processo.clientepf.nome
#         else:
#             context["clienteprocesso"] = processo.clientepj.razaosocial
#
#         pessoapf = get_object_or_404(PessoaFisica, pk=avalista.avalista_id)
#         context["nome"] = pessoapf.nome
#         context["numrg"] = pessoapf.numrg
#         context["orgexpedrg"] = pessoapf.orgexpedrg
#         context["sexo"] = pessoapf.sexo
#         context["numcpf"] = pessoapf.numcpf
#         context["nomemae"] = pessoapf.nomemae
#         context["nomepai"] = pessoapf.nomepai
#         context["conjuge"] = pessoapf.conjuge
#         context["cpfconjuge"] = pessoapf.cpfconjuge
#         context["dtnascimento"] = pessoapf.dtnascimento
#         context["logradouro"] = pessoapf.logradouro
#         context["numimovel"] = pessoapf.numimovel
#         context["bairro"] = pessoapf.bairro
#         context["cep"] = pessoapf.cep
#         context["telefones"] = pessoapf.telfixo + ' | ' + pessoapf.telcelular1 + ' | ' + pessoapf.telcelular2
#         context["rendaempresa"] = pessoapf.rendaempresa
#         context["rendaliqempresa"] = pessoapf.rendaliqempresa
#         context["observacao"] = pessoapf.observacao
#
#         return context
#
#     def form_valid(self, form):
#         processo = get_object_or_404(Processo, pk=form.instance.processo_id)
#         if not processo.status == 'N':
#             processo.status = 'A'
#             processo.save()
#
#         form.instance.data_edicao = datetime.today()
#         messages.success(self.request, "Dados do avalista " + form.instance.avalista.nome + " do Processo " + processo.numprocesso + " atualizados com sucesso.")
#         return super().form_valid(form)
#
#     def form_invalid(self, form):
#         # Adds errors to Django messaging framework in the case of an invalid form and redirects to the page
#         # messages.warning(self.request, str(form.errors.as_data())[31:-5])
#         messages.warning(self.request, dict(form.errors.items()))
#         return self.render_to_response(self.get_context_data())
#
#
# # usado para excluir um registro de avalista do processo
# # ----------------------------------------------------------------
# class AvalistaDeleteView(View):
#     template_name = "processoavalistas/delete_processoavalista.html"
#
#     def get(self, request, pk):
#         processoavalista = get_object_or_404(Avalista, pk=pk)
#         return render(request, self.template_name, {'object': processoavalista})
#
#     def post(self, request, pk):
#         processoavalista = get_object_or_404(Avalista, pk=pk)
#         processoavalista.is_deleted = True
#         processoavalista.data_edicao = datetime.today()
#         processoavalista.save()
#         messages.success(request, "Avalista " + processoavalista.avalista.nome + " do Processo " + processoavalista.processo.numprocesso + " excluído com sucesso.")
#         return redirect('processos-list')
#

# # usado para listar todos os registros da tabela de Referências
# # ----------------------------------------------------------------
# class ReferenciaListView(ListView):
#     model = Referencia
#     template_name = "processoreferencias/processoreferencias_list.html"
#
#     def get_queryset(self, **kwargs):
#         qs = super().get_queryset(**kwargs).filter(is_deleted=False)
#         return qs.filter(processo_id=self.kwargs['pk'])
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         processo = get_object_or_404(Processo, pk=self.kwargs['pk'])
#         context["idprocesso"] = processo.id
#         context["numprocesso"] = processo.numprocesso
#         context["statusprocesso"] = processo.texto_status
#         if processo.clientepf:
#             context["clienteprocesso"] = processo.clientepf.nome
#         else:
#             context["clienteprocesso"] = processo.clientepj.razaosocial
#         return context
#
#
# # usado para adicionar um novo registro
# # ----------------------------------------------------------------
# class ReferenciaCreateView(SuccessMessageMixin, CreateView):
#     model = Referencia
#     form_class = ReferenciaInsertForm
#     success_url = '/processos/processos'
#     template_name = "processoreferencias/edit_processoreferencia.html"
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["title"] = 'Nova Referência'
#         context["savebtn"] = 'Adiciona'
#
#         processo = get_object_or_404(Processo, pk=self.kwargs['pk'])
#         context["numprocesso"] = processo.numprocesso
#         context["statusprocesso"] = processo.texto_status
#         context["flagstatus"] = processo.status
#         if processo.clientepf:
#             context["clienteprocesso"] = processo.clientepf.nome
#         else:
#             context["clienteprocesso"] = processo.clientepj.razaosocial
#
#         return context
#
#     def form_valid(self, form):
#         processo = get_object_or_404(Processo, pk=self.kwargs['pk'])
#         processo.status = 'R'
#         processo.save()
#
#         form.instance.processo_id = self.kwargs['pk']
#         form.instance.criado_por = self.request.user
#         form.instance.data_criacao = datetime.today()
#         form.instance.data_edicao = datetime.today()
#
#         messages.success(self.request, "Referência " + form.instance.nome + " do Processo " + processo.numprocesso + " inserida com sucesso.")
#
#         return super().form_valid(form)
#
#
# # usado para atualizar as informações de uma Referência em um Processo
# # ----------------------------------------------------------------
# class ReferenciaUpdateView(SuccessMessageMixin, UpdateView):
#     model = Referencia
#     form_class = ReferenciaUpdateForm
#     success_url = '/processos/processos'
#     template_name = "processoreferencias/edit_processoreferencia.html"
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["title"] = 'Edita Referência'
#         context["savebtn"] = 'Salva'
#         context["delbtn"] = 'Apaga'
#
#         referencia = get_object_or_404(Referencia, pk=self.kwargs['pk'])
#         processo = get_object_or_404(Processo, pk=referencia.processo_id)
#
#         context["numprocesso"] = processo.numprocesso
#         context["statusprocesso"] = processo.texto_status
#         context["flagstatus"] = processo.status
#         if processo.clientepf:
#             context["clienteprocesso"] = processo.clientepf.nome
#         else:
#             context["clienteprocesso"] = processo.clientepj.razaosocial
#
#         return context
#
#     def form_valid(self, form):
#         processo = get_object_or_404(Processo, pk=form.instance.processo_id)
#         processo.status = 'R'
#         processo.save()
#
#         form.instance.data_edicao = datetime.today()
#         messages.success(self.request, "Referência " + form.instance.nome + " do Processo " + processo.numprocesso + " atualizada com sucesso.")
#         return super().form_valid(form)
#
#
# # usado para excluir um registro de referência do processo
# # ----------------------------------------------------------------
# class ReferenciaDeleteView(View):
#     template_name = "processoreferencias/delete_processoreferencia.html"
#
#     def get(self, request, pk):
#         processoreferencia = get_object_or_404(Referencia, pk=pk)
#         return render(request, self.template_name, {'object': processoreferencia})
#
#     def post(self, request, pk):
#         processoreferencia = get_object_or_404(Referencia, pk=pk)
#         processoreferencia.is_deleted = True
#         processoreferencia.data_edicao = datetime.today()
#         processoreferencia.save()
#         messages.success(request, "Referência " + processoreferencia.nome + " do Processo " + processoreferencia.processo.numprocesso + " excluída com sucesso.")
#         return redirect('processos-list')


# usado para adicionar as parcelas na tabela de ProcessoFinanc com base no Processo/Negociação cadastrado
# -------------------------------------------------------------------------------------------------------
class ProcessoFaturaNegocCreateView(View):
    template_name = "financeiro/gera_faturaprocesso.html"       # ver ainda
    # success_message = "Parcelas do financiamento - negociação geradas com sucesso"
    error_message = "Ocorreu um erro não identificado... Contacte o Desenvovimento."

    def get(self, request, pk):
        negociacao = get_object_or_404(Negociacao, pk=pk)
        processo = get_object_or_404(Processo, pk=negociacao.processo_id)
        return render(request, self.template_name, {'object': processo})

    def post(self, request, pk):

        negociacao = get_object_or_404(Negociacao, pk=pk, is_deleted=False, is_financeiro=False)

        processo_id = negociacao.processo_id
        negociacao_id = negociacao.id
        valororiginal = negociacao.vlrtotaloriginal / negociacao.novoprazo
        valorparcela = negociacao.valorparcela
        prazo = negociacao.novoprazo
        ultvencimento = negociacao.dtprivencto

        # pega percmulta e permulta na tabela de Configurações
        percmulta = Config.objects.filter(is_deleted=False).last().multa
        percjuros = Config.objects.filter(is_deleted=False).last().juros

        # utilizar o modelo de cálculo da tabela price - vide documentação

        # realiza loop para criação dos registros na tabela Financeiro
        for i in range(prazo):
            parcela = Financeiro()
            parcela.processo_id = processo_id
            parcela.negociacao_id = negociacao_id
            parcela.numparcela = i + 1
            parcela.dtemissao = datetime.today()
            parcela.valororiginal = valororiginal

            if i == 0:
                # pega a taxa de boleto aplicada somente na primeira parcela (taxa em R$ X qtde de parcelas)
                taxaboleto = Config.objects.filter(is_deleted=False).last().taxaboleto
                parcela.valorparcela = float(valorparcela) + (float(prazo) * float(taxaboleto))
            else:
                parcela.valorparcela = valorparcela

            parcela.valormulta = 0
            parcela.percmulta = percmulta
            parcela.valorjuros = 0
            parcela.percjuros = percjuros
            parcela.valorfinal = valorparcela
            # Formato anterior de cálculo do vencimento
            # if i == 0:
            #     parcela.dtvencimento = ultvencimento
            # else:
            #     if (ultvencimento.month == 1 or ultvencimento.month == 3 or ultvencimento.month == 5
            #             or ultvencimento.month == 7 or ultvencimento.month == 8 or ultvencimento.month == 10
            #             or ultvencimento.month == 12):
            #         parcela.dtvencimento = ultvencimento + timedelta(31)
            #     elif ultvencimento.month == 2 and (ultvencimento.year % 4 == 0):
            #         parcela.dtvencimento = ultvencimento + timedelta(29)
            #     elif ultvencimento.month == 2 and (ultvencimento.year % 4 > 0):
            #         parcela.dtvencimento = ultvencimento + timedelta(28)
            #     else:
            #         parcela.dtvencimento = ultvencimento + timedelta(30)

            # Novo formato de cálculo do vencimento solicitado por Zélia
            if i == 0:
                parcela.dtvencimento = ultvencimento
                diafixo = ultvencimento.day
                ultimomes = ultvencimento.month
                ultimoano = ultvencimento.year
            else:
                novodia = diafixo
                ultimomes = ultimomes + 1
                if ultimomes > 12:
                    ultimomes = 1
                    ultimoano = ultimoano + 1
                if ultimomes == 2 and diafixo > 28:
                    if ultimoano % 4 == 0:
                        novodia = 29
                    else:
                        novodia = 28
                if (ultimomes == 4 or ultimomes == 6 or ultimomes == 9 or ultimomes == 11) and diafixo > 30:
                    novodia = 30

                parcela.dtvencimento = str(ultimoano) + '-' + str(ultimomes) + '-' + str(novodia)

            parcela.criado_por = self.request.user
            parcela.data_criacao = datetime.today()
            parcela.data_edicao = datetime.today()
            parcela.save()

        # Atualiza o registro do Processo na tabela de Processo passando o processo para o status de Negociado
        # processo = get_object_or_404(Processo, pk=pk)
        # processo.status = 'N'
        # processo.data_edicao = datetime.today()
        # processo.save()

        # Atualiza o registro da Negociação inserindo o flag de is_financeiro para verdadeiro
        negociacao.is_financeiro = True
        negociacao.data_edicao = datetime.today()
        negociacao.save()

        messages.success(self.request, "Foram geradas com sucesso as " + str(prazo) +
                         " parcelas referentes a renegociação Nº " + str(negociacao.id).zfill(6) + " do processo nº "
                         + negociacao.processo.numprocesso + ".")
        return redirect('processofaturarnegoc-list')

    def form_invalid(self, form):
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())


class ProcessoFaturadoListView(BaseProcessoListView):
    """
    Lista de processos faturados (status 'F' ou 'N').
    """
    template_name = "financeiro/processosfaturados_list.html"

    def get_queryset(self):
        """
        Filtra processos com status 'F' ou 'N'.
        """
        qs = super().get_queryset()
        return qs.filter(status__in=['F', 'N'])


class ParecerListView(ListView):
    """
    View para listar todos os pareceres associados a um processo específico.
    """

    model = Parecer
    template_name = "processopareceres/processopareceres_list.html"
    context_object_name = "pareceres"  # Nome para o objeto no template

    def get_queryset(self):
        """
        Retorna os pareceres associados ao processo, excluindo os registros marcados como excluídos.
        """
        # Obtém o ID do processo a partir da URL
        processo_id = self.kwargs.get('pk')

        # Filtra os pareceres que não estão excluídos e são do processo especificado
        return Parecer.objects.filter(processo_id=processo_id, is_deleted=False)

    def get_context_data(self, **kwargs):
        """
        Adiciona informações adicionais ao contexto, como os detalhes do processo associado.
        """
        # Obtém o contexto padrão da view
        context = super().get_context_data(**kwargs)

        # Recupera o processo associado usando o ID passado na URL
        processo = get_object_or_404(Processo, pk=self.kwargs['pk'])

        # Adiciona informações detalhadas sobre o processo ao contexto
        context.update({
            "idprocesso": processo.id,
            "numprocesso": processo.numprocesso,
            "statusprocesso": processo.status,
            "clienteprocesso": self.get_cliente_nome(processo)  # Função para determinar o nome do cliente
        })

        return context

    def get_cliente_nome(self, processo):
        """
        Retorna o nome do cliente associado ao processo.
        Se for um cliente pessoa física, retorna o nome da pessoa física,
        caso contrário, retorna a razão social da pessoa jurídica.
        """
        if processo.clientepf:
            return processo.clientepf.nome
        elif processo.clientepj:
            return processo.clientepj.razaosocial
        return "Cliente desconhecido"


class Parecer1CreateView(SuccessMessageMixin, CreateView):
    """
    View para criar um novo Parecer 1 para um processo, atualizando o status do processo
    e associando o parecer ao processo correspondente.
    """
    model = Parecer
    form_class = Parecer1Form
    template_name = "processopareceres/edit_processoparecer1.html"
    success_url = reverse_lazy('processos-list')  # Redireciona para a lista de processos após sucesso

    def get_context_data(self, **kwargs):
        """
        Adiciona informações sobre o processo ao contexto da template, como número,
        status e nome do cliente.
        """
        context = super().get_context_data(**kwargs)

        # Recupera o processo associado ao parecer com base no 'pk' da URL
        processo = self.get_processo()

        # Adiciona detalhes do processo no contexto
        context.update({
            "title": 'Novo Parecer',
            "savebtn": 'Adicionar',
            "numprocesso": processo.numprocesso,
            "statusprocesso": processo.status,
            "clienteprocesso": self.get_cliente_nome(processo)
        })

        return context

    def form_valid(self, form):
        """
        Define os dados do parecer, incluindo o processo e o usuário responsável,
        e atualiza o status do processo para '1' (Parecer 1 Fase).
        """
        # Preenche o formulário com informações adicionais antes de salvar
        form.instance.processo = self.get_processo()
        form.instance.criado_por = self.request.user
        form.instance.data_criacao = now()
        form.instance.data_edicao = now()

        # Atualiza o processo para o status de Parecer 1 Fase
        processo = form.instance.processo
        processo.status = '1'
        processo.data_edicao = now()
        processo.save()

        # Exibe uma mensagem de sucesso após salvar o parecer
        messages.success(self.request, f"Dados do 1° Parecer do processo {processo.numprocesso} inseridos com sucesso.")
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Exibe uma mensagem de erro caso o formulário seja inválido.
        """
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())

    def get_processo(self):
        """
        Recupera o processo associado ao parecer com base no 'pk' da URL.
        """
        return get_object_or_404(Processo, pk=self.kwargs['pk'])

    def get_cliente_nome(self, processo):
        """
        Retorna o nome do cliente associado ao processo. Se for pessoa física, retorna o nome;
        caso contrário, retorna a razão social da pessoa jurídica.
        """
        if processo.clientepf:
            return processo.clientepf.nome
        elif processo.clientepj:
            return processo.clientepj.razaosocial
        return "Cliente desconhecido"


class Parecer2CreateView(SuccessMessageMixin, CreateView):
    """
    View para criar um novo Parecer 2 para um processo, atualizando o status do processo
    para 'Parecer 2 Fase' ou 'Negado', caso o parecer seja marcado como negado.
    """
    model = Parecer
    form_class = Parecer2Form
    template_name = "processopareceres/edit_processoparecer2.html"
    success_url = reverse_lazy('processos-list')  # Redireciona para a lista de processos após sucesso

    def get_context_data(self, **kwargs):
        """
        Adiciona informações sobre o processo ao contexto da template, como número,
        status e nome do cliente.
        """
        context = super().get_context_data(**kwargs)

        # Recupera o processo associado ao parecer com base no 'pk' da URL
        processo = self.get_processo()

        # Adiciona detalhes do processo no contexto
        context.update({
            "title": 'Novo Parecer',
            "savebtn": 'Adicionar',
            "numprocesso": processo.numprocesso,
            "statusprocesso": processo.status,
            "clienteprocesso": self.get_cliente_nome(processo)
        })

        return context

    def form_valid(self, form):
        """
        Define os dados do parecer, incluindo o processo e o usuário responsável,
        e atualiza o status do processo para 'Parecer 2 Fase' ou 'Negado'.
        """
        # Preenche o formulário com informações adicionais antes de salvar
        form.instance.processo = self.get_processo()
        form.instance.criado_por = self.request.user
        form.instance.data_criacao = now()
        form.instance.data_edicao = now()

        # Atualiza o processo para o status de Parecer 2 Fase ou Negado, dependendo da escolha no formulário
        processo = form.instance.processo
        if form.instance.is_negado:
            processo.status = 'X'  # Status 'X' para Negado
        else:
            processo.status = '2'  # Status '2' para Parecer 2 Fase
        processo.data_edicao = now()
        processo.save()

        # Atualiza o status do veículo passando pra vendido (is_vendido = True)
        veiculo = get_object_or_404(Veiculo, pk=processo)


        # Exibe uma mensagem de sucesso após salvar o parecer
        messages.success(self.request, f"2º Parecer do processo {processo.numprocesso} inserido com sucesso.")
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Exibe uma mensagem de erro caso o formulário seja inválido.
        """
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())

    def get_processo(self):
        """
        Recupera o processo associado ao parecer com base no 'pk' da URL.
        """
        return get_object_or_404(Processo, pk=self.kwargs['pk'])

    def get_cliente_nome(self, processo):
        """
        Retorna o nome do cliente associado ao processo. Se for pessoa física, retorna o nome;
        caso contrário, retorna a razão social da pessoa jurídica.
        """
        if processo.clientepf:
            return processo.clientepf.nome
        elif processo.clientepj:
            return processo.clientepj.razaosocial
        return "Cliente desconhecido"


class Parecer1UpdateView(SuccessMessageMixin, UpdateView):
    """
    View responsável pela atualização do 1º Parecer.
    Gerencia a lógica de exibição e processamento do formulário de edição.
    """
    model = Parecer
    form_class = Parecer1Form
    template_name = "processopareceres/edit_processoparecer1.html"
    success_url = reverse_lazy("processos-list")  # Utilizando reverse_lazy para maior flexibilidade
    success_message = "Dados do 1º Parecer atualizados com sucesso."

    def get_context_data(self, **kwargs):
        """
        Adiciona dados ao contexto da página.
        Inclui título da página e rótulos para os botões.
        """
        context = super().get_context_data(**kwargs)
        context.update({
            "title": "Editar 1º Parecer",
            "savebtn": "Salvar",
        })
        return context

    def form_valid(self, form):
        """
        Atualiza o campo `data_edicao` antes de salvar o formulário.
        Exibe mensagem de sucesso e redireciona para a URL definida.
        """
        form.instance.data_edicao = now()
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Trata o caso de formulário inválido.
        Exibe mensagens de erro e renderiza novamente a página com os dados inválidos.
        """
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data(form=form))


class Parecer2UpdateView(SuccessMessageMixin, UpdateView):
    """
    View responsável pela atualização do 2º Parecer.
    Gerencia a lógica de exibição, atualização de processos e validação do formulário.
    """
    model = Parecer
    form_class = Parecer2Form
    template_name = "processopareceres/edit_processoparecer2.html"
    success_url = reverse_lazy("processos-list")  # Utilizando reverse_lazy para flexibilidade

    def get_context_data(self, **kwargs):
        """
        Adiciona dados ao contexto da página, incluindo informações do processo associado.
        """
        context = super().get_context_data(**kwargs)
        context.update({
            "title": "Editar 2º Parecer",
            "savebtn": "Salvar",
        })

        # Recupera o parecer e o processo relacionado
        parecer = get_object_or_404(Parecer, pk=self.kwargs["pk"])
        processo = get_object_or_404(Processo, pk=parecer.processo_id)

        # Adiciona dados do processo ao contexto
        context.update({
            "numprocesso": processo.numprocesso,
            "statusprocesso": processo.status,
            "clienteprocesso": (
                processo.clientepf.nome if processo.clientepf
                else processo.clientepj.razaosocial
            ),
        })

        return context

    def form_valid(self, form):
        """
        Atualiza o campo `data_edicao` e o status do processo relacionado com base no formulário.
        """
        form.instance.data_edicao = now()

        # Recupera o processo associado ao parecer
        processo = get_object_or_404(Processo, pk=form.instance.processo_id)

        # Define o status do processo com base no campo `is_negado`
        processo.status = "X" if form.instance.is_negado else "2"
        processo.data_edicao = now()
        processo.save()

        # Adiciona mensagem de sucesso
        messages.success(
            self.request,
            f"Dados do 2º Parecer do processo {processo.numprocesso} "
            f"inseridos/atualizados com sucesso."
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Trata o caso de formulário inválido, exibindo mensagens de erro.
        """
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data(form=form))


class Parecer3UpdateView(SuccessMessageMixin, UpdateView):
    """
    View responsável pela geração de parcelas do processo
    Inclui lógica para cálculo financeiro, atualização de status e validações.
    """
    model = Parecer
    form_class = Parecer3Form
    template_name = "processopareceres/edit_processoparecer3.html"
    success_url = reverse_lazy("processofaturar-list")

    def get_context_data(self, **kwargs):
        """
        Adiciona dados do processo relacionado ao contexto da página.
        """
        context = super().get_context_data(**kwargs)
        context.update({
            "title": "Gerar Parcelas do Processo",
            "savebtn": "Salvar",
        })

        # Recupera o parecer e o processo associado
        parecer = get_object_or_404(Parecer, pk=self.kwargs["pk"])
        processo = get_object_or_404(Processo, pk=parecer.processo_id)

        # Adiciona informações do processo ao contexto
        context.update({
            "numprocesso": processo.numprocesso,
            "statusprocesso": processo.status,
            "clienteprocesso": (
                processo.clientepf.nome if processo.clientepf
                else processo.clientepj.razaosocial
            ),
        })

        return context

    @transaction.atomic
    def form_valid(self, form):
        """
        Processa o formulário validado, atualiza os dados do parecer,
        calcula as parcelas financeiras e finaliza o processo.
        """
        # Atualiza campos do parecer
        parecer = self._atualizar_parecer(form)

        # Gera as parcelas financeiras do processo
        self._gerar_parcelas(parecer)

        # Atualiza o status do processo para "Finalizado"
        self._finalizar_processo(parecer.processo_id)

        messages.success(
            self.request,
            f"Foram geradas com sucesso as {parecer.prazoaprovado} parcelas "
            f"do processo nº {parecer.processo.numprocesso}."
        )

        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Trata o caso de formulário inválido, exibindo mensagens de erro.
        """
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data(form=form))

    def _atualizar_parecer(self, form):
        """
        Atualiza os campos do parecer com base nos dados do formulário.
        """
        parecer = get_object_or_404(Parecer, pk=self.kwargs["pk"])
        form.instance.is_financeiro = True
        form.instance.data_edicao = now()

        parecer.is_financeiro = form.instance.is_financeiro
        parecer.data_edicao = form.instance.data_edicao
        parecer.dtprivencto = form.instance.dtprivencto
        parecer.dtliberacao = form.instance.dtliberacao
        parecer.save()

        return parecer

    def _gerar_parcelas(self, parecer):
        """
        Calcula e cria os registros financeiros para o parecer.
        """
        processo_id = parecer.processo_id
        prazo = parecer.prazoaprovado
        valororiginal = (parecer.valorfixo_aprovado + parecer.valorgiro_aprovado) / prazo
        ultvencimento = parecer.dtprivencto

        # Configurações financeiras
        config = Config.objects.filter(is_deleted=False).last()
        percmulta = config.multa
        percjuros = config.juros

        diafixo = ultvencimento.day
        mes = ultvencimento.month
        ano = ultvencimento.year

        for i in range(prazo):
            parcela = Financeiro(
                processo_id=processo_id,
                parecer_id=parecer.id,
                numparcela=i + 1,
                dtemissao=now(),
                valororiginal=valororiginal,
                valorparcela=parecer.valorparcela,
                valormulta=0,
                percmulta=percmulta,
                valorjuros=0,
                percjuros=percjuros,
                valorfinal=parecer.valorparcela,
                criado_por=self.request.user,
                data_criacao=now(),
                data_edicao=now(),
            )

    #         # Calcula vencimento da parcela
    #         if i > 0:
    #             mes += 1
    #             if mes > 12:
    #                 mes = 1
    #                 ano += 1
    #             diafixo = self._ajustar_dia_vencimento(diafixo, mes, ano)
    #
    #         parcela.dtvencimento = ultvencimento.replace(year=ano, month=mes, day=diafixo)
    #         parcela.save()
    #
    # def _ajustar_dia_vencimento(self, dia, mes, ano):
    #     """
    #     Ajusta o dia do vencimento para meses específicos (ex: fevereiro ou meses com 30 dias).
    #     """
    #     if mes == 2:
    #         if dia > 28:
    #             return 29 if (ano % 4 == 0 and (ano % 100 != 0 or ano % 400 == 0)) else 28
    #     if mes in {4, 6, 9, 11} and dia > 30:
    #         return 30
    #     return dia

            # Novo formato de cálculo do vencimento solicitado por Zélia
            if i == 0:
                parcela.dtvencimento = ultvencimento
                diafixo = ultvencimento.day
                ultimomes = ultvencimento.month
                ultimoano = ultvencimento.year
            else:
                novodia = diafixo
                ultimomes = ultimomes + 1
                if ultimomes > 12:
                    ultimomes = 1
                    ultimoano = ultimoano + 1
                if ultimomes == 2 and diafixo > 28:
                    if ultimoano % 4 == 0:
                        novodia = 29
                    else:
                        novodia = 28
                if (ultimomes == 4 or ultimomes == 6 or ultimomes == 9 or ultimomes == 11) and diafixo > 30:
                    novodia = 30

                parcela.dtvencimento = str(ultimoano) + '-' + str(ultimomes) + '-' + str(novodia)

            parcela.criado_por = self.request.user
            parcela.data_criacao = datetime.today()
            parcela.data_edicao = datetime.today()
            parcela.save()

    def _finalizar_processo(self, processo_id):
        """
        Atualiza o processo para o status "Finalizado".
        """
        processo = get_object_or_404(Processo, pk=processo_id)
        processo.status = "F"
        processo.data_edicao = now()
        processo.save()


class ParecerDeleteView(View):
    """
    View responsável pela exclusão lógica de um parecer, com validações associadas
    a parcelas financeiras e datas do comitê.
    """
    template_name = "processopareceres/delete_processoparecer.html"

    def get(self, request, pk):
        """
        Renderiza a página de confirmação de exclusão.
        """
        parecer = get_object_or_404(Parecer, pk=pk)
        return render(request, self.template_name, {"object": parecer})

    @transaction.atomic
    def post(self, request, pk):
        """
        Executa a exclusão lógica do parecer e atualiza o status do processo associado,
        caso as validações sejam satisfeitas.
        """
        parecer = get_object_or_404(Parecer, pk=pk)

        # Valida se a exclusão é permitida
        if not self._validar_exclusao(parecer):
            return redirect("processos-list")

        try:
            # Executa exclusão lógica do parecer
            self._excluir_parecer(parecer)

            # Atualiza o status do processo associado
            self._atualizar_processo(parecer.processo_id)

            messages.success(
                self.request,
                f"Parecer do processo {parecer.processo.numprocesso} excluído com sucesso."
            )
        except Exception as e:
            messages.warning(
                self.request,
                f"Ocorreu um erro na exclusão do parecer referente ao processo "
                f"{parecer.processo.numprocesso}. Erro: {str(e)}"
            )

        return redirect("processos-list")

    def _validar_exclusao(self, parecer):
        """
        Realiza as validações necessárias para a exclusão do parecer.
        Retorna `True` se a exclusão for permitida; caso contrário, retorna `False`.
        """
        processo_id = parecer.processo_id
        data_hoje = now().date()

        # Verifica se há parcelas financeiras geradas/movimentadas
        parcelas_ativas = Financeiro.objects.filter(
            processo_id=processo_id, status__in=["N", "P"]
        ).exists()
        if parcelas_ativas:
            messages.warning(
                self.request,
                "Parecer não pode ser excluído pois há parcelas geradas/movimentadas para este processo."
            )
            return False

        # Verifica se a data do comitê impede a exclusão
        if parecer.dtcomite and data_hoje > parecer.dtcomite:
            messages.warning(
                self.request,
                "Parecer não pode ser excluído pois a data do comitê é superior ao dia atual."
            )
            return False

        return True

    def _excluir_parecer(self, parecer):
        """
        Realiza a exclusão lógica do parecer.
        """
        parecer.is_deleted = True
        parecer.data_edicao = now()
        parecer.save()

    def _atualizar_processo(self, processo_id):
        """
        Atualiza o status do processo associado ao parecer para "Andamento".
        """
        processo = get_object_or_404(Processo, pk=processo_id)
        processo.status = "A"  # Status de "Andamento"
        processo.data_edicao = now()
        processo.save()


# usado para listar todos os processos com parecer passíveis de geração do financeiro
# ------------------------------------------------------------------------------------
class ProcessoFaturarListView(FilterView):
    filterset_class = ParecerFilter
    template_name = "financeiro/processosfaturar_list.html"
    queryset = Parecer.objects.filter(is_deleted=False, is_negado=False, is_financeiro=False, processo__status='2')


class ProcessoaNegociarListView(BaseProcessoListView):
    """
    View para listar processos que poder ser negociados.
    """
    template_name = "processonegociacoes/processosanegociar_list.html"

    def get_queryset(self):
        """
        Filtra processos finalizados (status 'F' ou 'N').
        """
        queryset = super().get_queryset()
        return queryset.filter(status__in=['F','N'])


class BaseNegociacaoListView(ListView):
    """
    Classe base para listagens de negociações associadas a um processo.
    """
    model = Negociacao
    ordering = 'id'
    template_name = None

    def get_queryset(self, **kwargs):
        """
        Retorna o queryset de negociações associadas a um processo, sem registros excluídos.
        """
        return super().get_queryset(**kwargs).filter(is_deleted=False)


class ProcessoFaturarNegocListView(BaseNegociacaoListView):
    """
    View para listar negociações de processos a serem faturados com status 'N'.
    """
    template_name = "financeiro/processosfaturarnegoc_list.html"

    def get_queryset(self, **kwargs):
        """
        Filtra negociações de processos com status 'N' (não faturado).
        """
        queryset = super().get_queryset(**kwargs)
        return queryset.filter(is_financeiro=False, processo__status='N')


class ProcessoNegociacaoListView(BaseNegociacaoListView):
    """
    View para listar negociações de um processo, com filtro para tipo normal ou REFIS.
    """
    template_name = "processonegociacoes/processonegociacoes_list.html"

    def get_tipo_negociacao(self):
        """
        Recupera o valor do tipo de negociação da URL ('normal' ou 'refis').
        """
        return self.kwargs.get('tipo')

    def get_queryset(self, **kwargs):
        """
        Retorna o conjunto de negociações com base no tipo especificado na URL.
        """
        tipo = self.get_tipo_negociacao()
        queryset = super().get_queryset(**kwargs)

        if tipo == 'normal':
            queryset = queryset.filter(is_refis=False)
        else:
            queryset = queryset.filter(is_refis=True)

        return queryset.filter(processo_id=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        """
        Adiciona informações adicionais ao contexto da template, como título e dados do processo.
        """
        context = super().get_context_data(**kwargs)
        processo = get_object_or_404(Processo, pk=self.kwargs['pk'])
        tipo = self.get_tipo_negociacao()

        context["title"] = " - Normal" if tipo == 'normal' else " - REFIS"
        context["idprocesso"] = processo.id
        context["numprocesso"] = processo.numprocesso
        context["statusprocesso"] = processo.texto_status
        context["clienteprocesso"] = processo.clientepf.nome if processo.clientepf else processo.clientepj.razaosocial

        return context


# usado para adicionar um novo registro de Negociação
# ----------------------------------------------------------------
class ProcessoNegociacaoCreateView(SuccessMessageMixin, CreateView):
    model = Negociacao
    form_class = NegociacaoForm
    success_url = '/processos/processos/view1'

    def __init__(self):
        self.object = None

    def get_template_names(self):
        # Verifica o valor de 'tipo' na URL para definir o template
        tipo = self.kwargs.get('tipo')
        if tipo == 'normal':
            return ["processonegociacoes/edit_processonegociacao.html"]
        else:
            return ["processonegociacoes/edit_processonegocrefis.html"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tipo = self.kwargs.get('tipo')
        if tipo == 'normal':
            context["title"] = 'Nova Renegociação - Normal'
        else:
            context["title"] = 'Nova Renegociação - REFIS'
        context["savebtn"] = 'Adiciona'

        # Dados novos
        if self.request.POST:
            context['formset_avalistas'] = AvalistaFormSet(self.request.POST)
        else:
            context['formset_avalistas'] = AvalistaFormSet()
        # ---------------------

        processo = get_object_or_404(Processo, pk=self.kwargs['pk'])
        context["numprocesso"] = processo.numprocesso
        context["statusprocesso"] = processo.texto_status

        if processo.clientepf:
            context["clienteprocesso"] = processo.clientepf.nome
        else:
            context["clienteprocesso"] = processo.clientepj.razaosocial

        context["linhacredito"] = processo.linhacredito.nome

        # ler da tabela de configurações
        qsconfig = Config.objects.filter(is_deleted=False).last()
        juros = qsconfig.juros / 100
        multa = (qsconfig.multa / 100) + 1
        modelocalculo = qsconfig.modelocalculo_financ

        # ler da tabela de linhas de crédito os percentuais
        # juros_linha = round(((pow((1 + (float(processo.linhacredito.juros) / 100)), 1 / 12)) - 1) * 100, 4)
        juros_linha = processo.linhacredito.juros_am

        qsdebito = Financeiro.objects.filter(Q(processo_id=self.kwargs['pk']) & Q(status='A'))
        if not qsdebito:
            messages.success(self.request, "Não constam parcelas em débito a negociar... Verifique.")

        qstabrefis = TabRefis.objects.filter(is_deleted=False,linhacredito_id=processo.linhacredito_id).order_by('faixaparc_ini')

        total_debito1 = 0
        total_debito2 = 0

        lista_debito_parcelas = []
        lista_debito_valores1 = []
        lista_debito_valores2 = []
        lista_debito_datas = []

        lista_faixaparc_ini = []
        lista_faixaparc_fin = []
        lista_descjuros = []
        lista_descmulta = []
        lista_parcmin_pf = []
        lista_parcmin_pj = []

        for item in qsdebito:
            lista_debito_parcelas.append(item.numparcela)
            lista_debito_valores1.append(float(item.valororiginal))
            lista_debito_valores2.append(float(item.valorparcela))
            lista_debito_datas.append(str(item.dtvencimento))
            total_debito1 = total_debito1 + item.valororiginal
            total_debito2 = total_debito2 + item.valorparcela

        for item in qstabrefis:
            lista_faixaparc_ini.append(item.faixaparc_ini)
            lista_faixaparc_fin.append(item.faixaparc_fin)
            lista_descjuros.append(item.descjuros)
            lista_descmulta.append(item.descmulta)
            lista_parcmin_pf.append(item.parcmin_pf)
            lista_parcmin_pj.append(item.parcmin_pj)

        context["multa"] = multa
        context["juros"] = juros
        context["modelocalculo"] = modelocalculo
        context["juros_linha"] = juros_linha

        context['qsdebito'] = qsdebito
        context['total_debito1'] = total_debito1
        context['total_debito2'] = total_debito2
        context["lista_debito_parcelas"] = lista_debito_parcelas
        context["lista_debito_valores1"] = lista_debito_valores1
        context["lista_debito_valores2"] = lista_debito_valores2
        context["lista_debito_datas"] = lista_debito_datas

        context["lista_faixaparc_ini"] = lista_faixaparc_ini
        context["lista_faixaparc_fin"] = lista_faixaparc_fin
        context["lista_descjuros"] = [float(valor) for valor in lista_descjuros]
        context["lista_descmulta"] = [float(valor) for valor in lista_descmulta]
        context["lista_parcmin_pf"] = [float(valor) for valor in lista_parcmin_pf]
        context["lista_parcmin_pj"] = [float(valor) for valor in lista_parcmin_pj]

        return context

    @transaction.atomic
    def form_valid(self, form):
        context = self.get_context_data()
        form.instance.processo_id = self.kwargs['pk']
        form.instance.criado_por = self.request.user
        form.instance.data_criacao = datetime.today()
        form.instance.data_edicao = datetime.today()
        tipo = self.kwargs.get('tipo')
        if tipo == 'normal':
            form.instance.is_refis = False
        else:
            form.instance.is_refis = True
        self.object = form.save()

        # inicia aqui a gravação dos avalistas
        processo = get_object_or_404(Processo, pk=self.object.processo_id)

        formset_avalistas = context['formset_avalistas']
        if not formset_avalistas.is_valid():
            messages.success(self.request,
                             "Verificação dos avalistas não validada... Verifique.")
            pass
        else:
            formset_avalistas = AvalistaFormSet(self.request.POST, instance=processo)
            avalistas = formset_avalistas
            for avalista_form in avalistas:
                avalista = avalista_form.save(commit=False)
                avalista.negociacao_id = self.object.pk
                avalista.criado_por = self.request.user
                avalista.data_criacao = datetime.today()
                avalista.data_edicao = datetime.today()
                avalista.save()

        # Atualiza os registros do financeiro passando as parcelas negociadas para o status "N - Negociadas"
        qsdebito = Financeiro.objects.filter(Q(processo_id=self.kwargs['pk']) & Q(status='A'))
        for i in qsdebito:
            i.status = 'N'
            i.data_edicao = datetime.today()
            if i.observacao:
                i.observacao = str(i.observacao + ' (RENEGOCIAÇÃO EM ' + str(datetime.today()) + ')')[0:127]
            else:
                i.observacao = str('(RENEGOCIAÇÃO EM ' + str(datetime.today()) + ')')[0:127]
            i.save()

        # Atualiza o registro do processo alterando o status de processo finalizado (F) para processo negociado (N)
        processo = get_object_or_404(Processo, pk=self.kwargs['pk'])
        processo.status = 'N'
        processo.data_edicao = datetime.today()
        processo.save()

        messages.success(self.request, "Renegociação do processo n° " + processo.numprocesso + " registrada com sucesso.")

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())

# usado para alterar um registro de Negociação
# ----------------------------------------------------------------
class ProcessoNegociacaoUpdateView(SuccessMessageMixin, UpdateView):
    model = Negociacao
    form_class = NegociacaoForm
    success_url = '/processos/processos/view1'
    # success_message = "Dados da renegociação atualizados com sucesso"

    def get_template_names(self):
        # Verifica o valor de 'tipo' na URL para definir o template
        tipo = self.kwargs.get('tipo')
        if tipo == 'normal':
            return ["processonegociacoes/edit_processonegociacao.html"]
        else:
            return ["processonegociacoes/edit_processonegocrefis.html"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Edita Renegociação'
        tipo = self.kwargs.get('tipo')
        if tipo == 'normal':
            context["title"] = 'Nova Renegociação - Normal'
        else:
            context["title"] = 'Nova Renegociação - REFIS'
        context["savebtn"] = 'Salva'

        # Carrega o processo e as referências associadas
        # processo = self.object
        negociacao = get_object_or_404(Negociacao, pk=self.kwargs['pk'])

        processo = get_object_or_404(Processo, pk=negociacao.processo_id)

        if self.request.POST:
            context['formset_avalistas'] = AvalistaFormSet(self.request.POST, instance=processo,
                                                           queryset=Avalista.objects.filter(Q(processo=processo) &
                                                                                            Q(is_deleted=False) &
                                                                                            Q(negociacao_id=negociacao.id)))
        else:
            context['formset_avalistas'] = AvalistaFormSet(instance=processo,
                                                           queryset=Avalista.objects.filter(Q(processo=processo) &
                                                                                            Q(is_deleted=False) &
                                                                                            Q(negociacao_id=negociacao.id)))

            # qsavalistaneg = Avalista.objects.filter(processo_id=negociacao.processo_id, is_deleted=False,
            #                                         negociacao_id=negociacao.id)

        context["numprocesso"] = processo.numprocesso
        context["statusprocesso"] = processo.texto_status
        if processo.clientepf:
            context["clienteprocesso"] = processo.clientepf.nome
        else:
            context["clienteprocesso"] = processo.clientepj.razaosocial
        context["linhacredito"] = processo.linhacredito.nome

        return context

    @transaction.atomic
    def form_valid(self, form):
        context = self.get_context_data()
        form.instance.data_edicao = datetime.today()
        self.object = form.save()

        # processo = get_object_or_404(Processo, pk=self.object.processo_id)

        formset_avalistas = context['formset_avalistas']
        if formset_avalistas.is_valid():
            avalistas = formset_avalistas.save(commit=False)  # Não salva imediatamente
            # Lida com formulários marcados para exclusão
            for avalista_form in formset_avalistas.deleted_forms:
                avalista = avalista_form.instance
                avalista.is_deleted = True
                avalista.save()
            for avalista in avalistas:
                avalista.criado_por = self.request.user
                avalista.negociacao_id = form.instance.pk
                avalista.data_edicao = datetime.today()
                avalista.save()
        else:
            for error in formset_avalistas.errors:
                print(error)

        messages.success(self.request, "Dados da renegociação do processo n° " + str(form.instance.processo) + " atualizados com sucesso.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())

# usado para excluir um registro de negociação do processo
# ----------------------------------------------------------------
class ProcessoNegociacaoDeleteView(View):
    template_name = "processonegociacoes/delete_processonegociacao.html"
    # success_message = "Renegociação excluída com sucesso"

    def get(self, request, pk, tipo=None):
        negociacao = get_object_or_404(Negociacao, pk=pk)
        return render(request, self.template_name, {'object': negociacao})

    def post(self, request, pk, tipo=None):
        negociacao = get_object_or_404(Negociacao, pk=pk)
        negociacao.is_deleted = True
        negociacao.data_edicao = datetime.today()
        negociacao.save()

        # Atualiza o registro do Processo na tabela de Processo passando o processo para o status que estava antes "2"
        processo = get_object_or_404(Processo, pk=negociacao.processo_id)
        processo.status = 'F'
        processo.data_edicao = datetime.today()
        processo.save()

        # Atualiza os registros do financeiro passando as parcelas negociadas para o status de antes "A - em aberto"
        financeiro = Financeiro.objects.filter(Q(processo_id=negociacao.processo_id) & Q(status='N'))
        for i in financeiro:
            i.status = 'A'
            i.data_edicao = datetime.today()
            # if i.observacao:
            #     i.observacao = str(i.observacao) + ' (EXCLUSÃO DE RENEGOCIAÇÃO EM ' + str(datetime.today()) + ')'
            # else:
            #     i.observacao = '(EXCLUSÃO DE RENEGOCIAÇÃO EM ' + str(datetime.today()) + ')'
            i.save()

        messages.success(self.request, f"Renegociação do processo n° {processo.numprocesso} excluída com sucesso.")

        return redirect('processos-list')

# usado para listar todos os títulos passíveis de cancelamento das parcelas (somente se todos os títulos do processo
# estiverem em aberto. Caso haja movimentação não poderá ser feito
# --------------------------------------------------------------------------
# class TitulosaCancelarListView(ListView):
#     template_name = "financeiro/titulosacancelar_list.html"
#     #  Rever este processo
#     # subquery_processo_parecer_pago = Financeiro.objects.filter(is_deleted=False, status='P').values_list('processo_id')
#     # queryset = (Financeiro.objects.filter(is_deleted=False, status='A').
#     #             exclude(processo_id__in=subquery_processo_parecer_pago).
#     #             values_list('processo__numprocesso', 'processo__dtprocesso', 'parecer_id', 'parecer__valorparcela',
#     #                         'parecer__prazoaprovado', 'negociacao_id', 'negociacao__valorparcela',
#     #                         'negociacao__novoprazo', 'processo_id').distinct().order_by())

#     # Obter a refência de fechamento para impedir que título emitidos antes da referência de fechamento sejam listados
#     fechamento = Fechamento.objects.filter(is_deleted=False).last()
#     if fechamento:
#         reffechamento = fechamento.referencia
#         anofechamento = reffechamento[0:4]
#         mesfechamento = reffechamento[4:6]
#         if mesfechamento in ['01', '03', '05', '07', '08', '10', '12']:
#             dtreferencia = anofechamento + '-' + mesfechamento + '-31'
#         elif mesfechamento in ['04', '06', '09', '11']:
#             dtreferencia = anofechamento + '-' + mesfechamento + '-30'
#         else:
#             dtreferencia = anofechamento + '-' + mesfechamento + '-28'

#         queryset = (Financeiro.objects.filter(is_deleted=False, status='A', dtemissao__gt=dtreferencia).
#             values_list('processo__numprocesso', 'processo__dtprocesso', 'parecer_id', 'parecer__valorparcela',
#                             'parecer__prazoaprovado', 'negociacao_id', 'negociacao__valorparcela',
#                             'negociacao__novoprazo', 'processo_id').distinct().order_by())


class TitulosaCancelarListView(ListView):
    template_name = "financeiro/titulosacancelar_list.html"
    context_object_name = "titulos"

    def get_queryset(self):
        # Verifica se a tabela Fechamento existe antes de tentar usá-la
        if tabela_existe('tabelas_fechamento'):
            fechamento = Fechamento.objects.filter(is_deleted=False).last()
        else:
            fechamento = None

        if fechamento and fechamento.referencia:
            reffechamento = fechamento.referencia  # Ex: '202508'
            anofechamento = reffechamento[:4]
            mesfechamento = reffechamento[4:6]

            # Define o último dia do mês (sem usar calendário para simplificar)
            if mesfechamento in ['01', '03', '05', '07', '08', '10', '12']:
                dia = '31'
            elif mesfechamento in ['04', '06', '09', '11']:
                dia = '30'
            else:
                dia = '28'  # fevereiro simplificado

            dtreferencia = f"{anofechamento}-{mesfechamento}-{dia}"
        else:
            # Nenhum fechamento disponível, não filtra por dtemissao
            dtreferencia = None

        # Subquery para títulos já pagos (status='P')
        subquery_pagos = Financeiro.objects.filter(
            is_deleted=False,
            status='P'
        ).values_list('processo_id', flat=True)

        queryset = Financeiro.objects.filter(
            is_deleted=False,
            status='A'
        ).exclude(
            processo_id__in=subquery_pagos
        )

        if dtreferencia:
            queryset = queryset.filter(dtemissao__gt=dtreferencia)

        return queryset.values_list(
            'processo__numprocesso',
            'processo__dtprocesso',
            'parecer_id',
            'parecer__valorparcela',
            'parecer__prazoaprovado',
            'negociacao_id',
            'negociacao__valorparcela',
            'negociacao__novoprazo',
            'processo_id'
        ).distinct().order_by()


# usado para cancelar todos os títulos com origem num parecer (desde que não tenha havia nenhuma movimentação financeira)
# ---------------------------------------------------------------------
class ProcessoTitulosPCancelView(View):
    template_name = "financeiro/cancel_processotitulos.html"

    def get(self, request, pk):
        financeiro = Financeiro.objects.filter(parecer_id=pk, is_deleted=False, status='A')
        return render(request, self.template_name, {'object': financeiro})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        parecer = get_object_or_404(Parecer, pk=self.kwargs['pk'])
        processo = get_object_or_404(Processo, pk=parecer.processo_id)
        context["numprocesso"] = processo.numprocesso
        if processo.clientepf:
            context["clienteprocesso"] = processo.clientepf.nome
        else:
            context["clienteprocesso"] = processo.clientepj.razaosocial
        return context

    @transaction.atomic
    def post(self, request, pk):
        parecer = get_object_or_404(Parecer, pk=pk)
        parecer.dtliberacao = None
        parecer.dtprivencto = None
        parecer.is_financeiro = False
        parecer.save()

        financeiro = Financeiro.objects.filter(parecer_id=pk, is_deleted=False, status='A')
        for i in financeiro:
            i.status = 'C'
            i.is_deleted = True
            i.data_edicao = datetime.today()
            i.observacao = 'TÍTULO CANCELADO VIA CANCELAMENTO DE TÍTULOS'
            i.save()

        # Atualiza o registro do Processo na tabela de Processo passando o processo para o status que estava antes "2"
        processo = get_object_or_404(Processo, pk=parecer.processo_id)
        processo.status = '2'
        processo.data_edicao = datetime.today()
        processo.save()

        messages.success(self.request, "Cancelamento dos títulos (" + str(parecer.prazoaprovado) +
                         " parcelas) do processo " + str(processo.numprocesso) + " realizado com sucesso.")

        return redirect('titulosacancelar-list')


# usado para cancelar todos os títulos com origem numa negociação (desde que não tenha havia nenhuma movimentação financeira)
# ---------------------------------------------------------------------
class ProcessoTitulosNCancelView(View):
    template_name = "financeiro/cancel_processotitulos.html"

    def get(self, request, pk):
        financeiro = Financeiro.objects.filter(negociacao_id=pk, is_deleted=False, status='A')
        return render(request, self.template_name, {'object': financeiro})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        negociacao = get_object_or_404(Negociacao, pk=self.kwargs['pk'])
        processo = get_object_or_404(Processo, pk=negociacao.processo_id)
        context["numprocesso"] = processo.numprocesso
        if processo.clientepf:
            context["clienteprocesso"] = processo.clientepf.nome
        else:
            context["clienteprocesso"] = processo.clientepj.razaosocial
        return context

    def post(self, request, pk):
        negociacao = get_object_or_404(Negociacao, pk=pk)
        negociacao.is_financeiro = False
        negociacao.save()

        financeiro = Financeiro.objects.filter(negociacao_id=pk, is_deleted=False, status='A')
        for i in financeiro:
            i.status = 'C'
            i.is_deleted = True
            i.data_edicao = datetime.today()
            i.observacao = 'TÍTULO CANCELADO VIA CANCELAMENTO DE TÍTULOS'
            i.save()

        # # Atualiza o registro do Processo na tabela de Processo passando o processo para o status que estava antes "F"
        # processo = get_object_or_404(Processo, pk=negociacao.processo_id)
        # processo.status = 'F'
        # processo.data_edicao = datetime.today()
        # processo.save()

        messages.success(self.request, "Cancelamento dos títulos realizado com sucesso.")

        return redirect('titulosacancelar-list')


# usado para listar todas as parcelas de faturamento de um processo
# ----------------------------------------------------------------
class ExtratoFaturaListView(ListView):
    model = Financeiro
    template_name = "financeiro/extratofinanc_list.html"
    # paginate_by = 10

    def get_queryset(self, **kwargs):
        qs = super().get_queryset(**kwargs).filter(is_deleted=False).order_by('id')

        # mostratitcancelados = Config.objects.filter(is_deleted=False).last().mostratitcancelados
        if mostra_cancelados:
            return qs.filter(processo_id=self.kwargs['pk'])
        else:
            return qs.filter(Q(processo_id=self.kwargs['pk']) & ~Q(status='C'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        processo = get_object_or_404(Processo, pk=self.kwargs['pk'])
        context["processo_id"] = processo.id
        context["processo_numprocesso"] = processo.numprocesso
        context["processo_status"] = processo.status
        if processo.clientepf:
            context["processo_cliente"] = processo.clientepf
        else:
            context["processo_cliente"] = processo.clientepj

        qstotal = Financeiro.objects.filter(Q(processo_id=self.kwargs['pk']) & ~Q(status='C') & ~Q(status='N'))
        if qstotal:
            valor_total_dict = qstotal.aggregate(valortotal=Sum('valorparcela'))
            valor_total = valor_total_dict['valortotal']
        else:
            valor_total = 0

        qstotalpago = Financeiro.objects.filter(Q(processo_id=self.kwargs['pk']) & Q(status='P'))
        if qstotalpago:
            valor_pago_dict = qstotalpago.aggregate(pagototal=Sum('valorpago'))
            valor_pago = valor_pago_dict['pagototal']
        else:
            valor_pago = 0

        qstotalaberto = Financeiro.objects.filter(Q(processo_id=self.kwargs['pk']) & Q(status='A'))
        if qstotalaberto:
            valor_aberto_dict = qstotalaberto.aggregate(abertototal=Sum('valorparcela'))
            valor_aberto = valor_aberto_dict['abertototal']
        else:
            valor_aberto = 0

        context["valor_total"] = valor_total
        context["valor_pago"] = valor_pago
        context["valor_aberto"] = valor_aberto

        return context


# usado para atualizar as informações (pagamento) de uma parcela de faturamento
# -------------------------------------------------------------------------------
class ProcessoFaturadoUpdateView(SuccessMessageMixin, UpdateView):
    model = Financeiro
    form_class = FinanceiroForm
    # success_url = '/processos/financeiro/view2'
    template_name = "financeiro/edit_processofaturado.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Baixa Parcela'
        context["savebtn"] = 'Salva'
        context["delbtn"] = 'Apaga'

        financeiro = get_object_or_404(Financeiro, pk=self.kwargs['pk'])

        processo = get_object_or_404(Processo, pk=financeiro.processo_id)

        # rotina para obter o número de dias não úteis (sábados, domigos e feriados
        # fonte: https://pt.stackoverflow.com/questions/553157/pegar-n-%C3%A9simo-dia-%C3%BAtil-do-m%C3%AAs-considerando-finais-de-semana-e-feriados
        # pais = 'BR'
        # feriados = holidays.country_holidays(pais)
        #

        # rotina para leitura e montagem da lista de feriados a serem repassadas à rotina javascript para o cálculo
        # de multa e juros. Os abonos referentes aos sábados e domingos estão sendo validados dentro da rotina em
        # javascript no momento do cálculo
        qsferiado = Feriado.objects.filter(is_deleted=False).order_by('dtferiado')
        feriadosdia = []
        for i in qsferiado:
            feriadosdia.append(str(i.dtferiado))

        context["numprocesso"] = processo.numprocesso
        context["statusprocesso"] = processo.status
        if processo.clientepf:
            context["clienteprocesso"] = processo.clientepf.nome
        else:
            context["clienteprocesso"] = processo.clientepj.razaosocial
        context["feriadosdia"] = feriadosdia

        return context

    def form_valid(self, form):
        form.instance.data_edicao = datetime.today()
        form.instance.status = 'P'
        messages.success(self.request, "Parcela número " + str(form.instance.numparcela) + " no valor de " +
                         str(form.instance.valorparcela) + " e vencimento " + str(form.instance.dtvencimento) +
                         " baixada com sucesso.")
        return super().form_valid(form)

    def get_success_url(self):
        # Redireciona para a página de edição do processo recém-criado
        return reverse('extratofatura-list', kwargs={'pk': self.object.processo_id})

    def form_invalid(self, form):
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())


# usado para cancelar uma parcela de faturamento
# ----------------------------------------------------------------
class ProcessoFaturadoCancelView(View):
    template_name = "financeiro/cancel_processofaturado.html"
    # success_message = "Parcela cancelada com sucesso"

    def get(self, request, pk):
        financeiro = get_object_or_404(Financeiro, pk=pk)
        return render(request, self.template_name, {'object': financeiro})

    def post(self, request, pk):
        financeiro = get_object_or_404(Financeiro, pk=pk)
        # processofinanc.is_deleted = True
        financeiro.status = 'C'
        financeiro.data_edicao = datetime.today()
        financeiro.save()
        # messages.success(request, self.success_message)
        messages.success(self.request, "Parcela número " + str(financeiro.numparcela) + " no valor de " +
                         str(financeiro.valorparcela) + " e vencimento " + str(financeiro.dtvencimento) +
                         " cancelada com sucesso.")
        # return redirect('processofaturado-list')
        return redirect(reverse('extratofatura-list', kwargs={'pk': financeiro.processo_id}))


# usado para cancelar uma parcela de faturamento
# ------------------------------------------------------------------------------------
class ProcessoFaturadoEstornView(View):
    template_name = "financeiro/estorn_processofaturado.html"
    # success_message = "Parcela estornada com sucesso"

    def get(self, request, pk):
        financeiro = get_object_or_404(Financeiro, pk=pk)
        return render(request, self.template_name, {'object': financeiro})

    def post(self, request, pk):
        financeiro = get_object_or_404(Financeiro, pk=pk)
        # processofinanc.is_deleted = True
        financeiro.status = 'A'
        financeiro.dtpagamento = None
        financeiro.valoracresc = 0
        financeiro.valordesc = 0
        financeiro.valorpago = 0
        financeiro.data_edicao = datetime.today()
        financeiro.save()
        messages.success(self.request, "Parcela número " + str(financeiro.numparcela) + " no valor de " +
                         str(financeiro.valorparcela) + " e vencimento " + str(financeiro.dtvencimento) +
                         " estornada com sucesso.")
        return redirect(reverse('extratofatura-list', kwargs={'pk': financeiro.processo_id}))
        # return redirect('processofaturado-list')


class ProcessoMovListView(BaseProcessoListView):
    """
    Lista processos que podem ser movimentados por um operador.
    """
    template_name = "processomovimentacoes/processosamovimentar_list.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        operador = get_object_or_404(Operador, user_id=self.request.user.id)
        qsopelocal = Operador_Local.objects.filter(is_deleted=False, operador_id=operador.id)
        return queryset.filter(localizacao__in=qsopelocal.values('localizacao'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titlerel"] = ""  # Ajuste o valor de acordo com a necessidade
        return context


# usado para listar todos os registros de movimentação de um processo
# ----------------------------------------------------------------------
class ProcessoMovimentacoesListView(ListView):
    model = Movimentacao
    template_name = "processomovimentacoes/processomovimentacoes_list.html"

    def get_queryset(self, **kwargs):
        qs = super().get_queryset(**kwargs).filter(is_deleted=False).order_by('-dtmovimento')
        return qs.filter(processo_id=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        processo = get_object_or_404(Processo, pk=self.kwargs['pk'])
        context["idprocesso"] = processo.id
        context["numprocesso"] = processo.numprocesso
        context["statusprocesso"] = processo.texto_status
        if processo.clientepf:
            context["clienteprocesso"] = processo.clientepf.nome
        else:
            context["clienteprocesso"] = processo.clientepj.razaosocial
        context["localizacao"] = processo.localizacao
        return context

# usado para adicionar um novo registro
# ----------------------------------------------------------------
class MovimentacaoCreateView(SuccessMessageMixin, CreateView):
    model = Movimentacao
    form_class = MovimentacaoForm
    success_url = '/processos/processos/movlist'
    template_name = "processomovimentacoes/edit_processomovimentacao.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Nova Movimentação'
        context["savebtn"] = 'Adiciona'

        processo = get_object_or_404(Processo, pk=self.kwargs['pk'])
        context["numprocesso"] = processo.numprocesso
        context["statusprocesso"] = processo.texto_status
        context["flagstatus"] = processo.status
        if processo.clientepf:
            context["clienteprocesso"] = processo.clientepf.nome
        else:
            context["clienteprocesso"] = processo.clientepj.razaosocial
        context["localizacao"] = processo.localizacao

        return context

    def form_valid(self, form):
        with transaction.atomic():
            # Busca o processo associado ou retorna 404
            processo = get_object_or_404(Processo, pk=self.kwargs['pk'])

            # Atualiza os campos do formulário com valores necessários
            form.instance.processo_id = self.kwargs['pk']
            form.instance.criado_por = self.request.user
            form.instance.data_criacao = datetime.now()
            form.instance.data_edicao = datetime.now()
            form.instance.origem = processo.localizacao

            # Salva o formulário
            response = super().form_valid(form)

            # Busca a última movimentação não deletada
            ultimalocalizacao = Movimentacao.objects.filter(is_deleted=False, processo_id=self.kwargs['pk']
                                                            ).last().destino

            # Atualiza a localização do processo
            processo.localizacao = ultimalocalizacao or form.instance.destino
            processo.save()

            messages.success(self.request, f"Movimentação {form.instance.origem} -> {form.instance.destino} do Processo"
                                           f" {processo.numprocesso} inserida com sucesso.")
        return response


# usado para atualizar as informações de uma Referência em um Processo
# ----------------------------------------------------------------
class MovimentacaoUpdateView(View):
    template_name = "processomovimentacoes/edit_processomovimentacao.html"

    def get(self, request, pk):
        processomovimentacao = get_object_or_404(Movimentacao, pk=pk)
        return render(request, self.template_name, {'object': processomovimentacao})

    def post(self, request, pk):
        # Marca a movimentação como recebida
        processomovimentacao = get_object_or_404(Movimentacao, pk=pk)
        processomovimentacao.is_recebido = True
        processomovimentacao.data_edicao = now()
        processomovimentacao.save()

        messages.success(self.request, f"Movimentação {processomovimentacao.origem} -> {processomovimentacao.destino}"
                                       f" do Processo {processomovimentacao.processo.numprocesso} recebida com sucesso.")
        return redirect('processomovimentacoes-list', processomovimentacao.processo_id)


# ----------------------------------------------------------------
class MovimentacaoDeleteView(View):
    template_name = "processomovimentacoes/delete_processomovimentacao.html"

    def get(self, request, pk):
        processomovimentacao = get_object_or_404(Movimentacao, pk=pk)
        return render(request, self.template_name, {'object': processomovimentacao})

    def post(self, request, pk):
        with transaction.atomic():
            # Marca a movimentação como deletada
            processomovimentacao = get_object_or_404(Movimentacao, pk=pk)
            processomovimentacao.is_deleted = True
            processomovimentacao.data_edicao = now()
            processomovimentacao.save()

            # Busca a última movimentação não deletada
            ultimalocalizacao = Movimentacao.objects.filter(is_deleted=False, processo_id=processomovimentacao.processo_id
                                                            ).last().destino

            # Busca o processo associado ou retorna 404
            processo = get_object_or_404(Processo, pk=processomovimentacao.processo_id)

            # Atualiza a localização do processo
            processo.localizacao = ultimalocalizacao or processomovimentacao.destino
            processo.save()

            messages.success(self.request, f"Movimentação {processomovimentacao.origem} -> {processomovimentacao.destino}"
                                           f" do Processo {processo.numprocesso} excluída com sucesso.")
        return redirect('processomovimentacoes-list', processomovimentacao.processo_id)


# usado para passar o status do registro de movimentação como recebido pelo setor
# ----------------------------------------------------------------
class MovimentacaoCheckView(View):
    template_name = "processomovimentacoes/check_processomovimentacao.html"

    def get(self, request, pk):
        processomovimentacao = get_object_or_404(Movimentacao, pk=pk)
        return render(request, self.template_name, {'object': processomovimentacao})

    def post(self, request, pk):
        with transaction.atomic():
            # Marca a movimentação como deletada
            processomovimentacao = get_object_or_404(Movimentacao, pk=pk)
            processomovimentacao.is_recebido = True
            processomovimentacao.data_edicao = now()
            processomovimentacao.save()

            # Busca a última movimentação não deletada
            ultimalocalizacao = Movimentacao.objects.filter(is_deleted=False, processo_id=processomovimentacao.processo_id
                                                            ).last().destino

            # Busca o processo associado ou retorna 404
            processo = get_object_or_404(Processo, pk=processomovimentacao.processo_id)

            # Atualiza a localização do processo
            processo.localizacao = ultimalocalizacao or processomovimentacao.destino
            processo.save()

            messages.success(self.request, f"Movimentação {processomovimentacao.origem} -> {processomovimentacao.destino}"
                                           f" do Processo {processo.numprocesso} recebida com sucesso.")
        return redirect('processomovimentacoes-list', processomovimentacao.processo_id)


class ComiteListView(ListView):
    """
    Lista todos os comitês, excluindo registros marcados como deletados.
    """
    template_name = "comites/comites_list.html"

    def get_queryset(self):
        queryset = Comite.objects.filter(is_deleted=False) if not mostra_excluidos else Comite.objects.all()
        return queryset
        # return queryset.values_list(
        #     'id', 'dtcomite', 'observacao', 'is_realizado', 'is_deleted'
        # )


class ComiteCreateView(SuccessMessageMixin, CreateView):
    """
    Cria um novo registro de Comitê.
    """
    model = Comite
    form_class = ComiteForm
    success_url = '/processos/comites'
    template_name = "comites/edit_comite.html"

    def get_context_data(self, **kwargs):
        """
        Insere informações adicionais no contexto.
        """
        context = super().get_context_data(**kwargs)
        context.update({
            "title": "Novo Comitê",
            "savebtn": "Adiciona",
            "formset_comiteprocessos": self._initialize_formset_processos(),
            "formset_comitemembros": self._initialize_formset_membros(),
        })
        return context

    def form_valid(self, form):
        """
        Processa a criação da Comitê, seus processos e membros do comitê.
        """
        form.instance.criado_por = self.request.user
        form.instance.data_criacao = now()
        form.instance.data_edicao = now()
        self.object = form.save()

        if not self._process_formset():
            return self.form_invalid(form)

        messages.success(
            self.request,
            f"Dados do comitê na data {form.instance.dtcomite} inseridos com sucesso."
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Exibe mensagens de erro quando o formulário principal é inválido.
        """
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())

    def _initialize_formset_processos(self):
        """
        Inicializa o formset de processos do comitê com ou sem dados POST.
        """
        if self.request.POST:
            return ComiteProcessoFormSet(self.request.POST)
        return ComiteProcessoFormSet()

    def _initialize_formset_membros(self):
        """
        Inicializa o formset de membros do comitê com ou sem dados POST.
        """
        if self.request.POST:
            return ComiteMembroFormSet(self.request.POST)
        return ComiteMembroFormSet()

    def _process_formset(self):
        """
        Processa o formset de processos do comitê e membros do comitê para validar e salvar.
        Retorna `False` se o formset for inválido, caso contrário, `True`.
        """
        formsetProcesso = ComiteProcessoFormSet(self.request.POST, instance=self.object)
        if not formsetProcesso.is_valid():
            return False

        for form in formsetProcesso:
            if form.cleaned_data:  # Ignora formulários vazios
                processoscomite = form.save(commit=False)
                processoscomite.criado_por = self.request.user
                processoscomite.data_criacao = now()
                processoscomite.data_edicao = now()
                processoscomite.save()

        formsetMembro = ComiteMembroFormSet(self.request.POST, instance=self.object)
        if not formsetMembro.is_valid():
            return False

        for form in formsetMembro:
            if form.cleaned_data:  # Ignora formulários vazios
                membroscomite = form.save(commit=False)
                membroscomite.criado_por = self.request.user
                membroscomite.data_criacao = now()
                membroscomite.data_edicao = now()
                membroscomite.save()

        return True


class ComiteUpdateView(SuccessMessageMixin, UpdateView):
    """
    Atualiza um registro existente de Comitê.
    """
    model = Comite
    form_class = ComiteForm
    success_url = '/processos/comites'
    template_name = "comites/edit_comite.html"

    def get_context_data(self, **kwargs):
        """
        Insere informações adicionais no contexto.
        """
        context = super().get_context_data(**kwargs)
        context.update({
            "title": "Edita Comitê",
            "savebtn": "Salva",
            "delbtn": "Apaga",
            "formset_comiteprocessos": self._initialize_formset_processos(),
            "formset_comitemembros": self._initialize_formset_membros(),
        })
        return context

    def form_valid(self, form):
        """
        Processa a atualização do Comitê, os processos e membros.
        """
        context = self.get_context_data()
        form.instance.data_edicao = now()
        self.object = form.save()

        if not self._process_formset(context["formset_comiteprocessos"]):
            return self.form_invalid(form)

        if not self._process_formset(context["formset_comitemembros"]):
            return self.form_invalid(form)

        messages.success(
            self.request,
            f"Dados do comitê na data {form.instance.dtcomite} atualizados com sucesso."
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Exibe mensagens de erro quando o formulário principal é inválido.
        """
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())

    def _initialize_formset_processos(self):
        """
        Inicializa o formset de processos do comitê com ou sem dados POST.
        """
        comite = self.object
        queryset = ProcessosComite.objects.filter(
            comite=comite, is_deleted=False
        )
        if self.request.POST:
            return ComiteProcessoFormSet(self.request.POST, instance=comite, queryset=queryset)
        return ComiteProcessoFormSet(instance=comite, queryset=queryset)

    def _initialize_formset_membros(self):
        """
        Inicializa o formset de membros do comitê com ou sem dados POST.
        """
        comite = self.object
        queryset = MembrosComite.objects.filter(
            comite=comite, is_deleted=False
        )
        if self.request.POST:
            return ComiteMembroFormSet(self.request.POST, instance=comite, queryset=queryset)
        return ComiteMembroFormSet(instance=comite, queryset=queryset)

    def _process_formset(self, formset):
        """
        Processa o formset de processos do comitê e seus membros, incluindo exclusões e atualizações.
        Retorna `False` se o formset for inválido, caso contrário, `True`.
        """
        if not formset.is_valid():
            return False

        for processo_form in formset.deleted_forms:
            processo = processo_form.instance
            processo.is_deleted = True
            processo.save()

        for processo in formset.save(commit=False):
            processo.comite = self.object
            processo.criado_por = self.request.user
            processo.save()

        return True


# usado para excluir um registro de comitê cadastrado
# ----------------------------------------------------------------
class ComiteDeleteView(View):
    template_name = "comites/delete_comite.html"

    def get(self, request, pk):
        comite = get_object_or_404(Comite, pk=pk)
        return render(request, self.template_name, {'object': comite})

    def post(self, request, pk):
        with transaction.atomic():
            # Marca o comitê como deletado
            comite = get_object_or_404(Comite, pk=pk)
            comite.is_deleted = True
            comite.data_edicao = now()
            comite.save()

            # Marca os processos deste mesmo comitê como deletados (FAZER AINDA)
            # ultimalocalizacao = Movimentacao.objects.filter(is_deleted=False, processo_id=processomovimentacao.processo_id
            #                                                 ).last().destino
            #
            # # Busca o processo associado ou retorna 404
            # processo = get_object_or_404(Processo, pk=processomovimentacao.processo_id)
            #
            # # Atualiza a localização do processo
            # processo.localizacao = ultimalocalizacao or processomovimentacao.destino
            # processo.save()

            messages.success(self.request, f"Comitê do dia {comite.dtcomite} excluído com sucesso.")
        return redirect('comites-list')


# ROTINAS DE IMPRESSÃO
# usado para imprimir a ficha do cliente
# ----------------------------------------------------------------
def fichaclientelist(self, pk):
    qsprocesso = Processo.objects.filter(pk=pk)
    qsreferencia = Referencia.objects.filter(processo_id=pk, is_deleted=False)
    logos = get_logo_images()
    for i in qsprocesso:
        if i.clientepf:
            template_name = "processos/print_fichaclientepf.html"
        else:
            template_name = "processos/print_fichaclientepj.html"
        pass

    return render_to_pdf(
        template_name,
            {
            "processo": qsprocesso,
            "referencias": qsreferencia,
            "user": self.user,
            "emissao": datetime.today(),
            "linhalogo1": logos["linhalogo1"],
            "linhalogo2": logos["linhalogo2"],
            "linhalogo3": logos["linhalogo3"],
            },
    )

# usado para imprimir a ficha do avalista
# ----------------------------------------------------------------
def fichaavalistalist(self, pk):
    template_name = "processos/print_fichaavalista.html"
    qsavalista = Avalista.objects.filter(processo_id=pk, is_deleted=False, negociacao_id=None)
    qsreferencia = Referencia.objects.filter(processo_id=pk, is_deleted=False)
    logos = get_logo_images()

    return render_to_pdf(
        template_name,
            {
            "avalistas": qsavalista,
            "referencias": qsreferencia,
            "user": self.user,
            "emissao": datetime.today(),
            "linhalogo1": logos["linhalogo1"],
            "linhalogo2": logos["linhalogo2"],
            "linhalogo3": logos["linhalogo3"],
            },
    )

# usado para imprimir o contrato do proceso
def contratolist(request, pk):

    try:
        # def taxa_equivalente(taxa_p):
        #     result = round(((pow((1 + (taxa_p / 100)), 1/12)) - 1) * 100, 4)
        #     return result

        logos = get_logo_images()

        processo = get_object_or_404(Processo, pk=pk, is_deleted=False)
        linhacredito = get_object_or_404(LinhaCredito, pk=processo.linhacredito_id)

        template_name = "processos/print_contrato.html"

        if linhacredito.modelo == '1':
            template_name = "processos/print_contrato1.html"
        elif linhacredito.modelo == '2':
                template_name = "processos/print_contrato2.html"

        qsavalista = Avalista.objects.filter(processo_id=pk, is_deleted=False, negociacao_id=None)

        qssocio = PJuridicaSocio.objects.filter(pessoajuridica_id=processo.empresa_id)

        qsconfig = Config.objects.filter(is_deleted=False).last()

        parecer = get_object_or_404(Parecer, processo_id=pk, is_deleted=False)

        processoscomite = ProcessosComite.objects.filter(processo_id=pk, is_deleted=False, is_aprovado=True).first()

        if not processoscomite:
            messages.warning(request, f"Aviso: Processo não consta de nenhum comitê ou ainda não foi aprovado... Verifique.")
            return redirect("processos-list")  # Redirecione para alguma página apropriada
        else:
            if not processoscomite.comite.is_realizado:
                messages.warning(request, f"Aviso: Comitê referente ao processo ainda não realizado... Verifique.")
                return redirect("processos-list")  # Redirecione para alguma página apropriada

        valorfixo_aprovado = parecer.valorfixo_aprovado
        valorgiro_aprovado = parecer.valorgiro_aprovado
        valortotal_aprovado = parecer.valorfixo_aprovado + parecer.valorgiro_aprovado
        valorparcela = parecer.valorparcela
        taxajuros = linhacredito.juros_aa
        taxaequivalente = linhacredito.juros_am
        valorfixo_extenso = valor_por_extenso(str(valorfixo_aprovado).replace('.', ','))
        valorgiro_extenso = valor_por_extenso(str(valorgiro_aprovado).replace('.', ','))
        valortotal_extenso = valor_por_extenso(str(valortotal_aprovado).replace('.', ','))
        parcelaextenso = valor_por_extenso(str(valorparcela).replace('.', ','))
        prazoaprovado = parecer.prazoaprovado
        prazoextenso = num2words(prazoaprovado, lang='pt_BR')

        return render_to_pdf(
            template_name,
            {
                "processo": processo,
                "avalistas": qsavalista,
                "socios": qssocio,
                "parametro": qsconfig,
                "valorfixo_aprovado": valorfixo_aprovado,
                "valorgiro_aprovado": valorgiro_aprovado,
                "valortotal_aprovado": valortotal_aprovado,
                "valorfixo_extenso": valorfixo_extenso,
                "valorgiro_extenso": valorgiro_extenso,
                "valortotal_extenso": valortotal_extenso,
                "valorparcela": valorparcela,
                "parcelaextenso": parcelaextenso,
                "prazoaprovado": prazoaprovado,
                "prazoextenso": prazoextenso,
                "taxajuros": taxajuros,
                "taxaequivalente": taxaequivalente,
                # "user": request.user,
                "emissao": datetime.today(),
                "linhalogo1": logos["linhalogo1"],
                "linhalogo2": logos["linhalogo2"],
                "linhalogo3": logos["linhalogo3"],
            },
        )

    # except Exception as e:
    #     # Handle exceptions, and the transaction will be rolled back automatically
    #     messages.warning(self.request, f"Ocorreu o erro {e} na impressão do contrato. Verifique junto ao setor de "
    #                                    f"Desenvolvimento do CIDAC.")
    except Exception as e:
        messages.warning(request, f"Ocorreu o erro {e} na impressão do contrato... Verifique junto ao setor de "
                                  f"Desenvolvimento.")
        return redirect("processos-list")  # Redirecione para alguma página apropriada

# usado para imprimir a autorização
def autorizacaolist(request, pk):

    try:
        logos = get_logo_images()

        processo = get_object_or_404(Processo, pk=pk, is_deleted=False)

        texto = (processo.numprocesso + str(processo.dtprocesso) + processo.clientepf.nome + processo.numprotocolo
                 + processo.empresa.razaosocial)
        hash_obj = hashlib.sha256(texto.encode())
        hash_hex = hash_obj.hexdigest()

        template_name = "processos/print_autorizacao.html"

        parecer = get_object_or_404(Parecer, processo_id=pk, is_deleted=False)

        valortotal_aprovado = parecer.valorfixo_aprovado + parecer.valorgiro_aprovado
        valortotal_extenso = valor_por_extenso(str(valortotal_aprovado).replace('.', ','))

        processoscomite = ProcessosComite.objects.filter(processo_id=pk, is_deleted=False, is_aprovado=True).first()

        if not processoscomite:
            messages.warning(request, f"Aviso: Processo não consta de nenhum comitê ou ainda não foi aprovado... Verifique.")
            return redirect("processos-list")  # Redirecione para alguma página apropriada
        else:
            if not processoscomite.comite.is_realizado:
                messages.warning(request, f"Aviso: Comitê referente ao processo ainda não realizado... Verifique.")
                return redirect("processos-list")  # Redirecione para alguma página apropriada
            else:
                numreuniao = processoscomite.comite.numreuniao
                dtcomite = processoscomite.comite.dtcomite

        return render_to_pdf(
            template_name,
            {
                "processo": processo,
                "valortotal_aprovado": valortotal_aprovado,
                "valortotal_extenso": valortotal_extenso,
                "texto_hash": hash_hex,
                "numreuniao": numreuniao,
                "dtcomite": dtcomite,
                # "user": request.user,
                "emissao": datetime.today(),
                "linhalogo1": logos["linhalogo1"],
                "linhalogo2": logos["linhalogo2"],
                "linhalogo3": logos["linhalogo3"],
            },
        )

    except Exception as e:
        messages.warning(request, f"Ocorreu o erro {e} na impressão da autorização... Verifique junto ao setor de "
                                  f"Desenvolvimento.")
        return redirect("processos-list")  # Redirecione para alguma página apropriada

def parecerlist(self, pk):
    def calcula_idade(datarefer):
        hoje = date.today()
        idade = hoje.year - datarefer.year - ((hoje.month, hoje.day) < (datarefer.month, datarefer.day))
        return idade

    template_name = "processos/print_parecer.html"

    linhalogo1 = Config.objects.filter(is_deleted=False).last().linhalogo1
    linhalogo2 = Config.objects.filter(is_deleted=False).last().linhalogo2
    linhalogo3 = Config.objects.filter(is_deleted=False).last().linhalogo3

    parecer = get_object_or_404(Parecer, processo_id=pk, is_deleted=False)
    if parecer.processo.clientepf:
        idadecliente = calcula_idade(parecer.processo.clientepf.dtnascimento)
    else:
        idadecliente = calcula_idade(parecer.processo.clientepj.dtiniatividade)

    testemunha1 = Config.objects.filter(is_deleted=False, exercicio=parecer.processo.dtprocesso.year).last().testemunha1
    if testemunha1:
        gerentecredito = testemunha1

    return render_to_pdf(
        template_name,
        {
            "parecer": parecer,
            "idadecliente": idadecliente,
            "gerentecredito": gerentecredito,
            "user": self.user,
            "emissao": datetime.today(),
            "linhalogo1": linhalogo1,
            "linhalogo2": linhalogo2,
            "linhalogo3": linhalogo3,
        },
    )


# usado para imprimir a ficha financeira/parcelas de um processo
# ----------------------------------------------------------------
def extratofaturalist(self, pk):
    template_name = "financeiro/print_extratofatura.html"
    qsprocesso = Processo.objects.filter(pk=pk)
    qsparecer = Parecer.objects.filter(Q(processo_id=pk) & Q(is_deleted=False))
    qsfinanceiro = Financeiro.objects.filter(Q(processo_id=pk) & ~Q(status='C') & ~Q(status='N')).order_by('id')
    qsnegociacao = Negociacao.objects.filter(Q(processo_id=pk) & Q(is_deleted=False))

    linhalogo1 = Config.objects.filter(is_deleted=False).last().linhalogo1
    linhalogo2 = Config.objects.filter(is_deleted=False).last().linhalogo2
    linhalogo3 = Config.objects.filter(is_deleted=False).last().linhalogo3

    if qsfinanceiro:
        valor_total_dict = qsfinanceiro.aggregate(valortotal=Sum('valorparcela'))
        valor_total = valor_total_dict['valortotal']
    else:
        valor_total = 0

    if qsnegociacao:
        valor_totaloriginal_dict = qsnegociacao.aggregate(vlrtotaloriginal=Sum('vlrtotaloriginal'))
        valor_totaloriginal = valor_totaloriginal_dict['vlrtotaloriginal']
        valor_totaldebito_dict = qsnegociacao.aggregate(valordebito=Sum('valordebito'))
        valor_totaldebito = valor_totaldebito_dict['valordebito']
    else:
        valor_totaloriginal = 0
        valor_totaldebito = 0

    qstotalpago = Financeiro.objects.filter(Q(processo_id=pk) & Q(status='P'))
    if qstotalpago:
        valor_pago_dict = qstotalpago.aggregate(pagototal=Sum('valorpago'))
        total_pago = valor_pago_dict['pagototal']
    else:
        total_pago = 0

    qstotalaberto = Financeiro.objects.filter(Q(processo_id=pk) & Q(status='A'))
    if qstotalaberto:
        valor_aberto_dict = qstotalaberto.aggregate(abertototal=Sum('valorparcela'))
        total_aberto = valor_aberto_dict['abertototal']
    else:
        total_aberto = 0

    return render_to_pdf(
        template_name,
        {
            "processo": qsprocesso,
            "parecer": qsparecer,
            "financeiro": qsfinanceiro,
            "vlrtotaloriginal": valor_totaloriginal,
            "valordebito": valor_totaldebito,
            "totalparcelas": valor_total,
            "totalpago": total_pago,
            "totalaberto": total_aberto,
            "user": self.user,
            "emissao": datetime.today(),
            "linhalogo1": linhalogo1,
            "linhalogo2": linhalogo2,
            "linhalogo3": linhalogo3,
        },
    )


# usado para imprimir o aditivo contratual de uma renegociação
def aditivocontratolist(self, pk, tipo=None):

    # def taxa_equivalente(taxa_p):
    #     result = round(((pow((1 + (taxa_p / 100)), 1/12)) - 1) * 100, 4)
    #     return result

    template_name = "processonegociacoes/print_aditivocontrato.html"

    linhalogo1 = Config.objects.filter(is_deleted=False).last().linhalogo1
    linhalogo2 = Config.objects.filter(is_deleted=False).last().linhalogo2
    linhalogo3 = Config.objects.filter(is_deleted=False).last().linhalogo3

    qsconfig = Config.objects.filter(is_deleted=False).last()
    negociacao = get_object_or_404(Negociacao, pk=pk)

    # # busca os avalistas originais
    # qsavalista = Avalista.objects.filter(processo_id=negociacao.processo_id, is_deleted=False, negociacao_id=None)

    # Busca os sócios quando o cliente for PJ
    if negociacao.processo.clientepj:
        qssocio = PJuridicaSocio.objects.filter(pessoajuridica_id=negociacao.processo.clientepj, is_deleted=False)
    else:
        qssocio = PJuridicaSocio.objects.none()

    # busca os avalistas que foram inseridos na negociacao
    qsavalistaneg = Avalista.objects.filter(processo_id=negociacao.processo_id, is_deleted=False, negociacao_id=negociacao.id)

    qsfinanceiro = Financeiro.objects.filter(negociacao_id=negociacao.id, is_deleted=False).exclude(status='C').order_by('numparcela')
    if qsfinanceiro:
        primeiroregistro = True
        valordivida = Decimal(0.00)
        for parcela in qsfinanceiro:
            valordivida = valordivida + Decimal(parcela.valorparcela)
            if primeiroregistro:
                primeiroregistro = False
                primeiraparcela = parcela.valorparcela
                primeiraparcela_extenso = valor_por_extenso(str(parcela.valorparcela).replace('.', ','))

        ultimaparcela = parcela.valorparcela
        ultimaparcela_extenso = valor_por_extenso(str(ultimaparcela).replace('.', ','))
        valordivida_extenso = valor_por_extenso(str(valordivida).replace('.', ','))
        ultimovencimento = parcela.dtvencimento

        return render_to_pdf(
            template_name,
            {
                "negociacao": negociacao,
                "socios": qssocio,
                "avalistasneg": qsavalistaneg,
                "parametro": qsconfig,
                "valordivida": valordivida,
                "valordivida_extenso": valordivida_extenso,
                "primeiraparcela": primeiraparcela,
                "primeiraparcela_extenso": primeiraparcela_extenso,
                "ultimaparcela": ultimaparcela,
                "ultimaparcela_extenso": ultimaparcela_extenso,
                "ultimovencimento": ultimovencimento,
                "emissao": datetime.today(),
                "linhalogo1": linhalogo1,
                "linhalogo2": linhalogo2,
                "linhalogo3": linhalogo3,
            },
        )
    else:
        return HttpResponseRedirect(
            f"{reverse('processoanegociar-list')}?error_message=Financeiro não foi gerado. Favor concluir o processo de geração das parcelas.")

# usado para imprimir as atas do comitê de crédito
def atacomitelist(request, pk):
    template_name = "comites/print_atacomite.html"

    linhalogo1 = Config.objects.filter(is_deleted=False).last().linhalogo1
    linhalogo2 = Config.objects.filter(is_deleted=False).last().linhalogo2
    linhalogo3 = Config.objects.filter(is_deleted=False).last().linhalogo3

    comite = get_object_or_404(Comite, pk=pk, is_deleted=False)
    if comite:
        datacomite = comite.dtcomite
        numreuniao = comite.numreuniao
    else:
        datacomite = None
        numreuniao = None

    # Query para buscar os registros de Membros do Comitê
    membroscomite = MembrosComite.objects.filter(is_deleted=False, comite_id=pk)

    # Subquery para buscar os IDs de processos em ProcessosComite
    processos_ids = (ProcessosComite.objects.filter(is_deleted=False, is_aprovado=True, comite_id=pk)
                     .values_list('processo_id', flat=True))

    # Query para buscar os sócios das empresas
    responsaveisempresa = PJuridicaSocio.objects.filter(is_deleted=False)

    # Query principal para buscar os registros de Parecer cujo processo_id está na subquery
    parecerescomite = Parecer.objects.filter(processo_id__in=processos_ids, is_deleted=False)

    # Query para buscar os totais de processos aprovados e seus valores
    if parecerescomite:
        totais_dict = parecerescomite.aggregate(total_aprovado=Sum(F("valorfixo_aprovado") + F("valorgiro_aprovado")),
                                                qtde_aprovada=Count("id"))

        total_aprovado = totais_dict['total_aprovado']
        qtde_aprovada = totais_dict['qtde_aprovada']
    else:
        total_aprovado = 0
        qtde_aprovada = 0

    numreuniao_ordinal = numero_para_ordinal(numreuniao)

    return render_to_pdf(
        template_name,
        {
            "datacomite": datacomite,
            "numreuniao": numreuniao_ordinal,
            "totalaprovado": total_aprovado,
            "qtdeaprovada": qtde_aprovada,
            "membroscomite": membroscomite,
            "processoscomite": processoscomite,
            "parecerescomite": parecerescomite,
            "responsaveisempresa": responsaveisempresa,
            "emissao": datetime.today(),
            "linhalogo1": linhalogo1,
            "linhalogo2": linhalogo2,
            "linhalogo3": linhalogo3,
        },
    )

# usado para imprimir clientes inadimplentes e suas parcelas - Analítico e Sintético
# -----------------------------------------------------------------------------------
def inadimplentes(request):
    def exportar_xlsx(queryset, tipo):
        # Definir as colunas padrão com base no tipo de cliente
        if tipo == 'PF':
            campos = {
                'processo__clientepf__nome': 'Nome',
                'processo__numprocesso': 'Número do Processo',
                'parecer__dtliberacao': 'Data de Liberação',
                'numparcela': 'Número da Parcela',
                'dtvencimento': 'Data de Vencimento',
                'valorparcela': 'Valor da Parcela',
                'processo__linhacredito__nome': 'Linha de Crédito',
                'processo__localizacao__nome': 'Localização',
                'processo__criado_por__first_name': 'Criado Por',
            }
        else:
            campos = {
                'processo__clientepj__razaosocial': 'Razão Social',
                'processo__numprocesso': 'Número do Processo',
                'parecer__dtliberacao': 'Data de Liberação',
                'numparcela': 'Número da Parcela',
                'dtvencimento': 'Data de Vencimento',
                'valorparcela': 'Valor da Parcela',
                'processo__linhacredito__nome': 'Linha de Crédito',
                'processo__localizacao__nome': 'Localização',
                'processo__criado_por__first_name': 'Criado Por',
            }

        # Obter os dados do queryset
        data = list(queryset.values(*campos.keys()))

        # Gerar arquivo Excel
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=inadimplentes.xlsx'

        # Criar um workbook e adicionar uma worksheet
        workbook = xlsxwriter.Workbook(response, {'in_memory': True})
        worksheet = workbook.add_worksheet()

        # Escrever o cabeçalho principal
        if tipo == 'PF':
            worksheet.merge_range('A1:I1', 'RELATÓRIO DOS INADIMPLENTES - PF')
        else:
            worksheet.merge_range('A1:I1', 'RELATÓRIO DOS INADIMPLENTES - PJ')

        # Escrever o cabeçalho das colunas
        for col_num, (key, header) in enumerate(campos.items()):
            worksheet.write(1, col_num, header)

        # Escrever os dados
        for row_num, row_data in enumerate(data, start=2):
            for col_num, key in enumerate(campos.keys()):
                worksheet.write(row_num, col_num, row_data.get(key))

        workbook.close()
        return response

    form = InadimplentesForm(data=request.POST or None)
    template_name1 = "relatorios/inadimplentes_tela.html"

    if request.method == 'POST':
        if form.is_valid():
            if form.cleaned_data.get('tipocliente') == 'PF':
                template_name2 = "relatorios/inadimplentesPF_pdf.html"
            else:
                template_name2 = "relatorios/inadimplentesPJ_pdf.html"

            modelo = form.cleaned_data['modelo']
            qs = form.processar()
            linhalogo1 = Config.objects.filter(is_deleted=False).last().linhalogo1
            linhalogo2 = Config.objects.filter(is_deleted=False).last().linhalogo2
            linhalogo3 = Config.objects.filter(is_deleted=False).last().linhalogo3

            tipo_relatorio = request.POST.get('tipo_relatorio')

            if tipo_relatorio == 'xlsx':
                return exportar_xlsx(qs, form.cleaned_data.get('tipocliente'))
            elif tipo_relatorio == 'pdf':
                qssubtot = form.processarsubtot()
                qstot = form.processartot()
                return render_to_pdf(template_name2, {"qs": qs, "qssubtot": qssubtot, "qstot": qstot,
                                                  "modelo": modelo, "user": request.user, "emissao": datetime.today(),
                                                      "linhalogo1": linhalogo1, "linhalogo2": linhalogo2,
                                                      "linhalogo3": linhalogo3})
        else:
            messages.warning(request, str(form.errors.as_data())[31:-5])
    return render(request, template_name1, {'form': form})


# usado para imprimir clientes que devem ir pra dívida ativa e seus débitos (tem que possuir ao menos uma parcela com mais de 6 meses em aberto)
# ----------------------------------------------------------------
def dividaativa(request):
    def exportar_xlsx(queryset):

        # Definir as colunas padrão com base no tipo de cliente
        campos = {
            'processo__numprocesso': 'Processo',
            'processo__clientepf__nome': 'Cliente',
            'parecer__dtliberacao': 'Liberação',
            'numparcela': 'Pc',
            'dtvencimento': 'Data de Vencimento',
            'valorparcela': 'Valor da Parcela',
            'processo__linhacredito__nome': 'Linha de Crédito',
            'processo__criado_por__first_name': 'Criado Por',
        }

        # Obter os dados do queryset
        data = list(queryset.values(*campos.keys()))

        # Gerar arquivo Excel
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=dividaativa.xlsx'

        # Criar um workbook e adicionar uma worksheet
        workbook = xlsxwriter.Workbook(response, {'in_memory': True})
        worksheet = workbook.add_worksheet()

        # Escrever o cabeçalho principal
        worksheet.merge_range('A1:I1', 'RELATÓRIO P/ INCLUSÃO NA DÍVIDA ATIVA')

        # Escrever o cabeçalho das colunas
        for col_num, (key, header) in enumerate(campos.items()):
            worksheet.write(1, col_num, header)

        # Escrever os dados
        for row_num, row_data in enumerate(data, start=2):
            for col_num, key in enumerate(campos.keys()):
                worksheet.write(row_num, col_num, row_data.get(key))
        workbook.close()
        return response

    form = DividaAtivaForm(data=request.POST or None)
    template_name1 = "relatorios/dividaativa_tela.html"
    template_name2 = "relatorios/dividaativa_pdf.html"
    if request.method == 'POST':
        if form.is_valid():
            qs = form.processar()
            linhalogo1 = Config.objects.filter(is_deleted=False).last().linhalogo1
            linhalogo2 = Config.objects.filter(is_deleted=False).last().linhalogo2
            linhalogo3 = Config.objects.filter(is_deleted=False).last().linhalogo3

            tipo_relatorio = request.POST.get('tipo_relatorio')

            dias_inadimp = form.cleaned_data['dias_inadimp']

            if tipo_relatorio == 'xlsx':
                return exportar_xlsx(qs)
            elif tipo_relatorio == 'pdf':
                # context_dict = {
                #     "qs": qs,
                #     "dias_inadimp": dias_inadimp,
                #     "user": request.user.username,
                #     "emissao": datetime.today()
                # }
                return render_to_pdf(template_name2, {"qs": qs, "dias_inadimp": dias_inadimp,
                                                      "user": request.user, "emissao": datetime.today(),
                                                      "linhalogo1": linhalogo1, "linhalogo2": linhalogo2,
                                                      "linhalogo3": linhalogo3})
        else:
            messages.warning(request, str(form.errors.as_data())[31:-5])
    return render(request, template_name1, {'form': form})

def titulosareceber(request):
    def exportar_xlsx(queryset):
        # Definir as colunas padrão
        campos = {
            'processo__clientepf__nome': 'Cliente',
            'processo__clientepj__razaosocial': 'Cliente',
            'processo__numprocesso': 'N° Processo',
            'dtemissao': 'Data de Emissão',
            'dtvencimento': 'Data de Venvimento',
            'valorparcela': 'Valor da Parcela',
            'processo__linhacredito__nome': 'Linha de Crédito',
            'processo__criado_por__first_name': 'Criado Por',
        }

        # Obter os dados do queryset
        data = list(queryset.values(*campos.keys()))

        # Gerar arquivo Excel
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        # response['Content-Disposition'] = 'attachment; filename=titulos_a_receber.xlsx'

        # Criar um workbook e adicionar uma worksheet
        workbook = xlsxwriter.Workbook(response, {'in_memory': True})
        worksheet = workbook.add_worksheet()

        # Escrever o cabeçalho principal
        worksheet.merge_range('A1:H1', 'RELATÓRIO DOS TÍTULOS A RECEBER')

        # Escrever o cabeçalho das colunas
        for col_num, (key, header) in enumerate(campos.items()):
            worksheet.write(1, col_num, header)

        # Escrever os dados
        for row_num, row_data in enumerate(data, start=2):
            for col_num, key in enumerate(campos.keys()):
                worksheet.write(row_num, col_num, row_data.get(key))

        workbook.close()
        return response

    template_name1 = "relatorios/titulosareceber_tela.html"

    form = TitulosaReceberForm(data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            template_name2 = "relatorios/titulosareceber_pdf.html"
            qs = form.processar()
            linhalogo1 = Config.objects.filter(is_deleted=False).last().linhalogo1
            linhalogo2 = Config.objects.filter(is_deleted=False).last().linhalogo2
            linhalogo3 = Config.objects.filter(is_deleted=False).last().linhalogo3

            tipo_relatorio = request.POST.get('tipo_relatorio')
            if tipo_relatorio == 'xlsx':
                return exportar_xlsx(qs)
            elif tipo_relatorio == 'pdf':
                qssubtot = form.processarsubtot()
                return render_to_pdf(template_name2, {"qs": qs, "qssubtot": qssubtot, "user": request.user,
                                                     "emissao": datetime.today(), "linhalogo1": linhalogo1,
                                                     "linhalogo2": linhalogo2, "linhalogo3": linhalogo3})
        else:
            messages.warning(request, str(form.errors.as_data())[31:-5])
    return render(request, template_name1, {'form': form})

def recebimentos(request):
    def exportar_xlsx(queryset):
        # Definir as colunas padrão
        campos = {
            'processo__clientepf__nome': 'Cliente',
            'processo__clientepj__razaosocial': 'Cliente',
            'processo__numprocesso': 'Número do Processo',
            'dtemissao': 'Data de Emissão',
            'dtvencimento': 'Data de Venvimento',
            'valorparcela': 'Valor da Parcela',
            'valorpago': 'Valor Pago',
            'dtpagamento': 'Data de Pagamento',
            'processo__linhacredito__nome': 'Linha de Crédito',
            'processo__criado_por__first_name': 'Criado Por',
        }

        # Obter os dados do queryset
        data = list(queryset.values(*campos.keys()))

        # Gerar arquivo Excel
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        # response['Content-Disposition'] = 'attachment; filename=recebimentos_periodo.xlsx'

        # Criar um workbook e adicionar uma worksheet
        workbook = xlsxwriter.Workbook(response, {'in_memory': True})
        worksheet = workbook.add_worksheet()

        # Escrever o cabeçalho principal
        worksheet.merge_range('A1:J1', 'Relatório de Recebimentos no Período')

        # Escrever o cabeçalho das colunas
        for col_num, (key, header) in enumerate(campos.items()):
            worksheet.write(1, col_num, header)

        # Escrever os dados
        for row_num, row_data in enumerate(data, start=2):
            for col_num, key in enumerate(campos.keys()):
                worksheet.write(row_num, col_num, row_data.get(key))

        workbook.close()
        return response

    template_name1 = "relatorios/recebimentos_tela.html"

    form = RecebimentosForm(data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            template_name2 = "relatorios/recebimentos_pdf.html"
            qs = form.processar()
            linhalogo1 = Config.objects.filter(is_deleted=False).last().linhalogo1
            linhalogo2 = Config.objects.filter(is_deleted=False).last().linhalogo2
            linhalogo3 = Config.objects.filter(is_deleted=False).last().linhalogo3

            tipo_relatorio = request.POST.get('tipo_relatorio')
            if tipo_relatorio == 'xlsx':
                return exportar_xlsx(qs)
            elif tipo_relatorio == 'pdf':
                qssubtot = form.processarsubtot()
                return render_to_pdf(template_name2, {"qs": qs, "qssubtot": qssubtot, "user": request.user,
                                                      "emissao": datetime.today(), "linhalogo1": linhalogo1,
                                                      "linhalogo2": linhalogo2, "linhalogo3": linhalogo3})
        else:
            messages.warning(request, str(form.errors.as_data())[31:-5])
    return render(request, template_name1, {'form': form})

def recebimentos1(request):
    def exportar_xlsx(queryset):
        # Definir as colunas padrão
        campos = {
            'processo__clientepf__nome': 'Cliente PF',
            'processo__clientepj__razaosocial': 'Cliente PJ',
            'parecer__valorgiro_aprovado': 'Valor Crédito - Giro',
            'parecer__valorfixo_aprovado': 'Valor Crédito - Fixo',
            'negociacao__vlrtotaloriginal': 'Valor Crédito',
            'valororiginal': 'Parcela',
            'valorparcela': 'Total Parcela',
            'juros_recebto': 'Juros/Acresc',
            # 'valoracres': 'Acréscimos',
            # 'valormulta': 'Multa',
            # 'valorjuros': 'Juros',
            # 'valordesc': 'Descontos',
            'valorpago': 'Valor Pago',
            'numparcela': 'No.Parcela',
            'parecer__prazoaprovado': 'Prazo',
            'processo__clientepf__numcpf': 'No.CPF',
            'processo__empresa__numcnpj': 'No.CNPJ'
        }

        # Obter os dados do queryset
        #data = list(queryset.values(*campos.keys()))       trecho está sendo trocado pelo abaixo por ter o campo juros_recebto que é property e não pertence ao model
        campos_db = {k: v for k, v in campos.items() if k != 'juros_recebto'}
        data = list(queryset.values(*campos_db.keys()))
        for idx, obj in enumerate(queryset):
            data[idx]['juros_recebto'] = obj.juros_recebto
        #

        # Gerar arquivo Excel
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=recebimentos_contabil.xlsx'

        # Criar um workbook e adicionar uma worksheet
        workbook = xlsxwriter.Workbook(response, {'in_memory': True})
        worksheet = workbook.add_worksheet()

        # Escrever o cabeçalho principal
        worksheet.merge_range('A1:P1', 'RELATÓRIO DOS RECEBIMENTOS - CONTABILIDADE')

        # Escrever o cabeçalho das colunas
        for col_num, (key, header) in enumerate(campos.items()):
            worksheet.write(1, col_num, header)

        # Escrever os dados
        for row_num, row_data in enumerate(data, start=2):
            for col_num, key in enumerate(campos.keys()):
                worksheet.write(row_num, col_num, row_data.get(key))

        workbook.close()
        return response

    logos = get_logo_images()
    form = Recebimentos1Form(data=request.POST or None)
    template_name1 = "relatorios/recebimentos1_tela.html"
    if request.method == 'POST':
        if form.is_valid():
            if form.cleaned_data.get('versao') == '1':
                template_name2 = "relatorios/recebimentos1v1_pdf.html"
            else:
                template_name2 = "relatorios/recebimentos1v2_pdf.html"

            qs = form.processar()
            # linhalogo1 = Config.objects.filter(is_deleted=False).last().linhalogo1
            # linhalogo2 = Config.objects.filter(is_deleted=False).last().linhalogo2
            # linhalogo3 = Config.objects.filter(is_deleted=False).last().linhalogo3

            tipo_relatorio = request.POST.get('tipo_relatorio')
            if tipo_relatorio == 'xlsx':
                return exportar_xlsx(qs)
            elif tipo_relatorio == 'pdf':
                qssubtot = form.processarsubtot()
                return render_to_pdf(template_name2, {"qs": qs, "qssubtot": qssubtot, "user": request.user,
                                                    "emissao": datetime.today(), "linhalogo1": logos["linhalogo1"],
                                                    "linhalogo2": logos["linhalogo2"],
                                                    "linhalogo3": logos["linhalogo3"]})
        else:
            messages.warning(request, str(form.errors.as_data())[31:-5])
    return render(request, template_name1, {'form': form})

# def dadoscadastraisclientes(request):
#     template_name1 = "relatorios/dadoscadastraisclientes_tela.html"
#     template_name2 = "relatorios/dadoscadastraisclientes_pdf.html"
#     qs = None
#     form = DadosCadastraisClientesForm(data=request.POST or None)
#     if request.method == 'POST':
#         if form.is_valid():
#             qs = form.processar()
#             linhalogo1 = Config.objects.filter(is_deleted=False).last().linhalogo1
#             linhalogo2 = Config.objects.filter(is_deleted=False).last().linhalogo2
#             linhalogo3 = Config.objects.filter(is_deleted=False).last().linhalogo3
#             return render_to_pdf(template_name2, {"qs": qs, "user": request.user,
#                                                   "emissao": datetime.today(),"linhalogo1": linhalogo1,
#                                                   "linhalogo2": linhalogo2, "linhalogo3": linhalogo3})
#         else:
#             messages.warning(request, str(form.errors.as_data())[31:-5])
#     return render(request, template_name1, {'form': form})

def dadoscadastraisclientes(request):
    """
    Função para exibir e processar os dados cadastrais dos clientes.
    """
    form = DadosCadastraisClientesForm(data=request.POST or None)
    template_name1 = "relatorios/dadoscadastraisclientes_tela.html"
    template_name2 = "relatorios/dadoscadastraisclientes_pdf.html"

    if request.method == 'POST':
        context_data = {
            "user": request.user.username,
            "emissao": datetime.today(),
        }

        # Chama a função que processa o formulário e gera o PDF
        return handle_form_submission(request, form, template_name2, context_data)

    return render(request, template_name1, {'form': form})

def processoscomite(request):
    template_name1 = "relatorios/processoscomite_tela.html"
    template_name2 = "relatorios/processoscomite_pdf.html"
    form = ProcessosComiteForm(data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            dtcomite = form.cleaned_data.get('dtcomite_ini')
            qs = form.processar()
            linhalogo1 = Config.objects.filter(is_deleted=False).last().linhalogo1
            linhalogo2 = Config.objects.filter(is_deleted=False).last().linhalogo2
            linhalogo3 = Config.objects.filter(is_deleted=False).last().linhalogo3
            qssubtot = form.processarsubtot()
            qstotal = form.processartotal()
            return render_to_pdf(template_name2, {"qs": qs, "dtcomite": dtcomite, "qssubtot": qssubtot,
                                                  "valor_total": qstotal['valor_total'], "qtde_total": qstotal['qtde_total'],
                                                  "media_final": qstotal['media_final'], "user": request.user,
                                                  "emissao": datetime.today(), "linhalogo1": linhalogo1,
                                                  "linhalogo2": linhalogo2, "linhalogo3": linhalogo3})
        else:
            messages.warning(request, str(form.errors.as_data())[31:-5])
    return render(request, template_name1, {'form': form})

def autorizadoscomite(request):
    template_name1 = "relatorios/autorizadoscomite_tela.html"
    template_name2 = "relatorios/autorizadoscomite_pdf.html"
    form = AutorizadosComiteForm(data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            qs = form.processar()
            linhalogo1 = Config.objects.filter(is_deleted=False).last().linhalogo1
            linhalogo2 = Config.objects.filter(is_deleted=False).last().linhalogo2
            linhalogo3 = Config.objects.filter(is_deleted=False).last().linhalogo3
            return render_to_pdf(template_name2, {"qs": qs, "user": request.user, "emissao": datetime.today(),
                                                                "linhalogo1": linhalogo1, "linhalogo2": linhalogo2,
                                                                "linhalogo3": linhalogo3})
        else:
            messages.warning(request, str(form.errors.as_data())[31:-5])
    return render(request, template_name1, {'form': form})

# def negociacoes(request):
#     template_name1 = "relatorios/renegociacoes_tela.html"
#     template_name2 = "relatorios/renegociacoes_pdf.html"
#     form = AutorizadosComiteForm(data=request.POST or None)
#     if request.method == 'POST':
#         if form.is_valid():
#             qs = form.processar()
#             linhalogo1 = Config.objects.filter(is_deleted=False).last().linhalogo1
#             linhalogo2 = Config.objects.filter(is_deleted=False).last().linhalogo2
#             linhalogo3 = Config.objects.filter(is_deleted=False).last().linhalogo3
#             return render_to_pdf(template_name2, {"qs": qs, "user": request.user, "emissao": datetime.today(),
#                                                                 "linhalogo1": linhalogo1, "linhalogo2": linhalogo2,
#                                                                 "linhalogo3": linhalogo3})
#         else:
#             messages.warning(request, str(form.errors.as_data())[31:-5])
#     return render(request, template_name1, {'form': form})

# def liberacaovalores(request):
#     template_name1 = "relatorios/liberacaovalores_tela.html"
#     template_name2 = "relatorios/liberacaovalores_pdf.html"
#     qs = None
#     form = LiberacaoValoresForm(data=request.POST or None)
#     if request.method == 'POST':
#         if form.is_valid():
#             qs = form.processar()
#             linhalogo1 = Config.objects.filter(is_deleted=False).last().linhalogo1
#             linhalogo2 = Config.objects.filter(is_deleted=False).last().linhalogo2
#             linhalogo3 = Config.objects.filter(is_deleted=False).last().linhalogo3
#             valortot = 0.0
#             for r in qs:
#                 valortot += float(r.vlrtotalaprovado)
#             return render_to_pdf(template_name2, {"qs": qs, "valortot": valortot, "user": request.user,
#                                                   "emissao": datetime.today(), "linhalogo1": linhalogo1,
#                                                   "linhalogo2": linhalogo2, "linhalogo3": linhalogo3})
#         else:
#             messages.warning(request, str(form.errors.as_data())[31:-5])
#     return render(request, template_name1, {'form': form})

def liberacaovalores(request):
    """
    View responsável por processar e exibir o relatório de valores liberados de empréstimo para pagamento.

    - GET: Exibe o formulário para que o usuário insira os filtros desejados.
    - POST: Processa os dados do formulário e, caso válido:
        - Gera o relatório em PDF com base nos dados processados.
        - Caso inválido, exibe os erros no formulário.
    """

    form = LiberacaoValoresForm(data=request.POST or None)
    if request.method == 'POST':
        return handle_form_submission(request, form, "relatorios/liberacaovalores_pdf.html",
                                      {}, include_totalliberado=True)

    return render(request, "relatorios/liberacaovalores_tela.html", {'form': form})

# def movimentos(request):
#     template_name1 = "relatorios/movimentos_tela.html"
#     template_name2 = "relatorios/movimentos_pdf.html"
#     form = MovimentosForm(data=request.POST or None)
#     if request.method == 'POST':
#         if form.is_valid():
#             qs = form.processar()
#             linhalogo1 = Config.objects.filter(is_deleted=False).last().linhalogo1
#             linhalogo2 = Config.objects.filter(is_deleted=False).last().linhalogo2
#             linhalogo3 = Config.objects.filter(is_deleted=False).last().linhalogo3
#             valortot = 0.0
#             for r in qs:
#                 valortot += float(r.valorpago)
#             return render_to_pdf(template_name2, {"qs": qs, "valortot": valortot, "user": request.user,
#                                                   "emissao": datetime.today(), "linhalogo1": linhalogo1,
#                                                   "linhalogo2": linhalogo2, "linhalogo3": linhalogo3})
#         else:
#             messages.warning(request, str(form.errors.as_data())[31:-5])
#     return render(request, template_name1, {'form': form})

def movimentos(request):
    """
    View responsável por processar e exibir o relatório de movimentos, seja em tela ou em PDF.

    - GET: Exibe o formulário para que o usuário insira os filtros desejados.
    - POST: Processa os dados do formulário e, caso válido:
        - Gera o relatório em PDF com base nos dados processados.
        - Caso inválido, exibe os erros no formulário.
    """

    form = MovimentosForm(data=request.POST or None)
    if request.method == 'POST':
        return handle_form_submission(request, form, "relatorios/movimentos_pdf.html", {}, include_valortotal=True)

    return render(request, "relatorios/movimentos_tela.html", {'form': form})

# def movimentos(request):
#     """
#     View responsável por processar e exibir o relatório de movimentos, seja em tela ou em PDF.
#
#     - GET: Exibe o formulário para que o usuário insira os filtros desejados.
#     - POST: Processa os dados do formulário e, caso válido:
#         - Gera o relatório em PDF com base nos dados processados.
#         - Caso inválido, exibe os erros no formulário.
#     """
#     template_form = "relatorios/movimentos_tela.html"
#     template_pdf = "relatorios/movimentos_pdf.html"
#
#     # Inicializa o formulário com os dados da requisição (se houver)
#     form = MovimentosForm(data=request.POST or None)
#
#     if request.method == 'POST':
#         # Define o contexto inicial para a geração do PDF
#         context_data = {"valortot": 0.0}
#
#         # Processa o formulário usando a função reutilizável
#         response = handle_form_submission(request, form, template_pdf, context_data)
#
#         if response:
#             # Adiciona o total ao contexto e retorna o PDF
#             qs = form.processar()
#             context_data["valortot"] = sum(float(r.valorpago) for r in qs)
#             return render_to_pdf(template_pdf, context_data)
#
#     # Retorna a página do formulário para GET ou caso o POST tenha falhas
#     return render(request, template_form, {'form': form})

# def listaprocessos(request):
#     template_name1 = "relatorios/listaprocessos_tela.html"
#     template_name2 = "relatorios/listaprocessos_pdf.html"
#     form = ListaProcessosForm(data=request.POST or None)
#     if request.method == 'POST':
#         if form.is_valid():
#             qs = form.processar()
#             linhalogo1 = Config.objects.filter(is_deleted=False).last().linhalogo1
#             linhalogo2 = Config.objects.filter(is_deleted=False).last().linhalogo2
#             linhalogo3 = Config.objects.filter(is_deleted=False).last().linhalogo3
#             return render_to_pdf(template_name2, {"qs": qs, "user": request.user,
#                                                   "emissao": datetime.today(), "linhalogo1": linhalogo1,
#                                                   "linhalogo2": linhalogo2, "linhalogo3": linhalogo3})
#         else:
#             messages.warning(request, str(form.errors.as_data())[31:-5])
#             # return self.render_to_response(self.get_context_data())
#     return render(request, template_name1, {'form': form})
#
# def renegociacoes(request):
#     template_name1 = "relatorios/renegociacoes_tela.html"
#     template_name2 = "relatorios/renegociacoes_pdf.html"
#     form = NegociacoesForm(data=request.POST or None)
#     if request.method == 'POST':
#         if form.is_valid():
#             qs = form.processar()
#             qstot = form.processartot()
#             linhalogo1 = Config.objects.filter(is_deleted=False).last().linhalogo1
#             linhalogo2 = Config.objects.filter(is_deleted=False).last().linhalogo2
#             linhalogo3 = Config.objects.filter(is_deleted=False).last().linhalogo3
#             return render_to_pdf(template_name2, {"qs": qs, "qstot": qstot, "user": request.user,
#                                                   'emissao': datetime.today(), "linhalogo1": linhalogo1,
#                                                   "linhalogo2": linhalogo2, "linhalogo3": linhalogo3})
#         else:
#             messages.warning(request, str(form.errors.as_data())[31:-5])
#     return render(request, template_name1, {'form': form})
#
# def processospendentes(request):
#     template_name1 = "relatorios/processospendentes_tela.html"
#     template_name2 = "relatorios/processospendentes_pdf.html"
#     form = ProcessosPendentesForm(data=request.POST or None)
#     if request.method == 'POST':
#         if form.is_valid():
#             qs = form.processar()
#             linhalogo1 = Config.objects.filter(is_deleted=False).last().linhalogo1
#             linhalogo2 = Config.objects.filter(is_deleted=False).last().linhalogo2
#             linhalogo3 = Config.objects.filter(is_deleted=False).last().linhalogo3
#
#             return render_to_pdf(template_name2, {"qs": qs, "user": request.user, 'emissao': datetime.today(),
#                                                   "linhalogo1": linhalogo1, "linhalogo2": linhalogo2,
#                                                   "linhalogo3": linhalogo3})
#         else:
#             messages.warning(request, str(form.errors.as_data())[31:-5])
#     return render(request, template_name1, {'form': form})
#
# def resumoatendimentos(request):
#     template_name1 = "relatorios/resumoatendimentos_tela.html"
#     template_name2 = "relatorios/resumoatendimentos_pdf.html"
#     form = ResumoAtendimentosForm(data=request.POST or None)
#     if request.method == 'POST':
#         if form.is_valid():
#             qs = form.processar()
#             linhalogo1 = Config.objects.filter(is_deleted=False).last().linhalogo1
#             linhalogo2 = Config.objects.filter(is_deleted=False).last().linhalogo2
#             linhalogo3 = Config.objects.filter(is_deleted=False).last().linhalogo3
#             return render_to_pdf(template_name2, {"qs": qs, "user": request.user, 'emissao': datetime.today(),
#                                                   "linhalogo1": linhalogo1, "linhalogo2": linhalogo2,
#                                                   "linhalogo3": linhalogo3})
#         else:
#             messages.warning(request, str(form.errors.as_data())[31:-5])
#     return render(request, template_name1, {'form': form})


def listaprocessos(request):
    """
    Função para exibir e processar a lista de processos.
    """
    form = ListaProcessosForm(data=request.POST or None)
    if request.method == 'POST':
        return handle_form_submission(request, form, "relatorios/listaprocessos_pdf.html", {}, include_totalsolicitado=True)
    return render(request, "relatorios/listaprocessos_tela.html", {'form': form})

# def renegociacoes(request):
#     """
#     Função para exibir e processar renegociações. Falta implementar o totalizador
#     """
#     form = NegociacoesForm(data=request.POST or None)
#     if request.method == 'POST':
#         # context_data = {"qstot": form.processartot()}
#         # return handle_form_submission(request, form, "relatorios/renegociacoes_pdf.html", context_data)
#         return handle_form_submission(request, form, "relatorios/renegociacoes_pdf.html", {})
#
#     return render(request, "relatorios/renegociacoes_tela.html", {'form': form})

def renegociacoes(request):
    """
    View responsável por processar e exibir o relatório de renegociações, seja em tela ou em PDF.

    - GET: Exibe o formulário para que o usuário insira os filtros desejados.
    - POST: Processa os dados do formulário e, caso válido:
        - Gera o relatório em PDF com base nos dados processados.
        - Caso inválido, exibe os erros no formulário.
    """

    form = NegociacoesForm(data=request.POST or None)
    if request.method == 'POST':
        return handle_form_submission(request, form, "relatorios/renegociacoes_pdf.html",
                                      {}, include_totaldebitonegociado=True)

    return render(request, "relatorios/renegociacoes_tela.html", {'form': form})

def processospendentes(request):
    """
    Função para exibir e processar processos pendentes.
    """
    form = ProcessosPendentesForm(data=request.POST or None)
    if request.method == 'POST':
        return handle_form_submission(request, form, "relatorios/processospendentes_pdf.html", {})

    return render(request, "relatorios/processospendentes_tela.html", {'form': form})

def resumoatendimentos(request):
    """
    Função para exibir e processar resumo de atendimentos.
    """
    form = ResumoAtendimentosForm(data=request.POST or None)
    if request.method == 'POST':
        return handle_form_submission(request, form, "relatorios/resumoatendimentos_pdf.html", {})

    return render(request, "relatorios/resumoatendimentos_tela.html", {'form': form})

def listapesfisicas(request):
    def exportar_xlsx(queryset):
        campos = {
            'id': 'Id',
            'nome': 'Nome',
            'numcpf': 'CPF',
            'tipo': 'Tipo de Cliente',
            'dtnascimento': 'Dt.Nascimento',
            'naturalidade': 'Naturalidade',
            'criado_por__first_name': 'Agente',
            'data_criacao': 'Dt.Cadastro',
            'is_deleted': 'Excl',
        }

        # Obter os dados do queryset
        data = list(queryset.values(*campos.keys()))

        # Gerar arquivo Excel
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=pessoasfisicas.xlsx'

        # Criar um workbook e adicionar uma worksheet
        workbook = xlsxwriter.Workbook(response, {'in_memory': True})
        worksheet = workbook.add_worksheet()

        # Escrever o cabeçalho principal
        worksheet.merge_range('A1:I1', 'RELAÇÃO DE PESSOAS FÍSICAS (CLIENTES/AVALISTAS')

        # Escrever o cabeçalho das colunas
        for col_num, (key, header) in enumerate(campos.items()):
            worksheet.write(1, col_num, header)

        # Escrever os dados
        for row_num, row_data in enumerate(data, start=2):
            for col_num, key in enumerate(campos.keys()):
                worksheet.write(row_num, col_num, row_data.get(key))
        workbook.close()
        return response

    form = ListaPesFisicasForm(data=request.POST or None)
    template_name1 = "relatorios/listapesfisicas_tela.html"
    template_name2 = "relatorios/listapesfisicas_pdf.html"
    if request.method == 'POST':
        if form.is_valid():
            qs = form.processar()
            linhalogo1 = Config.objects.filter(is_deleted=False).last().linhalogo1
            linhalogo2 = Config.objects.filter(is_deleted=False).last().linhalogo2
            linhalogo3 = Config.objects.filter(is_deleted=False).last().linhalogo3
            tipo_relatorio = request.POST.get('tipo_relatorio')
            if tipo_relatorio == 'xlsx':
                return exportar_xlsx(qs)
            elif tipo_relatorio == 'pdf':
                return render_to_pdf(template_name2, {"qs": qs, "user": request.user,
                                                      "emissao": datetime.today(), "linhalogo1": linhalogo1,
                                                      "linhalogo2": linhalogo2, "linhalogo3": linhalogo3})
        else:
            messages.warning(request, str(form.errors.as_data())[31:-5])
    return render(request, template_name1, {'form': form})
#
# def listapesjuridicas(request):
#     template_name1 = "relatorios/listapesjuridicas_tela.html"
#     template_name2 = "relatorios/listapesjuridicas_pdf.html"
#     form = ListaPesJuridicasForm(data=request.POST or None)
#     if request.method == 'POST':
#         if form.is_valid():
#             qs = form.processar()
#             linhalogo1 = Config.objects.filter(is_deleted=False).last().linhalogo1
#             linhalogo2 = Config.objects.filter(is_deleted=False).last().linhalogo2
#             linhalogo3 = Config.objects.filter(is_deleted=False).last().linhalogo3
#             return render_to_pdf(template_name2, {"qs": qs, "user": request.user, "emissao": datetime.today(),
#                                                   "linhalogo1": linhalogo1, "linhalogo2": linhalogo2,
#                                                   "linhalogo3": linhalogo3})
#         else:
#             messages.warning(request, str(form.errors.as_data())[31:-5])
#     return render(request, template_name1, dict(form=form))

# def listapesjuridicas(request):
#     """
#     Função para exibir e processar a lista de pessoas jurídicas.
#     """
#     form = ListaPesJuridicasForm(data=request.POST or None)
#     template_name1 = "relatorios/listapesjuridicas_tela.html"
#     template_name2 = "relatorios/listapesjuridicas_pdf.html"
#
#     if request.method == 'POST':
#         return handle_form_submission(request, form, template_name2, {})
#
#     return render(request, template_name1, {'form': form})

def listapesjuridicas(request):
    """
    Função para exibir e processar a lista de pessoas jurídicas.
    - Exibe um formulário para entrada de dados.
    - Processa a entrada de dados, gerando um PDF caso solicitado.
    """
    # Inicializa o formulário com dados do POST, se disponíveis, ou vazio.
    form = ListaPesJuridicasForm(data=request.POST or None)
    # Define os templates usados para visualização na tela e geração de PDF.
    template_name1 = "relatorios/listapesjuridicas_tela.html"
    template_name2 = "relatorios/listapesjuridicas_pdf.html"

    # Se o metodo for POST, processa o envio do formulário.
    if request.method == 'POST':
        # Valida os dados do formulário.
        if form.is_valid():
            return handle_form_submission(request, form, template_name2, {})
        else:
            # Exibe erros do formulário, se inválido.
            return render(request, template_name1, {'form': form, 'errors': form.errors})

    # Exibe o formulário em branco na tela.
    return render(request, template_name1, {'form': form})


def processarretorno(request):
    template_name = "financeiro/arquivoretorno_list.html"
    qs1 = None
    qs2 = None
    form = RetornoForm(data=request.POST or None)
    if form.is_valid():

        data = form.cleaned_data
        arquivo = data['nome_lista']

        caminho_arquivo = os.path.join(settings.BASE_DIR, 'Documentos/retorno/', arquivo)

        arquivo = open(caminho_arquivo)
        linhas = arquivo.read().splitlines()

        contador = 0
        processo_ok = True

        for linha in linhas:
            contador = contador + 1
            segmento = linha[13:14]
            if contador == 1:                     # primeira linha do arquivo
                dtgravacao = linha[147:151] + '-' + linha[145:147] + '-' + linha[143:145]
                numretorno = linha[158:163]
                qsretorno = RetornoHeader.objects.filter(dtgravacao=dtgravacao, numretorno=numretorno)
                if qsretorno:
                    processo_ok = False
                    for r in qsretorno:
                        id_retorno = r.id
                    break
                retorno_h = RetornoHeader()
                retorno_h.dtgravacao = dtgravacao
                retorno_h.numretorno = numretorno
                retorno_h.save()

            if segmento == 'T':
                numseq = linha[10:13]
                nossonumero = linha[37:54]
                numdocumento = linha[55:73]
                codmovimento = linha[15:17]
                valortitulo = linha[81:96]
                dtvencimento = linha[77:81] + '-' + linha[75:77] + '-' + linha[73:75]
            elif segmento == 'U':
                numseq = str(numseq) + '_' + linha[10:13]
                jurosmulta = linha[18:32]
                valordesc = linha[36:47]
                valorpago = linha[77:92]
                dtocorrencia = linha[141:145] + '-' + linha[139:141] + '-' + linha[137:139]

                retorno_header = get_object_or_404(RetornoHeader, dtgravacao=dtgravacao, numretorno=numretorno)
                id_retorno  = retorno_header.id

                retorno_d = RetornoDetail()
                retorno_d.retorno_id = id_retorno
                retorno_d.numseq = numseq
                retorno_d.nossonumero = nossonumero
                retorno_d.numdocumento = numdocumento
                retorno_d.codmovimento = codmovimento
                retorno_d.valortitulo = float(valortitulo) / 100
                retorno_d.dtvencimento = dtvencimento
                retorno_d.jurosmulta = float(jurosmulta) / 100
                retorno_d.valordesc = float(valordesc) / 100
                retorno_d.valorpago = float(valorpago) / 100
                retorno_d.dtocorrencia = dtocorrencia
                retorno_d.save()
                # print('Registro retorno gravado com sucesso', numseq)

        if processo_ok:
           messages.success(request, 'Arquivo retorno processado com sucesso.')
        else:
           messages.success(request, 'Arquivo retorno já foi processado... Verifique.')

        qs1 = RetornoHeader.objects.all().filter(pk=id_retorno)
        qs2 = RetornoDetail.objects.all().filter(retorno_id=id_retorno)

    return render(request, template_name, dict(form=form, qs1=qs1, qs2=qs2))

def processarenvio(request):
    template_name = "financeiro/arquivoenvio_list.html"
    qs = None
    form = EnvioForm(data=request.POST or None)
    if form.is_valid():
        if request.POST ['processar'] == 'Lista':
           qs = form.processar()
        else:
            qs = form.processar()
            if qs:
                seqregistro = 0

                qsconfig = Config.objects.filter(is_deleted=False).last()
                ultenviobanco = qsconfig.ultenviobanco
                ultnossonumero = int(qsconfig.ultnossonumero)
                # percmulta = qsparametro.multa
                is_remessateste = qsconfig.is_tstremessa

                ultenviobanco = ultenviobanco + 1

                nomarquivo = 'CNAB240_5_282727_'
                nomarquivo = nomarquivo \
                             + str(datetime.today().day).zfill(2) \
                             + str(datetime.today().month).zfill(2) \
                             + str(datetime.today().year)[2:4] + '_'
                nomarquivo = nomarquivo + str(ultenviobanco) + '.REM'
                caminho_arquivo = os.path.join(settings.BASE_DIR, 'Documentos/remessa/', nomarquivo)
                arquivo = open(caminho_arquivo, 'w')

                # gerando linha header do arquivo
                arquivo.write('001')
                arquivo.write('0000')
                arquivo.write('0')
                arquivo.write(' ' * 9)
                arquivo.write('2')
                arquivo.write('21545238000172')
                arquivo.write('003059740')
                arquivo.write('0014')
                arquivo.write('17')
                arquivo.write('019')
                arquivo.write('  ')
                arquivo.write('00005')
                arquivo.write('1')
                arquivo.write('000000282727')
                arquivo.write('1')
                arquivo.write(' ')
                arquivo.write('FUNDO DE DESENVOLVIMENTO DE CA')
                arquivo.write('BANCO DO BRASIL S.A.          ')
                arquivo.write(' ' * 10)
                arquivo.write('1')
                arquivo.write(str(datetime.today().day).zfill(2) + str(datetime.today().month).zfill(2) + str(datetime.today().year).zfill(2))
                arquivo.write(str(datetime.today().hour) + str(datetime.today().minute) + str(datetime.today().second))
                arquivo.write(str(ultenviobanco).zfill(6))
                arquivo.write('000')
                arquivo.write('0' * 5)
                arquivo.write(' ' * 20)
                arquivo.write(' ' * 20)
                arquivo.write(' ' * 29)
                arquivo.write('\n')

                # gerando linha header do lote
                arquivo.write('001')
                arquivo.write('0001')
                arquivo.write('1')
                arquivo.write('R')
                arquivo.write('01')
                arquivo.write('  ')
                arquivo.write('000')
                arquivo.write(' ')
                arquivo.write('2')
                arquivo.write('021545238000172')
                arquivo.write('003059740')
                arquivo.write('0014')
                arquivo.write('17')
                arquivo.write('019')
                if is_remessateste:
                    arquivo.write('TS')
                else:
                    arquivo.write('  ')
                arquivo.write('0000510000002827271 FUNDO DE DESENVOLVIMENTO DE CA')
                arquivo.write(' ' * 40)
                arquivo.write(' ' * 40)
                arquivo.write(str(ultenviobanco).zfill(8))
                arquivo.write(str(datetime.today().day).zfill(2) + str(datetime.today().month).zfill(2) + str(datetime.today().year).zfill(2))
                arquivo.write('0' * 8)
                arquivo.write(' ' * 33)
                arquivo.write('\n')

                # gerando linhas detalhe P, Q e R
                for r in qs:
                    ultnossonumero += 1

                    arquivo.write('001')
                    arquivo.write('0001')
                    arquivo.write('3')
                    seqregistro += 1
                    arquivo.write(str(seqregistro).zfill(5))
                    arquivo.write('P')
                    arquivo.write(' ')
                    arquivo.write('01')
                    arquivo.write('0000510000002827271')
                    arquivo.write(' ')
                    arquivo.write(str(ultnossonumero) + '   ')
                    arquivo.write('11111')
                    arquivo.write('0' * 15)         # ver qual será o número do documento de cobrança
                    arquivo.write(str(r.dtvencimento.day).zfill(2) + str(r.dtvencimento.month).zfill(2) + str(r.dtvencimento.year).zfill(4))
                    arquivo.write(str(r.valorparcela).replace('.','').zfill(15))
                    arquivo.write('0' * 5)         # ver qual será o número do documento de cobrança
                    arquivo.write(' ')
                    arquivo.write('02')
                    arquivo.write('N')
                    arquivo.write(str(r.dtemissao.day).zfill(2) + str(r.dtemissao.month).zfill(2) + str(r.dtemissao.year).zfill(4))
                    arquivo.write('1')
                    arquivo.write('0' * 8)
                    arquivo.write('0' * 15)
                    arquivo.write('0')
                    arquivo.write('0' * 8)
                    arquivo.write('0' * 15)
                    arquivo.write('0' * 15)
                    arquivo.write('0' * 15)
                    arquivo.write('0' * 25)
                    arquivo.write('3')
                    arquivo.write('00')
                    arquivo.write('0')
                    arquivo.write('000')
                    arquivo.write('00')
                    arquivo.write('0' * 10)
                    arquivo.write(' ')
                    arquivo.write('\n')

                    arquivo.write('001')
                    arquivo.write('0001')
                    arquivo.write('3')
                    seqregistro += 1
                    arquivo.write(str(seqregistro).zfill(5))
                    arquivo.write('Q')
                    arquivo.write(' ')
                    arquivo.write('01')
                    arquivo.write('1')

                    processo = get_object_or_404(Processo, pk=r.processo_id)

                    if processo.clientepf:
                        cliente = get_object_or_404(PessoaFisica, pk=processo.clientepf_id)
                    else:
                        cliente = get_object_or_404(PessoaJuridica, pk=processo.clientepj_id)

                    # numcpf_c_mask = qsprocesso.cliente.numcpf
                    numcpf_c_mask = cliente.numcpf
                    numcpf_s_mask = numcpf_c_mask.translate(str.maketrans('', '', '.-')).zfill(15)
                    arquivo.write(numcpf_s_mask)
                    arquivo.write(cliente.nome.ljust(40))
                    endereco_completo = cliente.logradouro + ', ' + cliente.numimovel + ' - ' \
                                      + cliente.complemento
                    arquivo.write(endereco_completo.ljust(40))
                    arquivo.write(cliente.bairro.ljust(15))
                    arquivo.write(cliente.cep[0:5])
                    arquivo.write(cliente.cep[6:9])
                    arquivo.write(cliente.cidade.nome[0:15])
                    arquivo.write(cliente.cidade.uf)
                    arquivo.write('0')
                    arquivo.write('0' * 15)
                    arquivo.write(' ' * 40)
                    arquivo.write('000')
                    arquivo.write(' ' * 20)
                    arquivo.write(' ' * 8)
                    arquivo.write('\n')

                    arquivo.write('001')
                    arquivo.write('0001')
                    arquivo.write('3')
                    seqregistro += 1
                    arquivo.write(str(seqregistro).zfill(5))
                    arquivo.write('R')
                    arquivo.write(' ')
                    arquivo.write('01')
                    arquivo.write('0')
                    arquivo.write('0' * 8)
                    arquivo.write('0' * 15)
                    arquivo.write('0')
                    arquivo.write('0' * 8)
                    arquivo.write('0' * 15)
                    arquivo.write('2')
                    arquivo.write(str(r.dtvencimento.day).zfill(2) + str(r.dtvencimento.month).zfill(2) + str(r.dtvencimento.year).zfill(4))
                    arquivo.write('000000000000200')
                    # arquivo.write(str(percmulta).zfill(13))
                    arquivo.write(' ' * 10)
                    arquivo.write('FUNDECAM - FUNDO DE DESENV. DE CAMPOS   ')
                    arquivo.write('0' * 40)
                    arquivo.write(' ' * 20)
                    arquivo.write('0' * 8)
                    arquivo.write('000')
                    arquivo.write('0' * 5)
                    arquivo.write('0')
                    arquivo.write('0' * 12)
                    arquivo.write('000')
                    arquivo.write(' ' * 9)
                    arquivo.write('\n')

                    financeiro = get_object_or_404(Financeiro, pk=r.id)
                    financeiro.numenvio = ultenviobanco
                    financeiro.nossonumero = ultnossonumero
                    financeiro.dtgravacao= datetime.today()
                    financeiro.data_edicao = datetime.today()
                    financeiro.save()


                qsconfig.ultenviobanco = ultenviobanco
                qsconfig.ultnossonumero = ultnossonumero
                qsconfig.save()

                # imprime trailer de Lote
                arquivo.write('00100015')
                arquivo.write(' ' * 9)
                seqregistro += 2
                arquivo.write(str(seqregistro).zfill(6))
                arquivo.write('0' * 217)
                arquivo.write('\n')

                # imprime trailer de arquivo
                arquivo.write('00199999')
                arquivo.write(' ' * 9)
                arquivo.write('000001')
                seqregistro += 2
                arquivo.write(str(seqregistro).zfill(6))
                arquivo.write('0' * 6)
                arquivo.write(' ' * 205)
                arquivo.write('\n')

                arquivo.close()
                messages.success(request, 'Arquivo cobrança ' + nomarquivo + ' gerado com com sucesso.')
    else:
        messages.warning(request, str(form.errors.as_data())[31:-5])

    return render(request, template_name, dict(form=form, qs=qs))

# def processarenvio(request):
#     """
#     View para processar o envio de arquivos de cobrança e gerar arquivos de remessa CNAB240.
#
#     Args:
#         request (HttpRequest): Requisição HTTP do cliente.
#
#     Returns:
#         HttpResponse: Página renderizada com o formulário e mensagens relevantes.
#     """
#     template_name = "financeiro/arquivoenvio_list.html"
#     form = EnvioForm(data=request.POST or None)
#     qs = None
#
#     if request.method == 'POST' and form.is_valid():
#         qs = form.processar()
#         if 'processar' in request.POST and request.POST['processar'] == 'Lista':
#             return render(request, template_name, {'form': form, 'qs': qs})
#
#         # Caso não seja apenas "Lista", processa o arquivo de remessa
#         try:
#             nomarquivo, ultenviobanco = gerar_arquivo_remessa(qs)
#             messages.success(request, f"Arquivo cobrança '{nomarquivo}' gerado com sucesso.")
#         except Exception as e:
#             messages.error(request, f"Ocorreu um erro ao gerar o arquivo: {str(e)}")
#     elif request.method == 'POST':
#         messages.warning(request, form.errors.as_text())
#
#     return render(request, template_name, {'form': form, 'qs': qs})
#
#
# def gerar_arquivo_remessa(qs):
#     """
#     Gera o arquivo de remessa CNAB240.
#
#     Args:
#         qs (QuerySet): Conjunto de dados para processar no arquivo de remessa.
#
#     Returns:
#         tuple: Nome do arquivo gerado e o último número de envio.
#
#     Raises:
#         ValueError: Se houver erro ao gerar o arquivo.
#     """
#     # Configurações e inicializações
#     qsconfig = Config.objects.filter(is_deleted=False).last()
#     if not qsconfig:
#         raise ValueError("Configuração não encontrada.")
#
#     ultenviobanco = qsconfig.ultenviobanco + 1
#     ultnossonumero = int(qsconfig.ultnossonumero)
#     is_remessateste = qsconfig.is_tstremessa
#
#     # Nome e caminho do arquivo
#     hoje = datetime.today()
#     nomarquivo = f"CNAB240_5_282727_{hoje.strftime('%d%m%y')}_{ultenviobanco}.REM"
#     caminho_arquivo = os.path.join(settings.BASE_DIR, 'Documentos/remessa/', nomarquivo)
#
#     # Criação do arquivo
#     with open(caminho_arquivo, 'w') as arquivo:
#         escrever_header_arquivo(arquivo, ultenviobanco)
#         escrever_header_lote(arquivo, ultenviobanco, is_remessateste)
#
#         seqregistro = 0
#         for r in qs:
#             ultnossonumero += 1
#             seqregistro = escrever_detalhe_remessa(arquivo, r, ultnossonumero, seqregistro)
#
#             # Atualização dos registros financeiros
#             atualizar_financeiro(r, ultenviobanco, ultnossonumero)
#
#         escrever_trailer_lote(arquivo, seqregistro)
#         escrever_trailer_arquivo(arquivo, seqregistro)
#
#     # Atualização das configurações
#     qsconfig.ultenviobanco = ultenviobanco
#     qsconfig.ultnossonumero = ultnossonumero
#     qsconfig.save()
#
#     return nomarquivo, ultenviobanco
#
#
# def escrever_header_arquivo(arquivo, ultenviobanco):
#     """
#     Escreve o cabeçalho do arquivo CNAB240.
#     """
#     hoje = datetime.today()
#     header = (
#         "00100000"  # Identificação do arquivo
#         "0" + " " * 9 + "2" + "21545238000172" + "003059740001417019" + "  "
#         f"{str(ultenviobanco).zfill(6)}"  # Número do envio
#         f"{hoje.strftime('%d%m%Y%H%M%S')}" + "000" + "0" * 5 + " " * 84 + "\n"
#     )
#     arquivo.write(header)
#
#
# def escrever_header_lote(arquivo, ultenviobanco, is_remessateste):
#     """
#     Escreve o cabeçalho do lote no arquivo CNAB240.
#     """
#     hoje = datetime.today()
#     lote = (
#         "00100011R01 0002" + "21545238000172" + "003059740001417019"
#         + ("TS" if is_remessateste else "  ")
#         + f"0000510000002827271 FUNDO DE DESENVOLVIMENTO DE CA"
#         + " " * 40 + " " * 40 + f"{str(ultenviobanco).zfill(8)}{hoje.strftime('%d%m%Y')}0" * 8 + "\n"
#     )
#     arquivo.write(lote)
#
#
# def escrever_detalhe_remessa(arquivo, r, ultnossonumero, seqregistro):
#     """
#     Escreve os detalhes da remessa (linhas P, Q e R) para cada registro.
#     """
#     seqregistro += 1
#     detalhe_p = f"00100013{str(seqregistro).zfill(5)}P 01 0000510000002827271 {ultnossonumero}11111{r.dtvencimento.strftime('%d%m%Y')}"
#     detalhe_p += f"{str(r.valorparcela).replace('.', '').zfill(15)}02N{r.dtemissao.strftime('%d%m%Y')}100" + "0" * 65 + "\n"
#     arquivo.write(detalhe_p)
#
#     seqregistro += 1
#     qsprocesso = Processo.objects.get(pk=r.processo_id)
#     cliente = qsprocesso.cliente
#     cpf_formatado = cliente.numcpf.translate(str.maketrans('', '', '.-')).zfill(15)
#     detalhe_q = f"00100013{str(seqregistro).zfill(5)}Q 01 1{cpf_formatado}{cliente.nome.ljust(40)}{cliente.logradouro[:40]}"
#     detalhe_q += f"{cliente.bairro[:15]}{cliente.cep[:5]}{cliente.cep[6:]}{cliente.cidade.nome[:15]}{cliente.cidade.uf}0" + " " * 105 + "\n"
#     arquivo.write(detalhe_q)
#
#     seqregistro += 1
#     detalhe_r = f"00100013{str(seqregistro).zfill(5)}R 01 0" + "0" * 65 + f"{r.dtvencimento.strftime('%d%m%Y')}000000000000200"
#     detalhe_r += "FUNDECAM - FUNDO DE DESENV. DE CAMPOS" + " " * 140 + "\n"
#     arquivo.write(detalhe_r)
#
#     return seqregistro
#
#
# def escrever_trailer_lote(arquivo, seqregistro):
#     """
#     Escreve o trailer do lote no arquivo CNAB240.
#     """
#     trailer_lote = f"00100015{' ' * 9}{str(seqregistro + 2).zfill(6)}{'0' * 217}\n"
#     arquivo.write(trailer_lote)
#
#
# def escrever_trailer_arquivo(arquivo, seqregistro):
#     """
#     Escreve o trailer do arquivo no arquivo CNAB240.
#     """
#     trailer_arquivo = f"00199999{' ' * 9}000001{str(seqregistro + 4).zfill(6)}{'0' * 6}{' ' * 205}\n"
#     arquivo.write(trailer_arquivo)
#
#
# def atualizar_financeiro(r, ultenviobanco, ultnossonumero):
#     """
#     Atualiza o registro financeiro com os números de envio e 'nosso número'.
#     """
#     financeiro = get_object_or_404(Financeiro, pk=r.id)
#     financeiro.numenvio = ultenviobanco
#     financeiro.nossonumero = ultnossonumero
#     financeiro.dtgravacao = datetime.today()
#     financeiro.data_edicao = datetime.today()
#     financeiro.save()


# def simulacaoemprestimo(request):
#     template_name1 = "financeiro/simulacaoemprestimo_tela.html"
#     form = SimulacaoEmprestimoForm(data=request.POST or None)
#     if request.method == 'POST':
#         if form.is_valid():
#             messages.success(request, 'Processo de simulação/orçamento realizado com sucesso.')
#         else:
#             messages.warning(request, showmessages_error(form=form))
#     return render(request, template_name1, dict(form=form, qs=None))

def simulacao_emprestimo(request):
    """
    View para processar e renderizar o formulário de simulação de empréstimo.

    Args:
        request (HttpRequest): Objeto de requisição HTTP.

    Returns:
        HttpResponse: Resposta renderizada com o formulário e mensagens apropriadas.
    """
    # Nome do template utilizado para renderização
    template_name = "financeiro/simulacaoemprestimo_tela.html"

    # Inicializa o formulário com dados do POST ou vazio
    form = SimulacaoEmprestimoForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            # Lógica de sucesso (simulação realizada com sucesso)
            messages.success(request, 'Processo de simulação/orçamento realizado com sucesso.')
            # Opcional: Adicione lógica adicional, como salvar os dados ou redirecionar.
        else:
            # Mensagens de erro com os detalhes de validação do formulário
            messages.warning(request, showmessages_error(form=form))

    # Renderiza a página com o formulário e quaisquer informações adicionais (qs pode ser usado no futuro)
    context = {
        'form': form,
        'qs': None,  # Exemplo para futuro uso (substitua conforme necessidade)
    }

    return render(request, template_name, context)

