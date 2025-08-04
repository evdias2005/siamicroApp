import os
from django.core.management.base import BaseCommand
from tabelas.models import Cidade, Profissao, EstadoCivil, RegimeBens
from processos.models import PessoaJuridica
from django.conf import settings
from tqdm import tqdm
from datetime import datetime


class Command(BaseCommand):
    def handle(self, *args, **options):
        print('INICIANDO IMPORTAÇÃO DA TABELA DE EMPRESAS DO ANTIGO MICROCREDITO =======')
        # print(settings.BASE_DIR)
        caminho_arquivo = os.path.join(settings.BASE_DIR, 'Arquivos/TabelaEmpresas_v1.csv')
        arquivo = open(caminho_arquivo)
        linhas = arquivo.read().splitlines()
        for linha in tqdm(linhas[1:]):
            linha = linha.split(';')
            # não será mais importado pois não há controle sobre o id final ocasionando erro no próximo isert no banco via sistema
            idorigem = linha[0].strip()
            nome_empresa = linha[1].strip()[0:99]
            cnpj = linha[2].strip().replace('"', '')[0:18]
            data_inicio_atividade = linha[3].strip()
            inscricao_estadual = linha[4].strip()[0:8]
            inscricao_municipal = linha[5].strip()[0:8]
            telefone = linha[6].strip()
            created_at = linha[8].strip()
            updated_at = linha[9].strip()
            logradouro = linha[10].strip()
            bairro = linha[11].strip()
            cep = linha[12].strip()[0:8]
            numero = linha[13].strip()
            complemento = linha[14].strip()
            municipio = linha[15].strip()
            uf = linha[16].strip()

            if PessoaJuridica.objects.all().filter(numcnpj=cnpj).count() == 0:
                empresa = PessoaJuridica()
                # cliente.id = id
                empresa.razaosocial = nome_empresa.upper()
                empresa.nomefantasia = nome_empresa.upper()
                empresa.dtiniatividade = data_inicio_atividade
                empresa.situacao_id = 2
                if cnpj:
                    empresa.porteempresa = 1
                else:
                    empresa.porteempresa = 6
                empresa.numcnpj = cnpj
                empresa.numinscest = inscricao_estadual
                empresa.numinscmun = inscricao_municipal
                empresa.telcelular1 = telefone[0:15]
                empresa.logradouro = logradouro.upper()[0:49]
                empresa.numimovel = numero
                empresa.complemento = complemento.replace('"', '').upper()[0:29]
                # cliente.bairro = bairro.upper()[0:29]
                qs=Cidade.objects.values_list('id').filter(nome=municipio.upper(),uf=uf.upper())
                if qs:
                    for x in qs:
                        empresa.cidade_id = x[0]
                else:
                    empresa.cidade_id = ''
                empresa.cep = cep.replace('"', '')

                empresa.is_deleted = False
                empresa.criado_por_id = 1                      # como não existe o campo o default é o ADMIN
                empresa.data_criacao = created_at
                empresa.data_edicao = updated_at
                empresa.observacao = 'ID ORIGEM: ' + str(idorigem).zfill(6) + ' | BAIRRO: ' + str(bairro) + ' | CIDADE: ' + str(municipio)
                empresa.save()
            #     print('Cliente inserido na base com sucesso', nome)
            # else:
            #     print('Cliente já cadastrado', nome)
