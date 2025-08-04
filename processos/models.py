import os
import hashlib
import pathlib
from contextlib import nullcontext

from django.db import models

from django.contrib.auth.models import User

from .validators import validate_cpf, validate_cnpj, validar_tamanho_arquivo

from tabelas.models import (Banco, SetorNegocio, Cidade, Bairro, RamoAtividade, Profissao, EstadoCivil, GrauRelacao,
                            RegimeBens, LinhaCredito, FinalidadeCredito, TipoFonteRefer, SituacaoPessoa, Localizacao,
                            Veiculo, Operador)

from simple_history.models import HistoricalRecords

from locale import setlocale, currency as moeda, LC_ALL

from datetime import datetime, date

from django.utils import timezone

from django.db.models import Q

from django.core.exceptions import ValidationError

ESCOLARIDADE_OPCOES = (
    ("01", "FUNDAMENTAL INCOMPLETO"),
    ("02", "FUNDAMENTAL COMPLETO"),
    ("03", "MÉDIO INCOMPLETO"),
    ("04", "MÉDIO COMPLETO"),
    ("05", "TÉCNICO NÍVEL MÉDIO"),
    ("06", "SUPERIOR INCOMPLETO"),
    ("07", "SUPERIOR COMPLETO"),
    ("08", "PÓS-GRADUAÇÃO"),
    ("09", "MESTRADO"),
    ("10", "DOUTORADO"),
)


# Tabela de Pessoas Físicas (Clientes, Avalistas, ...)
class PessoaFisica(models.Model):
    TIPO_OPCOES = (
        ("C", "CLIENTE"),
        ("A", "AVALISTA"),
        ("X", "CLIENTE/AVALISTA"),
    )

    SEXO_OPCOES = (
        ("M", "MASCULINO"),
        ("F", "FEMININO"),
    )

    UF_OPCOES = (
        ("AC", "ACRE"),
        ("AL", "ALAGOAS"),
        ("AM", "AMAZONAS"),
        ("AP", "AMAPÁ"),
        ("BA", "BAHIA"),
        ("CE", "CEARÁ"),
        ("DF", "DISTRITO FEDERAL"),
        ("ES", "ESPÍRITO SANTO"),
        ("GO", "GOIÁS"),
        ("MA", "MARANHÃO"),
        ("MG", "MINAS GERAIS"),
        ("MS", "MATO GROSSO DO SUL"),
        ("MT", "MATO GROSSO"),
        ("PA", "PARÁ"),
        ("PI", "PIAUÍ"),
        ("PB", "PARAÍBA"),
        ("PE", "PERNAMBUCO"),
        ("PR", "PARANÁ"),
        ("RS", "RIO GRANDE DO SUL"),
        ("RO", "RONDÔNIA"),
        ("RR", "RORAIMA"),
        ("RJ", "RIO DE JANEIRO"),
        ("RN", "RIO GRANDE DO NORTE"),
        ("SC", "SANTA CATARINA"),
        ("SE", "SERGIPE"),
        ("SP", "SÃO PAULO"),
        ("TO", "TOCANTINS"),
    )

    class Meta:
        ordering = ["id"]

    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=1, choices=TIPO_OPCOES, default='C')
    dtnascimento = models.DateField()
    sexo = models.CharField(max_length=1, choices=SEXO_OPCOES, default='M')
    nomepai = models.CharField(max_length=100, blank=True)
    nomemae = models.CharField(max_length=100)
    profissao = models.ForeignKey(Profissao, on_delete=models.PROTECT, null=True, blank=True,
                                  related_name='fk_pessoafisica_profissao')
    escolaridade = models.CharField(max_length=2, choices=ESCOLARIDADE_OPCOES)
    estadocivil = models.ForeignKey(EstadoCivil, on_delete=models.PROTECT, null=True, blank=True,
                                    related_name='fk_pessoafisica_estadocivil')
    regimebens = models.ForeignKey(RegimeBens, on_delete=models.PROTECT, null=True, blank=True,
                                   related_name='fk_pessoafisica_regimebens')
    numfilhos = models.PositiveIntegerField(null=True, default=0)
    numdependentes = models.PositiveIntegerField(null=True, default=0)
    conjuge = models.CharField(max_length=100, blank=True)
    cpfconjuge = models.CharField(max_length=14, blank=True, validators=[validate_cpf])
    numcpf = models.CharField(max_length=14, unique=True, validators=[validate_cpf])
    numrg= models.CharField(max_length=12)
    ufexpedrg = models.CharField(max_length=2, choices=UF_OPCOES, default='RJ')
    orgexpedrg = models.CharField(max_length=20, blank=True)
    tipoutrodoc = models.CharField(max_length=15, blank=True)
    numoutrodoc = models.CharField(max_length=15, blank=True)
    ufoutrodoc = models.CharField(max_length=2, choices=UF_OPCOES, blank=True, default='RJ')
    orgexpoutrodoc = models.CharField(max_length=20, blank=True)
    dtemisoutrodoc = models.DateField(null=True, blank=True)
    naturalidade = models.ForeignKey(Cidade, on_delete=models.PROTECT, null=True, blank=True,
                                     related_name='fk_pessoafisica_naturalidade')
    nacionalidade = models.CharField(max_length=20, blank=True, default='BRASILEIRO')
    telfixo = models.CharField(max_length=14, blank=True)
    telcelular1 = models.CharField(max_length=15, blank=True)
    telcelular2 = models.CharField(max_length=15, blank=True)
    logradouro = models.CharField(max_length=50)
    numimovel = models.CharField(max_length=4)
    complemento = models.CharField(max_length=30, blank=True)
    # bairro = models.CharField(max_length=30)
    cidade = models.ForeignKey(Cidade, on_delete=models.PROTECT, null=True, blank=True,
                               related_name='fk_pessoafisica_cidade')
    bairro = models.ForeignKey(Bairro, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='fk_pessoafisica_bairro')
    cep = models.CharField(max_length=9)
    is_residpropria = models.BooleanField(default=True)
    temporesidencia = models.PositiveIntegerField(null=True, default=0)
    email = models.EmailField(max_length=100, blank=True)
    is_deleted = models.BooleanField(default=False)
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    data_criacao = models.DateTimeField(editable=False)
    data_edicao = models.DateTimeField()
    situacao = models.ForeignKey(SituacaoPessoa, blank=True, null=True, on_delete=models.PROTECT,
                                 related_name='fk_pessoafisica_situacaopessoa')
    pontoreferencia = models.CharField(max_length=254, blank=True)
    rendaempresa = models.CharField(max_length=100, null=True, blank=True)
    dtadmissempresa = models.DateField(null=True, blank=True)
    rendaliqempresa = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    cargoempresa = models.CharField(max_length=30, blank=True)
    numbeneficio = models.CharField(max_length=20, blank=True)
    rendaalugueis = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    rendaliqtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    observacao = models.CharField(max_length=254, blank=True)
    history =HistoricalRecords()

    def __str__(self):
        if self.numcpf:
           return self.nome + ' (CPF: ' + self.numcpf + ')' + ' - ID: ' + (str(self.id).zfill(6))
        else:
            return self.nome + ' - ID: ' + (str(self.id).zfill(6))

    # @property
    # def is_devedor(self):
    #     qs = Financeiro.objects.filter(processo__clientepf_id=self.pk, status='A', dtvencimento__lt=date.today())
    #     if qs:
    #         return True
    #     else:
    #         return False


# Tabela de Pessoas Jurídicas (Empresas, Bancos e Fornecedores)
class PessoaJuridica(models.Model):
    PORTEMPRESA_OPCOES = (
        ("1", "MEI"),
        ("2", "ME"),
        ("3", "LTDA"),
        ("4", "EIRELI"),
        ("5", "EPP"),
        ("6", "INFORMAL")
    )

    class Meta:
        ordering = ["id"]

    id = models.AutoField(primary_key=True)
    razaosocial = models.CharField(max_length=100, null=False, blank=False, unique=True)
    nomefantasia = models.CharField(max_length=100, null=False, blank=False)
    dtiniatividade = models.DateField(null=False, blank=False)
    porteempresa = models.CharField(max_length=1, choices=PORTEMPRESA_OPCOES, default='2')
    setornegocio = models.ForeignKey(SetorNegocio, on_delete=models.PROTECT, null=True, blank=True,
                                     related_name='fk_pessoajuridica_setornegocio')
    ramoatividade = models.ForeignKey(RamoAtividade, on_delete=models.PROTECT, null=True, blank=True,
                                      related_name='fk_pessoajuridica_ramoatividade')
    numcnpj = models.CharField(max_length=18, null=True, blank=True, unique=True, validators=[validate_cnpj])
    numinscest = models.CharField(max_length=9, null=True, blank=True)
    numinscmun = models.CharField(max_length=9, null=True, blank=True)
    telfixo = models.CharField(max_length=14, blank=True)
    telcelular1 = models.CharField(max_length=15, blank=True)
    telcelular2 = models.CharField(max_length=15, blank=True)
    logradouro = models.CharField(max_length=50)
    numimovel = models.CharField(max_length=4)
    complemento = models.CharField(max_length=30, null=True, blank=True)
    cidade = models.ForeignKey(Cidade, on_delete=models.PROTECT, null=True, blank=True,
                               related_name='fk_pessoajuridica_cidade')
    bairro = models.ForeignKey(Bairro, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='fk_pessoajuridica_bairro')
    cep = models.CharField(max_length=9)
    is_deleted = models.BooleanField(default=False)
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    data_criacao = models.DateTimeField(editable=False)
    data_edicao = models.DateTimeField()
    situacao = models.ForeignKey(SituacaoPessoa, on_delete=models.PROTECT, null=True, blank=True,
                                 related_name='fk_pessoajuridica_situacaopessoa')
    pontoreferencia = models.CharField(max_length=254, blank=True)
    observacao = models.CharField(max_length=254, blank=True)
    history = HistoricalRecords()

    def __str__(self):
        if self.numcnpj:
           return self.razaosocial + ' (CNPJ: ' + self.numcnpj + ')' + ' - ID: ' + (str(self.id).zfill(6))
        else:
            return self.razaosocial + ' - ID: ' + (str(self.id).zfill(6))

    @property
    def nome_porte(self):
        portes = {
            '1': "MEI",
            '2': "ME",
            '3': "LTDA",
            '4': "EIRELI",
            '5': "EPP",
            '6': "INFORMAL"
        }
        return portes.get(self.porteempresa, "")

    # @property
    # def is_devedor(self):
    #     qs = Financeiro.objects.filter(processo__clientepj_id=self.pk, status='A', dtvencimento__lt=date.today())
    #     if qs:
    #         return True
    #     else:
    #         return False


# Tabela de Sócios da Pessoa Jurídica
class PJuridicaSocio(models.Model):

    class Meta:
        ordering = ["id"]

    id = models.AutoField(primary_key=True)
    pessoajuridica = models.ForeignKey(PessoaJuridica, on_delete=models.PROTECT, related_name='fk_pjuridicasocio_pjuridica')
    socio = models.ForeignKey(PessoaFisica, on_delete=models.PROTECT, null=True, blank=True,
                               related_name='fk_pjuridicasocio_socio')
    cota = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    is_deleted = models.BooleanField(default=False)
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    data_criacao = models.DateTimeField(editable=False, default=timezone.now)
    data_edicao = models.DateTimeField(default=timezone.now)
    history =HistoricalRecords()

    def __str__(self):
        return str(self.socio)


# Tabela de Processos dos Clientes
class Processo(models.Model):

    PROGRAMA_OPCOES = (
        ("1", "INDICAÇÃO"),
        ("2", "INTERNET"),
        ("3", "PANFLETO"),
        ("4", "TELEVISÃO"),
    )
    SITNEGOCIO_OPCOES = (
        ("1", "EXPANSÃO"),
        ("2", "IMPLANTAÇÃO"),
    )
    TIPCONTA_OPCOES = (
        ("1", "CORRENTE PF"),
        ("2", "POUPANÇA PF"),
        ("3", "CORRENTE PJ"),
        ("4", "POUPANÇA PJ"),
    )
    STATUS_OPCOES = (
        # ("P", "EM ANDAMENTO - INICIADO"),
        # ("A", "EM ANDAMENTO - A"),
        # ("R", "EM ANDAMENTO - R"),
        ("A", "EM ANDAMENTO"),
        ("C", "CANCELADO"),
        ("1", "1º PARECER"),
        ("2", "2º PARECER"),
        ("F", "FINALIZADO"),
        ("N", "NEGOCIADO"),
        ("X", "NEGADO"),
    )

    # def doc_image_path(self, filename):
    #     # ''' Returns the a unique image name in form of a hash '''
    #     extension = pathlib.Path(filename).suffix
    #     hashed_name = hashlib.sha256(filename.lower().encode('utf-8')).hexdigest()
    #     # return 'homepage/static/media/{0}{1}' \
    #     return '{0}{1}' \
    #         .format(hashed_name, extension)

    def doc_image_path(instance, filename):
        """Gera um caminho organizado para os arquivos PDF."""
        extension = os.path.splitext(filename)[1]  # Obtém a extensão do arquivo
        hashed_name = hashlib.sha256(filename.lower().encode('utf-8')).hexdigest()[:15]  # Nome hashado curto
        date_path = timezone.now().strftime('%Y/%m/%d')  # Organiza os arquivos por data
        return f"documentos/processo_{instance.id}/{date_path}/{hashed_name}{extension}"


    # não pode ativar pois os gráficos ficam incorretos. Tem q verificar a falha
    # class Meta:
    #     ordering = ["numprocesso"]

    id = models.AutoField(primary_key=True)
    numprocesso = models.CharField(max_length=9, unique=True)
    dtprocesso = models.DateField()
    clientepf = models.ForeignKey(PessoaFisica, on_delete=models.PROTECT, null=True, blank=True,
                                  related_name='fk_processo_pessoafisica')
    clientepj = models.ForeignKey(PessoaJuridica, on_delete=models.PROTECT, null=True, blank=True,
                                  related_name='fk_processo_pessoajuridica1')
    conhecimentoprograma = models.CharField(max_length=1, choices=PROGRAMA_OPCOES)
    linhacredito = models.ForeignKey(LinhaCredito, on_delete=models.PROTECT, null=True, blank=True,
                                     related_name='fk_processo_linhacredito')
    finalidadecredito = models.ForeignKey(FinalidadeCredito, on_delete=models.RESTRICT, null=True, blank=True,
                                          related_name='fk_processo_finalidadecredito')
    empresa = models.ForeignKey(PessoaJuridica, on_delete=models.PROTECT, null=True, blank=True,
                                related_name='fk_processo_pessoajuridica')
    situacaonegocio = models.CharField(max_length=1, choices=SITNEGOCIO_OPCOES)
    # funcao = models.ForeignKey(Funcao, on_delete=models.PROTECT, null=True, blank=True,
    #                            related_name='fk_processo_funcao')
    banco = models.ForeignKey(Banco, on_delete=models.PROTECT, null=True, blank=True,
                              related_name='fk_processo_banco')
    agencia = models.CharField(max_length=10, blank=True)
    conta = models.CharField(max_length=20, blank=True)
    tipconta = models.CharField(max_length=1, choices=TIPCONTA_OPCOES, default='1')
    # banco1 = models.ForeignKey(Banco, on_delete=models.PROTECT, null=True, blank=True,
    #                           related_name='fk_processo_banco1')
    # agencia1 = models.CharField(max_length=10, blank=True)
    # conta1 = models.CharField(max_length=20, blank=True)
    # tipconta1 = models.CharField(max_length=1, choices=TIPCONTA_OPCOES, default='1')
    # O item 6 (referências), bem como o(s) Avalista(s) encontram-se em outras Tabelas
    status = models.CharField(max_length=1, choices=STATUS_OPCOES, default='P')
    numprotocolo = models.CharField(max_length=20, unique=True)
    sobreonegocio = models.CharField(max_length=512, null=True, blank=True)
    porquedonegocio = models.CharField(max_length=512, null=True, blank=True)
    evolucaonegocio = models.CharField(max_length=512, null=True, blank=True)
    numbeneficiados = models.PositiveIntegerField(default=0)
    numfuncionarios = models.PositiveIntegerField(default=0)
    expecocupacoes = models.PositiveIntegerField(default=0)
    observacao = models.CharField(max_length=254, blank=True)
    valorcoberto = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    valorsolicitado = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    prazosolicitado = models.PositiveIntegerField(null=True, default=0)
    documentacao = models.FileField(upload_to=doc_image_path, null=True, blank=True,
                                    validators=[validar_tamanho_arquivo])
    valorrendanegoc = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    localizacao = models.ForeignKey(Localizacao, on_delete=models.PROTECT, null=True, blank=True,
                                    related_name='fk_processo_localizacao')
    # fornecedor = models.ForeignKey(PessoaJuridica, on_delete=models.PROTECT, null=True, blank=True,
    #                                related_name='fk_processo_pessoajuridica2')
    veiculo = models.ForeignKey(Veiculo, on_delete=models.PROTECT, null=True, blank=True,
                                   related_name='fk_processo_veiculo')
    # agenciafornec = models.CharField(max_length=10, blank=True)
    # contafornec = models.CharField(max_length=20, blank=True)
    is_deleted = models.BooleanField(default=False)
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    data_criacao = models.DateTimeField(editable=False)
    data_edicao = models.DateTimeField()
    history =HistoricalRecords()

    def __str__(self):
        return self.numprocesso

    @property
    def valorcoberto_real(self):
        setlocale(LC_ALL, 'pt_BR.UTF-8')
        return moeda(self.valorcoberto,grouping=True)

    @property
    def processo_status(self):
        status = 'Processo nº ' + self.numprocesso + ' | '
        if self.status == 'A':
            status = status + 'Em andamento'
        elif self.status == 'C':
            status = status + 'Cancelado'
        elif self.status == '1':
            status = status + '1º Parecer'
        elif self.status == '2':
            status = status + '2º Parecer'
        elif self.status == 'F':
            status = status + 'Finalizado'
        elif self.status == 'N':
            status = status + 'Negociado'
        elif self.status == 'X':
            status = status + 'Negado'
        status = status + ' (' + str(self.localizacao) + ')'
        return status

    @property
    def texto_status(self):
        texto = ''
        if self.status == 'A':
            texto = 'Em andamento'
        elif self.status == 'C':
            texto = 'Cancelado'
        elif self.status == '1':
            texto = '1º Parecer'
        elif self.status == '2':
            texto = '2º Parecer'
        elif self.status == 'F':
            texto = 'Finalizado'
        elif self.status == 'N':
            texto = 'Negociado'
        elif self.status == 'X':
            texto = 'Negado'
        return texto

    # @property
    # def is_devedor(self):
    #     qs = Financeiro.objects.filter(processo_id=self.pk, status='A', dtvencimento__lt=date.today())
    #     if qs:
    #         return True
    #     else:
    #         return False

    @property
    def texto_tipconta(self):
        texto = ''
        if self.tipconta == '1':
            texto = 'CORRENTE PF'
        elif self.tipconta == '2':
            texto = 'POUPANÇA PF'
        elif self.tipconta == '3':
            texto = 'CORRENTE PJ'
        elif self.tipconta == '4':
            texto = 'POUPANÇA PJ'
        return texto

    # @property
    # def is_quitado(self):
    #     qs = Financeiro.objects.filter(processo_id=self.pk, status='A')
    #     if qs:
    #         return False
    #     else:
    #         return True


class Referencia(models.Model):
    class Meta:
        ordering = ["nome"]

    id = models.AutoField(primary_key=True)
    processo = models.ForeignKey(Processo, on_delete=models.PROTECT, related_name='fk_referencia_processo')
    tipofonte = models.ForeignKey(TipoFonteRefer, on_delete=models.PROTECT,
                                  related_name='fk_referencia_tipofonterefer')
    nome = models.CharField(max_length=30)
    # tipo = models.CharField(max_length=1, choices=TIPO_OPCOES)
    telefone = models.CharField(max_length=15, blank=True)
    conceito = models.CharField(max_length=10, null=False, blank=True)
    is_deleted = models.BooleanField(default=False)
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    data_criacao = models.DateTimeField(editable=False, default=timezone.now)
    data_edicao = models.DateTimeField(default=timezone.now)
    history =HistoricalRecords()

    def __str__(self):
        return str(self.processo) + ' - ' + str(self.nome)


class Parecer(models.Model):
    TIPO_OPCOES = (
        ("N", "NOVO"),
        ("R", "RENOVAÇÃO"),
    )

    class Meta:
        ordering = ["processo"]

    id = models.AutoField(primary_key=True)
    dtcomite = models.DateField(null=True, blank=True)
    processo = models.ForeignKey(Processo, on_delete=models.PROTECT, related_name='fk_parecer_processo')
    valorgiro_sugerido = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    valorfixo_sugerido = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    valorgiro_aprovado = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    valorfixo_aprovado = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    taxasugerida = models.DecimalField(max_digits=12, decimal_places=10, default=0.00)
    taxaaprovada = models.DecimalField(max_digits=12, decimal_places=10, default=0.00)
    prazosugerido = models.PositiveIntegerField(null=True, default=0)
    prazoaprovado = models.PositiveIntegerField(null=True, default=0)
    dtprivencto = models.DateField(null=True, blank=True)
    valorparc_sugerido = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    valorparcela = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    dtliberacao = models.DateField(null=True, blank=True)
    pareceragente = models.CharField(max_length=512, blank=True)
    motivonegativa = models.CharField(max_length=254, blank=True)
    tipo = models.CharField(max_length=1, choices=TIPO_OPCOES, default='N')
    conceito = models.PositiveIntegerField(null=True, default=0)
    is_deleted = models.BooleanField(default=False)
    is_financeiro = models.BooleanField(default=False)
    is_negado = models.BooleanField(default=False)
    is_desistencia = models.BooleanField(default=False)
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    data_criacao = models.DateTimeField(editable=False)
    data_edicao = models.DateTimeField()
    history =HistoricalRecords()

    @property
    def vlrparcsemjuros(self):
        return (self.valorgiro_aprovado + self.valorfixo_aprovado) / self.prazoaprovado

    @property
    def vlrjuros(self):
        return self.valorparcela - ((self.valorgiro_aprovado + self.valorfixo_aprovado)/ self.prazoaprovado)

    @property
    def vlrtotalaprovado(self):
        return self.valorgiro_aprovado + self.valorfixo_aprovado

    def __str__(self):
        return str(self.processo)


class Negociacao(models.Model):

    class Meta:
        ordering = ["processo"]

    id = models.AutoField(primary_key=True)
    dtnegociacao = models.DateField()
    processo = models.ForeignKey(Processo, on_delete=models.PROTECT, related_name='fk_negociacao_processo')
    vlrtotaloriginal = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    valordebito = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    valoracres = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    valordesc = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    novoprazo = models.PositiveIntegerField(null=True, default=0)
    novovalor = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    dtprivencto = models.DateField()
    valorparcela = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    motivo = models.CharField(max_length=254, blank=True)
    is_deleted = models.BooleanField(default=False)
    is_financeiro = models.BooleanField(default=False)
    is_refis = models.BooleanField(default=False)
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    data_criacao = models.DateTimeField(editable=False)
    data_edicao = models.DateTimeField()
    history =HistoricalRecords()

    def __str__(self):
        return str(self.id).zfill(6) + ' (' + str(self.processo) + ')'


class Avalista(models.Model):

    class Meta:
        ordering = ["avalista"]

    id = models.AutoField(primary_key=True)
    processo = models.ForeignKey(Processo, on_delete=models.PROTECT, related_name='fk_avalista_processo')
    avalista = models.ForeignKey(PessoaFisica, on_delete=models.CASCADE,
                                 related_name='fk_avalista_pessoafisica')
    graurelacao = models.ForeignKey(GrauRelacao, on_delete=models.PROTECT, null=True, blank=True,
                                    related_name='fk_avalista_graurelacao')
    observacao = models.CharField(max_length=254, blank=True)
    negociacao = models.ForeignKey(Negociacao, on_delete=models.SET_NULL, null=True, blank=True)
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    # data_criacao = models.DateTimeField(editable=False)
    data_criacao = models.DateTimeField(editable=False, default=timezone.now)
    data_edicao = models.DateTimeField(default=timezone.now)
    history =HistoricalRecords()

    def __str__(self):
        return str(self.processo) + ' - ' + str(self.avalista.nome)


class Financeiro(models.Model):
    STATUS_OPCOES = (
        ("A", "EM ABERTO"),
        ("C", "CANCELADO"),
        ("N", "NEGOCIADO"),
        ("P", "PAGO"),
    )

    class Meta:
        ordering = ["id"]

    id = models.AutoField(primary_key=True)
    processo = models.ForeignKey(Processo, on_delete=models.PROTECT, related_name='fk_financeiro_processo')
    numparcela = models.PositiveIntegerField(null=True, default=0)
    valororiginal = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    valorparcela = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    parecer = models.ForeignKey(Parecer, on_delete=models.PROTECT, null=True, blank=True,
                                   related_name='fk_financeiro_parecer')
    negociacao = models.ForeignKey(Negociacao, on_delete=models.PROTECT, null=True, blank=True,
                                   related_name='fk_financeiro_negociacao')
    dtemissao = models.DateField()
    dtvencimento = models.DateField()
    valorpago = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    dtpagamento = models.DateField(null=True, blank=True)
    valormulta = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    valorjuros = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    valoracres = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    valordesc = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    percmulta = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    percjuros = models.DecimalField(max_digits=10, decimal_places=4, default=0.00)
    valorfinal = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    numenvio = models.PositiveIntegerField(default=0)
    dtgravacao = models.DateTimeField(null=True, blank=True)
    nossonumero = models.CharField(max_length=17, null=True, blank=True, default = '0')
    status = models.CharField(max_length=1, choices=STATUS_OPCOES, default='A')
    is_deleted = models.BooleanField(default=False)
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    data_criacao = models.DateTimeField(editable=False)
    data_edicao = models.DateTimeField()
    observacao = models.CharField(max_length=128, blank=True, null=True)
    valormultabolvenc = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    history =HistoricalRecords()

    def __str__(self):
        return str(self.processo) + ' - ' + str(self.numparcela)

    @property
    def jurosfinanc(self):
        return self.valorparcela - self.valororiginal

    @property
    def acresctotal(self):
        return self.valoracres + self.valormulta + self.valorjuros

    @property
    def data_dia(self):
        return datetime.today()

    @property
    def dias_atraso(self):
        d1 = datetime.strptime(str(self.dtvencimento), '%Y-%m-%d')
        d2 = datetime.strptime(str(date.today()), '%Y-%m-%d')
        numdias = 0
        if d2 > d1:
            numdias = abs((d2 - d1).days)
        return numdias

    @property
    def juros_recebto(self):
        return self.valoracres + self.valormulta + self.valorjuros - self.valordesc

    # Atenção:
    # valorparcela = valororiginal acrescido dos juros aplicados na parcela na geração
    # valororiginal = valoraprovado no Parecer dividido pela quantidade de parcelas do financiamento
    # valorfinal = valor após a aplicação da multa e dos juros
    # valorpago = valorfinal + valoracres - valordesc


class Movimentacao(models.Model):

    class Meta:
        ordering = ["id"]

    id = models.AutoField(primary_key=True)
    dtmovimento = models.DateField()
    origem = models.ForeignKey(Localizacao, on_delete=models.PROTECT, related_name='fk_movimentacao_origem')
    destino = models.ForeignKey(Localizacao, on_delete=models.PROTECT, related_name='fk_movimentacao_destino')
    processo = models.ForeignKey(Processo, on_delete=models.PROTECT, related_name='fk_movimentacao_processo')
    observacao = models.CharField(max_length=254, blank=True)
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    is_encaminhado = models.BooleanField(default=False)
    is_recebido = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(editable=False)
    data_edicao = models.DateTimeField()
    history = HistoricalRecords()

    def __str__(self):
        return str(self.setor) + ' (' + str(self.processo.numprocesso) + ') - ' + str(self.dtmovimento)


# Tabela utilizada para armazenar o arquivo retorno do banco. Cabecalho e Detalhe.
# Os dados armazenados contemplam somente os segmentos "T" e "U". Fonte: CNAB240SegPQRSTY.pdf
#
class RetornoHeader(models.Model):

    class Meta:
        ordering = ["id"]

    id = models.AutoField(primary_key=True)
    numretorno = models.PositiveIntegerField()
    dtgravacao = models.DateField()

    def __str__(self):
        return str(self.numretorno)


class RetornoDetail(models.Model):

    STATUS_CODMOVTO = (
        ("02", "ENTRADA CONFIRMADA"),
        ("03", "ENTRADA REJEITADA"),
        ("06", "LIQUIDAÇÃO"),
        ("14", "ALT.VENCIMENTO"),
        ("28", "DÉB.TARIFAS/CUSTOS"),
    )

    class Meta:
        ordering = ["id"]

    id = models.AutoField(primary_key=True)
    retorno = models.ForeignKey(RetornoHeader, on_delete=models.PROTECT, related_name='fk_retornodetail_retorno')
    numseq = models.CharField(max_length=10)
    nossonumero = models.CharField(max_length=17)
    codmovimento = models.CharField(max_length=2, choices=STATUS_CODMOVTO)
    numdocumento = models.CharField(max_length=15)
    valortitulo = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    dtvencimento = models.DateField()
    jurosmulta = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    valordesc = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    valorpago = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    dtocorrencia = models.DateField(null=True, blank=True)

    def __str__(self):
        return str(self.nossonumero)


# # Tabela utilizada para armazenar o arquivo de envio p/ o banco. Cabecalho e Detalhe.
# # Os dados armazenados contemplam somente os segmentos "P", "Q" e "R". Fonte: CNAB240SegPQRSTY.pdf
# #
# class EnvioHeader(models.Model):
#
#     class Meta:
#         ordering = ["id"]
#
#     id = models.AutoField(primary_key=True)
#     numenvio = models.PositiveIntegerField()
#     dtgravacao = models.DateField()
#
#     def __str__(self):
#         return str(self.numenvio)
#
#
# class EnvioDetail(models.Model):
#
#     class Meta:
#         ordering = ["id"]
#
#     id = models.AutoField(primary_key=True)
#     envio = models.ForeignKey(EnvioHeader, on_delete=models.CASCADE, related_name='fk_enviodetail_envio')
#     titulo = models.ForeignKey(ProcessoFinanc, on_delete=models.CASCADE, related_name='fk_enviodetail_titulo')
#     nossonumero = models.CharField(max_length=17)
#
#     def __str__(self):
#         return str(self.nossonumero)

class Comite(models.Model):

    class Meta:
        ordering = ["id"]

    id = models.AutoField(primary_key=True)
    dtcomite = models.DateField()
    observacao = models.CharField(max_length=254, blank=True)
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    is_realizado = models.BooleanField(default=True)
    numreuniao = models.PositiveIntegerField()
    data_criacao = models.DateTimeField(editable=False)
    data_edicao = models.DateTimeField()
    history = HistoricalRecords()

    def __str__(self):
        return str(self.dtcomite)


class ProcessosComite(models.Model):

    class Meta:
        ordering = ["id"]

    id = models.AutoField(primary_key=True)
    comite = models.ForeignKey(Comite, on_delete=models.PROTECT, related_name='fk_processoscomite_comite')
    processo = models.ForeignKey(Processo, on_delete=models.PROTECT, related_name='fk_processoscomite_processo')
    observacao = models.CharField(max_length=254, blank=True)
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    is_aprovado = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(editable=False, default=timezone.now)
    data_edicao = models.DateTimeField(default=timezone.now)
    history = HistoricalRecords()

    def __str__(self):
        return str(self.comite.dtcomite) + ' - ' + str(self.processo.numprocesso)


class MembrosComite(models.Model):

    class Meta:
        ordering = ["id"]

    id = models.AutoField(primary_key=True)
    comite = models.ForeignKey(Comite, on_delete=models.PROTECT, related_name='fk_membroscomite_comite')
    operador = models.ForeignKey(Operador, on_delete=models.PROTECT, related_name='fk_membroscomite_operador')
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(editable=False, default=timezone.now)
    data_edicao = models.DateTimeField(default=timezone.now)
    history = HistoricalRecords()

    def __str__(self):
        return str(self.comite.dtcomite) + ' - ' + str(self.operador.numcpf)

