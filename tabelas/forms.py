from django import forms

from django.core.exceptions import ValidationError

from datetime import datetime

from tabelas.models import *
from processos.models import PessoaFisica, PessoaJuridica

from django.db.models import Q

class BancoForm(forms.ModelForm):
    """
    Formulário para manipulação do modelo Banco.

    Este formulário é utilizado para criar e editar objetos do modelo Banco.
    Inclui validações personalizadas e estilização dos campos de entrada para
    facilitar a usabilidade e a consistência visual no frontend.
    """
    required_css_class = 'required'  # Classe CSS para campos obrigatórios

    def __init__(self, *args, **kwargs):
        """
        Inicializa o formulário com configurações personalizadas para os campos.
        """
        super().__init__(*args, **kwargs)
        # Configuração dos atributos dos campos
        field_settings = {
            'codigo': {
                'class': 'textinput form-control',
                'maxlength': '3',
                'pattern': '[0-9]{3}',
                'title': 'Código do banco. Somente números.',
            },
            'nome': {
                'class': 'textinput form-control',
                'maxlength': '50',
                'title': 'Nome do banco. Aceita letras e números.',
            },
            'site': {
                'class': 'textinput form-control',
                'maxlength': '50',
                'title': 'Site do banco. Aceita letras e números.',
            },
        }

        for field_name, attributes in field_settings.items():
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update(attributes)

    class Meta:
        """
        Metainformações do formulário, definindo o modelo e os campos a serem utilizados.
        """
        model = Banco
        fields = ['codigo', 'nome', 'site']
        # Definir rótulos personalizados, se necessário
        labels = {
            'codigo': 'Código do Banco',
            'nome': 'Nome do Banco',
            'site': 'Site Oficial',
        }
        # Definir mensagens de ajuda para os campos
        help_texts = {
            'codigo': 'Informe o código de 3 dígitos do banco.',
            'nome': 'Insira o nome completo do banco.',
            'site': 'Forneça o URL do site oficial do banco.',
        }


class FechamentoForm(forms.ModelForm):
    """
    Formulário para manipulação do modelo Fechamento.

    Este formulário é utilizado para criar e editar objetos do modelo Fechamento.
    Inclui validações personalizadas e estilização dos campos de entrada para
    facilitar a usabilidade e a consistência visual no frontend.
    """
    required_css_class = 'required'  # Classe CSS para campos obrigatórios

    def __init__(self, *args, **kwargs):
        """
        Inicializa o formulário com configurações personalizadas para os campos.
        """
        super().__init__(*args, **kwargs)
        # Configuração dos atributos dos campos
        field_settings = {
            'referencia': {
                'class': 'textinput form-control',
                'maxlength': '6',
                'pattern': '[0-9]{6}',
                'title': 'Informe a referência no formato AAAAMM (Ano c/ 4 dígitos + mês com 2 dígitos)'
            },
            'dtfechamento': {
                'class': 'textinput form-control',
                # 'maxlength': '10',
                # 'pattern': '[0-9]{10}',
            },
            'fechado_por': {
                'class': 'textinput form-control',
                'maxlength': '50',
            },
            'observacao': {
                'class': 'textinput form-control',
                'maxlength': '256',
                'rows': '3',
            },
        }

        self.fields['dtfechamento'] = forms.DateField(
            widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
        )

        for field_name, attributes in field_settings.items():
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update(attributes)

    def clean_referencia(self):
        """
        Validação personalizada para garantir que a referência siga o formato correto (AAAAMM).
        """
        referencia = self.cleaned_data.get('referencia')
        if not referencia.isdigit() or len(referencia) != 6:
            raise ValidationError("A referência deve conter exatamente 6 dígitos numéricos no formato AAAAMM.")

        ano = int(referencia[:4])
        mes = int(referencia[4:6])

        hoje = datetime.today().date()

        if not (2020 <= ano <= hoje.year):
            raise ValidationError("Ano inválido na referência.")
        if not (1 <= mes <= 12):
            raise ValidationError("Mês inválido na referência.")

        return referencia

    def clean_dtfechamento(self):
        """
        Validação personalizada para garantir que a data de fechamento não seja futura.
        """
        dtfechamento = self.cleaned_data.get('dtfechamento')
        hoje = datetime.today().date()
        if dtfechamento and dtfechamento > hoje:
            raise ValidationError("A data de fechamento não pode ser futura.")

        return dtfechamento

    class Meta:
        """
        Metainformações do formulário, definindo o modelo e os campos a serem utilizados.
        """
        model = Fechamento
        fields = ['referencia', 'dtfechamento', 'fechado_por', 'observacao']
        # Definir rótulos personalizados, se necessário
        labels = {
            'referencia': 'Referência',
            'dtfechamento': 'Data do Fechamento',
            'fechado_por': 'Fechamento realizado por',
            'observacao': 'Observações',
        }


class FeriadoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['dtferiado'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['descricao'].widget.attrs.update({'class': 'textinput form-control', 'maxlength': '100',
                                                 'title': 'Descrição do feriado. Aceita letras e números.'})
        self.fields['tipo'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['observacao'].widget.attrs.update({'class': 'textinput form-control', 'maxlength': '256',
                                                 'title': 'Observações acerca do registro. Aceita letras e números.'})

    class Meta:
        model = Feriado
        fields = ['dtferiado', 'descricao', 'tipo', 'observacao']

        widgets = {
            'dtferiado': forms.TextInput(
                # format=('%Y-%m-%d'),
                attrs={'class': 'textinput form-control',
                       'placeholder': 'Selecione uma data',
                       'required': 'true',
                       'type': 'date'  # <--- IF I REMOVE THIS LINE, THE INITIAL VALUE IS DISPLAYED
                       }),
            'observacao': forms.Textarea(
                attrs={
                    'class': 'textinput form-control',
                    'rows': '3'
                }),
        }


class CidadeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nome'].widget.attrs.update(
            {'class': 'textinput form-control', 'maxlength': '100',
             'title': 'Nome da cidade. Aceita letras e números até 100 caracteres.'})
        self.fields['codibge'].widget.attrs.update(
            {'class': 'textinput form-control', 'maxlength': '7', 'pattern': '[0-9]{7}',
             'title': 'Código da cidade no IBGE. Somente números até 7 dígitos.'})
        self.fields['uf'].widget.attrs.update(
            {'class': 'textinput form-control', 'pattern': '[A-Z]{2}', 'title': 'Somente letras'})

    class Meta:
        model = Cidade
        fields = ['nome', 'codibge', 'uf']


class BairroForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        qsparametro = Config.objects.filter(is_deleted=False).last()
        cidade_default = qsparametro.cidade_default

        self.fields['cidade'].initial = cidade_default
        self.fields['cidade'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['nome'].widget.attrs.update(
            {'class': 'textinput form-control', 'maxlength': '50',
             'title': 'Nome do bairro. Aceita letras e números até 50 caracteres.'})

    class Meta:
        model = Bairro
        fields = ['cidade', 'nome']


class EstadoCivilForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nome'].widget.attrs.update({'class': 'textinput form-control'})

    class Meta:
        model = EstadoCivil
        fields = ['nome']


class GrauRelacaoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nome'].widget.attrs.update({'class': 'textinput form-control'})

    class Meta:
        model = GrauRelacao
        fields = ['nome']


class RegimeBensForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nome'].widget.attrs.update({'class': 'textinput form-control'})

    class Meta:
        model = RegimeBens
        fields = ['nome']


class LinhaCreditoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nome'].widget.attrs.update({'class': 'textinput form-control', 'maxlength': '50'})
        self.fields['grupo'].widget.attrs.update({'class': 'textinput form-control', 'maxlength': '15'})
        self.fields['orcamentoanual'].widget.attrs.update({'class': 'textinput form-control',
                                                   'style': 'text-align: right',
                                                   'title': 'Orçamento total limite no ano para a Linha de Crédito.',
                                                   'required': 'true'})
        self.fields['limite'].widget.attrs.update({'class': 'textinput form-control',
                                                   'style': 'text-align: right',
                                                   'title': 'Limite de crédito a ser concedido para o ciente nesta Linha.',
                                                   'required': 'true'})
        self.fields['nminparcelas'].widget.attrs.update({'class': 'textinput form-control', 'min': '0', 'max': '99',
                                                         'style': 'text-align: right', 'title': 'Número mínimo de parcelas para o financiamento com '
                                                                  'até 2 dígitos numéricos.'})
        self.fields['nmaxparcelas'].widget.attrs.update({'class': 'textinput form-control', 'min': '0', 'max': '99',
                                                         'style': 'text-align: right',
                                                         'title': 'Número máximo de parcelas para o financiamento com '
                                                                  'até 2 dígitos numéricos.'})
        self.fields['juros_aa'].widget.attrs.update({'class': 'textinput form-control',
                                                  'style': 'text-align: right',
                                                  'title': '% de juros ao ano a ser aplicado no empréstimo.',
                                                  'required': 'true'})
        self.fields['juros_am'].widget.attrs.update({'class': 'textinput form-control setprice juros_am',
                                                  'style': 'text-align: right',
                                                  'title': '% de juros ao mês a ser aplicado no empréstimo.',
                                                  'required': 'true'})
        self.fields['nminavalistas'].widget.attrs.update({'class': 'textinput form-control', 'min': '0', 'max': '99',
                                                         'style': 'text-align: right',
                                                          'title': 'Número mínimo de avalistas para o financiamento com '
                                                                  'até 2 dígitos numéricos.'})
        self.fields['carencia'].widget.attrs.update(
            {'class': 'textinput form-control', 'min': '0', 'max': '99', 'style': 'text-align: right',
             'title': 'Prazo máximo para carência com até 2 dígitos numéricos.'})
        self.fields['tpcliente'].widget.attrs.update(
            {'class': 'textinput form-control', 'title': 'Tipo de cliente.'})
        self.fields['textotxcontrato'].widget.attrs.update({'class': 'textinput form-control', 'required': 'true'})
        self.fields['modelo'].widget.attrs.update(
            {'class': 'textinput form-control', 'title': 'Modelo de Contrato.'})

    class Meta:
        model = LinhaCredito
        fields = ['nome', 'grupo', 'limite', 'nminparcelas', 'nmaxparcelas', 'juros_aa', 'juros_am', 'carencia',
                  'nminavalistas', 'tpcliente', 'textotxcontrato', 'orcamentoanual', 'is_garantia', 'modelo']
        widgets = {
            # 'tpcliente': forms.Select(
            #     attrs={
            #         'class': 'textinput form-control',
            #     }),
            'is_garantia': forms.CheckboxInput(
                attrs={
                    'class': 'textinput form-control',
                }),
        }


class FinalidadeCreditoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nome'].widget.attrs.update({'class': 'textinput form-control'})

    class Meta:
        model = FinalidadeCredito
        fields = ['nome']


class SetorNegocioForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nome'].widget.attrs.update({'class': 'textinput form-control'})

    class Meta:
        model = SetorNegocio
        fields = ['nome']


class RamoAtividadeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nome'].widget.attrs.update({'class': 'textinput form-control'})

    class Meta:
        model = RamoAtividade
        fields = ['nome']


class ProfissaoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cbo'].widget.attrs.update(
            {'class': 'textinput form-control', 'maxlength': '6', 'pattern': '[0-9]{6}',
             'title': 'Código Brasileiro de Ocupação com 6 dígitos numéricos.'})
        self.fields['nome'].widget.attrs.update({'class': 'textinput form-control'})

    class Meta:
        model = Profissao
        fields = ['cbo', 'nome']


class LocalizacaoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nome'].widget.attrs.update({'class': 'textinput form-control', 'maxlength': '100'})
        self.fields['is_default'].widget.attrs.update({'class': 'textinput form-control'})

    class Meta:
        model = Localizacao
        fields = ['nome', 'is_default']


class SituacaoPessoaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['descricao'].widget.attrs.update({'class': 'textinput form-control', 'maxlength': '50'})

    class Meta:
        model = SituacaoPessoa
        fields = ['descricao', 'blq_processo']
        widgets = {
            'blq_processo': forms.CheckboxInput(
                attrs={
                    'class': 'textinput form-control',
                }),
        }

class TipoFonteReferForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nome'].widget.attrs.update({'class': 'textinput form-control'})

    class Meta:
        model = TipoFonteRefer
        fields = ['nome']


class ListarLogsForm(forms.Form):

    status_Opcoes = (
        ("A", "Em aberto"),
        ("T", "Em atendimento"),
        ("E", "Encerrado - Com êxito"),
        ("S", "Encerrado - Sem êxito/solução"),
        ("C", "Cancelado"),
        ("*", "Todos"))

    data_ini = forms.DateField(label='Data de início', widget=forms.NumberInput(attrs={'type': 'date'}),
                               help_text=" Período inicial do log", required=True)
    data_fin = forms.DateField(label='Data final', widget=forms.NumberInput(attrs={'type': 'date'}),
                               help_text=" Período final do log", required=True)

    def processar(self):
        qs = Log.objects.all()

        data_ini = self.cleaned_data['data_ini']
        data_fin = self.cleaned_data['data_fin']
        # usuario = self.cleaned_data['usuario']
        # status = self.cleaned_data['status']

        # if usuario:
        #     qs = qs.filter(usuario_id__username__icontains=usuario)
        # if status and status != "*":
        #     qs = qs.filter(status=status)
        if data_ini:
            qs = qs.filter(data__gte=data_ini)
        if data_fin:
            qs = qs.filter(data__lte=data_fin)
        return qs

class ConfigForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nome'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['exercicio'].widget.attrs.update({'class': 'textinput form-control', 'min': '2020', 'max': '2100',
                                                      'pattern': '[0-9]'})
        self.fields['multa'].widget.attrs.update({'class': 'textinput form-control', 'min': '0', 'max': '9999999,99'})
        self.fields['juros'].widget.attrs.update({'class': 'textinput form-control', 'min': '0', 'max': '9999,999999'})
        self.fields['metaagente'].widget.attrs.update({'class': 'textinput form-control', 'min': '0', 'max': '999',
                                                       'title': 'Meta mensal de concessões por agente/mês. Campo com '
                                                                'até 3 dígitos numéricos.'})
        self.fields['tmpconclusaoprocesso'].widget.attrs.update({'class': 'textinput form-control', 'min': '0',
                                                                 'max': '999', 'title':
                    'Tempo médio, em dias, para conclusão de um processo. Campo com até 3 dígitos numéricos.'})
        self.fields['ultenviobanco'].widget.attrs.update({'class': 'textinput form-control', 'min': '0',
                                                           'max': '999999', 'title': 'N° do útlimo envio para o banco '
                                                                                    'gerado pelo sistema. Não alterar'})
        self.fields['ultnossonumero'].widget.attrs.update({'class': 'textinput form-control', 'min': '0',
                                                           'max': '99999999999999999', 'title': 'Último nosso número '
                                                                                  'gerado pelo sistema. Não alterar'})
        self.fields['cidade_default'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['banco_default'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['estcivil_default'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['graurelacao_default'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['regimebens_default'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['linhacredito_default'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['finalidadecredito_default'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['setornegocio_default'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['cep_default'].widget.attrs.update({'class': 'textinput form-control',
                                                        'title': 'Somente números com no máximo 8 dígitos'})
        self.fields['tipdocumento_default'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['conhecimentoprograma_default'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['situacaonegocio_default'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['modelocalculo_financ'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['linhalogo1'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['linhalogo2'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['linhalogo3'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['taxaboleto'].widget.attrs.update({'class': 'textinput form-control', 'min': '0', 'max': '9999999,99'})
        self.fields['multaboleto'].widget.attrs.update({'class': 'textinput form-control', 'min': '0', 'max': '9999999,99'})

    class Meta:
        model = Config
        fields = ['nome', 'exercicio', 'multa', 'juros', 'cidade_default', 'banco_default',
                  'estcivil_default', 'graurelacao_default', 'regimebens_default', 'linhacredito_default',
                  'finalidadecredito_default', 'setornegocio_default', 'cep_default', 'tipdocumento_default',
                  'conhecimentoprograma_default', 'situacaonegocio_default', 'metaagente', 'representanteconselho',
                  'representantegoverno', 'agentefinanceiro', 'tmpconclusaoprocesso', 'ultenviobanco', 'ultnossonumero',
                  'testemunha1', 'is_tstremessa', 'mostratitcancelados', 'mostraregcancelados', 'modelocalculo_financ',
                  'linhalogo1', 'linhalogo2', 'linhalogo3', 'taxaboleto', 'multaboleto']
        # Definir rótulos personalizados, se necessário
        labels = {
            'nome': 'Nome do Parâmetro:',
            'exercicio': 'Exercício:',
            'multa': '% Multa:',
            'juros': '% Juros:',
            'modelocalculo_financ': 'Modelo de Cálculo:',
            'linhalogo1': '1ª Linha do Logo/Cabeçalho:',
            'linhalogo2': '2ª Linha do Logo/Cabeçalho:',
            'linhalogo3': '3ª Linha do Logo/Cabeçalho:',
            'ultenviobanco': 'Último Envio Banco:',
            'ultnossonumero': 'Último Nossonumero:',
            'is_tstremessa': 'Remessa Teste:',
            'taxaboleto': 'Taxa Boleto:',
            'multaboleto': 'Multa Boleto Vencido:',
        }
        # Definir mensagens de ajuda para os campos
        help_texts = {
            'nome': 'Informe o nome do parâmetro com no máximo 50 posições',
            'exercicio': 'Insira o ano/exercício atual',
            'multa': 'Informe % da multa',
            'juros': 'Informe % do juros',
            'modelocalculo_financ': 'Selecione o modelo de cálculo',
            'linhalogo1': 'Insira a 1ª Linha do Logo/Cabeçalho com no máximo 128 posições',
            'linhalogo2': 'Insira a 2ª Linha do Logo/Cabeçalho com no máximo 128 posições',
            'linhalogo3': 'Insira a 3ª Linha do Logo/Cabeçalho com no máximo 128 posições',
            'ultenviobanco': 'Insira o n° do último envio encaminhado ao Banco',
            'ultnossonumero': 'Insira o n° do último nossonumero (identificador do boleto no banco)',
            'is_tstremessa': 'Sinalize se a remessa bancária é uma remessa de teste ou não',
            'taxaboleto': 'Taxa a ser cobrada na geração de cada boleto',
            'multaboleto': 'Multa a ser cobrada por boleto renegociado',
        }
        widgets = {
            'representanteconselho': forms.Textarea(
                attrs={
                    'class': 'textinput form-control',
                    'rows': '4'
                }),
            'representantegoverno': forms.Textarea(
                attrs={
                    'class': 'textinput form-control',
                    'rows': '4'
                }),
            'agentefinanceiro': forms.Textarea(
                attrs={
                    'class': 'textinput form-control',
                    'rows': '8'
                }),
            'testemunha1': forms.Textarea(
                attrs={
                    'class': 'textinput form-control',
                    'rows': '2'
                }),
            'is_tstremessa': forms.CheckboxInput(
                attrs={
                    'class': 'textinput form-control',
                }),
            'mostratitcancelados': forms.CheckboxInput(
                attrs={
                    'class': 'textinput form-control',
                }),
            'mostraregcancelados': forms.CheckboxInput(
                attrs={
                    'class': 'textinput form-control',
                }),
        }

class VeiculoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['placa'].widget.attrs.update({'class': 'textinput form-control', 'maxlength': '7'})
        self.fields['uf'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['anofabr'].widget = forms.NumberInput(attrs={'class': 'form-control', 'min': '2022', 'max': '2999'})
        self.fields['anomodelo'].widget = forms.NumberInput(attrs={'class': 'form-control', 'min': '2022',
                                                                   'max': '2999'})
        self.fields['marca'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['modelo'].widget.attrs.update({'class': 'textinput form-control', 'maxlength': '50'})
        self.fields['renavam'].widget = forms.NumberInput(attrs={'class': 'form-control', 'min': '00000000000',
                                                                 'max': '99999999999'})
        self.fields['combustivel'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['cor'].widget.attrs.update({'class': 'textinput form-control', 'maxlength': '50'})
        self.fields['chassi'].widget.attrs.update({'class': 'textinput form-control', 'maxlength': '30'})
        self.fields['notafiscal'].widget.attrs.update({'class': 'textinput form-control', 'maxlength': '10'})
        self.fields['clientepf'].queryset = PessoaFisica.objects.filter(Q(is_deleted=False) & ~Q(tipo='A')).order_by('nome')
        self.fields['clientepf'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['fornecedor'].queryset = PessoaJuridica.objects.filter(Q(is_deleted=False) & ~Q(porteempresa='3')).order_by('razaosocial')
        self.fields['fornecedor'].widget.attrs.update({'class': 'textinput form-control'})

    class Meta:
        model = Veiculo
        fields = ['marca', 'modelo', 'placa', 'uf', 'anofabr', 'anomodelo', 'renavam', 'combustivel', 'cor', 'chassi',
                  'notafiscal', 'clientepf', 'fornecedor']
