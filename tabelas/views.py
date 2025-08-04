from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (View, CreateView, UpdateView, ListView, TemplateView)
from django_filters.views import FilterView

from django.urls import reverse_lazy

from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages

from tabelas.models import *
from processos.models import *

from tabelas.forms import *

from .filters import (BancoFilter, CidadeFilter, FeriadoFilter, BairroFilter, EstadoCivilFilter, GrauRelacaoFilter,
                      RegimeBensFilter, LinhaCreditoFilter, FinalidadeCreditoFilter, SetorNegocioFilter,
                      RamoAtividadeFilter, ProfissaoFilter, SituacaoPessoaFilter, TipoFonteReferFilter,
                      LocalizacaoFilter, VeiculoFilter, LogFilter)

# *** Utilizando o xhtml2pdf ***
from processos.utils import render_to_pdf, showmessages_error

from datetime import datetime

const_paginacao = 15
mostra_excluidos = True


class ConstrucaoView(TemplateView):
    template_name = "construcao/construcao.html"


# class ConfiguracaoListView(ListView):
#     """
#     View para listar todas as configurações, incluindo as excluídas (não filtradas).
#     """
#     queryset = Configuracao.objects.all()
#     template_name = "configuracoes/configuracoes_list.html"
#     paginate_by = const_paginacao
#
#     def get_context_data(self, **kwargs):
#         """
#         Adiciona informações extras ao contexto, se necessário, como título ou filtros.
#         """
#         context = super().get_context_data(**kwargs)
#         context["title"] = "Lista de Configurações"
#         return context
#
#
# class ConfiguracaoCreateView(SuccessMessageMixin, CreateView):
#     """
#     View para criar uma nova configuração.
#     """
#     model = Configuracao
#     form_class = ConfiguracaoForm
#     success_url = reverse_lazy('configuracoes-list')  # Redireciona para a lista de configurações
#     success_message = "Configuração criada com sucesso"
#     template_name = "configuracoes/edit_configuracao.html"
#
#     def get_context_data(self, **kwargs):
#         """
#         Adiciona informações extras ao contexto, como título e botão de ação.
#         """
#         context = super().get_context_data(**kwargs)
#         context["title"] = 'Nova Configuração'
#         context["savebtn"] = 'Adicionar'
#         return context
#
#     def form_invalid(self, form):
#         """
#         Exibe uma mensagem de erro quando o formulário for inválido.
#         """
#         messages.warning(self.request, showmessages_error(form))
#         return self.render_to_response(self.get_context_data())
#
#
# class ConfiguracaoUpdateView(SuccessMessageMixin, UpdateView):
#     """
#     View para atualizar os dados de uma configuração existente.
#     """
#     model = Configuracao
#     form_class = ConfiguracaoForm
#     success_url = reverse_lazy('configuracoes-list')
#     success_message = "Dados da configuração atualizados com sucesso"
#     template_name = "configuracoes/edit_configuracao.html"
#
#     def get_context_data(self, **kwargs):
#         """
#         Adiciona informações extras ao contexto, como título, botão de salvar e excluir.
#         """
#         context = super().get_context_data(**kwargs)
#         context["title"] = 'Editar Configuração'
#         context["savebtn"] = 'Salvar'
#         context["delbtn"] = 'Excluir'
#         return context
#
#     def form_invalid(self, form):
#         """
#         Exibe uma mensagem de erro quando o formulário for inválido.
#         """
#         messages.warning(self.request, showmessages_error(form))
#         return self.render_to_response(self.get_context_data())
#
#
# class ConfiguracaoDeleteView(View):
#     """
#     View para excluir uma configuração existente.
#     """
#     template_name = "configuracoes/delete_configuracao.html"
#     success_message = "Configuração excluída com sucesso"
#
#     def get(self, request, pk):
#         """
#         Exibe a tela de confirmação de exclusão para a configuração especificada.
#         """
#         configuracao = get_object_or_404(Configuracao, pk=pk)
#         return render(request, self.template_name, {'object': configuracao})
#
#     def post(self, request, pk):
#         """
#         Realiza a exclusão da configuração especificada.
#         """
#         configuracao = get_object_or_404(Configuracao, pk=pk)
#         configuracao.is_deleted = True
#         configuracao.save()
#
#         # Mensagem de sucesso após exclusão
#         messages.success(request, self.success_message)
#
#         # Redireciona para a lista de configurações
#         return redirect('configuracoes-list')


class ConfigListView(ListView):
    """
    View para listar todas as configurações, incluindo as excluídas (não filtradas).
    """
    queryset = Config.objects.all()
    template_name = "configs/configs_list.html"
    paginate_by = const_paginacao

    def get_context_data(self, **kwargs):
        """
        Adiciona informações extras ao contexto, se necessário, como título ou filtros.
        """
        context = super().get_context_data(**kwargs)
        context["title"] = "Lista de Configurações"
        return context


class ConfigCreateView(SuccessMessageMixin, CreateView):
    """
    View para criar uma nova configuração.
    """
    model = Config
    form_class = ConfigForm
    success_url = reverse_lazy('configs-list')  # Redireciona para a lista de configurações
    success_message = "Configuração criada com sucesso"
    template_name = "configs/edit_config.html"

    def get_context_data(self, **kwargs):
        """
        Adiciona informações extras ao contexto, como título e botão de ação.
        """
        context = super().get_context_data(**kwargs)
        context["title"] = 'Nova Configuração'
        context["savebtn"] = 'Adicionar'
        return context

    def form_invalid(self, form):
        """
        Exibe uma mensagem de erro quando o formulário for inválido.
        """
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())


class ConfigUpdateView(SuccessMessageMixin, UpdateView):
    """
    View para atualizar os dados de uma configuração existente.
    """
    model = Config
    form_class = ConfigForm
    success_url = reverse_lazy('configs-list')
    success_message = "Dados da configuração atualizados com sucesso"
    template_name = "configs/edit_config.html"

    def get_context_data(self, **kwargs):
        """
        Adiciona informações extras ao contexto, como título, botão de salvar e excluir.
        """
        context = super().get_context_data(**kwargs)
        context["title"] = 'Editar Configuração'
        context["savebtn"] = 'Salvar'
        context["delbtn"] = 'Excluir'
        return context

    def form_invalid(self, form):
        """
        Exibe uma mensagem de erro quando o formulário for inválido.
        """
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())


class ConfigDeleteView(View):
    """
    View para excluir uma configuração existente.
    """
    template_name = "configs/delete_config.html"
    success_message = "Configuração excluída com sucesso"

    def get(self, request, pk):
        """
        Exibe a tela de confirmação de exclusão para a configuração especificada.
        """
        config = get_object_or_404(Config, pk=pk)
        return render(request, self.template_name, {'object': config})

    def post(self, request, pk):
        """
        Realiza a exclusão da configuração especificada.
        """
        config = get_object_or_404(Config, pk=pk)
        config.is_deleted = True
        config.save()

        # Mensagem de sucesso após exclusão
        messages.success(request, self.success_message)

        # Redireciona para a lista de configurações
        return redirect('configs-list')


class FechamentoListView(ListView):
    """
    View para listar todas os fechamentos, incluindo os excluídos (não filtradas).
    """
    queryset = Fechamento.objects.all()
    template_name = "fechamentos/fechamentos_list.html"
    paginate_by = const_paginacao

    def get_context_data(self, **kwargs):
        """
        Adiciona informações extras ao contexto, se necessário, como título ou filtros.
        """
        context = super().get_context_data(**kwargs)
        context["title"] = "Lista de Fechamentos"
        return context


class FechamentoCreateView(SuccessMessageMixin, CreateView):
    """
    View para criar um novo Fechamento
    """
    model = Fechamento
    form_class = FechamentoForm
    success_url = reverse_lazy('fechamentos-list')  # Redireciona para a lista de fechamentos
    success_message = "Fechamento criado com sucesso"
    template_name = "fechamentos/edit_fechamento.html"

    def get_context_data(self, **kwargs):
        """
        Adiciona informações extras ao contexto, como título e botão de ação.
        """
        context = super().get_context_data(**kwargs)
        context["title"] = 'Novo Fechamento'
        context["savebtn"] = 'Adicionar'
        return context

    def form_invalid(self, form):
        """
        Exibe uma mensagem de erro quando o formulário for inválido.
        """
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())


class FechamentoUpdateView(SuccessMessageMixin, UpdateView):
    """
    View para atualizar as informações de um fechamento existente
    """
    model = Fechamento
    form_class = FechamentoForm
    success_url = reverse_lazy('fechamentos-list')  # Redireciona para a lista de fechamentos
    success_message = "Dados do fechamento atualizados com sucesso"
    template_name = "fechamentos/edit_fechamento.html"

    def get_context_data(self, **kwargs):
        """
        Adiciona informações extras ao contexto, como título, botão de salvar e excluir.
        """
        context = super().get_context_data(**kwargs)
        context["title"] = 'Editar Fechamento'
        context["savebtn"] = 'Salvar'
        context["delbtn"] = 'Excluir'
        return context

    def form_invalid(self, form):
        """
        Exibe uma mensagem de erro quando o formulário for inválido.
        """
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())


class FechamentoDeleteView(View):
    """
    View para excluir um fechamento existente.
    """
    template_name = "fechamentos/delete_fechamento.html"
    success_message = "Fechamento excluído com sucesso"

    def get(self, request, pk):
        """
        Exibe a tela de confirmação para a exclusão de um fechamento.
        """
        fechamento = get_object_or_404(Fechamento, pk=pk)
        return render(request, self.template_name, {'object': fechamento})

    def post(self, request, pk):
        """
        Exclui o fechamento especificado e redireciona para a lista de fechamentos.
        """
        fechamento = get_object_or_404(Fechamento, pk=pk)
        fechamento.is_deleted = True
        fechamento.save()

        # Mensagem de sucesso após exclusão
        messages.success(request, self.success_message)

        # Redireciona para a lista de fechamentos
        return redirect('fechamentos-list')


class CidadeListView(FilterView):
    """
    View para listar as cidades, com filtragem opcional para mostrar ou ocultar as excluídas.
    """
    filterset_class = CidadeFilter
    template_name = "cidades/cidades_list.html"
    paginate_by = const_paginacao

    def get_queryset(self):
        """
        Retorna o queryset de cidades, com base no filtro de exclusão.
        Filtra cidades excluídas se o parâmetro 'mostra_excluidos' for False.
        """
        queryset = Cidade.objects.all()
        if not mostra_excluidos:
            queryset = queryset.filter(is_deleted=False)
        return queryset


class CidadeCreateView(SuccessMessageMixin, CreateView):
    """
    View para criar uma nova cidade.
    """
    model = Cidade
    form_class = CidadeForm
    success_url = reverse_lazy('cidades-list')  # Redireciona para a lista de cidades
    success_message = "Cidade criada com sucesso"
    template_name = "cidades/edit_cidade.html"

    def get_context_data(self, **kwargs):
        """
        Adiciona informações extras ao contexto, como título e botão de ação.
        """
        context = super().get_context_data(**kwargs)
        context["title"] = 'Nova Cidade'
        context["savebtn"] = 'Adicionar'
        return context

    def form_invalid(self, form):
        """
        Exibe uma mensagem de erro quando o formulário for inválido.
        """
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())


class CidadeUpdateView(SuccessMessageMixin, UpdateView):
    """
    View para atualizar as informações de uma cidade existente.
    """
    model = Cidade
    form_class = CidadeForm
    success_url = reverse_lazy('cidades-list')  # Redireciona para a lista de cidades
    success_message = "Dados da cidade atualizados com sucesso"
    template_name = "cidades/edit_cidade.html"

    def get_context_data(self, **kwargs):
        """
        Adiciona informações extras ao contexto, como título, botão de salvar e excluir.
        """
        context = super().get_context_data(**kwargs)
        context["title"] = 'Editar Cidade'
        context["savebtn"] = 'Salvar'
        context["delbtn"] = 'Excluir'
        return context

    def form_invalid(self, form):
        """
        Exibe uma mensagem de erro quando o formulário for inválido.
        """
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())


class CidadeDeleteView(View):
    """
    View para excluir uma cidade existente.
    """
    template_name = "cidades/delete_cidade.html"
    success_message = "Cidade excluída com sucesso"

    def get(self, request, pk):
        """
        Exibe a tela de confirmação para a exclusão de uma cidade.
        """
        cidade = get_object_or_404(Cidade, pk=pk)
        return render(request, self.template_name, {'object': cidade})

    def post(self, request, pk):
        """
        Exclui a cidade especificada e redireciona para a lista de cidades.
        """
        cidade = get_object_or_404(Cidade, pk=pk)
        cidade.is_deleted = True
        cidade.save()

        # Mensagem de sucesso após exclusão
        messages.success(request, self.success_message)

        # Redireciona para a lista de cidades
        return redirect('cidades-list')


# usado para listar todas os feriados
class FeriadoListView(FilterView):
    filterset_class = FeriadoFilter
    template_name = "feriados/feriados_list.html"
    if not mostra_excluidos:
        queryset = Feriado.objects.filter(is_deleted=False)
    else:
        queryset = Feriado.objects.all()
    paginate_by = const_paginacao


# usado para adicionar um novo feriado
# ----------------------------------------------------------------
class FeriadoCreateView(SuccessMessageMixin, CreateView):
    model = Feriado
    form_class = FeriadoForm
    success_url = '/tabelas/feriados'
    success_message = "Feriado criado com sucesso"
    template_name = "feriados/edit_feriado.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Novo Feriado'
        context["savebtn"] = 'Adiciona'
        return context

    def form_invalid(self, form):
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())


# usado para atualizar as informações de um feriado
# ----------------------------------------------------------------
class FeriadoUpdateView(SuccessMessageMixin, UpdateView):
    model = Feriado
    form_class = FeriadoForm
    success_url = '/tabelas/feriados'
    success_message = "Dados do feriado atualizados com sucesso"
    template_name = "feriados/edit_feriado.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Edita Feriado'
        context["savebtn"] = 'Salva'
        context["delbtn"] = 'Apaga'
        return context

    def form_invalid(self, form):
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())


# usado para excluir um feriado
# ----------------------------------------------------------------
class FeriadoDeleteView(View):
    template_name = "feriados/delete_feriado.html"
    success_message = "Feriado excluído com sucesso"

    def get(self, request, pk):
        feriado = get_object_or_404(Feriado, pk=pk)
        return render(request, self.template_name, {'object': feriado})

    def post(self, request, pk):
        feriado = get_object_or_404(Feriado, pk=pk)
        feriado.is_deleted = True
        feriado.save()
        messages.success(request, self.success_message)
        return redirect('feriados-list')


# usado para listar todas os bairros que não estejam com o flag de registro apagado
class BairroListView(FilterView):
    filterset_class = BairroFilter
    template_name = "bairros/bairros_list.html"
    if not mostra_excluidos:
        queryset = Bairro.objects.filter(is_deleted=False)
    else:
        queryset = Bairro.objects.all()
    paginate_by = const_paginacao


# usado para adicionar um novo bairro
# ----------------------------------------------------------------
class BairroCreateView(SuccessMessageMixin, CreateView):
    model = Bairro
    form_class = BairroForm
    success_url = '/tabelas/bairros'
    template_name = "bairros/edit_bairro.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Novo Bairro'
        context["savebtn"] = 'Adiciona'
        return context

    def form_valid(self, form):
        messages.success(self.request, "Dados do bairro " + form.instance.nome + " inseridos com sucesso.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())

# usado para atualizar as informações de um bairro
# ----------------------------------------------------------------
class BairroUpdateView(SuccessMessageMixin, UpdateView):
    model = Bairro
    form_class = BairroForm
    success_url = '/tabelas/bairros'
    template_name = "bairros/edit_bairro.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Edita Bairro'
        context["savebtn"] = 'Salva'
        context["delbtn"] = 'Apaga'
        return context

    def form_valid(self, form):
        messages.success(self.request, "Dados do bairro " + form.instance.nome + " alterados com sucesso.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())

# usado para excluir um bairro
# ----------------------------------------------------------------
class BairroDeleteView(View):
    template_name = "bairros/delete_bairro.html"
    # success_message = "Bairro excluído com sucesso"

    def get(self, request, pk):
        bairro = get_object_or_404(Bairro, pk=pk)
        return render(request, self.template_name, {'object': bairro})

    def post(self, request, pk):
        bairro = get_object_or_404(Bairro, pk=pk)
        bairro.is_deleted = True
        bairro.save()
        messages.success(self.request, "Bairro " + bairro.nome + " excluído com sucesso.")
        # messages.success(request, self.success_message)
        return redirect('bairros-list')


# usado para listar todos os bancos que não estejam como o flag de exclusão
# -------------------------------------------------------------------------
class BancoListView(FilterView):
    filterset_class = BancoFilter
    template_name = "bancos/bancos_list.html"
    if not mostra_excluidos:
        queryset = Banco.objects.filter(is_deleted=False)
    else:
        queryset = Banco.objects.all()
    paginate_by = const_paginacao


# usado para adicionar um novo banco
# ----------------------------------------------------------------
class BancoCreateView(SuccessMessageMixin, CreateView):
    model = Banco
    form_class = BancoForm
    success_url = '/tabelas/bancos'
    template_name = "bancos/edit_banco.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Novo Banco'
        context["savebtn"] = 'Adiciona'
        return context

    def form_valid(self, form):
        messages.success(self.request, "Dados do banco " + form.instance.nome + " inseridos com sucesso.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())


# usado para atualizar as informações de um banco
# ----------------------------------------------------------------
class BancoUpdateView(SuccessMessageMixin, UpdateView):
    model = Banco
    form_class = BancoForm
    success_url = '/tabelas/bancos'
    template_name = "bancos/edit_banco.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Edita Banco'
        context["savebtn"] = 'Salva'
        context["delbtn"] = 'Apaga'
        return context

    def form_valid(self, form):
        messages.success(self.request, "Dados do banco " + form.instance.nome + " atualizados com sucesso.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())


# usado para excluir um banco
# ----------------------------------------------------------------
class BancoDeleteView(View):
    template_name = "bancos/delete_banco.html"
    # success_message = "Banco excluído com sucesso"

    def get(self, request, pk):
        banco = get_object_or_404(Banco, pk=pk)
        return render(request, self.template_name, {'object': banco})

    def post(self, request, pk):
        banco = get_object_or_404(Banco, pk=pk)
        banco.is_deleted = True
        banco.save()
        messages.success(self.request, "Banco " + banco.nome + " excluído com sucesso.")
        # messages.success(request, self.success_message)
        return redirect('bancos-list')


# usado para listar todos os registros da tabela
# ----------------------------------------------------------------
class EstadoCivilListView(FilterView):
    filterset_class = EstadoCivilFilter
    template_name = "estadoscivis/estadoscivis_list.html"
    if not mostra_excluidos:
        queryset = EstadoCivil.objects.filter(is_deleted=False)
    else:
        queryset = EstadoCivil.objects.all()
    paginate_by = const_paginacao


# usado para adicionar um novo registro
# ----------------------------------------------------------------
class EstadoCivilCreateView(SuccessMessageMixin, CreateView):
    model = EstadoCivil
    form_class = EstadoCivilForm
    success_url = '/tabelas/estadoscivis'
    template_name = "estadoscivis/edit_estadocivil.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Novo Estado Civil'
        context["savebtn"] = 'Adiciona'
        return context

    def form_valid(self, form):
        messages.success(self.request, "Dados do estado civil  " + form.instance.nome + " inseridos com sucesso.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())


# usado para atualizar as informações de um estado civil
# ----------------------------------------------------------------
class EstadoCivilUpdateView(SuccessMessageMixin, UpdateView):
    model = EstadoCivil
    form_class = EstadoCivilForm
    success_url = '/tabelas/estadoscivis'
    template_name = "estadoscivis/edit_estadocivil.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Edita Estado Civil'
        context["savebtn"] = 'Salva'
        context["delbtn"] = 'Apaga'
        return context

    def form_valid(self, form):
        messages.success(self.request, "Dados do estado civil  " + form.instance.nome + " atualizados com sucesso.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())


# usado para excluir um registro
# ----------------------------------------------------------------
class EstadoCivilDeleteView(View):
    template_name = "estadoscivis/delete_estadocivil.html"
    # success_message = "Estado civil excluído com sucesso"

    def get(self, request, pk):
        estadocivil = get_object_or_404(EstadoCivil, pk=pk)
        return render(request, self.template_name, {'object': estadocivil})

    def post(self, request, pk):
        estadocivil = get_object_or_404(EstadoCivil, pk=pk)
        estadocivil.is_deleted = True
        estadocivil.save()
        messages.success(request, "Estado civil " + estadocivil.nome + " excluído com sucesso.")
        return redirect('estadoscivis-list')


# usado para listar todos os registros da tabela
# ----------------------------------------------------------------
class RegimeBensListView(FilterView):
    filterset_class = RegimeBensFilter
    template_name = "regimesbens/regimesbens_list.html"
    if not mostra_excluidos:
        queryset = RegimeBens.objects.filter(is_deleted=False)
    else:
        queryset = RegimeBens.objects.all()
    paginate_by = const_paginacao


# usado para adicionar um novo registro
# ----------------------------------------------------------------
class RegimeBensCreateView(SuccessMessageMixin, CreateView):
    model = RegimeBens
    form_class = RegimeBensForm
    success_url = '/tabelas/regimesbens'
    template_name = "regimesbens/edit_regimebens.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Novo Regime de Bens'
        context["savebtn"] = 'Adiciona'
        return context

    def form_valid(self, form):
        messages.success(self.request, "Dados do regime de bens " + form.instance.nome + " inseridos com sucesso.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())


# usado para atualizar as informações de um registro de bens
# ----------------------------------------------------------------
class RegimeBensUpdateView(SuccessMessageMixin, UpdateView):
    model = RegimeBens
    form_class = RegimeBensForm
    success_url = '/tabelas/regimesbens'
    template_name = "regimesbens/edit_regimebens.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Edita Regime de Bens'
        context["savebtn"] = 'Salva'
        context["delbtn"] = 'Apaga'
        return context

    def form_valid(self, form):
        messages.success(self.request, "Dados do regime de bens " + form.instance.nome + " atualizados com sucesso.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())


# usado para excluir um registro
# ----------------------------------------------------------------
class RegimeBensDeleteView(View):
    template_name = "regimesbens/delete_regimebens.html"

    def get(self, request, pk):
        regimebens = get_object_or_404(RegimeBens, pk=pk)
        return render(request, self.template_name, {'object': regimebens})

    def post(self, request, pk):
        regimebens = get_object_or_404(RegimeBens, pk=pk)
        regimebens.is_deleted = True
        regimebens.save()
        messages.success(request, "Regime de bens " + regimebens.nome + " excluído com sucesso.")
        return redirect('regimesbens-list')


# usado para listar todos os registros da tabela
# ----------------------------------------------------------------
class LinhaCreditoListView(FilterView):
    filterset_class = LinhaCreditoFilter
    template_name = "linhascredito/linhascredito_list.html"
    if not mostra_excluidos:
        queryset = LinhaCredito.objects.filter(is_deleted=False)
    else:
        queryset = LinhaCredito.objects.all()
    paginate_by = const_paginacao


# usado para adicionar um novo registro
# ----------------------------------------------------------------
class LinhaCreditoCreateView(SuccessMessageMixin, CreateView):
    model = LinhaCredito
    form_class = LinhaCreditoForm
    success_url = '/tabelas/linhascredito'
    template_name = "linhascredito/edit_linhacredito.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Nova Linha de Crédito'
        context["savebtn"] = 'Adiciona'
        return context

    def form_valid(self, form):
        messages.success(self.request, "Dados da linha de crédito " + form.instance.nome + " inseridos com sucesso.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())


# usado para atualizar as informações de uma linha de crédito
# ----------------------------------------------------------------
class LinhaCreditoUpdateView(SuccessMessageMixin, UpdateView):
    model = LinhaCredito
    form_class = LinhaCreditoForm
    success_url = '/tabelas/linhascredito'
    template_name = "linhascredito/edit_linhacredito.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Edita Linha de Crédito'
        context["savebtn"] = 'Salva'
        context["delbtn"] = 'Apaga'
        return context

    def form_valid(self, form):
        messages.success(self.request, "Dados da linha de crédito " + form.instance.nome + " atualizados com sucesso.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())


# usado para excluir um registro
# ----------------------------------------------------------------
class LinhaCreditoDeleteView(View):
    template_name = "linhascredito/delete_linhacredito.html"

    def get(self, request, pk):
        linhacredito = get_object_or_404(LinhaCredito, pk=pk)
        return render(request, self.template_name, {'object': linhacredito})

    def post(self, request, pk):
        linhacredito = get_object_or_404(LinhaCredito, pk=pk)
        linhacredito.is_deleted = True
        linhacredito.save()
        messages.success(request, "Linha de crédito " + linhacredito.nome + " excluída com sucesso.")
        return redirect('linhascredito-list')


# usado para listar todos os registros da tabela
# ----------------------------------------------------------------
class FinalidadeCreditoListView(FilterView):
    filterset_class = FinalidadeCreditoFilter
    template_name = "finalidadescredito/finalidadescredito_list.html"
    if not mostra_excluidos:
        queryset = FinalidadeCredito.objects.filter(is_deleted=False)
    else:
        queryset = FinalidadeCredito.objects.all()
    paginate_by = const_paginacao


# usado para adicionar um novo registro
# ----------------------------------------------------------------
class FinalidadeCreditoCreateView(SuccessMessageMixin, CreateView):
    model = FinalidadeCredito
    form_class = FinalidadeCreditoForm
    success_url = '/tabelas/finalidadescredito'
    template_name = "finalidadescredito/edit_finalidadecredito.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Nova Finalidade do Crédito'
        context["savebtn"] = 'Adiciona'
        return context

    def form_valid(self, form):
        messages.success(self.request, "Dados da finalidade de crédito " + form.instance.nome + " inseridos com sucesso.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())


# usado para atualizar as informações de uma linha de crédito
# ----------------------------------------------------------------
class FinalidadeCreditoUpdateView(SuccessMessageMixin, UpdateView):
    model = FinalidadeCredito
    form_class = FinalidadeCreditoForm
    success_url = '/tabelas/finalidadescredito'
    template_name = "finalidadescredito/edit_finalidadecredito.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Edita Finalidade do Crédito'
        context["savebtn"] = 'Salva'
        context["delbtn"] = 'Apaga'
        return context

    def form_valid(self, form):
        messages.success(self.request, "Dados da finalidade de crédito " + form.instance.nome + " atualizados com sucesso.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())


# usado para excluir um registro
# ----------------------------------------------------------------
class FinalidadeCreditoDeleteView(View):
    template_name = "finalidadescredito/delete_finalidadecredito.html"

    def get(self, request, pk):
        finalidadecredito = get_object_or_404(FinalidadeCredito, pk=pk)
        return render(request, self.template_name, {'object': finalidadecredito})

    def post(self, request, pk):
        finalidadecredito = get_object_or_404(FinalidadeCredito, pk=pk)
        finalidadecredito.is_deleted = True
        finalidadecredito.save()
        messages.success(request, "Finalidade de crédito " + finalidadecredito.nome + " excluída com sucesso.")
        return redirect('finalidadescredito-list')


# usado para listar todos os registros da tabela
# ----------------------------------------------------------------
class SetorNegocioListView(FilterView):
    filterset_class = SetorNegocioFilter
    template_name = "setoresnegocio/setoresnegocio_list.html"
    if not mostra_excluidos:
        queryset = SetorNegocio.objects.filter(is_deleted=False)
    else:
        queryset = SetorNegocio.objects.all()
    paginate_by = const_paginacao


# usado para adicionar um novo registro
# ----------------------------------------------------------------
class SetorNegocioCreateView(SuccessMessageMixin, CreateView):
    model = SetorNegocio
    form_class = SetorNegocioForm
    success_url = '/tabelas/setoresnegocio'
    template_name = "setoresnegocio/edit_setornegocio.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Novo Setor de Negócio'
        context["savebtn"] = 'Adiciona'
        return context

    def form_valid(self, form):
        messages.success(self.request, "Dados do setor de negócio " + form.instance.nome + " inseridos com sucesso.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())


# usado para atualizar as informações de um setor de negócio
# ----------------------------------------------------------------
class SetorNegocioUpdateView(SuccessMessageMixin, UpdateView):
    model = SetorNegocio
    form_class = SetorNegocioForm
    success_url = '/tabelas/setoresnegocio'
    template_name = "setoresnegocio/edit_setornegocio.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Edita Setor de Negócio'
        context["savebtn"] = 'Salva'
        context["delbtn"] = 'Apaga'
        return context

    def form_valid(self, form):
        messages.success(self.request, "Dados do setor de negócio " + form.instance.nome + " atualizados com sucesso.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())


# usado para excluir um registro
# ----------------------------------------------------------------
class SetorNegocioDeleteView(View):
    template_name = "setoresnegocio/delete_setornegocio.html"

    def get(self, request, pk):
        setornegocio = get_object_or_404(SetorNegocio, pk=pk)
        return render(request, self.template_name, {'object': setornegocio})

    def post(self, request, pk):
        setornegocio = get_object_or_404(SetorNegocio, pk=pk)
        setornegocio.is_deleted = True
        setornegocio.save()
        messages.success(request, "Setor de negócio " + setornegocio.nome + " excluído com sucesso.")
        return redirect('setoresnegocio-list')


# usado para listar todos os registros da tabela
# ----------------------------------------------------------------
class RamoAtividadeListView(ListView):
    template_name = "ramosatividade/ramosatividade_list.html"

    def queryset(self):
        if not mostra_excluidos:
            queryset = RamoAtividade.objects.filter(is_deleted=False)
        else:
            queryset = RamoAtividade.objects.all()
        return queryset


# usado para adicionar um novo registro
# ----------------------------------------------------------------
class RamoAtividadeCreateView(SuccessMessageMixin, CreateView):
    model = RamoAtividade
    form_class = RamoAtividadeForm
    success_url = '/tabelas/ramosatividade'
    template_name = "ramosatividade/edit_ramoatividade.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Novo Ramo de Atividade'
        context["savebtn"] = 'Adiciona'
        return context

    def form_valid(self, form):
        messages.success(self.request, "Dados do ramo de atividade " + form.instance.nome + " inseridos com sucesso.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())


# usado para atualizar as informações de um ramo de atividade
# ----------------------------------------------------------------
class RamoAtividadeUpdateView(SuccessMessageMixin, UpdateView):
    model = RamoAtividade
    form_class = RamoAtividadeForm
    success_url = '/tabelas/ramosatividade'
    template_name = "ramosatividade/edit_ramoatividade.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Edita Ramo de Atividade'
        context["savebtn"] = 'Salva'
        context["delbtn"] = 'Apaga'
        return context

    def form_valid(self, form):
        messages.success(self.request, "Dados do ramo de atividade " + form.instance.nome + " atualizados com sucesso.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())


# usado para excluir um registro
# ----------------------------------------------------------------
class RamoAtividadeDeleteView(View):
    template_name = "ramosatividade/delete_ramoatividade.html"

    def get(self, request, pk):
        ramoatividade = get_object_or_404(RamoAtividade, pk=pk)
        return render(request, self.template_name, {'object': ramoatividade})

    def post(self, request, pk):
        ramoatividade = get_object_or_404(RamoAtividade, pk=pk)
        ramoatividade.is_deleted = True
        ramoatividade.save()
        messages.success(request, "Ramo de atividade " + ramoatividade.nome + " excluído com sucesso.")
        return redirect('ramosatividade-list')


# usado para listar todos os registros da tabela
# ----------------------------------------------------------------
class ProfissaoListView(ListView):
    template_name = "profissoes/profissoes_list.html"

    def queryset(self):
        if not mostra_excluidos:
            queryset = Profissao.objects.filter(is_deleted=False)
        else:
            queryset = Profissao.objects.all()

        return queryset


# usado para adicionar um novo registro
# ----------------------------------------------------------------
class ProfissaoCreateView(SuccessMessageMixin, CreateView):
    model = Profissao
    form_class = ProfissaoForm
    success_url = '/tabelas/profissoes'
    template_name = "profissoes/edit_profissao.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Nova Profissão'
        context["savebtn"] = 'Adiciona'
        return context

    def form_valid(self, form):
        messages.success(self.request, "Dados da profissão " + form.instance.nome + " inseridos com sucesso.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())

# usado para atualizar as informações de um ramo de atividade
# ----------------------------------------------------------------
class ProfissaoUpdateView(SuccessMessageMixin, UpdateView):
    model = Profissao
    form_class = ProfissaoForm
    success_url = '/tabelas/profissoes'
    template_name = "profissoes/edit_profissao.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Edita Profissão'
        context["savebtn"] = 'Salva'
        context["delbtn"] = 'Apaga'
        return context

    def form_valid(self, form):
        messages.success(self.request, "Dados da profissão " + form.instance.nome + " atualizados com sucesso.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())


# usado para excluir um registro
# ----------------------------------------------------------------
class ProfissaoDeleteView(View):
    template_name = "profissoes/delete_profissao.html"

    def get(self, request, pk):
        profissao = get_object_or_404(Profissao, pk=pk)
        return render(request, self.template_name, {'object': profissao})

    def post(self, request, pk):
        profissao = get_object_or_404(Profissao, pk=pk)
        profissao.is_deleted = True
        profissao.save()
        messages.success(request, "Profissão " + profissao.nome + " excluída com sucesso.")
        return redirect('profissoes-list')


# usado para listar todos os registros da tabela
# ----------------------------------------------------------------
class VeiculoListView(ListView):
    template_name = "veiculos/veiculos_list.html"

    def queryset(self):
        if not mostra_excluidos:
            queryset = Veiculo.objects.filter(is_deleted=False)
        else:
            queryset = Veiculo.objects.all()
        return queryset


# usado para adicionar um novo registro
# ----------------------------------------------------------------
class VeiculoCreateView(SuccessMessageMixin, CreateView):
    model = Veiculo
    form_class = VeiculoForm
    success_url = '/tabelas/veiculos'
    template_name = "veiculos/edit_veiculo.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Novo Veículo'
        context["savebtn"] = 'Adiciona'
        return context

    def form_valid(self, form):
        messages.success(self.request, "Dados do veículo " + form.instance.marca.nome + " " + form.instance.modelo
                         + " inseridos com sucesso.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())

# usado para atualizar as informações de um veículo
# ----------------------------------------------------------------
class VeiculoUpdateView(SuccessMessageMixin, UpdateView):

    model = Veiculo
    form_class = VeiculoForm
    success_url = '/tabelas/veiculos'
    template_name = "veiculos/edit_veiculo.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Edita Veículo'
        context["savebtn"] = 'Salva'
        context["delbtn"] = 'Apaga'
        return context

    def form_valid(self, form):
        messages.success(self.request, "Dados do veículo " + form.instance.marca.nome + " " + form.instance.modelo
                         + " atualizados com sucesso.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())


# usado para excluir um registro
# ----------------------------------------------------------------
class VeiculoDeleteView(View):

    # template_name = "veiculos/delete_veiculo.html"
    def get(self, request, pk):
        veiculo = get_object_or_404(Veiculo, pk=pk)
        return render(request, self.template_name, {'object': veiculo})

    def post(self, request, pk):
        veiculo = get_object_or_404(Veiculo, pk=pk)
        veiculo.is_deleted = True
        veiculo.save()
        messages.success(request, "Veículo " + veiculo.marca.nome + " " + veiculo.modelo + " excluído com sucesso.")
        return redirect('veiculos-list')


# usado para listar todos os registros da tabela
# ----------------------------------------------------------------
class LocalizacaoListView(FilterView):
    filterset_class = LocalizacaoFilter
    template_name = "localizacoes/localizacoes_list.html"
    if not mostra_excluidos:
        queryset = Localizacao.objects.filter(is_deleted=False)
    else:
        queryset = Localizacao.objects.all()
    paginate_by = const_paginacao


# usado para adicionar um novo registro
# ----------------------------------------------------------------
class LocalizacaoCreateView(SuccessMessageMixin, CreateView):
    model = Localizacao
    form_class = LocalizacaoForm
    success_url = '/tabelas/localizacoes'
    template_name = "localizacoes/edit_localizacao.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Nova Localização'
        context["savebtn"] = 'Adiciona'
        return context

    def form_valid(self, form):
        messages.success(self.request, "Dados da localização " + form.instance.nome + " inseridos com sucesso.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())


# usado para atualizar as informações de uma localização
# ----------------------------------------------------------------
class LocalizacaoUpdateView(SuccessMessageMixin, UpdateView):
    model = Localizacao
    form_class = LocalizacaoForm
    success_url = '/tabelas/localizacoes'
    template_name = "localizacoes/edit_localizacao.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Edita Localização'
        context["savebtn"] = 'Salva'
        context["delbtn"] = 'Apaga'
        return context

    def form_valid(self, form):
        messages.success(self.request, "Dados da localização " + form.instance.nome + " atualizados com sucesso.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())


# usado para excluir um registro
# ----------------------------------------------------------------
class LocalizacaoDeleteView(View):
    template_name = "localizacoes/delete_localizacao.html"

    def get(self, request, pk):
        localizacao = get_object_or_404(Localizacao, pk=pk)
        return render(request, self.template_name, {'object': localizacao})

    def post(self, request, pk):
        localizacao = get_object_or_404(Localizacao, pk=pk)
        localizacao.is_deleted = True
        localizacao.save()
        messages.success(request, "Localização " + localizacao.nome + " excluída com sucesso.")
        return redirect('localizacoes-list')


# usado para listar todos os Logs CRUD das tabelas
class LogListView(FilterView):
    filterset_class = LogFilter
    template_name = "logs/logs_list.html"
    queryset = Log.objects.all().order_by("-history_date")
    # paginate_by = const_paginacao


def ResultList(request):
    template_name = "logs/logs_print.html"
    records = Log.objects.all().order_by("-history_date")

    return render_to_pdf(
        template_name,
        {
            "record": records,
            "user": request.user,
            "emissao": datetime.today(),
        },
    )


# usado para listar todos os registros da tabela
# ----------------------------------------------------------------
class GrauRelacaoListView(FilterView):
    filterset_class = GrauRelacaoFilter
    template_name = "grausrelacao/grausrelacao_list.html"
    if not mostra_excluidos:
        queryset = GrauRelacao.objects.filter(is_deleted=False)
    else:
        queryset = GrauRelacao.objects.all()
    paginate_by = const_paginacao


# usado para adicionar um novo registro
# ----------------------------------------------------------------
class GrauRelacaoCreateView(SuccessMessageMixin, CreateView):
    model = GrauRelacao
    form_class = GrauRelacaoForm
    success_url = '/tabelas/grausrelacao'
    template_name = "grausrelacao/edit_graurelacao.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Novo Grau de Relação'
        context["savebtn"] = 'Adiciona'
        return context

    def form_valid(self, form):
        messages.success(self.request, "Dados do grau de relação " + form.instance.nome + " inseridos com sucesso.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())

# usado para atualizar as informações de um estado civil
# ----------------------------------------------------------------
class GrauRelacaoUpdateView(SuccessMessageMixin, UpdateView):
    model = GrauRelacao
    form_class = GrauRelacaoForm
    success_url = '/tabelas/grausrelacao'
    template_name = "grausrelacao/edit_graurelacao.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Edita Grau de Relação'
        context["savebtn"] = 'Salva'
        context["delbtn"] = 'Apaga'
        return context

    def form_valid(self, form):
        messages.success(self.request, "Dados do grau de relação " + form.instance.nome + " alterados com sucesso.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())


# usado para excluir um registro
# ----------------------------------------------------------------
class GrauRelacaoDeleteView(View):
    template_name = "grausrelacao/delete_graurelacao.html"

    def get(self, request, pk):
        graurelacao = get_object_or_404(GrauRelacao, pk=pk)
        return render(request, self.template_name, {'object': graurelacao})

    def post(self, request, pk):
        graurelacao = get_object_or_404(GrauRelacao, pk=pk)
        graurelacao.is_deleted = True
        graurelacao.save()
        messages.success(request, "Grau de relação " + graurelacao.nome + " excluído com sucesso.")
        return redirect('grausrelacao-list')


# usado para listar todos os registros da tabela
# ----------------------------------------------------------------
class SituacaoPessoaListView(FilterView):
    filterset_class = SituacaoPessoaFilter
    template_name = "situacoespessoa/situacoespessoa_list.html"
    if not mostra_excluidos:
        queryset = SituacaoPessoa.objects.filter(is_deleted=False)
    else:
        queryset = SituacaoPessoa.objects.all()
    paginate_by = const_paginacao


# usado para adicionar um novo registro
# ----------------------------------------------------------------
class SituacaoPessoaCreateView(SuccessMessageMixin, CreateView):
    model = SituacaoPessoa
    form_class = SituacaoPessoaForm
    success_url = '/tabelas/situacoespessoa'
    template_name = "situacoespessoa/edit_situacaopessoa.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Nova Situação'
        context["savebtn"] = 'Adiciona'
        return context

    def form_valid(self, form):
        messages.success(self.request, "Dados da situação da pessoa " + form.instance.descricao + " inseridos com sucesso.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())

# usado para atualizar as informações de uma situação
# ----------------------------------------------------------------
class SituacaoPessoaUpdateView(SuccessMessageMixin, UpdateView):
    model = SituacaoPessoa
    form_class = SituacaoPessoaForm
    success_url = '/tabelas/situacoespessoa'
    template_name = "situacoespessoa/edit_situacaopessoa.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Edita Situação'
        context["savebtn"] = 'Salva'
        context["delbtn"] = 'Apaga'
        return context

    def form_valid(self, form):
        messages.success(self.request, "Dados da situação da pessoa " + form.instance.descricao + " atualizados com sucesso.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())


# usado para excluir um registro
# ----------------------------------------------------------------
class SituacaoPessoaDeleteView(View):
    template_name = "situacoespessoa/delete_situacaopessoa.html"

    def get(self, request, pk):
        situacaopessoa = get_object_or_404(SituacaoPessoa, pk=pk)
        return render(request, self.template_name, {'object': situacaopessoa})

    def post(self, request, pk):
        situacaopessoa = get_object_or_404(SituacaoPessoa, pk=pk)
        situacaopessoa.is_deleted = True
        situacaopessoa.save()
        messages.success(request, "Situação da pessoa " + situacaopessoa.descricao + " excluída com sucesso.")
        return redirect('situacoespessoa-list')


# usado para listar todos os registros da tabela
# ----------------------------------------------------------------
class TipoFonteReferListView(FilterView):
    filterset_class = TipoFonteReferFilter
    template_name = "tiposfonterefer/tiposfonterefer_list.html"
    if not mostra_excluidos:
        queryset = TipoFonteRefer.objects.filter(is_deleted=False)
    else:
        queryset = TipoFonteRefer.objects.all()
    paginate_by = const_paginacao


# usado para adicionar um novo registro
# ----------------------------------------------------------------
class TipoFonteReferCreateView(SuccessMessageMixin, CreateView):
    model = TipoFonteRefer
    form_class = TipoFonteReferForm
    success_url = '/tabelas/tiposfonterefer'
    template_name = "tiposfonterefer/edit_tipofonterefer.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Novo Tipo de Fonte'
        context["savebtn"] = 'Adiciona'
        return context

    def form_valid(self, form):
        messages.success(self.request, "Dados do tipo de fonte de referência " + form.instance.nome + " inseridos com sucesso.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())


# usado para atualizar as informações de um tipo de fonte de referência
# ----------------------------------------------------------------
class TipoFonteReferUpdateView(SuccessMessageMixin, UpdateView):
    model = TipoFonteRefer
    form_class = TipoFonteReferForm
    success_url = '/tabelas/tiposfonterefer'
    template_name = "tiposfonterefer/edit_tipofonterefer.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Edita Tipo de Fonte'
        context["savebtn"] = 'Salva'
        context["delbtn"] = 'Apaga'
        return context

    def form_valid(self, form):
        messages.success(self.request, "Dados do tipo de fonte de referência " + form.instance.nome + " atualizados com sucesso.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, showmessages_error(form))
        return self.render_to_response(self.get_context_data())


# usado para excluir um registro
# ----------------------------------------------------------------
class TipoFonteReferDeleteView(View):
    template_name = "tiposfonterefer/delete_tipofonterefer.html"

    def get(self, request, pk):
        tipofonterefer = get_object_or_404(TipoFonteRefer, pk=pk)
        return render(request, self.template_name, {'object': tipofonterefer})

    def post(self, request, pk):
        tipofonterefer = get_object_or_404(TipoFonteRefer, pk=pk)
        tipofonterefer.is_deleted = True
        tipofonterefer.save()
        messages.success(request, "Tipo de fonte de referência " + tipofonterefer.nome + " excluída com sucesso.")
        return redirect('tiposfonterefer-list')


class LogsMenuView(View):
    template_name = "logs/logsmenu.html"

    def get(self, request):

        context={}
        quantidade_logs = {}

        quantidade_logs['pessoasfisicas'] = HistoricalPessoaFisica.objects.filter(is_deleted=False).count()
        quantidade_logs['pessoasjuridicas'] = HistoricalPessoaJuridica.objects.filter(is_deleted=False).count()
        quantidade_logs['processos'] = HistoricalProcesso.objects.filter(is_deleted=False).count()
        quantidade_logs['negociacoes'] = HistoricalNegociacao.objects.filter(is_deleted=False).count()

        context['quantidade_logs'] = quantidade_logs

        return render(request, self.template_name, context)


class LogsPessoaFisicaView(View):
    template_name = "logs/logspessoafisica_list.html"

    def get(self, request):
        context={}
        queryset = HistoricalPessoaFisica.objects.all()
        context['logspessoa'] = queryset
        return render(request, self.template_name, context)


class LogsPessoaJuridicaView(View):
    template_name = "logs/logspessoajuridica_list.html"

    def get(self, request):
        context={}
        queryset = HistoricalPessoaJuridica.objects.all()
        context['logspessoa'] = queryset
        return render(request, self.template_name, context)


class LogsProcessoView(View):
    template_name = "logs/logsprocesso_list.html"

    def get(self, request):
        context={}
        queryset = HistoricalProcesso.objects.all()
        context['logs'] = queryset
        return render(request, self.template_name, context)



