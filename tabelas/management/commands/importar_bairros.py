import os
from django.core.management.base import BaseCommand
from tabelas.models import Bairro
from django.conf import settings
from tqdm import tqdm


class Command(BaseCommand):
    def handle(self, *args, **options):
        print('INICIANDO IMPORTAÇÃO DA TABELA DE BAIRRO =======')
        # print(settings.BASE_DIR)
        caminho_arquivo = os.path.join(settings.BASE_DIR, 'Arquivos/TabelaBairrosNew.csv')
        arquivo = open(caminho_arquivo, encoding='utf-8')
        linhas = arquivo.read().splitlines()
        for linha in tqdm(linhas[1:]):
            linha = linha.split(';')
            descricaobairro =  linha[0].strip().upper() + " (" + linha[1].strip().upper() + ")"
            print (descricaobairro)
            # print (bairro + ' - ' + distrito, end="\r")
            if Bairro.objects.all().filter(cidade_id=3192, nome=descricaobairro).count() == 0:
                bairro = Bairro()
                bairro.cidade_id = 3192
                bairro.nome = descricaobairro
                bairro.save()
            #     print('Profissão inserida na base com sucesso', titulo)
            # else:
            #     print('Profissão já cadastrada', titulo)
