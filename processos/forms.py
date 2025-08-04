import os
# TESTE INLINE FORMSET
from django.forms.models import inlineformset_factory

from django.conf import settings

from django import forms

from django.core.exceptions import ValidationError

from tabelas.models import *
from processos.models import *
from django.contrib.auth.models import User

from datetime import date, datetime, timedelta

from django.db.models import Count, Sum, Avg, F, Q, Case, When, IntegerField

from django.db.models.functions import ExtractMonth

from django.shortcuts import render, redirect, get_object_or_404


class PessoaFisicaForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['rendaliqempresa'].localize = True
        self.fields['rendaalugueis'].localize = True
        self.fields['rendaliqtotal'].localize = True

        cidade_default = Config.objects.filter(is_deleted=False).last().cidade_default
        cep_default = Config.objects.filter(is_deleted=False).last().cep_default

        self.fields['nome'].widget.attrs.update({'class': 'textinput form-control',
                                                 'pattern': '[A-Z ÃÂÉÊÇÔ]{3,100}',
                                                 'title': 'Somente Letras com no máximo 100 caracteres.'})
        self.fields['situacao'].queryset = SituacaoPessoa.objects.filter(is_deleted=False).order_by('descricao')
        self.fields['situacao'].widget.attrs.update({'class': 'textinput form-control', 'required': 'true'})
        self.fields['sexo'].widget.attrs.update({'class': 'textinput form-control'})

        self.fields['tipo'].widget.attrs.update({'class': 'textinput form-control'})

        self.fields['profissao'].queryset = Profissao.objects.filter(is_deleted=False).order_by('nome')
        self.fields['profissao'].widget.attrs.update({'class': 'textinput form-control'})

        self.fields['escolaridade'].widget.attrs.update({'class': 'textinput form-control'})

        self.fields['estadocivil'].queryset = EstadoCivil.objects.filter(is_deleted=False).order_by('nome')
        self.fields['estadocivil'].initial = Config.objects.filter(is_deleted=False).last().estcivil_default

        self.fields['regimebens'].queryset = RegimeBens.objects.filter(is_deleted=False).order_by('nome')
        self.fields['regimebens'].initial = Config.objects.filter(is_deleted=False).last().regimebens_default

        self.fields['numfilhos'].widget.attrs.update({'class': 'textinput form-control',
                                                      'style': 'text-align: right', 'pattern': '[0-9]{1}',
                                                      'title': 'Somente números com no máximo 1 dígito.'})
        self.fields['numdependentes'].widget.attrs.update({'class': 'textinput form-control',
                                                           'style': 'text-align: right', 'pattern': '[0-9]{1}',
                                                           'title': 'Somente números com no máximo 1 dígito.'})
        self.fields['conjuge'].widget.attrs.update({'class': 'textinput form-control',
                                                    'pattern': '[A-Z ÃÂÉÊÇÔ]{3,100}',
                                                    'title': 'Letras com no máximo 100 caracteres.'})
        self.fields['cpfconjuge'].widget.attrs.update({'class': 'textinput form-control',
                                                       'title': 'Somente números com no máximo 11 dígitos.'})
        self.fields['nomepai'].widget.attrs.update({'class': 'textinput form-control',
                                                    'pattern': '[A-Z ÃÂÉÊÇÔ]{3,100}',
                                                    'title': 'Letras com no máximo 100 caracteres.'})
        self.fields['nomemae'].widget.attrs.update({'class': 'textinput form-control',
                                                    'pattern': '[A-Z ÃÂÉÊÇÔ]{3,100}',
                                                    'title': 'Letras com no máximo 100 caracteres.'})
        self.fields['numcpf'].widget.attrs.update({'class': 'textinput form-control',
                                                   'title': 'Somente números com no máximo 11 dígitos.'})
        self.fields['numrg'].widget.attrs.update({'class': 'textinput form-control', 'pattern': '[A-Z 0-9 . -]{1,12}',
                                                   'title': 'Letras, números, pontos e hífem com no máximo 12 caracteres.'})
        self.fields['ufexpedrg'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['orgexpedrg'].widget.attrs.update({'class': 'textinput form-control', 'maxlength': '20',
                                                         'pattern': '[A-Z]{1,20}',
                                                         'title': 'Somente letras com no máximo 20 caracteres.'})
        self.fields['tipoutrodoc'].\
            widget.attrs.update({'class': 'textinput form-control', 'maxlength': '15', 'pattern': '[A-Z ÃÂÉÊÇÔ 0-9]{1,15}',
                                 'title': 'Tipo de documento de identificação (CRM, CTPS, OAB, CREA, etc. Letras e '
                                          'números com no máximo 15 caracteres.'})
        self.fields['numoutrodoc'].widget.attrs.update({'class': 'textinput form-control', 'maxlength': '15',
                                                         'pattern': '[A-Z 0-9]{1,15}',
                                                         'title': 'Letras e números com no máximo 15 caracteres.'})
        self.fields['ufoutrodoc'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['orgexpoutrodoc'].widget.attrs.update({'class': 'textinput form-control', 'maxlength': '20',
                                                         'pattern': '[A-Z]{1,20}',
                                                         'title': 'Somente letras com no máximo 20 caracteres.'})
        self.fields['naturalidade'].initial = cidade_default
        self.fields['nacionalidade'].widget.attrs.update({'class': 'textinput form-control',
                                                          'pattern': '[A-Z]{0,20}',
                                                          'title': 'Somente letras com no máximo 20 caracteres.'})
        self.fields['telfixo'].widget.attrs.update({'class': 'textinput form-control',
                                                    'title': 'Somente números (DDD + Telefone com 8 dígitos.'})
        self.fields['telcelular1'].widget.attrs.update({'class': 'textinput form-control',
                                                        'title': 'Somente números (DDD + Telefone com 9 dígitos.'})
        self.fields['telcelular2'].widget.attrs.update({'class': 'textinput form-control',
                                                        'title': 'Somente números (DDD + Telefone com 9 dígitos.'})
        self.fields['logradouro'].widget.attrs.update({'class': 'textinput form-control',
                                                       'maxlength': '50',
                                                       'title': 'Letras e números com no máximo 50 caracteres.'})
        self.fields['numimovel'].widget.attrs.update({'class': 'textinput form-control',
                                                      'pattern': '[0-9]{0,4}',
                                                      'title': 'Somente números com no máximo 4 dígitos.'})
        self.fields['complemento'].widget.attrs.update({'class': 'textinput form-control',
                                                        'maxlength': '30',
                                                        'title': 'Letras e números com no máximo 30 caracteres.'})
        # self.fields['bairro'].widget.attrs.update({'class': 'textinput form-control',
        #                                            'maxlength': '30',
        #                                            'title': 'Letras e números com no máximo 30 caracteres.'})

        self.fields['cidade'].initial = cidade_default

        self.fields['bairro'].queryset = Bairro.objects.all()
        if 'cidade' in self.data:
            try:
                cidade_id = int(self.data.get('cidade'))
                self.fields['bairro'].queryset = Bairro.objects.filter(cidade_id=cidade_id, is_deleted=False).order_by('nome')
            except (ValueError, TypeError):
                pass
        # elif self.instance.pk and self.instance.cidade:
        #     self.fields['bairro'].queryset = Bairro.objects.all()


        self.fields['cep'].initial = cep_default
        self.fields['cep'].widget.attrs.update({'class': 'textinput form-control',
                                                'title': 'Somente números com no máximo 8 dígitos'})
        self.fields['temporesidencia'].widget.attrs.update({'class': 'textinput form-control',
                                                            'style': 'text-align: right', 'pattern': '[0-9]{2}',
                                                            'title': 'Tempo na residência em anos. Somente números.'})

        self.fields['rendaempresa'].widget.attrs.update({'class': 'textinput form-control', 'maxlength': '100',
                                                         'title': 'Letras e números com no máximo 100 caracteres.'})

        self.fields['cargoempresa'].widget.attrs.update({'class': 'textinput form-control', 'maxlength': '20',
                                                         'title': 'Letras e números com no máximo 20 caracteres'})
        self.fields['numbeneficio'].widget.attrs.update({'class': 'textinput form-control', 'maxlength': '20',
                                                         'title': 'Letras e números com no máximo 20 caracteres'})
        self.fields['rendaliqempresa'].widget.attrs.update({'class': 'textinput form-control setprice rendaliqempresa',
                                                            'style': 'text-align: right', 'min': '0', 'required': 'true'})
        self.fields['rendaalugueis'].widget.attrs.update({'class': 'textinput form-control setprice rendaalugueis',
                                                          'style': 'text-align: right', 'min': '0', 'required': 'true'})
        self.fields['rendaliqtotal'].widget.attrs.update({'class': 'textinput form-control setprice rendaliqtotal',
                                                          'style': 'text-align: right', 'min': '0', 'required': 'true'})
        self.fields['email'].widget.attrs.update({'class': 'textinput form-control',
                                                  'maxlength': '100',
                                                  'title': 'Letras e números com no máximo 100 caracteres.'})

    class Meta:
        model = PessoaFisica
        fields = ['nome', 'dtnascimento', 'sexo', 'profissao', 'estadocivil', 'escolaridade', 'regimebens', 'numfilhos',
                  'numdependentes', 'nomepai', 'nomemae', 'numcpf', 'numrg', 'ufexpedrg', 'orgexpedrg', 'tipo',
                  'tipoutrodoc', 'numoutrodoc', 'ufoutrodoc', 'orgexpoutrodoc', 'dtemisoutrodoc', 'naturalidade',
                  'nacionalidade', 'telfixo', 'telcelular1', 'telcelular2', 'logradouro', 'numimovel', 'complemento',
                  'cidade', 'bairro', 'cep', 'email', 'temporesidencia', 'is_residpropria', 'situacao',
                  'pontoreferencia', 'conjuge', 'cpfconjuge', 'rendaempresa', 'dtadmissempresa', 'rendaliqempresa',
                  'cargoempresa', 'numbeneficio', 'rendaalugueis', 'rendaliqtotal', 'observacao', 'is_deleted']

        widgets = {
            'rendaliqempresa': forms.TextInput(attrs={'class': 'mask-money form-control', 'placeholder': '0,00'}),
            'rendaalugueis': forms.TextInput(attrs={'class': 'mask-money form-control', 'placeholder': '0,00'}),
            'rendaliqtotal': forms.TextInput(attrs={'class': 'mask-money form-control', 'placeholder': '0,00'}),
            'dtnascimento': forms.TextInput(
                # format=('%Y-%m-%d'),
                attrs={'class': 'textinput form-control',
                       'placeholder': 'Selecione uma data',
                       'type': 'date'  # <--- IF I REMOVE THIS LINE, THE INITIAL VALUE IS DISPLAYED
                       }),
            'dtemisoutrodoc': forms.TextInput(
                # format=('%Y-%m-%d'),
                attrs={'class': 'textinput form-control',
                       'placeholder': 'Selecione uma data',
                       'type': 'date'  # <--- IF I REMOVE THIS LINE, THE INITIAL VALUE IS DISPLAYED
                       }),
            'dtadmissempresa': forms.TextInput(
                # format=('%Y-%m-%d'),
                attrs={'class': 'textinput form-control',
                       'placeholder': 'Selecione uma data',
                       'type': 'date'  # <--- IF I REMOVE THIS LINE, THE INITIAL VALUE IS DISPLAYED
                       }),
            'estadocivil': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                }),
            'regimebens': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                }),
            'naturalidade': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                }),
            'situacao': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                }),
            'cidade': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                }),
            'bairro': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                }),
            # 'is_residpropria': forms.CheckboxInput(
            #     attrs={
            #         'class': 'textinput form-control',
            #     }),
            'observacao': forms.Textarea(
                attrs={
                    'class': 'textinput form-control',
                    'rows': '2'
                }),
            'pontoreferencia': forms.Textarea(
                attrs={
                    'class': 'textinput form-control',
                    'rows': '3'
                }),
        }

    def clean(self):
        cleaned_data = super().clean()

        datahoje = date.today()

        telfixo = cleaned_data.get("telfixo")
        telcelular1 = cleaned_data.get("telcelular1")
        telcelular2 = cleaned_data.get("telcelular2")

        if not telfixo:
            if not telcelular1:
                if not telcelular2:
                    raise ValidationError(
                        "AVISO: Ao menos um telefone de contato precisa ser digitado... Verifique."
            )

        dtnascimento = cleaned_data.get("dtnascimento")
        if dtnascimento:
            if dtnascimento > datahoje:
                raise ValidationError(
                    "AVISO: A data de nascimento da pessoa não pode ser superior a data de hoje... Verifique."
                )

        # atenção: campos de combos e listas precisam ser convertidos para string pois a comparação não funciona
        estadocivil = str(cleaned_data.get("estadocivil"))
        regimebens = str(cleaned_data.get("regimebens"))
        if estadocivil == 'CASADO(A)':
            if regimebens == 'None':
                raise ValidationError('AVISO: Regime de bens ' + regimebens + ' incompatível com o estado civil ' + estadocivil + ' ... Verifique.')
        else:
            if regimebens != 'None':
                raise ValidationError('AVISO: Regime de bens ' + regimebens + ' incompatível com o estado civil ' + estadocivil + ' ... Verifique.')

        conjuge = str(cleaned_data.get("conjuge"))
        cpfconjuge = str(cleaned_data.get("cpfconjuge"))
        if estadocivil == 'CASADO(A)' or estadocivil == 'UNIAO ESTAVEL':
            if conjuge == '' or cpfconjuge == '':
                raise ValidationError(
                    'AVISO: Cônjuge/companheiro(a) e CPF necessitam ser informados para o estado civil ' + estadocivil + ' ... Verifique.')
        else:
            if conjuge != '' or cpfconjuge != '':
                raise ValidationError(
                    'AVISO: Cônjuge/companheiro(a) e CPF não necessitam ser informados para o estado civil ' + estadocivil + ' ... Verifique.')

        numcpf = str(cleaned_data.get("numcpf"))
        if numcpf == cpfconjuge:
            raise ValidationError(
                'AVISO: CPF do cônjuge/companheiro(a) não pode ser o mesmo da Pessoa... Verifique.')

        dtadmissempresa = cleaned_data.get("dtadmissempresa")
        if dtadmissempresa:
            if dtadmissempresa > datahoje:
                raise ValidationError(
                    "AVISO: A data de admissão na empresa não pode ser superior a data de hoje... Verifique."
                )

        rendaliqempresa = cleaned_data.get("rendaliqempresa")
        rendaalugueis = cleaned_data.get("rendaalugueis")
        rendaliqtotal = cleaned_data.get("rendaliqtotal")
        if float(rendaliqtotal) != float(rendaliqempresa + rendaalugueis):
            raise ValidationError(
                "AVISO: O valor da renda total não corresponde as demais rendas... Verifique."
            )

        # dtcomprovante = cleaned_data.get("dtcomprovante")
        # datalimite = date.today() - timedelta(60)
        # # print ("dtcomprovante", dtcomprovante)
        # # print ("datalimite", datalimite)
        # if str(dtcomprovante) < str(datalimite):
        #     print ('AVISO: Data de comprovante excede em 60 dias o limite para comprovação... Verifique.')
        #     raise ValidationError(
        #         "AVISO: Data de comprovante excede em 60 dias o limite para comprovação... Verifique."
        #     )

class PessoaJuridicaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        cidade_default = Config.objects.filter(is_deleted=False).last().cidade_default
        cep_default = Config.objects.filter(is_deleted=False).last().cep_default

        self.fields['razaosocial'].widget.attrs.update({'class': 'textinput form-control',
                                                        'pattern': '[a-z A-Z 0-9 Ç]{3,100}',
                                                        'title': 'Letras e números com no máximo 100 caracteres.'})
        self.fields['nomefantasia'].widget.attrs.update({'class': 'textinput form-control',
                                                         'pattern': '[a-z A-Z 0-9 Ç]{3,100}',
                                                         'title': 'Letras e números com no máximo 100 caracteres.'})
        self.fields['situacao'].queryset = SituacaoPessoa.objects.filter(is_deleted=False).order_by('descricao')
        self.fields['situacao'].widget.attrs.update({'class': 'textinput form-control', 'required': 'true'})
        self.fields['porteempresa'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['setornegocio'].queryset = SetorNegocio.objects.filter(is_deleted=False).order_by('nome')
        self.fields['setornegocio'].widget.attrs.update({'class': 'textinput form-control', 'required': 'true'})
        self.fields['ramoatividade'].queryset = RamoAtividade.objects.filter(is_deleted=False).order_by('nome')
        self.fields['ramoatividade'].widget.attrs.update({'class': 'textinput form-control', 'required': 'true'})
        self.fields['numcnpj'].widget.attrs.update({'class': 'textinput form-control',
                                                    'title': 'Somente números com 14 dígitos.'})
        self.fields['numinscest'].widget.attrs.update({'class': 'textinput form-control',
                                                       'pattern': '[0-9]{9}',
                                                       'title': 'Somente números com no máximo 9 dígitos.'})
        self.fields['numinscmun'].widget.attrs.update({'class': 'textinput form-control',
                                                       'pattern': '[0-9]{9}',
                                                       'title': 'Somente números com no máximo 9 dígitos.'})
        self.fields['telfixo'].widget.attrs.update({'class': 'textinput form-control',
                                                    'title': 'Somente números (DDD + Telefone com 8 dígitos.'})
        self.fields['telcelular1'].widget.attrs.update({'class': 'textinput form-control',
                                                        'title': 'Somente números (DDD + Telefone com 9 dígitos.'})
        self.fields['telcelular2'].widget.attrs.update({'class': 'textinput form-control',
                                                        'title': 'Somente números (DDD + Telefone com 9 dígitos.'})
        self.fields['logradouro'].widget.attrs.update({'class': 'textinput form-control',
                                                       'maxlength': '50',
                                                       'title': 'Letras e números com no máximo 50 caracteres.'})
        self.fields['numimovel'].widget.attrs.update({'class': 'textinput form-control',
                                                      'pattern': '[0-9]{0,4}',
                                                      'title': 'Somente números com no máximo 4 dígitos.'})
        self.fields['complemento'].widget.attrs.update({'class': 'textinput form-control',
                                                        'maxlength': '30',
                                                        'title': 'Letras e números com no máximo 30 caracteres.'})
        self.fields['cidade'].initial = cidade_default

        self.fields['bairro'].queryset = Bairro.objects.all()
        if 'cidade' in self.data:
            try:
                cidade_id = int(self.data.get('cidade'))
                self.fields['bairro'].queryset = Bairro.objects.filter(cidade_id=cidade_id, is_deleted=False).order_by('nome')
            except (ValueError, TypeError):
                pass

        self.fields['cep'].initial = cep_default
        self.fields['cep'].widget.attrs.update({'class': 'textinput form-control',
                                                'title': 'Somente números com 8 dígitos.'})
        # self.fields['socio1'].queryset = PessoaFisica.objects.filter(is_deleted=False).order_by('nome')
        # self.fields['socio1'].widget.attrs.update({'class': 'textinput form-control'})
        # self.fields['socio2'].queryset = PessoaFisica.objects.filter(is_deleted=False).order_by('nome')
        # self.fields['socio2'].widget.attrs.update({'class': 'textinput form-control'})
        # self.fields['socio3'].queryset = PessoaFisica.objects.filter(is_deleted=False).order_by('nome')
        # self.fields['socio3'].widget.attrs.update({'class': 'textinput form-control'})
        # self.fields['cota1'].widget.attrs.update({'class': 'textinput form-control setprice cota1',
        #                                                   'style': 'text-align: right', 'min': '0', 'max': '100', 'required': 'true'})
        # self.fields['cota2'].widget.attrs.update({'class': 'textinput form-control setprice cota2',
        #                                                   'style': 'text-align: right', 'min': '0', 'max': '100', 'required': 'true'})
        # self.fields['cota3'].widget.attrs.update({'class': 'textinput form-control setprice cota3',
        #                                                   'style': 'text-align: right', 'min': '0', 'max': '100', 'required': 'true'})

    class Meta:
        model = PessoaJuridica
        fields = ['razaosocial', 'nomefantasia', 'dtiniatividade', 'porteempresa', 'setornegocio', 'ramoatividade',
                  'numcnpj', 'numinscest', 'numinscmun', 'telfixo', 'telcelular1', 'telcelular2', 'logradouro',
                  'numimovel', 'complemento', 'cidade', 'bairro', 'cep', 'situacao', 'pontoreferencia', 'observacao',
                  'is_deleted']
        # fields = ['razaosocial', 'nomefantasia', 'dtiniatividade', 'porteempresa', 'setornegocio', 'ramoatividade',
        #           'numcnpj', 'numinscest', 'numinscmun', 'telfixo', 'telcelular1', 'telcelular2', 'logradouro',
        #           'numimovel', 'complemento', 'cidade', 'bairro', 'cep', 'situacao', 'socio1', 'cota1',
        #           'socio2', 'cota2', 'socio3', 'cota3', 'pontoreferencia', 'observacao', 'is_deleted']
        widgets = {
            'dtiniatividade': forms.TextInput(
                # format=('%Y-%m-%d'),
                attrs={'class': 'textinput form-control',
                       'placeholder': 'Selecione uma data',
                       'type': 'date'  # <--- IF I REMOVE THIS LINE, THE INITIAL VALUE IS DISPLAYED
                       }),
            # 'situacao': forms.Select(
            #     attrs={
            #         'class': 'textinput form-control',
            #     }),
            'cidade': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                }),
            'bairro': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                }),
            'observacao': forms.Textarea(
                attrs={
                    'class': 'textinput form-control',
                    'rows': '2'
                }),
            'pontoreferencia': forms.Textarea(
                attrs={
                    'class': 'textinput form-control',
                    'rows': '3'
                }),
        }

    def clean(self):
        error = {}
        cleaned_data = super().clean()

        telfixo = cleaned_data.get("telfixo")
        telcelular1 = cleaned_data.get("telcelular1")
        telcelular2 = cleaned_data.get("telcelular2")
        if not telfixo:
            if not telcelular1:
                if not telcelular2:
                    error['telfixo'] = ['Ao menos um telefone de contato precisa ser digitado.']

        porteempresa = cleaned_data.get("porteempresa")
        # socio1 = cleaned_data.get("socio1")
        # socio2 = cleaned_data.get("socio2")
        # socio3 = cleaned_data.get("socio3")
        # if porteempresa != '1' and porteempresa != '6':
        #     if not socio1:
        #         if not socio2:
        #             if not socio3:
        #                 error['socio1'] = 'Ao menos um socio precisa ser selecionado.'

        # cota1 = cleaned_data.get("cota1")
        # cota2 = cleaned_data.get("cota2")
        # cota3 = cleaned_data.get("cota3")
        # if porteempresa != '1' and porteempresa != '6':
        #     if float(cota1 + cota2 + cota3) != 100.00:
        #         error['cota1'] = 'O valor total das cotas necessita ser de 100%.'

        numcnpj = cleaned_data.get("numcnpj")
        if porteempresa != '6':
            if not numcnpj:
                error['numcnpj'] = 'Porte da empresa exige a digitação de um CNPJ válido.'

        setornegocio = cleaned_data.get("setornegocio")
        if not setornegocio:
            error['setornegocio'] = ['Um setor de negócio precisa ser selecionado.']

        ramoatividade = cleaned_data.get("ramoatividade")
        if not setornegocio:
            error['ramoatividade'] = ['Um ramo de atividade precisa ser selecionado.']

        if len(error) != 0:
            raise ValidationError(error)


class SocioForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['socio'].queryset = PessoaFisica.objects.filter(is_deleted=False).order_by('nome')
        self.fields['socio'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['cota'].widget.attrs.update({'class': 'textinput form-control setprice cota',
                                                          'style': 'text-align: right', 'min': '0', 'max': '100', 'required': 'true'})

    class Meta:
        model = PJuridicaSocio
        fields = ['socio', 'cota', 'is_deleted']
        widgets = {
            'socio': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                }),
        }

    # def clean(self):
    #     cleaned_data = super().clean()
    #     socio = cleaned_data.get('socio')
    #     cota = cleaned_data.get('cota')
    #
    #     # Verifica se ao menos dois sócios foram adicionados
    #     if not socio:
    #         raise ValidationError('É necessário adicionar ao menos dois sócios.')
    #
    #     # Supondo que 'self.instance.pessoajuridica' é a PessoaJuridica à qual os sócios estão associados
    #     total_socios = PJuridicaSocio.objects.filter(pessoajuridica=self.instance.pessoajuridica, is_deleted=False).count()
    #     if total_socios < 2:
    #         raise ValidationError('É necessário adicionar ao menos dois sócios.')
    #
    #     print (total_socios)
    #
    #     return cleaned_data

    # def clean(self):
    #     error = {}
    #     cleaned_data = super().clean()
    #
    #     telfixo = cleaned_data.get("telfixo")
    #     telcelular1 = cleaned_data.get("telcelular1")
    #     telcelular2 = cleaned_data.get("telcelular2")
    #     if not telfixo:
    #         if not telcelular1:
    #             if not telcelular2:
    #                 error['telfixo'] = ['Ao menos um telefone de contato precisa ser digitado.']
    #
    #     porteempresa = cleaned_data.get("porteempresa")
    #     socio1 = cleaned_data.get("socio1")
    #     socio2 = cleaned_data.get("socio2")
    #     socio3 = cleaned_data.get("socio3")
    #     if porteempresa != '1' and porteempresa != '6':
    #         if not socio1:
    #             if not socio2:
    #                 if not socio3:
    #                     error['socio1'] = 'Ao menos um socio precisa ser selecionado.'
    #
    #     cota1 = cleaned_data.get("cota1")
    #     cota2 = cleaned_data.get("cota2")
    #     cota3 = cleaned_data.get("cota3")
    #     if porteempresa != '1' and porteempresa != '6':
    #         if float(cota1 + cota2 + cota3) != 100.00:
    #             error['cota1'] = 'O valor total das cotas necessita ser de 100%.'
    #
    #     numcnpj = cleaned_data.get("numcnpj")
    #     if porteempresa != '6':
    #         if not numcnpj:
    #             error['numcnpj'] = 'Porte da empresa exige a digitação de um CNPJ válido.'
    #
    #     if len(error) != 0:
    #         raise ValidationError(error)

SocioFormSet = inlineformset_factory(PessoaJuridica, PJuridicaSocio, form=SocioForm,
                                          fields=['socio', 'cota'], extra=1, can_delete=True)

class ProcessoPFForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['valorcoberto'].localize = True
        self.fields['valorsolicitado'].localize = True
        self.fields['valorrendanegoc'].localize = True

        self.fields['dtprocesso'].initial = date.today()

        self.fields['clientepf'].queryset = PessoaFisica.objects.filter(Q(is_deleted=False) & ~Q(tipo='A')).order_by('nome')
        self.fields['clientepf'].widget.attrs.update({'class': 'textinput form-control', 'required': 'true'})

        self.fields['numprotocolo'].widget.attrs.update({'class': 'textinput form-control', 'maxlength': '20'})

        self.fields['conhecimentoprograma'].initial = Config.objects.filter(is_deleted=False).last().conhecimentoprograma_default
        self.fields['conhecimentoprograma'].widget.attrs.update({'class': 'textinput form-control'})

        self.fields['linhacredito'].queryset = LinhaCredito.objects.filter(is_deleted=False, tpcliente='F')
        # self.fields['linhacredito'].initial = Config.objects.filter(is_deleted=False).last().linhacredito_default

        self.fields['finalidadecredito'].queryset = FinalidadeCredito.objects.filter(is_deleted=False)
        self.fields['finalidadecredito'].initial = Config.objects.filter(is_deleted=False).last().finalidadecredito_default

        self.fields['empresa'].queryset = PessoaJuridica.objects.filter(is_deleted=False).order_by('razaosocial')
        self.fields['empresa'].widget.attrs.update({'class': 'textinput form-control'})

        self.fields['situacaonegocio'].initial = Config.objects.filter(is_deleted=False).last().situacaonegocio_default
        self.fields['situacaonegocio'].widget.attrs.update({'class': 'textinput form-control'})

        self.fields['banco'].queryset = Banco.objects.filter(is_deleted=False)
        self.fields['banco'].initial = Config.objects.filter(is_deleted=False).last().banco_default
        self.fields['banco'].widget.attrs.update({'class': 'textinput form-control', 'required': 'true'})
        self.fields['agencia'].widget.attrs.update({'class': 'textinput form-control', 'maxlength': '10', 'required': 'true',
                                                    'title': 'Letras e números com no máximo 10 caracteres'})
        self.fields['conta'].widget.attrs.update({'class': 'textinput form-control', 'maxlength': '20', 'required': 'true',
                                                  'title': 'Letras e números com no máximo 20 caracteres'})
        self.fields['tipconta'].widget.attrs.update({'class': 'textinput form-control', 'required': 'true'})
        self.fields['valorcoberto'].widget.attrs.update({'class': 'textinput form-control',
                                                         'style': 'text-align: right', 'min': '0', 'required': 'true'})
        self.fields['valorsolicitado'].widget.attrs.update({'class': 'textinput form-control', 'required': 'true',
                                                            'style': 'text-align: right', 'min': '0'})
        self.fields['prazosolicitado'].widget.attrs.update({'class': 'textinput form-control', 'pattern': '[0-9]{1,2}',
                                                        'style': 'text-align: right', 'min': '1', 'required': 'true',
                                                        'title': 'Somente números com no máximo 2 dígitoS.'})
        self.fields['numbeneficiados'].widget.attrs.update({'class': 'textinput form-control', 'pattern': '[0-9]',
                                                            'style': 'text-align: right', 'min': '0', 'max':'9999',
                                                            'title': 'N° de beneficiados, de 0 a 9999.'})
        self.fields['numfuncionarios'].widget.attrs.update({'class': 'textinput form-control', 'pattern': '[0-9]',
                                                            'style': 'text-align: right', 'min': '0', 'max':'9999',
                                                            'title': 'N° de beneficiados, de 0 a 9999.'})
        self.fields['expecocupacoes'].widget.attrs.update({'class': 'textinput form-control', 'pattern': '[0-9]',
                                                           'style': 'text-align: right', 'min': '0', 'max':'9999',
                                                           'title': 'N° de beneficiados, de 0 a 9999.'})
        self.fields['documentacao'].widget.attrs.update({'class': 'form-control'})
        self.fields['valorrendanegoc'].widget.attrs.update({'class': 'textinput form-control',
                                                         'style': 'text-align: right', 'min': '0', 'required': 'true'})
        # self.fields['fornecedor'].queryset = PessoaJuridica.objects.filter(is_deleted=False)
        # self.fields['fornecedor'].widget.attrs.update({'class': 'textinput form-control'})
        # self.fields['veiculo'].queryset = Veiculo.objects.filter(is_deleted=False, clientepf=self.clientepf.id)
        # self.fields['veiculo'].widget.attrs.update({'class': 'textinput form-control'})
        # self.fields['documentacao'].widget.attrs['disabled'] = 'disabled'
        # self.fields['agenciafornec'].widget.attrs.update({'class': 'textinput form-control', 'maxlength': '10',
        #                                             'title': 'Letras e números com no máximo 10 caracteres'})
        # self.fields['contafornec'].widget.attrs.update({'class': 'textinput form-control', 'maxlength': '20',
        #                                           'title': 'Letras e números com no máximo 20 caracteres'})

    class Meta:
        model = Processo
        fields = ['dtprocesso', 'clientepf', 'conhecimentoprograma', 'linhacredito', 'finalidadecredito',
                  'empresa', 'situacaonegocio', 'banco', 'agencia', 'conta', 'tipconta', 'observacao',
                  'numprotocolo', 'sobreonegocio', 'porquedonegocio', 'evolucaonegocio', 'valorcoberto',
                  'valorsolicitado', 'prazosolicitado', 'numbeneficiados', 'numfuncionarios', 'expecocupacoes',
                  'valorrendanegoc', 'documentacao']
        widgets = {
            'valorcoberto': forms.TextInput(attrs={'class': 'mask-money form-control', 'placeholder': '0,00'}),
            'valorsolicitado': forms.TextInput(attrs={'class': 'mask-money form-control', 'placeholder': '0,00'}),
            'valorrendanegoc': forms.TextInput(attrs={'class': 'mask-money form-control', 'placeholder': '0,00'}),
            'dtprocesso': forms.TextInput(
                # format=('%Y-%m-%d'),
                attrs={'class': 'textinput form-control',
                       'placeholder': 'Selecione uma data',
                       'type': 'date'  # <--- IF I REMOVE THIS LINE, THE INITIAL VALUE IS DISPLAYED
                       }),
            'linhacredito': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                    'required': 'True',
                }),
            'finalidadecredito': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                    'required': 'True',
                }),
            'sobreonegocio': forms.Textarea(
                attrs={
                    'class': 'textinput form-control',
                    'required': 'True',
                    'rows': '3'
                }),
            'porquedonegocio': forms.Textarea(
                attrs={
                    'class': 'textinput form-control',
                    'required': 'True',
                    'rows': '3'
                }),
            'evolucaonegocio': forms.Textarea(
                attrs={
                    'class': 'textinput form-control',
                    'required': 'True',
                    'rows': '5'
                }),
            'observacao': forms.Textarea(
                attrs={
                    'class': 'textinput form-control',
                    'rows': '3'
                }),
        }

    def clean(self):
        cleaned_data = super().clean()

        # banco = cleaned_data.get("banco")
        # if not banco:
        #     raise ValidationError(
        #         "AVISO: Em 'INFORMAÇÕES DO CLIENTE' o campo banco não foi preenchido... Verifique."
        #     )
        #
        # agencia = cleaned_data.get("agencia")
        # if not agencia:
        #     raise ValidationError(
        #         "AVISO: Em 'INFORMAÇÕES DO CLIENTE' o campo agência não foi preenchido... Verifique."
        #     )
        #
        # conta = cleaned_data.get("conta")
        # if not conta:
        #     raise ValidationError(
        #         "AVISO: Em 'INFORMAÇÕES DO CLIENTE' o campo conta corrente não foi preenchido... Verifique."
        #     )
        #
        # tipconta = cleaned_data.get("tipconta")
        # if not tipconta:
        #     raise ValidationError(
        #         "AVISO: Em 'INFORMAÇÕES DO CLIENTE' o campo tipo de conta não foi preenchido... Verifique."
        #     )

        clientepf = cleaned_data.get("clientepf")
        if clientepf:
            cliente = get_object_or_404(PessoaFisica, pk=str(clientepf)[-7:])
            if not cliente:
                raise ValidationError(
                    "ERRO: Ocorreu um erro com a informação do CPF do Cliente... Verifique os dados do cadastro."
                )
            else:
                cliente_id = cliente.id
        else:
            raise ValidationError(
                "AVISO: O campo Cliente precisa ser informado."
            )

        # Verificação se há um veículo cadastrado disponível para o cliente selecionado quando a linha de crédito exigir
        nom_linhacredito = cleaned_data.get("linhacredito")
        linhacredito = get_object_or_404(LinhaCredito, nome=nom_linhacredito)
        if linhacredito:
            if linhacredito.is_garantia:
                veiculo = Veiculo.objects.filter(is_deleted=False, clientepf = clientepf, is_vendido=False)
                if not veiculo:
                    raise ValidationError(
                        "AVISO: Não foi encontrado um veículo cadastrado como Bem Garantidor para o cliente "
                        + cliente.nome + "... Verifique."
                    )

        situacao = get_object_or_404(SituacaoPessoa, pk=cliente.situacao_id)
        if situacao.blq_processo:
            raise ValidationError(
                "AVISO: Situação do Cliente não possibilita a criação e/ou movimentação de processos. Verifique o cadastro."
            )

        # Suspenso temporariamente a pedido de Zélia (reativado em 20/02/2025)
        # Verifica se o cliente já não possui outro processo com parcelas em aberto
        qsdebitos = Financeiro.objects.filter(processo__clientepf=cliente_id, status='A',
                                              dtvencimento__lt=datetime.today(), is_deleted=False)
        if qsdebitos:
            raise ValidationError(
                "AVISO: Cliente já possui processo(s) com parcela(s) em aberto. Favor verificar situação financeira."
            )

        # Verifica se a data do processo pertence ao exercício atual e se não são anteriores a referência de fechamento
        exercicioatual = Config.objects.filter(is_deleted=False).last().exercicio
        dtprocesso = cleaned_data.get("dtprocesso")
        if dtprocesso:
            if dtprocesso.year != exercicioatual:
                raise ValidationError(
                    "AVISO: Data do processo não pertence ao exercício atual que é de " + str(exercicioatual) + "."
                )
            refprocesso = str(dtprocesso.year) + str(dtprocesso.month).zfill(2)
            reffechamento = Fechamento.objects.filter(is_deleted=False).last().referencia
            if refprocesso <= reffechamento:
                raise ValidationError(
                    "AVISO: Data do processo antecede o mês de fechamento que é " + reffechamento +
                    ". Verifique os fechamentos realizados.")

        # atenção: campos de combos e listas precisam ser convertidos para string pois a comparação não funciona

        # Verifica os limites de solicitação do valor, campos da garantia e do prazo para o financiamento
        valorsolicitado = cleaned_data.get("valorsolicitado")
        prazosolicitado = cleaned_data.get("prazosolicitado")
        nom_linhacredito = cleaned_data.get("linhacredito")
        if nom_linhacredito:
            linhacredito = get_object_or_404(LinhaCredito, nome=nom_linhacredito)
            if linhacredito:
                if float(valorsolicitado) > float(linhacredito.limite):
                    raise ValidationError(
                        "AVISO: Crédito solicitado excede o limite máximo para essa linha de crédito que é de R$ " +
                        str(linhacredito.limite) + ". Verifique os limites em Tabelas Gerais."
                    )
                if int(prazosolicitado) > int(linhacredito.nmaxparcelas):
                    raise ValidationError(
                        "AVISO: Prazo solicitado excede o limite máximo para essa linha de crédito que é de " +
                        str(linhacredito.nmaxparcelas) + " parcelas. Verifique os limites em Tabelas Gerais."
                    )
        else:
            raise ValidationError(
                "AVISO: Linha de Crédito necessita ser informada."
            )


class ProcessoPJForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['valorcoberto'].localize = True
        self.fields['valorsolicitado'].localize = True
        self.fields['valorrendanegoc'].localize = True

        self.fields['dtprocesso'].initial = date.today()

        self.fields['clientepj'].queryset = PessoaJuridica.objects.filter(is_deleted=False).order_by('razaosocial')
        self.fields['clientepj'].widget.attrs.update({'class': 'textinput form-control', 'required': 'true'})

        self.fields['numprotocolo'].widget.attrs.update({'class': 'textinput form-control', 'maxlength': '20'})

        self.fields['conhecimentoprograma'].initial = Config.objects.filter(is_deleted=False).last().conhecimentoprograma_default
        self.fields['conhecimentoprograma'].widget.attrs.update({'class': 'textinput form-control'})

        self.fields['linhacredito'].queryset = LinhaCredito.objects.filter(is_deleted=False, tpcliente='J')
        # self.fields['linhacredito'].initial = Config.objects.filter(is_deleted=False).last().linhacredito_default

        self.fields['finalidadecredito'].queryset = FinalidadeCredito.objects.filter(is_deleted=False)
        self.fields['finalidadecredito'].initial = Config.objects.filter(is_deleted=False).last().finalidadecredito_default

        self.fields['empresa'].queryset = PessoaJuridica.objects.filter(is_deleted=False).order_by('razaosocial')
        self.fields['empresa'].widget.attrs.update({'class': 'textinput form-control'})

        self.fields['situacaonegocio'].initial = Config.objects.filter(is_deleted=False).last().situacaonegocio_default
        self.fields['situacaonegocio'].widget.attrs.update({'class': 'textinput form-control'})

        # self.fields['funcao'].queryset = Funcao.objects.filter(is_deleted=False)
        # self.fields['funcao'].widget.attrs.update({'class': 'textinput form-control'})

        self.fields['banco'].queryset = Banco.objects.filter(is_deleted=False)
        self.fields['banco'].initial = Config.objects.filter(is_deleted=False).last().banco_default
        self.fields['banco'].widget.attrs.update({'class': 'textinput form-control', 'required': 'true'})

        self.fields['agencia'].widget.attrs.update({'class': 'textinput form-control', 'maxlength': '10',
                                                    'title': 'Letras e números com no máximo 10 caracteres', 'required': 'True'})
        self.fields['conta'].widget.attrs.update({'class': 'textinput form-control', 'maxlength': '20', 'required': 'True',
                                                  'title': 'Letras e números com no máximo 20 caracteres'})
        self.fields['tipconta'].widget.attrs.update({'class': 'textinput form-control', 'required': 'true'})
        self.fields['valorcoberto'].widget.attrs.update({'class': 'textinput form-control',
                                                         'style': 'text-align: right', 'min': '0', 'required': 'true'})
        self.fields['valorsolicitado'].widget.attrs.update({'class': 'textinput form-control',
                                                            'style': 'text-align: right', 'min': '0', 'required': 'true'})
        self.fields['prazosolicitado'].widget.attrs.update({'class': 'textinput form-control', 'pattern': '[0-9]{1,2}',
                                                            'style': 'text-align: right', 'min': '1',
                                                            'title': 'Somente números com no máximo 2 dígitoS.'})
        self.fields['numbeneficiados'].widget.attrs.update({'class': 'textinput form-control', 'pattern': '[0-9]',
                                                            'style': 'text-align: right', 'min': '0', 'max':'9999',
                                                            'title': 'N° de beneficiados, de 0 a 9999.'})
        self.fields['numfuncionarios'].widget.attrs.update({'class': 'textinput form-control', 'pattern': '[0-9]',
                                                            'style': 'text-align: right', 'min': '0', 'max':'9999',
                                                            'title': 'N° de beneficiados, de 0 a 9999.'})
        self.fields['expecocupacoes'].widget.attrs.update({'class': 'textinput form-control', 'pattern': '[0-9]',
                                                           'style': 'text-align: right', 'min': '0', 'max':'9999',
                                                           'title': 'N° de beneficiados, de 0 a 9999.'})
        self.fields['valorrendanegoc'].widget.attrs.update({'class': 'textinput form-control',
                                                         'style': 'text-align: right', 'min': '0', 'required': 'true'})
        self.fields['documentacao'].widget.attrs['disabled'] = 'disabled'

    class Meta:
        model = Processo
        fields = ['dtprocesso', 'clientepj', 'conhecimentoprograma', 'linhacredito', 'finalidadecredito', 'empresa',
                  'situacaonegocio', 'banco', 'agencia', 'conta', 'tipconta', 'observacao', 'numprotocolo',
                  'sobreonegocio', 'porquedonegocio', 'evolucaonegocio', 'valorcoberto', 'valorsolicitado',
                  'prazosolicitado', 'numbeneficiados', 'numfuncionarios', 'expecocupacoes', 'valorrendanegoc',
                  'documentacao']
        widgets = {
            'valorcoberto': forms.TextInput(attrs={'class': 'mask-money form-control', 'placeholder': '0,00'}),
            'valorsolicitado': forms.TextInput(attrs={'class': 'mask-money form-control', 'placeholder': '0,00'}),
            'valorrendanegoc': forms.TextInput(attrs={'class': 'mask-money form-control', 'placeholder': '0,00'}),
            'dtprocesso': forms.TextInput(
                # format=('%Y-%m-%d'),
                attrs={'class': 'textinput form-control',
                       'placeholder': 'Selecione uma data',
                       'type': 'date'  # <--- IF I REMOVE THIS LINE, THE INITIAL VALUE IS DISPLAYED
                       }),
            'linhacredito': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                    'required': 'True',
                }),
            'finalidadecredito': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                    'required': 'True',
                }),
            'sobreonegocio': forms.Textarea(
                attrs={
                    'class': 'textinput form-control',
                    'required': 'True',
                    'rows': '3'
                }),
            'porquedonegocio': forms.Textarea(
                attrs={
                    'class': 'textinput form-control',
                    'required': 'True',
                    'rows': '3'
                }),
            'evolucaonegocio': forms.Textarea(
                attrs={
                    'class': 'textinput form-control',
                    'required': 'True',
                    'rows': '3'
                }),
            'observacao': forms.Textarea(
                attrs={
                    'class': 'textinput form-control',
                    'rows': '3'
                }),
        }

    def clean(self):
        cleaned_data = super().clean()

        # Como o cliente nem sempre tem uma conta corrente aberta estes campos serão verificados no momento da geração das parcelas
        # banco = cleaned_data.get("banco")
        # if not banco:
        #     raise ValidationError(
        #         "AVISO: Em 'INFORMAÇÕES DO CLIENTE' o campo banco não foi preenchido... Verifique."
        #     )
        #
        # agencia = cleaned_data.get("agencia")
        # if not agencia:
        #     raise ValidationError(
        #         "AVISO: Em 'INFORMAÇÕES DO CLIENTE' o campo agência não foi preenchido... Verifique."
        #     )
        #
        # conta = cleaned_data.get("conta")
        # if not conta:
        #     raise ValidationError(
        #         "AVISO: Em 'INFORMAÇÕES DO CLIENTE' o campo conta corrente não foi preenchido... Verifique."
        #     )
        #
        # tipconta = cleaned_data.get("tipconta")
        # if not tipconta:
        #     raise ValidationError(
        #         "AVISO: Em 'INFORMAÇÕES DO CLIENTE' o campo tipo de conta não foi preenchido... Verifique."
        #     )

        clientepj = cleaned_data.get("clientepj")
        empresa = get_object_or_404(PessoaJuridica, pk=str(clientepj)[-7:])
        if not empresa:
            raise ValidationError(
                "ERRO: Ocorreu um erro com a informação da Empresa... Verifique os dados do cadastro."
            )
        else:
            cliente_id = empresa.id

        situacao = get_object_or_404(SituacaoPessoa, pk=empresa.situacao_id)
        if situacao.blq_processo:
            raise ValidationError(
                "AVISO: Situação da Empresa não possibilita a criação e/ou movimentação de processos. Verifique o cadastro."
            )

        # Suspenso temporariamente a pedido de Zélia - reativado em 20/02/2025
        # Verifica se o cliente já não possui outro processo com parcelas em aberto
        qsdebitos = Financeiro.objects.filter(processo__clientepj=cliente_id, status='A', is_deleted=False)
        if qsdebitos:
            raise ValidationError(
                "AVISO: Cliente já possui processo(s) com parcela(s) em aberto. Favor verificar situação financeira."
            )

        # Verifica se a data do processo pertence ao exercício atual e se não são anteriores a referência de fechamento
        exercicioatual = Config.objects.filter(is_deleted=False).last().exercicio
        dtprocesso = cleaned_data.get("dtprocesso")
        if dtprocesso:
            if dtprocesso.year != exercicioatual:
                raise ValidationError(
                    "AVISO: Data do processo não pertence ao exercício atual que é de " + str(exercicioatual) + "."
                )
            refprocesso = str(dtprocesso.year) + str(dtprocesso.month).zfill(2)
            reffechamento = Fechamento.objects.filter(is_deleted=False).last().referencia
            if refprocesso <= reffechamento:
                raise ValidationError(
                    "AVISO: Data do processo antecede o mês de fechamento que é " + reffechamento +
                    ". Verifique os fechamentos realizados.")

        # atenção: campos de combos e listas precisam ser convertidos para string pois a comparação não funciona


        # Verifica os limites de solicitação do valor e do prazo para o financiamento
        valorsolicitado = cleaned_data.get("valorsolicitado")
        prazosolicitado = cleaned_data.get("prazosolicitado")
        nom_linhacredito = cleaned_data.get("linhacredito")
        linhacredito = get_object_or_404(LinhaCredito, nome=nom_linhacredito)
        if linhacredito:
            if float(valorsolicitado) > float(linhacredito.limite):
                raise ValidationError(
                    "AVISO: Crédito solicitado excede o limite máximo para essa linha de crédito que é de R$ " +
                    str(linhacredito.limite) + ". Verifique os limites em Tabelas Gerais."
                )
            if int(prazosolicitado) > int(linhacredito.nmaxparcelas):
                raise ValidationError(
                    "AVISO: Prazo solicitado excede o limite máximo para essa linha de crédito que é de " +
                    str(linhacredito.nmaxparcelas) + " parcelas. Verifique os limites em Tabelas Gerais."
                )


class OutrosDadosProcessoForm(forms.ModelForm):
    class Meta:
        model = Processo
        fields = ['banco', 'agencia', 'conta', 'tipconta']


class AvalistaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        graurelacao_default = Config.objects.filter(is_deleted=False).last().graurelacao_default

        self.fields['avalista'].queryset = PessoaFisica.objects.filter(Q(is_deleted=False) & ~Q(tipo='C')).order_by('nome')
        self.fields['avalista'].widget.attrs.update({'class': 'textinput form-control'})
        # self.fields['avalista'].widget.attrs.update({'class': 'textinput form-control', 'required': 'true'})

        self.fields['graurelacao'].queryset = GrauRelacao.objects.filter(is_deleted=False)
        self.fields['graurelacao'].initial = graurelacao_default
        self.fields['observacao'].widget.attrs.update({'class': 'textinput form-control'})

    class Meta:
        model = Avalista
        fields = ['avalista', 'graurelacao', 'observacao', 'is_deleted']
        widgets = {
            'avalista': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                }),
            'graurelacao': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                }),
            # 'negociacao': forms.Select(
            #     attrs={
            #         'class': 'textinput form-control',
            #     }),
            # 'observacao': forms.Textarea(
            #     attrs={
            #         'class': 'textinput form-control',
            #         'rows': '3'
            #     }),
        }

    # # ESTE TESTE DEVERÁ SER FEITO NA VIEW POIS PRECISARÁ COMPARA TAMBÉM O MESMO PROCESSO PRA QUE NÃO POSSA SER CONSIDERADO
    # def clean(self):
    #     error = {}
    #     cleaned_data = super().clean()
    #     count = 0
    #     for form in self.forms:
    #         # Verifica se o formulário é válido e se o campo 'is_deleted' não está marcado como True
    #         if form.cleaned_data and not form.cleaned_data.get('is_deleted', False):
    #             count += 1
    #     print(count)
    #
    #     avalista = cleaned_data.get("avalista")
    #
    #     qsavalistas = Avalista.objects.filter(avalista_id=avalista, is_deleted=False)
    #     if qsavalistas:
    #         error['avalista'] = ['AVISO: Já existe avalista cadastrado em outro processo não encerrado.']
    #
    #     if len(error) != 0:
    #         raise ValidationError(error)

AvalistaFormSet = inlineformset_factory(Processo, Avalista, form=AvalistaForm,
                                        fields=['avalista', 'graurelacao', 'observacao'], extra=1,
                                        can_delete=True)


class ReferenciaInsertForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['nome'].widget.attrs.update({'class': 'textinput form-control',
                                                 'pattern': '[a-z A-Z 0-9 Ç]{3,30}',
                                                 'required': True,
                                                 'title': 'Letras e números com no máximo 30 caracteres.'})
        self.fields['telefone'].widget.attrs.update({'class': 'textinput form-control',
                                                     'required': True,
                                                     'title': 'Somente números (DDD + Telefone com 9 dígitos.'})
        self.fields['conceito'].widget.attrs.update({'class': 'textinput form-control', 'maxlength': '10',
                                                     'required': True,
                                                     'title': 'Letras e números com no máximo 10 caracteres'})

    class Meta:
        model = Referencia
        fields = ['nome', 'tipofonte', 'telefone', 'conceito', 'is_deleted']
        widgets = {
            'tipofonte': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                    'required': 'True',
                }),
        }

ReferenciaInsertFormSet = inlineformset_factory(Processo, Referencia, form=ReferenciaInsertForm,
                                          fields=['nome', 'tipofonte', 'telefone', 'conceito'], extra=1)


class ReferenciaUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['nome'].widget.attrs.update({'class': 'textinput form-control',
                                                 'pattern': '[a-z A-Z 0-9 Ç]{3,30}',
                                                 'title': 'Letras e números com no máximo 30 caracteres.'})
        self.fields['telefone'].widget.attrs.update({'class': 'textinput form-control',
                                                     'title': 'Somente números (DDD + Telefone com 9 dígitos.'})
        self.fields['conceito'].widget.attrs.update({'class': 'textinput form-control', 'maxlength': '10',
                                                     'title': 'Letras e números com no máximo 10 caracteres'})

    class Meta:
        model = Referencia
        fields = ['nome', 'tipofonte', 'telefone', 'conceito', 'is_deleted']
        widgets = {
            'tipofonte': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                }),
        }

ReferenciaUpdateFormSet = inlineformset_factory(Processo, Referencia, form=ReferenciaUpdateForm,
                                          fields=['nome', 'tipofonte', 'telefone', 'conceito'], extra=1, can_delete=True)


class FinanceiroForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['valorparcela'].localize = True
        self.fields['valormulta'].localize = True
        self.fields['valorjuros'].localize = True
        self.fields['valorfinal'].localize = True
        self.fields['valoracres'].localize = True
        self.fields['valordesc'].localize = True
        self.fields['valorpago'].localize = True

        self.fields['numparcela'].widget.attrs.update({'class': 'textinput form-control', 'style': 'text-align: center', 'readonly': 'true'})
        self.fields['dtemissao'].widget.attrs.update({'class': 'textinput form-control', 'readonly': 'true'})
        self.fields['dtvencimento'].widget.attrs.update({'class': 'textinput form-control', 'readonly': 'true'})
        self.fields['valorparcela'].widget.attrs.update({'class': 'textinput form-control', 'style': 'text-align: right', 'readonly': 'true'})
        self.fields['valormulta'].widget.attrs.update({'class': 'textinput form-control', 'style': 'text-align: right', 'required': 'true'})
        self.fields['valorjuros'].widget.attrs.update({'class': 'textinput form-control', 'style': 'text-align: right', 'required': 'true'})
        self.fields['percmulta'].widget.attrs.update({'class': 'textinput form-control', 'style': 'text-align: right', 'readonly': 'true'})
        self.fields['percjuros'].widget.attrs.update({'class': 'textinput form-control', 'style': 'text-align: right', 'readonly': 'true'})
        self.fields['valorfinal'].widget.attrs.update({'class': 'textinput form-control', 'style': 'text-align: right', 'readonly': 'true'})
        self.fields['valoracres'].widget.attrs.update({'class': 'textinput form-control', 'style': 'text-align: right',
                                                        'min': '0', 'required': 'true'})
        self.fields['valordesc'].widget.attrs.update({'class': 'textinput form-control', 'style': 'text-align: right', 'min': '0', 'required': 'true'})
        self.fields['valorpago'].widget.attrs.update({'class': 'textinput form-control','style': 'text-align: right',
                                                      'min': '0', 'required': 'true'})
        self.fields['observacao'].widget.attrs.update({'class': 'textinput form-control', 'maxlength': '128',
                                                      'title': 'Letras e números com no máximo 128 caracteres'})

    class Meta:
        model = Financeiro
        fields = ['numparcela', 'dtemissao', 'dtvencimento', 'valorparcela', 'valormulta', 'valorjuros', 'percmulta',
                  'percjuros', 'valorfinal', 'valoracres', 'valordesc', 'observacao', 'valorpago', 'dtpagamento',
                  'is_deleted']
        widgets = {
            'valorparcela': forms.TextInput(attrs={'class': 'mask-money form-control', 'placeholder': '0,00'}),
            'valormulta': forms.TextInput(attrs={'class': 'mask-money form-control', 'placeholder': '0,00'}),
            'valorjuros': forms.TextInput(attrs={'class': 'mask-money form-control', 'placeholder': '0,00'}),
            'valorfinal': forms.TextInput(attrs={'class': 'mask-money form-control', 'placeholder': '0,00'}),
            'valoracres': forms.TextInput(attrs={'class': 'mask-money form-control', 'placeholder': '0,00'}),
            'valordesc': forms.TextInput(attrs={'class': 'mask-money form-control', 'placeholder': '0,00'}),
            'valorpago': forms.TextInput(attrs={'class': 'mask-money form-control', 'placeholder': '0,00'}),
            'dtpagamento': forms.TextInput(
                # format=('%Y-%m-%d'),
                attrs={'class': 'textinput form-control',
                       'placeholder': 'Selecione uma data',
                       'type': 'date'  # <--- IF I REMOVE THIS LINE, THE INITIAL VALUE IS DISPLAYED
                       }),
            'observacao': forms.Textarea(
                attrs={'class': 'textinput form-control',
                       'rows': '2',
                       }),
        }

    def clean(self):
        cleaned_data = super().clean()

        # Verificação suspensa temporariamente a pedido de Zélia
        # -----------------------------------------------------------
        # dtemissao = cleaned_data.get("dtemissao")
        # dtpagamento = cleaned_data.get("dtpagamento")
        # if dtpagamento:
        #     if dtemissao > dtpagamento:
        #         raise ValidationError(
        #             "AVISO: A data de pagamento não pode ser inferior a data de emissão do título... Verifique."
        #         )

        dtpagamento = cleaned_data.get("dtpagamento")
        if not dtpagamento:
            raise ValidationError("AVISO: A data de pagamento precisa ser informada... Verifique.")

        # Verificação do mês de pagamento para ver se encontra-se fechado
        refpagamento = str(dtpagamento.year) + str(dtpagamento.month).zfill(2)

        reffechamento = Fechamento.objects.filter(is_deleted=False).last().referencia

        if refpagamento <= reffechamento:
            raise ValidationError(
                "AVISO: Data do pagamento antecede o mês de fechamento que é " + reffechamento + ". Verifique os fechamentos realizados.")

        # mesfechamento = Config.objects.filter(is_deleted=False).last().mesfechamento
        # if int(dtpagamento.month) <= int(mesfechamento):
        #     raise ValidationError(
        #         "AVISO: Data do pagamento antecede o mês de fechamento que é " + mesfechamento + ". Verifique os parâmetros em Tabelas Básicas.")

        # Verificação da conferência dos valores digitados (totais)
        valorfinal = cleaned_data.get("valorfinal")
        valoracres = cleaned_data.get("valoracres")
        valordesc = cleaned_data.get("valordesc")
        valorpago = cleaned_data.get("valorpago")
        if float(valorpago - valoracres + valordesc) != float(valorfinal):
            raise ValidationError(
                "AVISO: O valor pago juntamente com os acréscimos/descontos difere do valor final da parcela.")


class Parecer1Form(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['valorfixo_sugerido'].localize = True
        self.fields['valorgiro_sugerido'].localize = True
        self.fields['taxasugerida'].localize = True

        self.fields['conceito'].widget.attrs.update({'class': 'textinput form-control', 'pattern': '[0-9]{1,2}',
                                                     'min': '0', 'max':'10', 'title': 'Conceito de 0 a 10.'})
        self.fields['valorfixo_sugerido'].widget.attrs.update({'class': 'textinput form-control',
                                                               'style': 'text-align: right', 'min': '0.00', 'required': 'true'})
        self.fields['valorgiro_sugerido'].widget.attrs.update({'class': 'textinput form-control',
                                                               'style': 'text-align: right', 'min': '0.00', 'required': 'true'})
        self.fields['taxasugerida'].widget.attrs.update({'class': 'textinput form-control',
                                                         'style': 'text-align: right','min': '0.01', 'required': 'true'})
        self.fields['prazosugerido'].widget.attrs.update({'class': 'textinput form-control', 'pattern': '[0-9]{1,2}',
                                                          'style': 'text-align: right', 'min': '1', 'required': 'true',
                                                          'title': 'Somente números com no máximo 2 dígitoS.'})
        self.fields['valorparc_sugerido'].widget.attrs.update({'class': 'textinput form-control setprice valorparc_sugerido',
                                                               'style': 'text-align: right', 'min': '0.00',
                                                               'readonly': 'true', 'required': 'true'})

    class Meta:
        model = Parecer
        fields = ['valorfixo_sugerido', 'valorgiro_sugerido', 'taxasugerida', 'prazosugerido', 'pareceragente',
                  'valorparc_sugerido', 'conceito', 'tipo', 'is_deleted']
        widgets = {
            'valorfixo_sugerido': forms.TextInput(attrs={'class': 'mask-money form-control', 'placeholder': '0,00'}),
            'valorgiro_sugerido': forms.TextInput(attrs={'class': 'mask-money form-control', 'placeholder': '0,00'}),
            'taxasugerida': forms.TextInput(attrs={'class': 'mask-money form-control', 'placeholder': '0,00000000'}),
            'pareceragente': forms.Textarea(
                attrs={
                    'class': 'textinput form-control',
                    'rows': '5',
                    'required': 'true',
                }),
            'tipo': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                    'required': 'True',
                }),
        }

    def clean(self):
        error = {}
        cleaned_data = super().clean()

        valorparc_sugerido = cleaned_data.get("valorparc_sugerido")
        if valorparc_sugerido == 0.00:
            error['valorparc_sugerido'] = ["O valor da parcela não pode ser igual a 0 (zero)."]
        if len(error) != 0:
            raise ValidationError(error)


class Parecer2Form(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['valorfixo_sugerido'].localize = True
        self.fields['valorgiro_sugerido'].localize = True
        self.fields['taxasugerida'].localize = True
        self.fields['valorfixo_aprovado'].localize = True
        self.fields['valorgiro_aprovado'].localize = True
        self.fields['taxaaprovada'].localize = True

        self.fields['conceito'].widget.attrs.update({'class': 'textinput form-control',
                                                     'style': 'background-color: gray', 'readonly': 'true'})
        self.fields['dtcomite'].initial = date.today()
        self.fields['valorfixo_sugerido'].widget.attrs.update({'class': 'textinput form-control',
                                                               'style': 'background-color: gray; text-align: right', 'readonly': 'true'})
        self.fields['valorgiro_sugerido'].widget.attrs.update({'class': 'textinput form-control',
                                                               'style': 'background-color: gray; text-align: right', 'readonly': 'true'})
        self.fields['taxasugerida'].widget.attrs.update({'class': 'textinput form-control',
                                                         'style': 'background-color: gray; text-align: right', 'readonly': 'true'})
        self.fields['prazosugerido'].widget.attrs.update({'class': 'textinput form-control',
                                                          'style': 'background-color: gray; text-align: right', 'readonly': 'true'})
        self.fields['valorfixo_aprovado'].widget.attrs.update({'class': 'textinput form-control',
                                                               'style': 'text-align: right', 'min': '0.00'})
        self.fields['valorgiro_aprovado'].widget.attrs.update({'class': 'textinput form-control setprice valorgiro_aprovado',
                                                               'style': 'text-align: right', 'min': '0.00'})
        self.fields['taxaaprovada'].widget.attrs.update({'class': 'textinput form-control',
                                                         'style': 'text-align: right', 'min': '0.00'})
        self.fields['prazoaprovado'].widget.attrs.update({'class': 'textinput form-control', 'pattern': '[0-9]{1,2}',
                                                          'style': 'text-align: right', 'min': '0',
                                                          'title': 'Somente números com no máximo 2 dígitos.'})
        self.fields['valorparc_sugerido'].widget.attrs.update({'class': 'textinput form-control',
                                                         'style': 'text-align: right', 'min': '0.00', 'readonly': 'true', 'required': 'true'})
        self.fields['valorparcela'].widget.attrs.update({'class': 'textinput form-control setprice valorparcela',
                                                         'style': 'text-align: right', 'min': '0.00', 'readonly': 'true', 'required': 'true'})

    class Meta:
        model = Parecer
        fields = ['conceito', 'dtcomite', 'dtliberacao', 'valorfixo_sugerido', 'valorgiro_sugerido', 'valorfixo_aprovado',
                  'valorgiro_aprovado', 'taxasugerida', 'taxaaprovada', 'prazosugerido', 'prazoaprovado', 'valorparcela',
                  'valorparc_sugerido', 'dtprivencto', 'pareceragente', 'is_negado', 'motivonegativa', 'tipo', 'is_deleted']
        widgets = {
            'valorfixo_sugerido': forms.TextInput(attrs={'class': 'mask-money form-control', 'placeholder': '0,00'}),
            'valorgiro_sugerido': forms.TextInput(attrs={'class': 'mask-money form-control', 'placeholder': '0,00'}),
            'taxasugerida': forms.TextInput(attrs={'class': 'mask-money form-control', 'placeholder': '0,0000000000'}),
            'valorfixo_aprovado': forms.TextInput(attrs={'class': 'mask-money form-control', 'placeholder': '0,00'}),
            'valorgiro_aprovado': forms.TextInput(attrs={'class': 'mask-money form-control', 'placeholder': '0,00'}),
            'taxaaprovada': forms.TextInput(attrs={'class': 'mask-money form-control', 'placeholder': '0,0000000000'}),
            'dtcomite': forms.TextInput(
                # format=('%Y-%m-%d'),
                attrs={'class': 'textinput form-control',
                       'placeholder': 'Selecione uma data',
                       'required': 'true',
                       'type': 'date'  # <--- IF I REMOVE THIS LINE, THE INITIAL VALUE IS DISPLAYED
                       }),
            'pareceragente': forms.Textarea(
                attrs={
                    'class': 'textinput form-control',
                    'rows': '4',
                    'style': 'background-color: gray',
                    'readonly': 'true'
                }),
            'is_negado': forms.CheckboxInput(
                attrs={
                    'class': 'textinput form-control',
                }),
            'motivonegativa': forms.Textarea(
                attrs={
                    'class': 'textinput form-control',
                    'rows': '2',
                }),
            'tipo': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                    'style': 'background-color: gray',
                    'readonly': 'true',
                }),
        }

    def clean(self):
        error = {}
        cleaned_data = super().clean()

        processo_id = self.instance.processo_id
        valorfixo_aprovado = cleaned_data.get("valorfixo_aprovado")
        valorgiro_aprovado = cleaned_data.get("valorgiro_aprovado")
        prazoaprovado = cleaned_data.get("prazoaprovado")
        taxaaprovada = cleaned_data.get("taxaaprovada")

        processo = get_object_or_404(Processo, pk=processo_id)
        id_linhacredito = processo.linhacredito_id

        linhacredito = get_object_or_404(LinhaCredito, pk=id_linhacredito)
        # juros_mes = round(((pow((1 + (float(linhacredito.juros) / 100)), 1 / 12)) - 1) * 100, 4)
        juros_mes = float(linhacredito.juros_am)

        if float(valorfixo_aprovado +  valorgiro_aprovado) < 0.01:
            error['valorfixo_aprovado'] = ["Ao menos um dos valores (fixo ou giro) precisa ser maior que 0 (zero). Verifique."]

        if float(valorfixo_aprovado +  valorgiro_aprovado) > float(linhacredito.limite):
            error['valorfixo_aprovado'] = ["Valor aprovado excede o limite de crédito para esta linha que é de "
                                        + str(linhacredito.limite)]

        if prazoaprovado > linhacredito.nmaxparcelas:
            error['prazoaprovado'] = ["Prazo de parcelamento aprovado excede o limite máximo de parcelas para "
                         "esta linha que é de " + str(linhacredito.nmaxparcelas) + " parcelas"]

        if float(taxaaprovada) != float(juros_mes):
            error['taxaaprovada'] = ["Taxa mensal de juros aprovada difere da taxa padrão para esta linha de "
                                     "crédito que é de " + str(juros_mes) + "% a.m."]

        # if valorsugerido > linhacredito.limite:
        #     error['valorsugerido'] = ["Valor sugerido excede o limite de crédito para esta linha que é de "
        #                          + str(linhacredito.limite)]
        #
        # if prazosugerido > linhacredito.nmaxparcelas:
        #     error['prazosugerido'] = ["Prazo de parcelamento sugerido excede o limite máximo de parcelas para "
        #                  "esta linha que é de " + str(linhacredito.nmaxparcelas) + " parcelas"]
        #
        # if taxasugerida != juros_mes:
        #     error['taxasugerida'] = ["Taxa mensal de juros sugerida difere da taxa padrão para esta linha de "
        #                              "crédito que é de " + str(juros_mes) + "% a.m."]

        is_negado = cleaned_data.get("is_negado")
        motivonegativa = cleaned_data.get("motivonegativa")
        valorparcela = cleaned_data.get("valorparcela")
        if is_negado:
            if not motivonegativa:
                error['motivonegativa'] = ["Parecer negado exige justificativa."]
        else:
            if valorparcela == 0.00:
                error['valorparcela'] = ["O valor da parcela não pode ser igual a 0 (zero)."]
        if len(error) != 0:
            raise ValidationError(error)


class Parecer3Form(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['dtliberacao'].initial = date.today()
        self.fields['dtprivencto'].initial = date.today()

    class Meta:
        model = Parecer
        fields = ['dtliberacao', 'dtprivencto']

        widgets = {
            'dtliberacao': forms.TextInput(
                # format=('%Y-%m-%d'),
                attrs={'class': 'textinput form-control',
                       'placeholder': 'Entre ou selecione uma data',
                       'required': 'true',
                       'type': 'date'  # <--- IF I REMOVE THIS LINE, THE INITIAL VALUE IS DISPLAYED
                       }),
            'dtprivencto': forms.TextInput(
                # format=('%Y-%m-%d'),
                attrs={'class': 'textinput form-control',
                       'placeholder': 'Entre ou selecione uma data',
                       'required': 'true',
                       'type': 'date'  # <--- IF I REMOVE THIS LINE, THE INITIAL VALUE IS DISPLAYED
                       }),
        }


class NegociacaoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['valoracres'].localize = True
        self.fields['valordesc'].localize = True

        self.fields['dtnegociacao'].initial = date.today()

        self.fields['vlrtotaloriginal'].widget.attrs.update({'class': 'textinput form-control', 'style': 'text-align: right',
                                                             'min': '0.01', 'readonly': 'true', 'required': 'true'})
        self.fields['valordebito'].widget.attrs.update({'class': 'textinput form-control', 'style': 'text-align: right',
                                                        'min': '0.01', 'readonly': 'true', 'required': 'true'})
        self.fields['valoracres'].widget.attrs.update({'class': 'textinput form-control', 'style': 'text-align: right', })
        self.fields['valordesc'].widget.attrs.update({'class': 'textinput form-control', 'style': 'text-align: right', })
        self.fields['novoprazo'].widget.attrs.update({'class': 'textinput form-control', 'pattern': '[0-9]{1,2}',
                                                      'style': 'text-align: right', 'min': '1', 'required': 'true',
                                                      'title': 'Somente números com no máximo 2 dígitoS.'})
        self.fields['novovalor'].widget.attrs.update({'class': 'textinput form-control', 'style': 'text-align: right',
                                                      'min': '0.01', 'readonly': 'true', 'required': 'true'})
        self.fields['valorparcela'].widget.attrs.update({'class': 'textinput form-control', 'style': 'text-align: right',
                                                         'min': '0.01', 'readonly': 'true', 'required': 'true'})

    class Meta:
        model = Negociacao
        fields = ['dtnegociacao', 'vlrtotaloriginal', 'valordebito', 'valoracres', 'valordesc', 'novoprazo', 'novovalor',
                  'dtprivencto', 'valorparcela', 'motivo', 'is_deleted', 'is_refis']
        widgets = {
            'valoracres': forms.TextInput(attrs={'class': 'mask-money form-control', 'placeholder': '0,00'}),
            'valordesc': forms.TextInput(attrs={'class': 'mask-money form-control', 'placeholder': '0,00'}),
            'dtnegociacao': forms.TextInput(
                # format=('%Y-%m-%d'),
                attrs={'class': 'textinput form-control',
                       'placeholder': 'Selecione uma data',
                       'type': 'date'  # <--- IF I REMOVE THIS LINE, THE INITIAL VALUE IS DISPLAYED
                       }),
            'dtprivencto': forms.TextInput(
                # format=('%Y-%m-%d'),
                attrs={'class': 'textinput form-control',
                       'placeholder': 'Selecione uma data',
                       'type': 'date'  # <--- IF I REMOVE THIS LINE, THE INITIAL VALUE IS DISPLAYED
                       }),
            'motivo': forms.Textarea(
                attrs={
                    'class': 'textinput form-control',
                    'required': 'true',
                    'rows': '3'
                }),
        }

    def clean(self):
        cleaned_data = super().clean()

        # Verifica se a data da negociação pertence ao exercício atual e se não são é anterior a referência de fechamento
        exercicioatual = Config.objects.filter(is_deleted=False).last().exercicio
        dtnegociacao = cleaned_data.get("dtnegociacao")
        if dtnegociacao:
            if dtnegociacao.year != exercicioatual:
                raise ValidationError(
                    "AVISO: Data da negociação não pertence ao exercício atual que é de " + str(exercicioatual) + "."
                )
            refnegociacao = str(dtnegociacao.year) + str(dtnegociacao.month).zfill(2)
            reffechamento = Fechamento.objects.filter(is_deleted=False).last().referencia
            if refnegociacao <= reffechamento:
                raise ValidationError(
                    "AVISO: Data da negociação antecede o mês de fechamento que é " + reffechamento +
                    ". Verifique os fechamentos realizados.")

        valorparcela = cleaned_data.get("valorparcela")
        if valorparcela == 0.00:
            raise ValidationError(
                "AVISO: O valor da parcela não pode ser 0 (zero)."
            )


class MovimentacaoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['dtmovimento'].initial = date.today()
        self.fields['dtmovimento'].widget.attrs.update({'class': 'textinput form-control', 'readonly': 'true'})
        self.fields['destino'].queryset = Localizacao.objects.filter(is_deleted=False)
        self.fields['observacao'].widget.attrs.update({'class': 'textinput form-control', 'maxlength': '256',
                                                      'title': 'Letras e números com no máximo 256 caracteres'})

    class Meta:
        model = Movimentacao
        fields = ['dtmovimento', 'destino', 'is_recebido', 'observacao']
        widgets = {
            'dtmovimento': forms.TextInput(
                attrs={'class': 'textinput form-control',
                       'placeholder': 'Selecione uma data',
                       'type': 'date'  # <--- IF I REMOVE THIS LINE, THE INITIAL VALUE IS DISPLAYED
                       }),
            'destino': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                }),
            'observacao': forms.Textarea(
                attrs={
                    'class': 'textinput form-control',
                    'rows': '3'
                }),
        }


class ListaProcessosForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['data_ini'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['data_fin'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['linhacredito'].queryset = LinhaCredito.objects.filter(is_deleted=False).order_by('nome')
        self.fields['finalidadecredito'].queryset = FinalidadeCredito.objects.filter(is_deleted=False).order_by('nome')
        self.fields['criado_por'].queryset = User.objects.all().order_by('username')

        # status_opcoes = [("T", "TODOS")] + list(Processo.STATUS_OPCOES)
        status_opcoes = list(Processo.STATUS_OPCOES)
        self.fields['status'].choices = status_opcoes

    data_ini = forms.DateField(widget=forms.NumberInput(attrs={'type': 'date'}))
    data_fin = forms.DateField(widget=forms.NumberInput(attrs={'type': 'date'}))

    class Meta:
        model = Processo
        fields = ['linhacredito', 'finalidadecredito', 'criado_por', 'status']

        widgets = {
            'linhacredito': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                }),
            'finalidadecredito': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                }),
            'criado_por': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                }),
            'status': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                }),
        }

    def clean(self):
        cleaned_data = super().clean()

        data_ini = cleaned_data.get("data_ini")
        data_fin = cleaned_data.get("data_fin")

        if data_ini > data_fin:
            raise ValidationError(
                "AVISO: A data do processo inicial não pode ser superior a data final... Verifique."
            )

    def processar(self):
        qs = Processo.objects.filter(is_deleted=False)

        data_ini = self.cleaned_data['data_ini']
        data_fin = self.cleaned_data['data_fin']
        linhacredito = self.cleaned_data['linhacredito']
        finalidadecredito = self.cleaned_data['finalidadecredito']
        agente = self.cleaned_data['criado_por']
        status = self.cleaned_data['status']

        if linhacredito:
            if str(linhacredito) != '*':
                qs = qs.filter(linhacredito__nome=linhacredito)

        if finalidadecredito:
            if str(finalidadecredito) != '*':
                qs = qs.filter(finalidadecredito__nome=finalidadecredito)

        if status:
            qs = qs.filter(status=status)

        if agente:
            if str(agente) != '*':
                qs = qs.filter(criado_por__username=agente)

        if data_ini:
            qs = qs.filter(dtprocesso__gte=data_ini)
        if data_fin:
            qs = qs.filter(dtprocesso__lte=data_fin)

        return qs

    def calcular_total(self):
        """
        Calcula o total de 'valorsolicitado' no queryset processado. Somente registros com status = 'P'
        """
        return self.processar().aggregate(total=Sum("valorsolicitado"))["total"] or 0.0

class ProcessosPendentesForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['data_ini'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['data_fin'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['linhacredito'].queryset = LinhaCredito.objects.filter(is_deleted=False).order_by('nome')
        self.fields['finalidadecredito'].queryset = FinalidadeCredito.objects.filter(is_deleted=False).order_by('nome')
        self.fields['criado_por'].queryset = User.objects.all().order_by('username')

    data_ini = forms.DateField(widget=forms.NumberInput(attrs={'type': 'date'}), required=True)
    data_fin = forms.DateField(widget=forms.NumberInput(attrs={'type': 'date'}), required=True)


    class Meta:
        model = Processo
        fields = ['linhacredito', 'finalidadecredito', 'criado_por']

        widgets = {
            'linhacredito': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                }),
            'finalidadecredito': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                }),
            'criado_por': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                }),
        }

    def clean(self):
        cleaned_data = super().clean()

        data_ini = cleaned_data.get("data_ini")
        data_fin = cleaned_data.get("data_fin")

        if data_ini > data_fin:
            raise ValidationError(
                "AVISO: A data do processo inicial não pode ser superior a data do processo final... Verifique."
            )

    def processar(self):
        tmpconclusao = Config.objects.filter(is_deleted=False).last().tmpconclusaoprocesso

        datalimite = datetime.today() - timedelta(tmpconclusao)

        qs = Processo.objects.filter(Q(is_deleted=False) & ~Q(status='F') & ~Q(status='N') & Q(dtprocesso__lte=datalimite)).order_by('-id')

        data_ini = self.cleaned_data['data_ini']
        data_fin = self.cleaned_data['data_fin']
        linhacredito = self.cleaned_data['linhacredito']
        finalidadecredito = self.cleaned_data['finalidadecredito']
        agente = self.cleaned_data['criado_por']

        if linhacredito:
            if str(linhacredito) != '*':
                qs = qs.filter(linhacredito__nome=linhacredito)

        if finalidadecredito:
            if str(finalidadecredito) != '*':
                qs = qs.filter(finalidadecredito__nome=finalidadecredito)

        if agente:
            if str(agente) != '*':
                qs = qs.filter(criado_por__username=agente)

        if data_ini:
            qs = qs.filter(dtprocesso__gte=data_ini)
        if data_fin:
            qs = qs.filter(dtprocesso__lte=data_fin)

        return qs


class ResumoAtendimentosForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['data_ini'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['data_fin'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['linhacredito'].queryset = LinhaCredito.objects.filter(is_deleted=False).order_by('nome')
        self.fields['finalidadecredito'].queryset = FinalidadeCredito.objects.filter(is_deleted=False).order_by('nome')
        self.fields['criado_por'].queryset = User.objects.all().order_by('username')

    data_ini = forms.DateField(widget=forms.NumberInput(attrs={'type': 'date'}), required=True)
    data_fin = forms.DateField(widget=forms.NumberInput(attrs={'type': 'date'}), required=True)

    class Meta:
        model = Processo
        fields = ['linhacredito', 'finalidadecredito', 'criado_por']

        widgets = {
            'linhacredito': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                }),
            'finalidadecredito': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                }),
            'criado_por': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                }),
        }

    def clean(self):
        cleaned_data = super().clean()

        data_ini = cleaned_data.get("data_ini")
        data_fin = cleaned_data.get("data_fin")

        if data_ini > data_fin:
            raise ValidationError(
                "AVISO: A data do processo inicial não pode ser superior a data do processo final... Verifique."
            )

    def processar(self):

        qs = Processo.objects.filter(status__in=['F', 'N'], is_deleted=False)

        data_ini = self.cleaned_data['data_ini']
        data_fin = self.cleaned_data['data_fin']
        linhacredito = self.cleaned_data['linhacredito']
        finalidadecredito = self.cleaned_data['finalidadecredito']
        agente = self.cleaned_data['criado_por']

        if linhacredito:
            if str(linhacredito) != '*':
                qs = qs.filter(linhacredito__nome=linhacredito)

        if finalidadecredito:
            if str(finalidadecredito) != '*':
                qs = qs.filter(finalidadecredito__nome=finalidadecredito)

        if agente:
            if str(agente) != '*':
                qs = qs.filter(criado_por__username=agente)

        if data_ini:
            qs = qs.filter(dtprocesso__gte=data_ini)
        if data_fin:
            qs = qs.filter(dtprocesso__lte=data_fin)

        # qs = qs.values('criado_por__first_name', mes=Extract('dtprocesso', 'month')).annotate(qtde=Count('id'))

        qs = qs.values('criado_por__first_name').annotate(
            Jan=Count(Case(When(dtprocesso__month=1, then=1), output_field=IntegerField())),
            Fev=Count(Case(When(dtprocesso__month=2, then=1), output_field=IntegerField())),
            Mar=Count(Case(When(dtprocesso__month=3, then=1), output_field=IntegerField())),
            Abr=Count(Case(When(dtprocesso__month=4, then=1), output_field=IntegerField())),
            Mai=Count(Case(When(dtprocesso__month=5, then=1), output_field=IntegerField())),
            Jun=Count(Case(When(dtprocesso__month=6, then=1), output_field=IntegerField())),
            Jul=Count(Case(When(dtprocesso__month=7, then=1), output_field=IntegerField())),
            Ago=Count(Case(When(dtprocesso__month=8, then=1), output_field=IntegerField())),
            Set=Count(Case(When(dtprocesso__month=9, then=1), output_field=IntegerField())),
            Out=Count(Case(When(dtprocesso__month=10, then=1), output_field=IntegerField())),
            Nov=Count(Case(When(dtprocesso__month=11, then=1), output_field=IntegerField())),
            Dez=Count(Case(When(dtprocesso__month=12, then=1), output_field=IntegerField())),
            Total=Count(1),
            )

        return qs


class ListaPesFisicasForm(forms.ModelForm):

    MESANIVER_OPCOES = (
        ("00", "<<TODOS>>"),
        ("01", "JANEIRO"),
        ("02", "FEVEREIRO"),
        ("03", "MARÇO"),
        ("04", "ABRIL"),
        ("05", "MAIO"),
        ("06", "JUNHO"),
        ("07", "JULHO"),
        ("08", "AGOSTO"),
        ("09", "SETEMBRO"),
        ("10", "OUTUBRO"),
        ("11", "NOVEMBRO"),
        ("12", "DEZEMBRO"),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['data_ini'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['data_fin'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['tipo'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['mes_aniver'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['naturalidade'].queryset = Cidade.objects.filter(is_deleted=False).order_by('nome')
        self.fields['criado_por'].queryset = User.objects.all().order_by('username')

    data_ini = forms.DateField(widget=forms.NumberInput(attrs={'type': 'date'}), required=True)
    data_fin = forms.DateField(widget=forms.NumberInput(attrs={'type': 'date'}), required=True)
    mes_aniver = forms.ChoiceField(choices=MESANIVER_OPCOES, required=False)

    class Meta:
        model = PessoaFisica
        fields = ['tipo', 'naturalidade', 'criado_por']

        widgets = {
            'naturalidade': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                }),
            'criado_por': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                }),
        }

    def clean(self):
        cleaned_data = super().clean()

        data_ini = cleaned_data.get("data_ini")
        data_fin = cleaned_data.get("data_fin")

        if data_ini > data_fin:
            raise ValidationError(
                "AVISO: A data de cadastro inicial não pode ser superior a data de cadastro final... Verifique."
            )

    def processar(self):
        qs = PessoaFisica.objects.filter(is_deleted=False)

        tipo = self.cleaned_data['tipo']
        data_ini = self.cleaned_data['data_ini']
        data_fin = self.cleaned_data['data_fin']
        naturalidade = self.cleaned_data['naturalidade']
        mes_aniver = self.cleaned_data['mes_aniver']
        agente = self.cleaned_data['criado_por']

        if tipo:
            qs = qs.filter(tipo=tipo)
        if naturalidade:
            if str(naturalidade) != '*(**)':
                qs = qs.filter(naturalidade=naturalidade)
        if mes_aniver:
            if mes_aniver != '00':
                qs = qs.filter(dtnascimento__month=mes_aniver)
        if agente:
            if str(agente) != '*':
                qs = qs.filter(criado_por__username=agente)

        if data_ini:
            qs = qs.filter(data_criacao__gte=data_ini)
        if data_fin:
            qs = qs.filter(data_criacao__lte=data_fin)

        return qs

    # def processar(self):
    #     filtros = {'is_deleted': False}
    #
    #     tipo = self.cleaned_data.get('tipo')
    #     data_ini = self.cleaned_data.get('data_ini')
    #     data_fin = self.cleaned_data.get('data_fin')
    #     naturalidade = self.cleaned_data.get('naturalidade')
    #     mes_aniver = self.cleaned_data.get('mes_aniver')
    #     agente = self.cleaned_data.get('criado_por')
    #
    #     if tipo:
    #         filtros['tipo'] = tipo
    #
    #     if naturalidade and str(naturalidade) != '*(**)':
    #         filtros['naturalidade'] = naturalidade
    #
    #     if agente and str(agente) != '*':
    #         filtros['criado_por__username'] = agente
    #
    #     if data_ini:
    #         filtros['data_criacao__gte'] = data_ini
    #
    #     if data_fin:
    #         filtros['data_criacao__lte'] = data_fin
    #
    #     if mes_aniver and mes_aniver != '00':
    #         filtros['dtnascimento__month'] = mes_aniver
    #
    #     return PessoaFisica.objects.filter(**filtros)

class ListaPesJuridicasForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['data_ini'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['data_fin'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['porteempresa'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['setornegocio'].queryset = SetorNegocio.objects.filter(is_deleted=False).order_by('nome')
        self.fields['ramoatividade'].queryset = RamoAtividade.objects.filter(is_deleted=False).order_by('nome')
        self.fields['criado_por'].queryset = User.objects.all().order_by('username')

    data_ini = forms.DateField(widget=forms.NumberInput(attrs={'type': 'date'}), required=True)
    data_fin = forms.DateField(widget=forms.NumberInput(attrs={'type': 'date'}), required=True)

    class Meta:
        model = PessoaJuridica
        fields = ['porteempresa', 'setornegocio', 'ramoatividade', 'criado_por']

        widgets = {
            'setornegocio': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                }),
            'ramoatividade': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                }),
            'criado_por': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                }),
        }

    def clean(self):
        cleaned_data = super().clean()

        data_ini = cleaned_data.get("data_ini")
        data_fin = cleaned_data.get("data_fin")

        if data_ini > data_fin:
            raise ValidationError(
                "AVISO: A data de cadastro inicial não pode ser superior a data de cadastro final... Verifique."
            )

    def processar(self):
        qs = PessoaJuridica.objects.filter(is_deleted=False)

        data_ini = self.cleaned_data['data_ini']
        data_fin = self.cleaned_data['data_fin']
        porteempresa = self.cleaned_data['porteempresa']
        setornegocio = self.cleaned_data['setornegocio']
        ramoatividade = self.cleaned_data['ramoatividade']
        agente = self.cleaned_data['criado_por']

        if setornegocio:
            qs = qs.filter(setornegocio=setornegocio)
        if ramoatividade:
            qs = qs.filter(ramoatividade=ramoatividade)
        if porteempresa:
            qs = qs.filter(porteempresa=porteempresa)
        if agente:
            if str(agente) != '*':
                qs = qs.filter(criado_por__username=agente)

        if data_ini:
            qs = qs.filter(data_criacao__gte=data_ini)
        if data_fin:
            qs = qs.filter(data_criacao__lte=data_fin)

        return qs


class InadimplentesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['data_ini'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['data_fin'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['datavenc_ini'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['datavenc_fin'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['linhacredito'].queryset = LinhaCredito.objects.filter(is_deleted=False).order_by('nome')
        self.fields['finalidadecredito'].queryset = FinalidadeCredito.objects.filter(is_deleted=False).order_by('nome')
        self.fields['criado_por'].queryset = User.objects.all().order_by('username')

    data_ini = forms.DateField(widget=forms.NumberInput(attrs={'type': 'date'}), required=True)
    data_fin = forms.DateField(widget=forms.NumberInput(attrs={'type': 'date'}), required=True)
    datavenc_ini = forms.DateField(widget=forms.NumberInput(attrs={'type': 'date'}), required=True)
    datavenc_fin = forms.DateField(widget=forms.NumberInput(attrs={'type': 'date'}), required=True)

    opcoes_tipo = [('PF', 'Pessoa Física'), ('PJ', 'Pessoa Jurídica')]
    tipocliente = forms.CharField(label='Tipo de Cliente:', widget=forms.RadioSelect(choices=opcoes_tipo), required=True)

    modelos_tipo = [('1', 'Analítico'), ('2', 'Sintético')]
    modelo = forms.CharField(widget=forms.RadioSelect(choices=modelos_tipo), required=True)

    class Meta:
        model = Processo
        fields = ['linhacredito', 'finalidadecredito', 'criado_por']

        widgets = {
            'linhacredito': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                }),
            'finalidadecredito': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                }),
            'criado_por': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                }),
        }

    def clean(self):
        cleaned_data = super().clean()

        data_ini = cleaned_data.get("data_ini")
        data_fin = cleaned_data.get("data_fin")
        datavenc_ini = cleaned_data.get("datavenc_ini")
        datavenc_fin = cleaned_data.get("datavenc_fin")

        if data_ini > data_fin:
            raise ValidationError(
                "AVISO: A data inicial do processo não pode ser superior a data final do processo... Verifique."
            )
        if datavenc_ini > datavenc_fin:
            raise ValidationError(
                "AVISO: A data inicial do vencimento não pode ser superior a data final do vencimento... Verifique."
            )

    def processar(self):
        cleaned_data = super().clean()
        if cleaned_data.get("tipocliente") == 'PF':
            qs = Financeiro.objects.filter(is_deleted=False, status='A', processo__clientepj_id=None)
            # qs = Financeiro.objects.filter(is_deleted=False, status='A', dtvencimento__lt=datetime.today(), processo__clientepj_id=None)
        else:
            qs = Financeiro.objects.filter(is_deleted=False, status='A', processo__clientepf_id=None)
            # qs = Financeiro.objects.filter(is_deleted=False, status='A', dtvencimento__lt=datetime.today(), processo__clientepf_id=None)

        data_ini = self.cleaned_data['data_ini']
        data_fin = self.cleaned_data['data_fin']
        datavenc_ini = self.cleaned_data['datavenc_ini']
        datavenc_fin = self.cleaned_data['datavenc_fin']
        linhacredito = self.cleaned_data['linhacredito']
        finalidadecredito = self.cleaned_data['finalidadecredito']
        agente = self.cleaned_data['criado_por']

        if linhacredito:
            qs = qs.filter(processo__linhacredito__nome=linhacredito)

        if finalidadecredito:
            qs = qs.filter(processo__finalidadecredito__nome=finalidadecredito)

        if agente:
            qs = qs.filter(criado_por__username=agente)

        if data_ini:
            qs = qs.filter(processo__dtprocesso__gte=data_ini)
        if data_fin:
            qs = qs.filter(processo__dtprocesso__lte=data_fin)

        if datavenc_ini:
            qs = qs.filter(dtvencimento__gte=datavenc_ini)
        if datavenc_fin:
            qs = qs.filter(dtvencimento__lte=datavenc_fin)

        return qs

    def processarsubtot(self):
        cleaned_data = super().clean()
        if cleaned_data.get("tipocliente") == 'PF':
            qssubtot = self.processar().values("processo__clientepf__nome").annotate(subtotparcela=Sum("valorparcela")).order_by()
        else:
            qssubtot = self.processar().values("processo__clientepj__razaosocial").annotate(
                subtotparcela=Sum("valorparcela")).order_by()
        return qssubtot

    def processartot(self):
        qstot = self.processar().aggregate(Sum("valorparcela")).values()
        qstot = list(qstot)
        return qstot


class DividaAtivaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['data_ini'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['data_fin'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['datavenc_ini'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['datavenc_fin'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['dias_inadimp'].widget.attrs.update({'class': 'textinput form-control',
                                                        'style': 'text-align: right', 'pattern': '[0-9]'})
        self.fields['linhacredito'].queryset = LinhaCredito.objects.filter(is_deleted=False).order_by('nome')
        self.fields['finalidadecredito'].queryset = FinalidadeCredito.objects.filter(is_deleted=False).order_by('nome')

    data_ini = forms.DateField(widget=forms.NumberInput(attrs={'type': 'date'}), required=True)
    data_fin = forms.DateField(widget=forms.NumberInput(attrs={'type': 'date'}), required=True)
    datavenc_ini = forms.DateField(widget=forms.NumberInput(attrs={'type': 'date'}), required=True)
    datavenc_fin = forms.DateField(widget=forms.NumberInput(attrs={'type': 'date'}), required=True)
    dias_inadimp = forms.IntegerField(widget=forms.NumberInput(attrs={'type': 'number'}), required=True)

    class Meta:
        model = Processo
        fields = ['linhacredito', 'finalidadecredito']

        widgets = {
            'linhacredito': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                }),
            'finalidadecredito': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                }),
        }

    def clean(self):
        cleaned_data = super().clean()

        data_ini = cleaned_data.get("data_ini")
        data_fin = cleaned_data.get("data_fin")
        datavenc_ini = cleaned_data.get("datavenc_ini")
        datavenc_fin = cleaned_data.get("datavenc_fin")
        dias_inadimp = cleaned_data.get("dias_inadimp")

        if data_ini > data_fin:
            raise ValidationError(
                "AVISO: A data inicial não pode ser superior a data final de pesquisa... Verifique."
            )
        if datavenc_ini > datavenc_fin:
            raise ValidationError(
                "AVISO: A data inicial do vencimento não pode ser superior a data final do vencimento... Verifique."
            )

        if int(dias_inadimp) < 1 or int(dias_inadimp) > 999:
            raise ValidationError(
                "AVISO: Valor incorreto para o n° de dias de inadimplência. Entrar com um valor entre 1 em 999."
            )


    def processar(self):
        data_ini = self.cleaned_data['data_ini']
        data_fin = self.cleaned_data['data_fin']
        datavenc_ini = self.cleaned_data['datavenc_ini']
        datavenc_fin = self.cleaned_data['datavenc_fin']
        dias_inadimp = self.cleaned_data['dias_inadimp']

        qs = Financeiro.objects.filter(is_deleted=False, status='A')

        linhacredito = self.cleaned_data['linhacredito']
        finalidadecredito = self.cleaned_data['finalidadecredito']

        if linhacredito:
            qs = qs.filter(processo__linhacredito__nome=linhacredito)

        if finalidadecredito:
            qs = qs.filter(processo__finalidadecredito__nome=finalidadecredito)

        if data_ini:
            qs = qs.filter(processo__dtprocesso__gte=data_ini)
        if data_fin:
            qs = qs.filter(processo__dtprocesso__lte=data_fin)

        if datavenc_ini:
            qs = qs.filter(dtvencimento__gte=datavenc_ini)
        if datavenc_fin:
            qs = qs.filter(dtvencimento__lte=datavenc_fin)

        # Não está funcional
        # if dias_inadimp:
        #     qs = qs.filter(dias_atraso__gte=dias_inadimp)

        return qs


class TitulosaReceberForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['venc_ini'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['venc_fin'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['linhacredito'].queryset = LinhaCredito.objects.filter(is_deleted=False).order_by('nome')
        self.fields['finalidadecredito'].queryset = FinalidadeCredito.objects.filter(is_deleted=False).order_by('nome')
        self.fields['criado_por'].queryset = User.objects.all().order_by('username')

    venc_ini = forms.DateField(widget=forms.NumberInput(attrs={'type': 'date'}), required=True)
    venc_fin = forms.DateField(widget=forms.NumberInput(attrs={'type': 'date'}), required=True)

    class Meta:
        model = Processo
        fields = ['linhacredito', 'finalidadecredito', 'criado_por']

        widgets = {
            'linhacredito': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                }),
            'finalidadecredito': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                }),
            'criado_por': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                }),
        }

    def clean(self):
        cleaned_data = super().clean()

        venc_ini = cleaned_data.get("venc_ini")
        venc_fin = cleaned_data.get("venc_fin")

        if venc_ini > venc_fin:
            raise ValidationError(
                "AVISO: A data de vencimento inicial não pode ser superior a data de vencimento final... Verifique."
            )

    def processar(self):
        qs = Financeiro.objects.filter(is_deleted=False, status='A').order_by("dtvencimento")

        venc_ini = self.cleaned_data['venc_ini']
        venc_fin = self.cleaned_data['venc_fin']
        linhacredito = self.cleaned_data['linhacredito']
        finalidadecredito = self.cleaned_data['finalidadecredito']
        agente = self.cleaned_data['criado_por']

        if linhacredito:
            if str(linhacredito) != '*':
                qs = qs.filter(processo__linhacredito__nome=linhacredito)

        if finalidadecredito:
            if str(finalidadecredito) != '*':
                qs = qs.filter(processo__finalidadecredito__nome=finalidadecredito)

        if agente:
            if str(agente) != '*':
                qs = qs.filter(criado_por__username=agente)

        if venc_ini:
            qs = qs.filter(dtvencimento__gte=venc_ini)
        if venc_fin:
            qs = qs.filter(dtvencimento__lte=venc_fin)
        return qs

    def processarsubtot(self):
        qssubtot = (self.processar().values("dtvencimento").annotate(subtotapagar=Sum("valorparcela")).
                    order_by("dtvencimento"))
        return qssubtot


class RecebimentosForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['pgto_ini'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['pgto_fin'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['venc_ini'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['venc_fin'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['linhacredito'].queryset = LinhaCredito.objects.filter(is_deleted=False).order_by('nome')
        self.fields['finalidadecredito'].queryset = FinalidadeCredito.objects.filter(is_deleted=False).order_by('nome')
        self.fields['criado_por'].queryset = User.objects.all().order_by('username')


    pgto_ini = forms.DateField(widget=forms.NumberInput(attrs={'type': 'date'}), required=True)
    pgto_fin = forms.DateField(widget=forms.NumberInput(attrs={'type': 'date'}), required=True)
    venc_ini = forms.DateField(widget=forms.NumberInput(attrs={'type': 'date'}), required=True)
    venc_fin = forms.DateField(widget=forms.NumberInput(attrs={'type': 'date'}), required=True)

    class Meta:
        model = Processo
        fields = ['linhacredito', 'finalidadecredito', 'criado_por']

        widgets = {
            'linhacredito': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                }),
            'finalidadecredito': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                }),
            'criado_por': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                }),
        }

    def clean(self):
        cleaned_data = super().clean()

        venc_ini = cleaned_data.get("venc_ini")
        venc_fin = cleaned_data.get("venc_fin")
        pgto_ini = cleaned_data.get("pgto_ini")
        pgto_fin = cleaned_data.get("pgto_fin")

        if venc_ini > venc_fin:
            raise ValidationError(
                "AVISO: A data de vencimento inicial não pode ser superior a data de vencimento final... Verifique."
            )
        if pgto_ini > pgto_fin:
            raise ValidationError(
                "AVISO: A data de pagamento inicial não pode ser superior a data de pagamento final... Verifique."
            )

    def processar(self):
        qs = Financeiro.objects.filter(status='P').order_by("dtpagamento")

        pgto_ini = self.cleaned_data['pgto_ini']
        pgto_fin = self.cleaned_data['pgto_fin']
        venc_ini = self.cleaned_data['venc_ini']
        venc_fin = self.cleaned_data['venc_fin']
        linhacredito = self.cleaned_data['linhacredito']
        finalidadecredito = self.cleaned_data['finalidadecredito']
        agente = self.cleaned_data['criado_por']

        if linhacredito:
            if str(linhacredito) != '*':
                qs = qs.filter(processo__linhacredito__nome=linhacredito)

        if finalidadecredito:
            if str(finalidadecredito) != '*':
                qs = qs.filter(processo__finalidadecredito__nome=finalidadecredito)

        if agente:
            if str(agente) != '*':
                qs = qs.filter(criado_por__username=agente)

        if pgto_ini:
            qs = qs.filter(dtpagamento__gte=pgto_ini)
        if pgto_fin:
            qs = qs.filter(dtpagamento__lte=pgto_fin)

        if venc_ini:
            qs = qs.filter(dtvencimento__gte=venc_ini)
        if venc_fin:
            qs = qs.filter(dtvencimento__lte=venc_fin)
        return qs

    def processarsubtot(self):
        qssubtot = self.processar().values("dtpagamento").annotate(subtotpago=Sum("valorpago")).order_by("dtpagamento")
        return qssubtot


class DadosCadastraisClientesForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dtcomite_ini'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['dtcomite_fin'].widget.attrs.update({'class': 'textinput form-control'})

    dtcomite_ini = forms.DateField(widget=forms.NumberInput(attrs={'type': 'date'}), required=True)
    dtcomite_fin = forms.DateField(widget=forms.NumberInput(attrs={'type': 'date'}), required=True)

    def clean(self):
        cleaned_data = super().clean()

        dtcomite_ini = cleaned_data.get("dtcomite_ini")
        dtcomite_fin = cleaned_data.get("dtcomite_fin")

        if dtcomite_ini > dtcomite_fin:
            raise ValidationError(
                "AVISO: A data inicial não pode ser superior a data final... Verifique."
            )

    def processar(self):
        qs = Parecer.objects.filter(is_deleted=False).order_by('dtcomite')
        qs = qs.filter(Q(processo__status='2') | Q(processo__status='N') | Q(processo__status='F'))

        dtcomite_ini = self.cleaned_data['dtcomite_ini']
        dtcomite_fin = self.cleaned_data['dtcomite_fin']

        if dtcomite_ini:
            qs = qs.filter(dtcomite__gte=dtcomite_ini)
        if dtcomite_fin:
            qs = qs.filter(dtcomite__lte=dtcomite_fin)
        return qs

# Vai mudar depois que for criada a estrutura para movimentação dos processos no Comitê
class ProcessosComiteForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dtcomite_ini'].widget.attrs.update({'class': 'textinput form-control'})
        # self.fields['dtcomite_fin'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['linhacredito'].queryset = LinhaCredito.objects.filter(is_deleted=False).order_by('nome')
        self.fields['criado_por'].queryset = User.objects.all().order_by('username')

    dtcomite_ini = forms.DateField(widget=forms.NumberInput(attrs={'type': 'date'}), required=True)
    # dtcomite_fin = forms.DateField(widget=forms.NumberInput(attrs={'type': 'date'}), required=True)

    class Meta:
        model = Processo
        fields = ['linhacredito', 'criado_por']

        widgets = {
            'linhacredito': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                }),
            'criado_por': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                }),
        }

    # def clean(self):
    #     cleaned_data = super().clean()
    #
    #     dtcomite_ini = cleaned_data.get("dtcomite_ini")
    #     # dtcomite_fin = cleaned_data.get("dtcomite_fin")
    #
    #     # if dtcomite_ini > dtcomite_fin:
    #     #     raise ValidationError(
    #     #         "AVISO: A data inicial não pode ser superior a data final... Verifique."
    #     #     )

    def processar(self):
        qs = Parecer.objects.filter(is_deleted=False).order_by('processo__criado_por')
        qs = qs.filter(Q(processo__status='2') | Q(processo__status='N') | Q(processo__status='X') | Q(processo__status='F'))

        dtcomite_ini = self.cleaned_data['dtcomite_ini']
        # dtcomite_fin = self.cleaned_data['dtcomite_fin']
        linhacredito = self.cleaned_data['linhacredito']
        agente = self.cleaned_data['criado_por']

        if linhacredito:
            qs = qs.filter(processo__linhacredito__nome=linhacredito)

        if agente:
            qs = qs.filter(processo__criado_por__username=agente)

        if dtcomite_ini:
            qs = qs.filter(dtcomite=dtcomite_ini)

        # if dtcomite_ini:
        #     qs = qs.filter(dtcomite__gte=dtcomite_ini)
        # if dtcomite_fin:
        #     qs = qs.filter(dtcomite__lte=dtcomite_fin)

        return qs

    def processarsubtot(self):
        qssubtot = (self.processar().values("processo__linhacredito__nome")
                    .annotate(subtot=Sum(F("valorfixo_aprovado") + F("valorgiro_aprovado")), qtde=Count("id"),
                              mediasub=Avg(F("valorfixo_aprovado") + F("valorgiro_aprovado")))
                    .order_by("processo__linhacredito__nome"))
        return qssubtot

    def processartotal(self):
        qstotal = (self.processar().aggregate(valor_total=Sum(F("valorfixo_aprovado") + F("valorgiro_aprovado")),
                                              qtde_total=Count("id"), media_final=Avg(F("valorfixo_aprovado") + F("valorgiro_aprovado"))))
        return qstotal


class AutorizadosComiteForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dtcomite_ini'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['dtcomite_fin'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['linhacredito'].queryset = LinhaCredito.objects.filter(is_deleted=False).order_by('nome')
        self.fields['criado_por'].queryset = User.objects.all().order_by('username')

    dtcomite_ini = forms.DateField(widget=forms.NumberInput(attrs={'type': 'date'}), required=True)
    dtcomite_fin = forms.DateField(widget=forms.NumberInput(attrs={'type': 'date'}), required=True)

    class Meta:
        model = Processo
        fields = ['linhacredito', 'criado_por']

        widgets = {
            'linhacredito': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                }),
            'criado_por': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                }),
        }

    def clean(self):
        cleaned_data = super().clean()

        dtcomite_ini = cleaned_data.get("dtcomite_ini")
        dtcomite_fin = cleaned_data.get("dtcomite_fin")

        if dtcomite_ini > dtcomite_fin:
            raise ValidationError(
                "AVISO: A data inicial não pode ser superior a data final... Verifique."
            )

    def processar(self):
        qs = Parecer.objects.filter(is_deleted=False).order_by('dtcomite')
        qs = qs.filter(Q(processo__status='2') | Q(processo__status='N') | Q(processo__status='X') | Q(processo__status='F'))

        dtcomite_ini = self.cleaned_data['dtcomite_ini']
        dtcomite_fin = self.cleaned_data['dtcomite_fin']
        linhacredito = self.cleaned_data['linhacredito']
        agente = self.cleaned_data['criado_por']

        if linhacredito:
            qs = qs.filter(processo__linhacredito__nome=linhacredito)

        if agente:
            qs = qs.filter(processo__criado_por__username=agente)

        if dtcomite_ini:
            qs = qs.filter(dtcomite__gte=dtcomite_ini)
        if dtcomite_fin:
            qs = qs.filter(dtcomite__lte=dtcomite_fin)
        return qs


class NegociacoesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dtcriacao_ini'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['dtcriacao_fin'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['linhacredito'].queryset = LinhaCredito.objects.filter(is_deleted=False).order_by('nome')
        self.fields['criado_por'].queryset = User.objects.all().order_by('username')

    dtcriacao_ini = forms.DateField(widget=forms.NumberInput(attrs={'type': 'date'}), required=True)
    dtcriacao_fin = forms.DateField(widget=forms.NumberInput(attrs={'type': 'date'}), required=True)

    class Meta:
        model = Processo
        fields = ['linhacredito', 'criado_por']

        widgets = {
            'linhacredito': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                }),
            'criado_por': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                }),
        }

    def clean(self):
        cleaned_data = super().clean()

        dtcriacao_ini = cleaned_data.get("dtcriacao_ini")
        dtcriacao_fin = cleaned_data.get("dtcriacao_fin")

        if dtcriacao_ini > dtcriacao_fin:
            raise ValidationError(
                "AVISO: A data inicial não pode ser superior a data final... Verifique."
            )

    def processar(self):
        qs = Negociacao.objects.filter(is_deleted=False).order_by('data_criacao')

        dtcriacao_ini = self.cleaned_data['dtcriacao_ini']
        dtcriacao_fin = self.cleaned_data['dtcriacao_fin']
        linhacredito = self.cleaned_data['linhacredito']
        agente = self.cleaned_data['criado_por']

        if linhacredito:
            qs = qs.filter(processo__linhacredito__nome=linhacredito)

        if agente:
            qs = qs.filter(processo__criado_por__username=agente)

        if dtcriacao_ini:
            qs = qs.filter(data_criacao__gte=dtcriacao_ini)
        if dtcriacao_fin:
            qs = qs.filter(data_criacao__lte=dtcriacao_fin)
        return qs

    def calcular_total(self):
        """
        Calcula o total de 'novovalor' no queryset processado.
        """
        return self.processar().aggregate(total=Sum("novovalor"))["total"] or 0.0


class Recebimentos1Form(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['pgto_ini'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['pgto_fin'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['linhacredito'].queryset = LinhaCredito.objects.filter(is_deleted=False).order_by('nome')

    pgto_ini = forms.DateField(widget=forms.NumberInput(attrs={'type': 'date'}), required=True)
    pgto_fin = forms.DateField(widget=forms.NumberInput(attrs={'type': 'date'}), required=True)

    opcoes_tipo = [('1', 'Versão 1'), ('2', 'Versão 2')]
    versao = forms.CharField(label='Versão do Relatório:', widget=forms.RadioSelect(choices=opcoes_tipo), required=True)

    class Meta:
        model = Processo
        fields = ['linhacredito']

        widgets = {
            'linhacredito': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                }),
        }

    def clean(self):
        cleaned_data = super().clean()

        pgto_ini = cleaned_data.get("pgto_ini")
        pgto_fin = cleaned_data.get("pgto_fin")

        if pgto_ini > pgto_fin:
            raise ValidationError(
                "AVISO: A data inicial não pode ser superior a data final... Verifique."
            )

    def processar(self):
        qs = Financeiro.objects.filter(status='P').order_by("dtpagamento")

        pgto_ini = self.cleaned_data['pgto_ini']
        pgto_fin = self.cleaned_data['pgto_fin']
        linhacredito = self.cleaned_data['linhacredito']

        if linhacredito:
            qs = qs.filter(processo__linhacredito__nome=linhacredito)

        if pgto_ini:
            qs = qs.filter(dtpagamento__gte=pgto_ini)
        if pgto_fin:
            qs = qs.filter(dtpagamento__lte=pgto_fin)

        return qs

    def processarsubtot(self):
        versao = self.cleaned_data.get("versao")
        if versao == '1':
            qssubtot = (self.processar().values("dtpagamento").
                        annotate(subtotoriginal=Sum("valororiginal"), subtotparcela=Sum("valorparcela"),
                                 subtotjurosfinanc=Sum(F("valorparcela") - F("valororiginal")),
                                 subtotacres=Sum(F("valoracres") + F("valormulta") + F("valorjuros")),
                                 subtotdesc=Sum("valordesc"),  subtotpago=Sum("valorpago")).order_by("dtpagamento"))
        else:
            qssubtot = (self.processar().values("dtpagamento").
                        annotate(subtotoriginal=Sum("valororiginal"), subtotparcela=Sum("valorparcela"),
                                 subtotjuros_recebto=Sum(F("valoracres") + F("valormulta") + F("valorjuros") - F("valordesc")),
                                 subtotpago=Sum("valorpago")).order_by("dtpagamento"))
        return qssubtot


class LiberacaoValoresForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['liberacao_ini'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['liberacao_fin'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['linhacredito'].queryset = LinhaCredito.objects.filter(is_deleted=False).order_by('nome')


    liberacao_ini = forms.DateField(widget=forms.NumberInput(attrs={'type': 'date'}), required=True)
    liberacao_fin = forms.DateField(widget=forms.NumberInput(attrs={'type': 'date'}), required=True)

    class Meta:
        model = Processo
        fields = ['linhacredito']

        widgets = {
            'linhacredito': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                }),
        }

    def clean(self):
        cleaned_data = super().clean()

        liberacao_ini = cleaned_data.get("liberacao_ini")
        liberacao_fin = cleaned_data.get("liberacao_fin")

        if liberacao_ini > liberacao_fin:
            raise ValidationError(
                "AVISO: A data inicial não pode ser superior a data final... Verifique."
            )

    def processar(self):
        qs = Parecer.objects.filter(is_deleted=False).order_by('dtliberacao', 'processo_id')

        liberacao_ini = self.cleaned_data['liberacao_ini']
        liberacao_fin = self.cleaned_data['liberacao_fin']
        linhacredito = self.cleaned_data['linhacredito']

        if linhacredito:
            qs = qs.filter(processo__linhacredito__nome=linhacredito, processo__status='F')

        if liberacao_ini:
            qs = qs.filter(dtliberacao__gte=liberacao_ini)
        if liberacao_fin:
            qs = qs.filter(dtliberacao__lte=liberacao_fin)

        return qs

    def calcular_total(self):
        """
        Calcula o total de 'vlrtotalaprovado' no queryset processado.
        """
        return self.processar().aggregate(total=Sum("valorgiro_aprovado") + Sum("valorfixo_aprovado"))["total"] or 0.0


class MovimentosForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['edicao_ini'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['edicao_fin'].widget.attrs.update({'class': 'textinput form-control'})


    edicao_ini = forms.DateField(widget=forms.NumberInput(attrs={'type': 'date'}), required=True)
    edicao_fin = forms.DateField(widget=forms.NumberInput(attrs={'type': 'date'}), required=True)

    def clean(self):
        cleaned_data = super().clean()

        edicao_ini = cleaned_data.get("edicao_ini")
        edicao_fin = cleaned_data.get("edicao_fin")

        if edicao_ini > edicao_fin:
            raise ValidationError(
                "AVISO: A data de movimentação inicial não pode ser superior a data de movimentação final... Verifique."
            )

    def processar(self):
        qs = Financeiro.objects.filter(is_deleted=False)

        edicao_ini = self.cleaned_data['edicao_ini']
        edicao_fin = self.cleaned_data['edicao_fin']

        if edicao_ini:
            qs = qs.filter(data_edicao__gte=edicao_ini)
        if edicao_fin:
            qs = qs.filter(data_edicao__lte=edicao_fin)

        return qs

    def calcular_total(self):
        """
        Calcula o total de 'valorpago' no queryset processado. Somente registros com status = 'P'
        """
        return self.processar().filter(status='P').aggregate(total=Sum("valorparcela"))["total"] or 0.0


class ComiteForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['numreuniao'].widget.attrs.update({'class': 'textinput form-control'}, required=True)
        self.fields['is_realizado'].widget.attrs.update({'class': 'textinput form-control'})

    class Meta:
        model = Comite
        fields = ['numreuniao', 'dtcomite', 'observacao', 'is_realizado']
        widgets = {
            'dtcomite': forms.TextInput(
                # format=('%Y-%m-%d'),
                attrs={'class': 'textinput form-control',
                       'placeholder': 'Selecione uma data',
                       'type': 'date'  # <--- IF I REMOVE THIS LINE, THE INITIAL VALUE IS DISPLAYED
                       }),
            'observacao': forms.Textarea(
                attrs={
                    'class': 'textinput form-control',
                    'rows': '1'
                }),
        }

class ComiteProcessoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['processo'].queryset = Processo.objects.filter(is_deleted=False, status='2').order_by('numprocesso')
        self.fields['observacao'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['is_aprovado'].widget.attrs.update({'class': 'textinput form-control'})

    class Meta:
        model = ProcessosComite
        fields = ['processo', 'observacao', 'is_aprovado', 'is_deleted']
        widgets = {
            'processo': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                }),
        }

ComiteProcessoFormSet = inlineformset_factory(Comite, ProcessosComite, form=ComiteProcessoForm,
                                          fields=['processo', 'observacao', 'is_aprovado'], extra=4, can_delete=True)


class ComiteMembroForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['operador'].queryset = Operador.objects.filter(is_deleted=False, is_membrocomite=True)

    class Meta:
        model = MembrosComite
        fields = ['operador', 'is_deleted']
        widgets = {
            'operador': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                }),
        }

ComiteMembroFormSet = inlineformset_factory(Comite, MembrosComite, form=ComiteMembroForm,
                                          fields=['operador'], extra=3, can_delete=True)


class RetornoForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    caminho_arquivo = os.path.join(settings.BASE_DIR, 'Documentos/retorno/')
    nome_lista = forms.FilePathField(widget=forms.Select(attrs={'type': 'text'}), required=True, path=caminho_arquivo)

    class Meta:
        widgets = {
            'nome_lista': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                }),
        }


class EnvioForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['data_ini'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['data_fin'].widget.attrs.update({'class': 'textinput form-control'})

    data_ini = forms.DateField(widget=forms.NumberInput(attrs={'type': 'date'}), required=True)
    data_fin = forms.DateField(widget=forms.NumberInput(attrs={'type': 'date'}), required=True)

    class Meta:
        widgets = {
            'data_ini': forms.TextInput(
                # format=('%Y-%m-%d'),
                attrs={'class': 'textinput form-control',
                       'placeholder': 'Selecione uma data',
                       'type': 'date'  # <--- IF I REMOVE THIS LINE, THE INITIAL VALUE IS DISPLAYED
                       }),
            'data_fin': forms.TextInput(
                # format=('%Y-%m-%d'),
                attrs={'class': 'textinput form-control',
                       'placeholder': 'Selecione uma data',
                       'type': 'date'  # <--- IF I REMOVE THIS LINE, THE INITIAL VALUE IS DISPLAYED
                       }),
        }

    def clean(self):
        cleaned_data = super().clean()

        data_ini = cleaned_data.get("data_ini")
        data_fin = cleaned_data.get("data_fin")

        if data_ini > data_fin:
            raise ValidationError(
                "AVISO: A data de emissão inicial não pode ser superior a data de emissão final... Verifique."
            )

    def processar(self):
        qs = Financeiro.objects.filter(Q(status='A') & Q(nossonumero='0'))

        emissao_ini = self.cleaned_data['data_ini']
        emissao_fin = self.cleaned_data['data_fin']

        if emissao_ini:
            qs = qs.filter(dtemissao__gte=emissao_ini)
        if emissao_fin:
            qs = qs.filter(dtemissao__lte=emissao_fin)

        return qs

class SimulacaoEmprestimoForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['linhacredito'].queryset = LinhaCredito.objects.filter(is_deleted=False).order_by('nome')
        self.fields['numcpf'].widget.attrs.update({'class': 'textinput form-control',
                                                   'title': 'Somente números com no máximo 11 dígitos.'})
        self.fields['valorrenda'].widget.attrs.update({'class': 'textinput-money form-control'})
        self.fields['valorsolicitado1'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['nparcelas'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['taxa_am'].widget.attrs.update({'class': 'textinput form-control'})

    numcpf = forms.CharField(widget=forms.TextInput(attrs={'type': 'text'}), required=True)
    valorrenda = forms.DecimalField(widget=forms.NumberInput(attrs={'style': 'text-align: right'}))
    valorsolicitado1 = forms.DecimalField(widget=forms.NumberInput(attrs={'style': 'text-align: right'}))
    nparcelas = forms.CharField(widget=forms.NumberInput(attrs={'style': 'text-align: right'}))
    taxa_am = forms.DecimalField(widget=forms.NumberInput(attrs={'style': 'text-align: right'}))
    valorparcela = forms.DecimalField(widget=forms.TextInput(attrs={'type': 'text', 'readonly': 'true'}))

    class Meta:
        model = Processo
        fields = ['linhacredito']

        widgets = {
            'linhacredito': forms.Select(
                attrs={
                    'class': 'textinput form-control',
                    'required': 'True'
                }),
        }

    def clean(self):
        error = {}
        cleaned_data = super().clean()

        nome_linhacredito = cleaned_data.get("linhacredito")
        valorlimite = cleaned_data.get("valorsolicitado1")
        maxparcelas = cleaned_data.get("nparcelas")
        taxa_am = cleaned_data.get("taxa_am")

        # valida valores limite na simulação com a Linha de Crédito solicitada
        linhacredito = get_object_or_404(LinhaCredito, nome=nome_linhacredito)

        if float(valorlimite) > linhacredito.limite:
            error['valorsolicitado1'] = ['Valor de crédito solicitado excede o valor limite para esta linha de crédito que é de R$ ' + str(linhacredito.limite)]

        if int(maxparcelas) > linhacredito.nmaxparcelas:
            error['nparcelas'] = ['Nº de parcelas solicitado excede o valor limite para esta linha de crédito que é de ' + str(linhacredito.nmaxparcelas)]

        if float(taxa_am) != float(linhacredito.juros_am):
            error['taxa_am'] = ['Valor da taxa de juros utilizada difere da taxa para esta linha de crédito que é de ' + str(linhacredito.juros_am) + '%']

        if len(error) != 0:
            raise ValidationError(error)

