import os
from django.core.management.base import BaseCommand
from tabelas.models import Config, EstadoCivil, GrauRelacao, FinalidadeCredito, LinhaCredito, RegimeBens, \
    SetorNegocio, TipoFonteRefer, RamoAtividade, SituacaoPessoa
from processos.models import PessoaFisica, PessoaJuridica

from django.conf import settings

from datetime import datetime

class Command(BaseCommand):

    def handle(self, *args, **options):
        print('CRIANDO O REGISTRO PADRÃO PARA A TABELA  PARAMETRO')
        # print(settings.BASE_DIR)
        if not Config.objects.all().exists():
            parametro = Config()
            parametro.nome = "PARAMETRO_DEFAULT_2025"
            parametro.exercicio = 2025
            parametro.multa = 2.00
            parametro.juros = 0.033
            parametro.metaagente = 15
            parametro.tmpconclusaoprocesso = 10
            parametro.mostratitcancelados = False
            parametro.mostraregcancelados = False
            parametro.situacaonegocio_default = "1"
            parametro.conhecimentoprograma_default = "1"
            parametro.tipdocumento_default = "CNH"
            parametro.cep_default = "28100-000"
            parametro.ultenviobanco = 0
            parametro.ultnossonumero = 0

            parametro.representanteconselho = ("CONSELHO GESTOR do FUNDECAM - Fundo de Desenvolvimento de Campos dos "
                                               "Goytacazes, daqui por diante denominado CONSELHO GESTOR, instituído "
                                               "através do Decreto n.º 262 de 20 de Novembro de 2001, que criou o "
                                               "FUNDECAM, com o objetivo de implantação, ampliação ou reforma de "
                                               "empreendimentos empresariais localizados no município. Assim habilitado,"
                                               " o CONSELHO GESTOR, representado pelo seu presidente, o Sr. ORLANDO LINO "
                                               "PINHEIRO PORTUGAL, brasileiro, casado, empresário, Ident. nº 064651049 "
                                               "expedida pelo DETRAN em 24.05.2005, CPF n 841.900.277-15, residente à "
                                               "Avenida Dr. Nilo Pessanha nº 10, Quadra D, lote 16, Bairro: Centro, nesta "
                                               "Cidade, nomeado nos termos da Portaria nº 098/2021 de 01.01.2021,")

            parametro.representantegoverno = ("WLADIMIR BARROS ASSED MATHEUS DE OLIVEIRA, brasileiro, casado, portador"
                                              " da carteira de identidade RG n.º.204219935, expedida pelo DETRAN-RJ, "
                                              "inscrito no CPF/MF sob o n.º108.558.347-30, com endereço para notificação "
                                              "na Rua Coronel Ponciano Azevedo Furtado, 47, Centro, nesta cidade de "
                                              "Campos dos Goytacazes, Estado do Rio de Janeiro, investido no cargo de "
                                              "prefeito municipal, nos termos do “DIPLOMA” firmado pelo Tribunal Regional "
                                              "Eleitoral do Município de Campos dos Goytacazes, Estado do Rio de Janeiro, "
                                              "em 17.12.2020.")

            parametro.agentefinanceiro = ("Banco do Brasil S.A; sociedade de economia mista, com sede em Brasília, Capital "
                                          "Federal, inscrito no CNPJ/MF sob o n.º 00.000.000/0005-15, por sua Agência "
                                          "(005-1) de Campos dos Goytacazes – RJ, neste instrumento representado pelo Sr."
                                          " ANTONIO SERGIO DE SOUZA FILHO, brasileiro, casado, bancário, matrícula n° "
                                          "F1112281, portador do documento de identificação 105002265/IFP-RJ, inscrito no"
                                          " CPF sob nº 072.729.657-46, residente e domiciliado no Rio de Janeiro/RJ; na"
                                          " qualidade de Gerente Geral, conforme substabelecimento conferido pelo "
                                          "Superintendente do Banco do Brasil S.A., nos termos do substabelecimento de "
                                          "procuração por instrumento público, com reservas de iguais poderes para si, "
                                          "lavrado em 14.06.2021, no 1º Ofício de Notas e Protestos de Brasília (Cartório"
                                          " JK), Livro 7099-P, fls. 111, mediante exceção dos poderes descritos na alínea"
                                          " 14-a e observadas as alíneas 9, 13, 14-b, 14-c e 14-d, dos termos da procuração"
                                          " pública lavrada no dia 05.02.2021, no Serviço Notarial do 5º Ofício de "
                                          "Taguatinga – DF, fls. 162/165, livro 3345.")

            parametro.testemunha1 = "Paulo Gustavo Barbosa de Abreu - CPF: 655.375.487-04"

            parametro.save()
            print('Registro inserido na base com sucesso.')
        else:
            print('Registro já cadastrado.')

        print('CRIANDO REGISTROS PARA A TABELA ESTADOCIVIL')
        if not EstadoCivil.objects.all().exists():
            estadocivil = EstadoCivil()
            estadocivil.nome = "*** NÃO INFORMADO ***"
            estadocivil.save()

            estadocivil = EstadoCivil()
            estadocivil.nome = "SOLTEIRO(A)"
            estadocivil.save()

            estadocivil = EstadoCivil()
            estadocivil.nome = "CASADO(A)"
            estadocivil.save()

            estadocivil = EstadoCivil()
            estadocivil.nome = "UNIAO ESTAVEL"
            estadocivil.save()

            estadocivil = EstadoCivil()
            estadocivil.nome = "DIVORCIADO(A)"
            estadocivil.save()

            estadocivil = EstadoCivil()
            estadocivil.nome = "SEPARADO(A)"
            estadocivil.save()

            estadocivil = EstadoCivil()
            estadocivil.nome = "VIÚVO(A)"
            estadocivil.save()

            print('Registros inseridos na base com sucesso.')
        else:
            print('Tabela de EstadoCivil já encontra-se populada.')

        print('CRIANDO REGISTROS PARA A TABELA REGIMEBENS')
        if not RegimeBens.objects.all().exists():

            regimebens = RegimeBens()
            regimebens.nome = "COMUNHÃO PARCIAL DE BENS"
            regimebens.save()

            regimebens = RegimeBens()
            regimebens.nome = "COMUNHAO UNIVERSAL DE BENS"
            regimebens.save()

            regimebens = RegimeBens()
            regimebens.nome = "SEPARACAO OBRIGATORIA DE BENS"
            regimebens.save()

            regimebens = RegimeBens()
            regimebens.nome = "PARTICIPACAO FINAL NOS AQUESTOS"
            regimebens.save()

            print('Registros inseridos na base com sucesso.')
        else:
            print('Tabela de Regime de Bens já encontra-se populada.')


        print('CRIANDO REGISTROS PARA A TABELA GRAURELACAO')
        if not GrauRelacao.objects.all().exists():
            graurelacao = GrauRelacao()
            graurelacao.nome = "IRMÃO/IRMÃ"
            graurelacao.save()

            graurelacao = GrauRelacao()
            graurelacao.nome = "PAI"
            graurelacao.save()

            graurelacao = GrauRelacao()
            graurelacao.nome = "MÃE"
            graurelacao.save()

            graurelacao = GrauRelacao()
            graurelacao.nome = "PRIMO(A)"
            graurelacao.save()

            graurelacao = GrauRelacao()
            graurelacao.nome = "SOGRO(A)"
            graurelacao.save()

            graurelacao = GrauRelacao()
            graurelacao.nome = "AMIGO(A)"
            graurelacao.save()

            graurelacao = GrauRelacao()
            graurelacao.nome = "VIZINHO"
            graurelacao.save()

            graurelacao = GrauRelacao()
            graurelacao.nome = "FILHO(A)"
            graurelacao.save()

            graurelacao = GrauRelacao()
            graurelacao.nome = "AVÔ(Á)"
            graurelacao.save()

            graurelacao = GrauRelacao()
            graurelacao.nome = "OUTROS"
            graurelacao.save()

            print('Registros inseridos na base com sucesso')
        else:
            print('Tabela de Grau de Relação já encontra-se populada.')

        print('CRIANDO REGISTROS PARA A TABELA FINALIDADECREDITO')
        if not FinalidadeCredito.objects.all().exists():

            finalidadecredito = FinalidadeCredito()
            finalidadecredito.nome = "CAPITAL DE GIRO"
            finalidadecredito.save()

            finalidadecredito = FinalidadeCredito()
            finalidadecredito.nome = "INVESTIMENTO FIXO"
            finalidadecredito.save()

            finalidadecredito = FinalidadeCredito()
            finalidadecredito.nome = "INVESTIMENTO MISTO"
            finalidadecredito.save()

            print('Registros inseridos na base com sucesso.')
        else:
            print('Tabela de Finalidade de Crédito já encontra-se populada.')

        print('CRIANDO REGISTROS PARA A TABELA LINHACREDITO')
        if not LinhaCredito.objects.all().exists():

            linhacredito = LinhaCredito()
            linhacredito.nome = "ECONOMIA SOLIDÁRIA"
            linhacredito.limite = 5000
            linhacredito.nmaxparcelas = 36
            linhacredito.juros = 2
            linhacredito.nminavalistas = 2
            linhacredito.save()

            linhacredito = LinhaCredito()
            linhacredito.nome = "EMPREENDEDOR/MICROCRÉDITO"
            linhacredito.limite = 10000
            linhacredito.nmaxparcelas = 21
            linhacredito.juros = 8.16
            linhacredito.nminavalistas = 1
            linhacredito.save()

            linhacredito = LinhaCredito()
            linhacredito.nome = "INOVAÇÃO"
            linhacredito.limite = 50000
            linhacredito.nmaxparcelas = 36
            linhacredito.juros = 6
            linhacredito.nminavalistas = 1
            linhacredito.save()

            linhacredito = LinhaCredito()
            linhacredito.nome = "EMPRESARIAL"
            linhacredito.limite = 50000
            linhacredito.nmaxparcelas = 36
            linhacredito.juros = 9.48
            linhacredito.nminavalistas = 2
            linhacredito.save()

            print('Registros inseridos na base com sucesso.')
        else:
            print('Tabela de Linhas de Crédito já encontra-se populada.')

        print('CRIANDO REGISTROS PARA A TABELA SETORNEGOCIO')
        if not SetorNegocio.objects.all().exists():

            setornegocio = SetorNegocio()
            setornegocio.nome = "SERVIÇO"
            setornegocio.save()

            setornegocio = SetorNegocio()
            setornegocio.nome = "PRODUÇÃO"
            setornegocio.save()

            setornegocio = SetorNegocio()
            setornegocio.nome = "COMÉRCIO"
            setornegocio.save()

            print('Registros inseridos na base com sucesso.')
        else:
            print('Tabela de Setores de Negócio já encontra-se populada.')

        print('CRIANDO REGISTROS PARA A TABELA SITUACAOPESSOA')
        if not SituacaoPessoa.objects.all().exists():

            situacaopessoa = SituacaoPessoa()
            situacaopessoa.descricao = "SEM RESTRIÇÕES"
            situacaopessoa.blq_processo = False
            situacaopessoa.save()

            situacaopessoa = SituacaoPessoa()
            situacaopessoa.descricao = "ARQUIVADO - PROCESSO FINALIZADO"
            situacaopessoa.blq_processo = False
            situacaopessoa.save()

            situacaopessoa = SituacaoPessoa()
            situacaopessoa.descricao = "ARQUIVADO EM RAZÃO DE PARECER NEGATIVO"
            situacaopessoa.blq_processo = False
            situacaopessoa.save()

            situacaopessoa = SituacaoPessoa()
            situacaopessoa.descricao = "SUSPENSO TEMPORARIAMENTE"
            situacaopessoa.blq_processo = True
            situacaopessoa.save()

            situacaopessoa = SituacaoPessoa()
            situacaopessoa.descricao = "BLOQUEADO - REGISTRO NO SERASA"
            situacaopessoa.blq_processo = True
            situacaopessoa.save()

            situacaopessoa = SituacaoPessoa()
            situacaopessoa.descricao = "ARQUIVADO POR DESISTÊNCIA DO CLIENTE"
            situacaopessoa.blq_processo = False
            situacaopessoa.save()

            situacaopessoa = SituacaoPessoa()
            situacaopessoa.descricao = "BLOQUEADO - DÍVIDA ATIVA"
            situacaopessoa.blq_processo = True
            situacaopessoa.save()

            print('Registros inseridos na base com sucesso.')
        else:
            print('Tabela de Situações da Pessoa já encontra-se populada.')


        print('CRIANDO REGISTROS PARA A TABELA TIPOFONTEREFER')
        if not TipoFonteRefer.objects.all().exists():

            tipofonterefer = TipoFonteRefer()
            tipofonterefer.nome = "PESSOAIS-CLIENTE"
            tipofonterefer.save()

            tipofonterefer = TipoFonteRefer()
            tipofonterefer.nome = "PESSOAIS-AVALISTA"
            tipofonterefer.save()

            tipofonterefer = TipoFonteRefer()
            tipofonterefer.nome = "PESSOAIS-CONJUGE"
            tipofonterefer.save()

            tipofonterefer = TipoFonteRefer()
            tipofonterefer.nome = "COMERCIAIS-CLIENTE"
            tipofonterefer.save()

            tipofonterefer = TipoFonteRefer()
            tipofonterefer.nome = "COMERCIAIS-AVALISTA"
            tipofonterefer.save()

            tipofonterefer = TipoFonteRefer()
            tipofonterefer.nome = "COMERCIAIS-CONJUGE"
            tipofonterefer.save()

            tipofonterefer = TipoFonteRefer()
            tipofonterefer.nome = "BANCÁRIAS-CLIENTE"
            tipofonterefer.save()

            tipofonterefer = TipoFonteRefer()
            tipofonterefer.nome = "BANCÁRIAS-AVALISTA"
            tipofonterefer.save()

            tipofonterefer = TipoFonteRefer()
            tipofonterefer.nome = "BANCÁRIAS-CONJUGE"
            tipofonterefer.save()

            print('Registros inseridos na base com sucesso.')
        else:
            print('Tabela de Tipos de Referência já encontra-se populada.')


