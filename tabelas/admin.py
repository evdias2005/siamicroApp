from django.contrib import admin

from .models import Log, Operador, Operador_Local, TabRefis, MarcaVeiculo

@admin.register(Operador)
class OperadorAdmin(admin.ModelAdmin):
    list_display = ('numcpf', 'user', 'secretaria', 'is_membrocomite', 'is_deleted')
    list_filter = ['secretaria', 'numcpf', 'is_membrocomite']
    ordering = ['numcpf']

@admin.register(Operador_Local)
class OperadorLocalAdmin(admin.ModelAdmin):
    list_display = ('localizacao', 'operador')
    list_filter = ['localizacao', 'operador']
    ordering = ['operador']

@admin.register(TabRefis)
class TabRefisAdmin(admin.ModelAdmin):
    list_display = ('linhacredito', 'faixaparc_ini', 'faixaparc_fin', 'descjuros', 'descmulta', 'parcmin_pf',
                    'parcmin_pj')
    list_filter = ['linhacredito']
    ordering = ['linhacredito','faixaparc_ini']

@admin.register(MarcaVeiculo)
class MarcaVeiculoAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    list_filter = ['nome']
    ordering = ['nome']

# admin.site.register(Log)
