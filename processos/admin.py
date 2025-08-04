from django.contrib import admin

from django.contrib.auth.models import User

from processos.models import PessoaFisica, PessoaJuridica, Processo, Avalista

@admin.register(Avalista)
class AvalistaAdmin(admin.ModelAdmin):
    list_display = ('processo', 'avalista', 'graurelacao', 'negociacao', 'criado_por')
    list_filter = ['processo', 'avalista', 'criado_por']
    ordering = ['processo']

@admin.register(PessoaFisica)
class PessoaFisicaAdmin(admin.ModelAdmin):
    list_display = ('numcpf', 'nome', 'tipo', 'criado_por')
    list_filter = ['numcpf', 'nome', 'tipo', 'criado_por']
    ordering = ['nome']

@admin.register(PessoaJuridica)
class PessoaJuridicaAdmin(admin.ModelAdmin):
    list_display = ('numcnpj', 'razaosocial', 'criado_por')
    list_filter = ['numcnpj', 'razaosocial', 'criado_por']
    ordering = ['razaosocial']

@admin.register(Processo)
class ProcessoAdmin(admin.ModelAdmin):
    list_display = ('numprocesso', 'dtprocesso', 'clientepf', 'clientepj', 'criado_por')
    list_filter = ['dtprocesso', 'clientepf', 'clientepj', 'criado_por']
    ordering = ['numprocesso']

admin.site.site_header = 'Módulo de Administração - SIAMICRO'
admin.site.site_title = 'Módulo de Administração - SIAMICRO'