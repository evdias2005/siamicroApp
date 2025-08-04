import os
from django.core.management.base import BaseCommand
from tabelas.models import Cidade
from django.conf import settings
from tqdm import tqdm

class Command(BaseCommand):
    def handle(self, *args, **options):
        print('INICIANDO IMPORTAÇÃO DA TABELA DE CIDADES =======')
        # print(settings.BASE_DIR)
        caminho_arquivo = os.path.join(settings.BASE_DIR, 'Arquivos/TabelaMunicipios.csv')
        arquivo = open(caminho_arquivo)
        linhas = arquivo.read().splitlines()
        for linha in tqdm(linhas[1:]):
            linha = linha.split(';')
            codibge = linha[2].strip()
            uf = linha[3].strip()
            nomcidade = linha[4].strip()
            if Cidade.objects.all().filter(codibge=codibge).count() == 0:
                cidade = Cidade()
                cidade.uf = uf
                cidade.nome = nomcidade.upper()
                cidade.codibge = codibge
                cidade.save()
            #     print('Município inserido na base com sucesso', nomcidade)
            # else:
            #     print('Município já cadastrado', nomcidade)

        # Criando o registro auxiliar "NO INFORMADO"
        cidade = Cidade()
        cidade.id = 9998
        cidade.uf = '**'
        cidade.nome = 'NAO INFORMADO'
        cidade.codibge = '8888888'
        cidade.save()
