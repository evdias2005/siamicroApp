import os
from django.core.management.base import BaseCommand
from tabelas.models import RamoAtividade
from django.conf import settings
from tqdm import tqdm


class Command(BaseCommand):
    def handle(self, *args, **options):
        print('INICIANDO IMPORTAÇÃO DA TABELA DE RAMOS DE ATIVIDADE =======')
        # print(settings.BASE_DIR)
        caminho_arquivo = os.path.join(settings.BASE_DIR, 'Arquivos/segments.csv')
        arquivo = open(caminho_arquivo, encoding='utf-8')
        linhas = arquivo.read().splitlines()
        for linha in tqdm(linhas[1:]):
            linha = linha.split(';')
            # nome = linha[1][0:149].strip().upper()
            nome = linha[1][0:149].strip()
            print(nome)
            if RamoAtividade.objects.all().filter(nome=nome).count() == 0:
                ramoatividade = RamoAtividade()
                ramoatividade.nome = nome.upper()
                ramoatividade.save()
