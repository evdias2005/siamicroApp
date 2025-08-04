from django.urls import path
from . import views
from .views import handler404, handler500

urlpatterns = [

    # Clientes e Avalistas
    path('pessoasjuridicas/', views.PessoaJuridicaListView.as_view(), name='pessoasjuridicas-list'),
    path('pessoasjuridicas/new', views.PessoaJuridicaCreateView.as_view(), name='new-pessoajuridica'),
    path('pessoasjuridicas/<pk>/edit', views.PessoaJuridicaUpdateView.as_view(), name='edit-pessoajuridica'),
    path('pessoasjuridicas/<pk>/delete', views.PessoaJuridicaDeleteView.as_view(), name='delete-pessoajuridica'),

    # Empresas
    path('pessoasfisicas/', views.PessoaFisicaListView.as_view(), name='pessoasfisicas-list'),
    path('pessoasfisicas/new', views.PessoaFisicaCreateView.as_view(), name='new-pessoafisica'),
    path('pessoasfisicas/<pk>/edit', views.PessoaFisicaUpdateView.as_view(), name='edit-pessoafisica'),
    path('pessoasfisicas/<pk>/delete', views.PessoaFisicaDeleteView.as_view(), name='delete-pessoafisica'),

    # Processos
    path('processos/', views.ProcessoListView.as_view(), name='processos-list'),
    path('processos/movlist', views.ProcessoMovListView.as_view(), name='processosmov-list'),
    # path('processos/movlist', views.processosmovimentar_list, name='processosmov-list'),
    path('processos/<pk>/movimentacoeslist', views.ProcessoMovimentacoesListView.as_view(),
         name='processomovimentacoes-list'),

    path('processos/listpendentes', views.ProcessosPendentesListView.as_view(), name='processospendentes-list'),
    path('processos/newpf', views.ProcessoPFCreateView.as_view(), name='new-processopf'),
    path('processos/<pk>/editpf', views.ProcessoPFUpdateView.as_view(), name='edit-processopf'),
    path('processos/newpj', views.ProcessoPJCreateView.as_view(), name='new-processopj'),
    path('processos/<pk>/editpj', views.ProcessoPJUpdateView.as_view(), name='edit-processopj'),
    # path('processos/<pk>/delete', views.ProcessoDeleteView.as_view(), name='delete-processo'),
    # path('processos/<pk>/cancel', views.ProcessoCancelView.as_view(), name='cancel-processo'),
    path('processos/<pk>/print', views.fichaclientelist, name='print-fichacliente'),
    path('processos/<pk>/print1', views.contratolist, name='print-contrato'),
    path('processos/<pk>/print2', views.parecerlist, name='print-parecer'),
    path('processos/<pk>/print4', views.fichaavalistalist, name='print-fichaavalista'),
    path('processos/<pk>/print5', views.autorizacaolist, name='print-autorizacao'),
    path('processos/view1', views.ProcessoaNegociarListView.as_view(), name='processoanegociar-list'),
    path('atualizar-outros-dados-processo/<int:pk>/', views.atualizar_outros_dados_processo,
         name='atualizar_outros_dados_processo'),
    path('cancelar-processo/<int:pk>/', views.cancelar_processo, name='cancelar_processo'),
    path('apagar-processo/<int:pk>/', views.apagar_processo, name='apagar_processo'),

    # Avalistas
    # path('processoavalistas/<pk>/', views.AvalistaListView.as_view(), name='processoavalistas-list'),
    # path('processoavalistas/<pk>/new', views.AvalistaCreateView.as_view(), name='new-processoavalista'),
    # path('processoavalistas/<pk>/edit', views.AvalistaUpdateView.as_view(), name='edit-processoavalista'),
    # path('processosavalista/<pk>/delete', views.AvalistaDeleteView.as_view(), name='delete-processoavalista'),

    # Referências
    # path('processoreferencias/<pk>/', views.ReferenciaListView.as_view(), name='processoreferencias-list'),
    # path('processoreferencias/<pk>/new', views.ReferenciaCreateView.as_view(), name='new-processoreferencia'),
    # path('processoreferencias/<pk>/edit', views.ReferenciaUpdateView.as_view(), name='edit-processoreferencia'),
    # path('processoreferencias/<pk>/delete', views.ReferenciaDeleteView.as_view(),
    #      name='delete-processoreferencia'),

    # Financeiro
    path('financeiro/view/', views.ProcessoFaturarListView.as_view(), name='processofaturar-list'),
    path('financeiro/view1/', views.ProcessoFaturarNegocListView.as_view(), name='processofaturarnegoc-list'),
    path('financeiro/<pk>/newnegoc', views.ProcessoFaturaNegocCreateView.as_view(), name='new-processofaturanegoc'),
    path('financeiro/view2/', views.ProcessoFaturadoListView.as_view(), name='processofaturado-list'),
    path('financeiro/<pk>/edit', views.ProcessoFaturadoUpdateView.as_view(), name='edit-processofaturado'),
    path('financeiro/<pk>/cancel', views.ProcessoFaturadoCancelView.as_view(), name='cancel-processofaturado'),
    path('financeiro/<pk>/estorn', views.ProcessoFaturadoEstornView.as_view(), name='estorn-processofaturado'),
    path('financeiro/<pk>/view', views.ExtratoFaturaListView.as_view(), name='extratofatura-list'),
    path('financeiro/<pk>/print', views.extratofaturalist, name='print-extratofatura'),
    path('financeiro/simulacao/', views.simulacao_emprestimo, name='simulacao-tela'),
    path('financeiro/view3/', views.TitulosaCancelarListView.as_view(), name='titulosacancelar-list'),
    path('financeiro/<pk>/deleteP', views.ProcessoTitulosPCancelView.as_view(), name='cancel-processotitulosP'),
    path('financeiro/<pk>/deleteN', views.ProcessoTitulosNCancelView.as_view(), name='cancel-processotitulosN'),
    path('financeiro/retorno/', views.processarretorno, name='retorno-list'),
    path('financeiro/envio/', views.processarenvio, name='envio-list'),

    # Pareceres
    path('processopareceres/<pk>/', views.ParecerListView.as_view(), name='processopareceres-list'),
    path('processopareceres/<pk>/new1', views.Parecer1CreateView.as_view(), name='new-processoparecer1'),
    path('processopareceres/<pk>/new2', views.Parecer2CreateView.as_view(), name='new-processoparecer2'),
    path('processopareceres/<pk>/edit1', views.Parecer1UpdateView.as_view(), name='edit-processoparecer1'),
    path('processopareceres/<pk>/edit2', views.Parecer2UpdateView.as_view(), name='edit-processoparecer2'),
    path('processopareceres/<pk>/edit3', views.Parecer3UpdateView.as_view(), name='edit-processoparecer3'),
    path('processopareceres/<pk>/delete', views.ParecerDeleteView.as_view(), name='delete-processoparecer'),

    # Negociações
    path('processonegociacoes/<pk>/<tipo>', views.ProcessoNegociacaoListView.as_view(), name='processonegociacoes-list'),
    path('processonegociacoes/<pk>/new/<tipo>', views.ProcessoNegociacaoCreateView.as_view(), name='new-processonegociacao'),
    path('processonegociacoes/<pk>/edit/<tipo>', views.ProcessoNegociacaoUpdateView.as_view(), name='edit-processonegociacao'),
    # o parâmetro "tipo" foi criado propositalmente para as urls abaixo, apesar de não haver influência dentros das views
    # pois a busca da urls estava se perdendendo
    path('processonegociacoes/<pk>/delete/<tipo>', views.ProcessoNegociacaoDeleteView.as_view(),
         name='delete-processonegociacao'),
    path('processonegociacoes/<pk>/print/<tipo>', views.aditivocontratolist, name='print-aditivocontrato'),

    # Movimentações
    path('processomovimentacoes/<pk>/new', views.MovimentacaoCreateView.as_view(), name='new-processomovimentacao'),
    # path('processomovimentacoes/<pk>/edit', views.MovimentacaoUpdateView.as_view(), name='edit-processomovimentacao'),
    path('processomovimentacoes/<pk>/delete', views.MovimentacaoDeleteView.as_view(),
         name='delete-processomovimentacao'),
    path('processomovimentacoes/<pk>/check', views.MovimentacaoCheckView.as_view(),
         name='check-processomovimentacao'),
    path('apagar-movimentacao/<int:pk>/', views.apagar_movimentacao, name='apagar_movimentacao'),
    path('checar-movimentacao/<int:pk>/', views.checar_movimentacao, name='checar_movimentacao'),

    # Comitês
    path('comites/', views.ComiteListView.as_view(), name='comites-list'),
    path('comites/new', views.ComiteCreateView.as_view(), name='new-comite'),
    path('comites/<pk>/edit', views.ComiteUpdateView.as_view(), name='edit-comite'),
    path('comites/<pk>/delete', views.ComiteDeleteView.as_view(), name='delete-comite'),
    path('comites/<pk>/print', views.atacomitelist, name='print-atacomite'),

    # Relatórios Diversos
    path('relatorios/listaprocessos/', views.listaprocessos, name='listaprocessos-tela'),
    path('relatorios/inadimplentes/', views.inadimplentes, name='inadimplentes-tela'),
    path('relatorios/dividaativa/', views.dividaativa, name='dividaativa-tela'),
    path('relatorios/titulosareceber/', views.titulosareceber, name='titulosareceber-tela'),
    path('relatorios/recebimentos/', views.recebimentos, name='recebimentos-tela'),
    path('relatorios/recebimentos1/', views.recebimentos1, name='recebimentos1-tela'),
    path('relatorios/dadoscadastraisclientes/', views.dadoscadastraisclientes, name='dadoscadastraisclientes-tela'),
    path('relatorios/processoscomite/', views.processoscomite, name='processoscomite-tela'),
    path('relatorios/autorizadoscomite/', views.autorizadoscomite, name='autorizadoscomite-tela'),
    path('relatorios/liberacaovalores/', views.liberacaovalores, name='liberacaovalores-tela'),
    path('relatorios/movimentos/', views.movimentos, name='movimentos-tela'),
    path('relatorios/listapesfisicas/', views.listapesfisicas, name='listapesfisicas-tela'),
    path('relatorios/listapesjuridicas/', views.listapesjuridicas, name='listapesjuridicas-tela'),
    path('relatorios/processospendentes/', views.processospendentes, name='processospendentes-tela'),
    path('relatorios/resumoatendimentos/', views.resumoatendimentos, name='resumoatendimentos-tela'),
    path('relatorios/renegociacoes/', views.renegociacoes, name='renegociacoes-tela'),

    path('ajax/load-bairros/',views.load_bairros,name='ajax_load_bairros'),     #AJAX
    path('consultar-cep/', views.consultar_cep, name='consultar_cep'),
    path('consultar-cnpj/', views.consultar_cnpj, name='consultar_cnpj'),
    path('consultar-geolocalizacao/', views.consultar_geolocalizacao, name='consultar_geolocalizacao'),

]

# Adicione as rotas de erro no final
handler404 = 'processos.views.handler404'
handler500 = 'processos.views.handler500'
