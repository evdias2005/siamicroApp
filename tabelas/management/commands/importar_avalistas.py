import os
from django.core.management.base import BaseCommand
from tabelas.models import Cidade, Profissao, EstadoCivil, RegimeBens
from processos.models import PessoaFisica
from django.conf import settings
from tqdm import tqdm
from datetime import datetime


class Command(BaseCommand):
    def handle(self, *args, **options):
        print('INICIANDO IMPORTAÇÃO DA TABELA DE AVALISTA DO ANTIGO MICROCRÉDITO =======')
        # print(settings.BASE_DIR)
        caminho_arquivo = os.path.join(settings.BASE_DIR, 'Arquivos/TabelaAvalistas_v3.csv')
        arquivo = open(caminho_arquivo)
        linhas = arquivo.read().splitlines()
        for linha in tqdm(linhas[1:]):
            linha = linha.split(';')
            # não será mais importado pois não há controle sobre o id final ocasionando erro no próximo isert no banco via sistema
            idorigem = linha[0].strip()
            nome = linha[1].strip()[0:99]
            print (idorigem, nome)
            cpf = linha[2].strip().replace('"', '')
            tipoutrodoc = 'NÃO INFORMADO'
            numoutrodoc = linha[3].strip()
            # ufoutrodoc =
            orgexpoutrodoc = linha[4].strip()
            dtemisoutrodoc = linha[5].strip()
            data_nascimento = linha[6].strip()
            naturalidade = linha[7].strip()
            nacionalidade = linha[8].strip()
            sexo = linha[9].strip()
            email = linha[10].strip()
            tempo_residencia = linha[11].strip()
            residencia_propria = linha[12].strip()
            profissao = linha[13].strip().replace('"', '')
            numero_filhos = linha[14].strip()
            # dependentes = linha[15].strip()
            nome_pai = linha[15].strip()
            nome_mae = linha[16].strip()
            nome_conjuge = linha[17].strip().replace('"', '')
            cpf_conjuge = linha[18].strip().replace('"', '')
            # ponto_referencia = linha[20].strip()                # alguns campos são removidos manualmente pois há erros
            created_at = linha[19].strip()
            updated_at = linha[20].strip()
            logradouro = linha[21].strip()
            # bairro = linha[22].strip()
            cep = linha[23].strip()
            numero = linha[24].strip()
            complemento = linha[25].strip()
            municipio = linha[26].strip()
            uf = linha[27].strip()
            escolaridade = linha[28].strip()
            estadocivil = linha[29].strip()
            nome_empresa = linha[30].strip()
            data_admissao = linha[31].strip().replace('"', '')
            cargo = linha[32].strip()
            renda_liquida = linha[33].strip()
            numero_beneficio = linha[34].strip().replace('"', '')
            rendimentos_alugueis = linha[35].strip()


            regime_bens = 1             # corrigir

            if PessoaFisica.objects.all().filter(numcpf=cpf).count() == 0:
                cliente = PessoaFisica()
                # cliente.id = id
                cliente.nome = nome.upper()
                cliente.tipo = 'A'
                if cliente.nome.find('ARQUIVADO') == -1:
                    cliente.situacao_id = 1
                else:
                    cliente.situacao_id = 2
                if data_nascimento:
                    cliente.dtnascimento = data_nascimento
                else:
                    cliente.dtnascimento = '1899-12-31'

                cliente.sexo = sexo.replace('"', '')[0:1]
                cliente.nomepai = nome_pai.upper()
                cliente.nomemae = nome_mae.upper()
                cliente.numcpf = cpf
                cliente.tipoutrodoc = tipoutrodoc
                cliente.numoutrodoc = numoutrodoc.replace('"', '')[0:14]
                # ufoutrodoc =
                cliente.orgexpoutrodoc = orgexpoutrodoc.replace('"', '')[0:19]
                if dtemisoutrodoc:
                    cliente.dtemisoutrodoc = dtemisoutrodoc
                else:
                    cliente.dtemisoutrodoc = '1899-12-31'
                qs=Cidade.objects.values_list('id').filter(nome=naturalidade.upper())
                if qs:
                    for x in qs:
                        cliente.naturalidade_id = x[0]
                else:
                    cliente.naturalidade_id = ''

                cliente.nacionalidade = nacionalidade.upper()[0:19]
                cliente.telfixo = ''                   # VER AINDA
                cliente.telcelular1 = ''               # VER AINDA
                cliente.telcelular2 = ''               # VER AINDA
                cliente.logradouro = logradouro.upper()[0:49]
                cliente.numimovel = numero
                cliente.complemento = complemento.replace('"', '').upper()[0:29]
                # cliente.bairro = bairro.upper()[0:29]
                qs=Cidade.objects.values_list('id').filter(nome=municipio.upper(),uf=uf.upper())
                if qs:
                    for x in qs:
                        cliente.cidade_id = x[0]
                else:
                    cliente.cidade_id = ''
                cliente.cep = cep.replace('"', '')
                if residencia_propria == 'true':
                   cliente.is_residpropria = True
                else:
                   cliente.is_residpropria = False
                if tempo_residencia:
                    cliente.temporesidencia = tempo_residencia
                else:
                    cliente.temporesidencia = 0
                cliente.email = email.replace('"', '').lower()

                qsprofissao=Profissao.objects.values_list('id').filter(nome=profissao.upper())
                if qsprofissao:
                    for x in qsprofissao:
                        cliente.profissao_id = x[0]
                else:
                    cliente.profissao_id = ''

                cliente.numfilhos = 0
                if numero_filhos:
                    if numero_filhos.isnumeric():
                        cliente.numfilhos = int(numero_filhos)

                # cliente.numdependentes = 0
                # if dependentes:
                #     if dependentes.isnumeric():
                #         cliente.numdependentes = int(dependentes)

                cliente.conjuge = nome_conjuge.upper()
                cliente.cpfconjuge = cpf_conjuge
                # cliente.pontoreferencia = ponto_referencia


                qsestcivil=EstadoCivil.objects.values_list('id').filter(nome=estadocivil.upper())
                if qsestcivil:
                    for x in qsestcivil:
                        cliente.estadocivil_id = x[0]
                else:
                    cliente.estadocivil_id = ''

                if escolaridade.upper() == 'FUNDAMENTAL INCOMPLETO':
                    cliente.escolaridade = '01'
                elif escolaridade.upper() == 'FUNDAMENTAL COMPLETO':
                        cliente.escolaridade = '01'
                elif escolaridade.upper() == 'MÉDIO INCOMPLETO':
                        cliente.escolaridade = '03'
                elif escolaridade.upper() == 'MÉDIO COMPLETO':
                        cliente.escolaridade = '04'
                elif escolaridade.upper() == 'TÉCNICO NÍVEL MÉDIO':
                        cliente.escolaridade = '05'
                elif escolaridade.upper() == 'SUPERIOR INCOMPLETO':
                        cliente.escolaridade = '06'
                elif escolaridade.upper() == 'SUPERIOR COMPLETO':
                        cliente.escolaridade = '07'
                elif escolaridade.upper() == 'PÓS-GRADUAÇÃO':
                        cliente.escolaridade = '08'
                elif escolaridade.upper() == 'MESTRADO':
                        cliente.escolaridade = '09'
                elif escolaridade.upper() == 'DOUTORADO':
                        cliente.escolaridade = '10'


                cliente.regimebens_id = regime_bens

                cliente.is_deleted = False
                cliente.criado_por_id = 1                      # como não existe o campo o default é o ADMIN
                cliente.data_criacao = created_at
                cliente.data_edicao = updated_at
                cliente.observacao = 'ID ORIGEM: ' + str(idorigem).zfill(6) + ' | PROFISSÃO: ' + str(profissao) + \
                                     ' | ESTADO CIVIL: ' + str(estadocivil) + ' | CIDADE: ' + str(municipio) + '-' + str(uf)


                if nome_empresa:
                    cliente.rendaempresa = nome_empresa.upper()[0:49]
                if data_admissao:
                    cliente.dtadmissempresa = data_admissao
                cliente.cargoempresa = cargo.upper()[0:29]
                cliente.rendaliqempresa = 0
                if renda_liquida:
                    cliente.rendaliqempresa = renda_liquida
                cliente.numbeneficio = numero_beneficio
                cliente.rendaalugueis = 0
                if rendimentos_alugueis:
                    cliente.rendaalugueis = rendimentos_alugueis
                # cliente.rendaliqtotal = cliente.rendaliqempresa + cliente.rendaalugueis

                cliente.save()
            #     print('Avalista inserido na base com sucesso', nome)
            # else:
            #     print('Avalista já cadastrado', nome)
