import os
from django.core.management.base import BaseCommand
from tabelas.models import Profissao
from django.conf import settings
from tqdm import tqdm


class Command(BaseCommand):
    def handle(self, *args, **options):
        print('INICIANDO IMPORTAÇÃO DA TABELA DE CBO =======')
        # print(settings.BASE_DIR)
        caminho_arquivo = os.path.join(settings.BASE_DIR, 'Arquivos/TabelaOcupacaoCBO.csv')
        arquivo = open(caminho_arquivo, encoding='latin-1')
        linhas = arquivo.read().splitlines()
        for linha in tqdm(linhas[1:]):
            linha = linha.split(';')
            codigo = linha[0].strip()
            titulo = linha[1].strip()[:100]
            if Profissao.objects.all().filter(cbo=codigo).count() == 0:
                profissao = Profissao()
                profissao.cbo = codigo
                profissao.nome = titulo.upper()
                profissao.save()
            #     print('Profissão inserida na base com sucesso', titulo)
            # else:
            #     print('Profissão já cadastrada', titulo)
