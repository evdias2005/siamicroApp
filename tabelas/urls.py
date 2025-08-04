from django.urls import path
from . import views

urlpatterns = [

    path('configs/', views.ConfigListView.as_view(), name='configs-list'),
    path('configs/new', views.ConfigCreateView.as_view(), name='new-config'),
    path('configs/<pk>/edit', views.ConfigUpdateView.as_view(), name='edit-config'),
    path('configs/<pk>/delete', views.ConfigDeleteView.as_view(), name='delete-config'),

    path('bancos/', views.BancoListView.as_view(), name='bancos-list'),
    path('bancos/new', views.BancoCreateView.as_view(), name='new-banco'),
    path('bancos/<pk>/edit', views.BancoUpdateView.as_view(), name='edit-banco'),
    path('bancos/<pk>/delete', views.BancoDeleteView.as_view(), name='delete-banco'),

    path('feriados/', views.FeriadoListView.as_view(), name='feriados-list'),
    path('feriados/new', views.FeriadoCreateView.as_view(), name='new-feriado'),
    path('feriados/<pk>/edit', views.FeriadoUpdateView.as_view(), name='edit-feriado'),
    path('feriados/<pk>/delete', views.FeriadoDeleteView.as_view(), name='delete-feriado'),

    path('cidades/', views.CidadeListView.as_view(), name='cidades-list'),
    path('cidades/new', views.CidadeCreateView.as_view(), name='new-cidade'),
    path('cidades/<pk>/edit', views.CidadeUpdateView.as_view(), name='edit-cidade'),
    path('cidades/<pk>/delete', views.CidadeDeleteView.as_view(), name='delete-cidade'),

    path('bairros/', views.BairroListView.as_view(), name='bairros-list'),
    path('bairros/new', views.BairroCreateView.as_view(), name='new-bairro'),
    path('bairros/<pk>/edit', views.BairroUpdateView.as_view(), name='edit-bairro'),
    path('bairros/<pk>/delete', views.BairroDeleteView.as_view(), name='delete-bairro'),

    path('estadoscivis/', views.EstadoCivilListView.as_view(), name='estadoscivis-list'),
    path('estadoscivis/new', views.EstadoCivilCreateView.as_view(), name='new-estadocivil'),
    path('estadoscivis/<pk>/edit', views.EstadoCivilUpdateView.as_view(), name='edit-estadocivil'),
    path('estadoscivis/<pk>/delete', views.EstadoCivilDeleteView.as_view(), name='delete-estadocivil'),

    path('grausrelacao/', views.GrauRelacaoListView.as_view(), name='grausrelacao-list'),
    path('grausrelacao/new', views.GrauRelacaoCreateView.as_view(), name='new-graurelacao'),
    path('grausrelacao/<pk>/edit', views.GrauRelacaoUpdateView.as_view(), name='edit-graurelacao'),
    path('grausrelacao/<pk>/delete', views.GrauRelacaoDeleteView.as_view(), name='delete-graurelacao'),

    path('regimesbens/', views.RegimeBensListView.as_view(), name='regimesbens-list'),
    path('regimesbens/new', views.RegimeBensCreateView.as_view(), name='new-regimebens'),
    path('regimesbens/<pk>/edit', views.RegimeBensUpdateView.as_view(), name='edit-regimebens'),
    path('regimesbens/<pk>/delete', views.RegimeBensDeleteView.as_view(), name='delete-regimebens'),

    path('linhascredito/', views.LinhaCreditoListView.as_view(), name='linhascredito-list'),
    path('linhascredito/new', views.LinhaCreditoCreateView.as_view(), name='new-linhacredito'),
    path('linhascredito/<pk>/edit', views.LinhaCreditoUpdateView.as_view(), name='edit-linhacredito'),
    path('linhascredito/<pk>/delete', views.LinhaCreditoDeleteView.as_view(), name='delete-linhacredito'),

    path('finalidadescredito/', views.FinalidadeCreditoListView.as_view(), name='finalidadescredito-list'),
    path('finalidadescredito/new', views.FinalidadeCreditoCreateView.as_view(), name='new-finalidadecredito'),
    path('finalidadescredito/<pk>/edit', views.FinalidadeCreditoUpdateView.as_view(), name='edit-finalidadecredito'),
    path('finalidadescredito/<pk>/delete', views.FinalidadeCreditoDeleteView.as_view(), name='delete-finalidadecredito'),

    path('setoresnegocio/', views.SetorNegocioListView.as_view(), name='setoresnegocio-list'),
    path('setoresnegocio/new', views.SetorNegocioCreateView.as_view(), name='new-setornegocio'),
    path('setoresnegocio/<pk>/edit', views.SetorNegocioUpdateView.as_view(), name='edit-setornegocio'),
    path('setoresnegocio/<pk>/delete', views.SetorNegocioDeleteView.as_view(),
         name='delete-setornegocio'),

    path('ramosatividade/', views.RamoAtividadeListView.as_view(), name='ramosatividade-list'),
    path('ramosatividade/new', views.RamoAtividadeCreateView.as_view(), name='new-ramoatividade'),
    path('ramosatividade/<pk>/edit', views.RamoAtividadeUpdateView.as_view(), name='edit-ramoatividade'),
    path('ramosatividade/<pk>/delete', views.RamoAtividadeDeleteView.as_view(),
         name='delete-ramoatividade'),

    path('profissoes/', views.ProfissaoListView.as_view(), name='profissoes-list'),
    path('profissoes/new', views.ProfissaoCreateView.as_view(), name='new-profissao'),
    path('profissoes/<pk>/edit', views.ProfissaoUpdateView.as_view(), name='edit-profissao'),
    path('profissoes/<pk>/delete', views.ProfissaoDeleteView.as_view(), name='delete-profissao'),

    path('veiculos/', views.VeiculoListView.as_view(), name='veiculos-list'),
    path('veiculos/new', views.VeiculoCreateView.as_view(), name='new-veiculo'),
    path('veiculos/<pk>/edit', views.VeiculoUpdateView.as_view(), name='edit-veiculo'),
    path('veiculos/<pk>/delete', views.VeiculoDeleteView.as_view(), name='delete-veiculo'),

    path('localizacoes/', views.LocalizacaoListView.as_view(), name='localizacoes-list'),
    path('localizacoes/new', views.LocalizacaoCreateView.as_view(), name='new-localizacao'),
    path('localizacoes/<pk>/edit', views.LocalizacaoUpdateView.as_view(), name='edit-localizacao'),
    path('localizacoes/<pk>/delete', views.LocalizacaoDeleteView.as_view(), name='delete-localizacao'),

    path('situacoespessoa/', views.SituacaoPessoaListView.as_view(), name='situacoespessoa-list'),
    path('situacoespessoa/new', views.SituacaoPessoaCreateView.as_view(), name='new-situacaopessoa'),
    path('situacoespessoa/<pk>/edit', views.SituacaoPessoaUpdateView.as_view(), name='edit-situacaopessoa'),
    path('situacoespessoa/<pk>/delete', views.SituacaoPessoaDeleteView.as_view(),
         name='delete-situacaopessoa'),

    path('tiposfonterefer/', views.TipoFonteReferListView.as_view(), name='tiposfonterefer-list'),
    path('tiposfonterefer/new', views.TipoFonteReferCreateView.as_view(), name='new-tipofonterefer'),
    path('tiposfonterefer/<pk>/edit', views.TipoFonteReferUpdateView.as_view(), name='edit-tipofonterefer'),
    path('tiposfonterefer/<pk>/delete', views.TipoFonteReferDeleteView.as_view(),
         name='delete-tipofonterefer'),

    # Fechamentos
    path('fechamentos/', views.FechamentoListView.as_view(), name='fechamentos-list'),
    path('fechamentos/new', views.FechamentoCreateView.as_view(), name='new-fechamento'),
    path('fechamentos/<pk>/edit', views.FechamentoUpdateView.as_view(), name='edit-fechamento'),
    path('fechamentos/<pk>/delete', views.FechamentoDeleteView.as_view(), name='delete-fechamento'),

    path('logs/', views.LogListView.as_view(), name='logs-list'),
    path('logs/print', views.ResultList, name='logs-print'),
    # path('logs/excel', views.LogExcelListView.as_view(), name='logsexcel-list'),
    path('logs/view', views.LogsMenuView.as_view(), name='logsmenu'),
    path('logs/view1', views.LogsPessoaFisicaView.as_view(), name='logspessoafisica-list'),
    path('logs/view2', views.LogsPessoaJuridicaView.as_view(), name='logspessoajuridica-list'),
    path('logs/view3', views.LogsProcessoView.as_view(), name='logsprocesso-list'),

    path('construcao/', views.ConstrucaoView.as_view(), name='construcao')

]

