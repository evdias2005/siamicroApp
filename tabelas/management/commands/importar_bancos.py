import os
from django.core.management.base import BaseCommand
from tabelas.models import Banco
from django.conf import settings
from tqdm import tqdm

class Command(BaseCommand):
    def handle(self, *args, **options):
        print('INICIANDO IMPORTAÇÃO DA TABELA DE BANCOS =======')
        # print(settings.BASE_DIR)
        caminho_arquivo = os.path.join(settings.BASE_DIR, 'Arquivos/TabelaBancosBrasil.csv')
        arquivo = open(caminho_arquivo)
        linhas = arquivo.read().splitlines()
        for linha in tqdm(linhas[1:]):
            linha = linha.split(',')
            codigo = linha[0].strip()[:3]
            nome = linha[1].strip()[:50]
            site = linha[2].strip()[:50]
            if Banco.objects.all().filter(codigo=codigo).count() == 0:
                banco = Banco()
                banco.codigo = codigo
                banco.nome = nome.upper()
                banco.site = site
                banco.save()
            #     print('Banco inserido na base com sucesso', nome)
            # else:
            #     print('Banco já cadastrado', nome)
