from email.policy import default

from django.db import models

from processos.validators import validate_cpf

from django.utils import timezone

from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords

UF_OPCOES = (
    ("RO", "RONDÔNIA"),
    ("AC", "ACRE"),
    ("AM", "AMAZONAS"),
    ("RR", "RORAIMA"),
    ("PA", "PARÁ"),
    ("AP", "AMAPÁ"),
    ("TO", "TOCANTINS"),
    ("MA", "MARANHÃO"),
    ("PI", "PIAUÍ"),
    ("CE", "CEARÁ"),
    ("RN", "RIO GRANDE DO NORTE"),
    ("PB", "PARAÍBA"),
    ("PE", "PERNAMBUCO"),
    ("AL", "ALAGOAS"),
    ("SE", "SERGIPE"),
    ("BA", "BAHIA"),
    ("MG", "MINAS GERAIS"),
    ("ES", "ESPÍRITO SANTO"),
    ("RJ", "RIO DE JANEIRO"),
    ("SP", "SÃO PAULO"),
    ("PR", "PARANÁ"),
    ("SC", "SANTA CATARINA"),
    ("RS", "RIO GRANDE DO SUL"),
    ("MS", "MATO GROSSO DO SUL"),
    ("MT", "MATO GROSSO"),
    ("GO", "GOIÁS"),
    ("DF", "DISTRITO FEDERAL"),
)

UF_OPCOES1 = (
    ("RO", "RO"),
    ("AC", "AC"),
    ("AM", "AM"),
    ("RR", "RR"),
    ("PA", "PA"),
    ("AP", "AP"),
    ("TO", "TO"),
    ("MA", "MA"),
    ("PI", "PI"),
    ("CE", "CE"),
    ("RN", "RN"),
    ("PB", "PB"),
    ("PE", "PE"),
    ("AL", "AL"),
    ("SE", "SE"),
    ("BA", "BA"),
    ("MG", "MG"),
    ("ES", "ES"),
    ("RJ", "RJ"),
    ("SP", "SP"),
    ("PR", "PR"),
    ("SC", "SC"),
    ("RS", "RS"),
    ("MS", "MS"),
    ("MT", "MT"),
    ("GO", "GO"),
    ("DF", "DF"),
)

# Tabela de Bancos
class Banco(models.Model):

    class Meta:
        ordering = ["nome"]

    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=3, unique=True, null=False)
    nome = models.CharField(max_length=50, unique=True, null=False)
    site = models.CharField(max_length=50, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    history = HistoricalRecords()

    def __str__(self):
        return self.nome


# Tabela de Cidades
class Cidade(models.Model):

    class Meta:
        ordering = ["nome"]

    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100, null=False, blank=False)
    codibge = models.CharField(max_length=7, unique=True)
    uf = models.CharField(max_length=2, choices=UF_OPCOES, blank=False, null=False)
    is_deleted = models.BooleanField(default=False)
    history = HistoricalRecords()

    def __str__(self):
        # return self.nome + " (" + self.uf + ")"
        return self.nome


# Tabela de Bairros
class Bairro(models.Model):

    class Meta:
        ordering = ["nome"]

    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=50)
    cidade = models.ForeignKey(Cidade, on_delete=models.SET_NULL, null=True, blank=True, related_name='fk_bairro_cidade')
    is_deleted = models.BooleanField(default=False)
    history = HistoricalRecords()

    def __str__(self):
        return self.nome


# Tabela de Estado Civil
class EstadoCivil(models.Model):

    class Meta:
        ordering = ["nome"]

    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=50, unique=True)
    is_deleted = models.BooleanField(default=False)
    history = HistoricalRecords()

    def __str__(self):
        return self.nome


# Tabela de Regimes de Bens
class RegimeBens(models.Model):

    class Meta:
        ordering = ["nome"]

    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=50, unique=True)
    is_deleted = models.BooleanField(default=False)
    history = HistoricalRecords()

    def __str__(self):
        return self.nome


# Tabela de Linhas de Crédito
class LinhaCredito(models.Model):
    TPCLIENTE_OPCOES = (
        ("F", "P.FÍSICA"),
        ("J", "P.JURÍDICA"),
    )

    MODELO_OPCOES = (
        ("1", "MODELO 1"),
        ("2", "MODELO 2"),
    )

    class Meta:
        ordering = ["nome"]

    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=50, unique=True)
    grupo = models.CharField(max_length=15)
    limite = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    orcamentoanual = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    nmaxparcelas = models.PositiveIntegerField(default=0)
    nminparcelas = models.PositiveIntegerField(default=0)
    juros_aa = models.DecimalField(max_digits=12, decimal_places=10, default=0.00000000)
    juros_am = models.DecimalField(max_digits=12, decimal_places=10, default=0.00000000)
    carencia = models.PositiveIntegerField(default=0)
    nminavalistas = models.PositiveIntegerField(default=0)
    tpcliente = models.CharField(max_length=1, choices=TPCLIENTE_OPCOES, default='F')
    textotxcontrato = models.CharField(max_length=100, null=True)
    is_deleted = models.BooleanField(default=False)
    is_garantia = models.BooleanField(default=False)
    modelo = models.CharField(max_length=1, choices=MODELO_OPCOES, default='1')
    history = HistoricalRecords()

    def __str__(self):
        return self.nome


# Tabela de Finalidade do Crédito
class FinalidadeCredito(models.Model):

    class Meta:
        ordering = ["nome"]

    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=50, unique=True)
    is_deleted = models.BooleanField(default=False)
    history = HistoricalRecords()

    def __str__(self):
        return self.nome


# Tabela de Setores de Negócio
class SetorNegocio(models.Model):

    class Meta:
        ordering = ["nome"]

    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=50, unique=True)
    is_deleted = models.BooleanField(default=False)
    history = HistoricalRecords()

    def __str__(self):
        return self.nome


# Tabela de Setores de Negócio
class RamoAtividade(models.Model):

    class Meta:
        ordering = ["nome"]

    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=150, unique=True)
    is_deleted = models.BooleanField(default=False)
    history = HistoricalRecords()

    def __str__(self):
        return self.nome


# Tabela de Profissões
class Profissao(models.Model):

    class Meta:
        ordering = ["nome"]

    id = models.AutoField(primary_key=True)
    cbo = models.CharField(max_length=6)
    # cbo = models.CharField(max_length=6, unique=True)
    nome = models.CharField(max_length=100, unique=True)
    is_deleted = models.BooleanField(default=False)
    history = HistoricalRecords()

    def __str__(self):
        return self.nome


# Tabela de visualização dos Logs CRUD - somente consulta
class Log(models.Model):

    class Meta:
        managed = False
        db_table = 'vw_log'

    username = models.CharField(max_length=150)
    is_superuser = models.BooleanField()
    is_active = models.BooleanField()
    tabela = models.CharField(max_length=30)
    nome = models.CharField(max_length=50)
    is_deleted = models.BooleanField()
    history_date = models.DateTimeField()
    history_type = models.CharField(max_length=1)

    def __str__(self):
        return str(self.data) + ': ' + self.evento


# Tabela de Graus de Relação (Pai, Mãe, Irmão, ...)
class GrauRelacao(models.Model):

    class Meta:
        ordering = ["nome"]

    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=50, unique=True)
    is_deleted = models.BooleanField(default=False)
    history = HistoricalRecords()

    def __str__(self):
        return self.nome


# Tabela de Tipos de Fonte de Refências para clientes e avalistas
class TipoFonteRefer(models.Model):

    class Meta:
        ordering = ["nome"]

    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=50, unique=True)
    is_deleted = models.BooleanField(default=False)
    history = HistoricalRecords()

    def __str__(self):
        return self.nome


# Tabela de Situação da Pessoaa (Pessoa Física ou Jurídica)
class SituacaoPessoa(models.Model):

    class Meta:
        ordering = ["descricao"]

    id = models.AutoField(primary_key=True)
    descricao = models.CharField(max_length=50, unique=True)
    is_deleted = models.BooleanField(default=False)
    blq_processo = models.BooleanField(default=False)
    history = HistoricalRecords()

    def __str__(self):
        return self.descricao


# Tabela de Feriados
class Feriado(models.Model):
    TIPO_OPCOES = (
        ("N", "NACIONAL"),
        ("M", "MUNICIPAL"),
        ("O", "OUTROS"),
    )

    class Meta:
        ordering = ["dtferiado"]

    id = models.AutoField(primary_key=True)
    dtferiado = models.DateField(unique=True)
    descricao = models.CharField(max_length=100, null=True, blank=True)
    tipo = models.CharField(max_length=1, choices=TIPO_OPCOES)
    observacao = models.CharField(max_length=256, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    history = HistoricalRecords()

    def __str__(self):
        return str(self.dtferiado)

    @property
    def nome_tipo(self):
        if self.tipo == 'N':
            return "NACIONAL"
        elif self.tipo == 'M':
            return "MUNICIPAL"
        elif self.tipo == 'O':
            return "OUTROS"


# Tabela de Localizações dos Processos
class Localizacao(models.Model):

    class Meta:
        ordering = ["nome"]

    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100, unique=True)
    is_deleted = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    history = HistoricalRecords()

    def __str__(self):
        return self.nome


# Tabela de Operadores do Sistema
class Operador(models.Model):

    class Meta:
        ordering = ["numcpf"]

    id = models.AutoField(primary_key=True)
    numcpf = models.CharField(max_length=14, unique=True, validators=[validate_cpf])
    secretaria = models.CharField(max_length=50, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    is_membrocomite = models.BooleanField(default=False)
    history = HistoricalRecords()

    def __str__(self):
        return str(self.user) + " (" + str(self.numcpf) + ")"


# Tabela de Operadores x Localizões de Movimentação - Setores do Sistema
class Operador_Local(models.Model):

    class Meta:
        ordering = ["id"]

    id = models.AutoField(primary_key=True)
    localizacao = models.ForeignKey(Localizacao, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='fk_operador_local_localizacao')
    operador = models.ForeignKey(Operador, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='fk_operador_local_operador')
    is_deleted = models.BooleanField(default=False)
    history = HistoricalRecords()

    def __str__(self):
        return str(self.operador) + " (" + str(self.localizacao) + ")"


# Tabela de Valores de Descontos para o REFIS
class TabRefis(models.Model):

    class Meta:
        ordering = ["id"]

    id = models.AutoField(primary_key=True)
    linhacredito = models.ForeignKey(LinhaCredito, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='fk_tabrefis_linhacredito')
    faixaparc_ini = models.PositiveIntegerField(default=0)
    faixaparc_fin = models.PositiveIntegerField(default=0)
    descjuros = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    descmulta = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    parcmin_pf = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    parcmin_pj = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    is_deleted = models.BooleanField(default=False)
    is_teste = models.BooleanField(default=False)
    history = HistoricalRecords()

    def __str__(self):
        return self.linhacredito.nome + " - Faixa: " + str(self.faixaparc_ini) + " a " + str(self.faixaparc_fin) + ")"

# Nova Tabela de Parâmetros Gerais/Configuração do sistema
class Config(models.Model):

    MODCALCULO_OPCOES = (
        ("1", "MODELO 1"),
        ("2", "MODELO2 - PRICE"),
    )
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

    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=50, null=True, blank=True)
    exercicio = models.PositiveIntegerField(null=False)
    multa = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    juros = models.DecimalField(max_digits=12, decimal_places=10, default=0.00000000)
    metaagente = models.PositiveIntegerField(null=False)
    tmpconclusaoprocesso = models.PositiveIntegerField(null=False)
    ultenviobanco = models.PositiveIntegerField()
    ultnossonumero = models.CharField(max_length=17)
    is_tstremessa = models.BooleanField(default=False)
    cidade_default = models.ForeignKey(Cidade, on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='fk_config_cidade')
    banco_default = models.ForeignKey(Banco, on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='fk_config_banco')
    estcivil_default = models.ForeignKey(EstadoCivil, on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name='fk_config_estcivil')
    graurelacao_default = models.ForeignKey(GrauRelacao, on_delete=models.SET_NULL, null=True, blank=True,
                                            related_name='fk_config_graurelacao')
    regimebens_default = models.ForeignKey(RegimeBens, on_delete=models.SET_NULL, null=True, blank=True,
                                           related_name='fk_config_regimebens')
    linhacredito_default = models.ForeignKey(LinhaCredito, on_delete=models.SET_NULL, null=True, blank=True,
                                             related_name='fk_config_linhacredito')
    finalidadecredito_default = models.ForeignKey(FinalidadeCredito, on_delete=models.SET_NULL, null=True, blank=True,
                                                  related_name='fk_config_finalidadecredito')
    setornegocio_default = models.ForeignKey(SetorNegocio, on_delete=models.SET_NULL, null=True, blank=True,
                                             related_name='fk_config_setornegocio')
    cep_default = models.CharField(max_length=9, null=True, blank=True)
    tipdocumento_default = models.CharField(max_length=10, null=True, blank=True)
    conhecimentoprograma_default = models.CharField(max_length=1, choices=PROGRAMA_OPCOES)
    situacaonegocio_default = models.CharField(max_length=1, choices=SITNEGOCIO_OPCOES)
    representanteconselho = models.CharField(max_length=2048, null=True, blank=True)
    representantegoverno = models.CharField(max_length=2048, null=True, blank=True)
    agentefinanceiro = models.CharField(max_length=2048, null=True, blank=True)
    testemunha1 = models.CharField(db_column='testemunha1', max_length=128, null=True, blank=True)
    mostraregcancelados = models.BooleanField(default=False)
    mostratitcancelados = models.BooleanField(default=True)
    modelocalculo_financ = models.CharField(max_length=1, choices=MODCALCULO_OPCOES, default='2')
    linhalogo1 = models.CharField(max_length=128, null=True, blank=True)
    linhalogo2 = models.CharField(max_length=128, null=True, blank=True)
    linhalogo3 = models.CharField(max_length=128, null=True, blank=True)
    taxaboleto = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    multaboleto = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_deleted = models.BooleanField(default=False)
    history = HistoricalRecords()

    def __str__(self):
        return self.nome

# Tabela de Fechamentos
class Fechamento(models.Model):

    class Meta:
        ordering = ["id"]

    id = models.AutoField(primary_key=True)
    referencia = models.CharField(max_length=6)
    dtfechamento = models.DateField()
    observacao = models.CharField(max_length=256, null=True, blank=True)
    fechado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    data_criacao = models.DateTimeField(editable=False, default=timezone.now)
    is_deleted = models.BooleanField(default=False)
    history = HistoricalRecords()

    def __str__(self):
        return str(self.referencia) + " (" + str(self.dtfechamento) + ")"

# Tabela de Bens Garantidores - Veículos
class MarcaVeiculo(models.Model):
    class Meta:
        ordering = ["nome"]

    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=50, unique=True)
    is_deleted = models.BooleanField(default=False)
    campo_teste = models.BooleanField(default=False)
    # history = HistoricalRecords()

    def __str__(self):
        return self.nome


class Veiculo(models.Model):
    COMBUSTIVEL_OPCOES = (
        ("1", "DIESEL"),
        ("2", "GASOLINA"),
        ("3", "ALCOOL"),
        ("4", "ALCOOL/GASOLINA"),
    )

    class Meta:
        ordering = ["placa"]

    id = models.AutoField(primary_key=True)
    marca = models.ForeignKey(MarcaVeiculo, on_delete=models.PROTECT, related_name='fk_veiculo_marcaveiculo')
    clientepf = models.ForeignKey('processos.PessoaFisica', on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='fk_veiculo_pessoafisica')  # utilizado processos.PessoaFisica para solucionar o problema que circular imports
    fornecedor = models.ForeignKey('processos.PessoaJuridica', on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='fk_veiculo_pessoajuridica')  # idem anterior
    modelo = models.CharField(max_length=50)
    placa = models.CharField(max_length=7, blank=True, null=True)
    uf = models.CharField(max_length=2, choices=UF_OPCOES1)
    renavam = models.CharField(max_length=11, blank=True, null=True)
    anofabr = models.CharField(max_length=4)
    anomodelo = models.CharField(max_length=4)
    combustivel = models.CharField(max_length=1, choices=COMBUSTIVEL_OPCOES)
    cor = models.CharField(max_length=50, blank=True, null=True)
    chassi = models.CharField(max_length=30, blank=True, null=True)
    notafiscal = models.CharField(max_length=10, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    is_vendido = models.BooleanField(default=False)
    # history = HistoricalRecords()

    def __str__(self):
        return self.marca.nome + " - " + self.modelo + " (" + self.clientepf.nome + ")"
