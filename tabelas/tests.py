# tests.py
from django.test import TestCase
from .forms import BancoForm
from .models import Banco


class BancoFormTest(TestCase):

    def setUp(self):
        # Dados válidos para teste
        self.valid_data = {
            'codigo': '123',
            'nome': 'Banco Exemplo',
            'site': 'https://www.bancoexemplo.com',
        }
        # Dados inválidos: código com valor não numérico ou fora do padrão
        self.invalid_data = {
            'codigo': '12A',  # Inválido: deve ser 3 dígitos numéricos
            'nome': 'Banco Exemplo',
            'site': 'https://www.bancoexemplo.com',
        }

    def test_form_fields_attributes(self):
        """
        Testa se os atributos dos widgets foram configurados corretamente.
        """
        form = BancoForm()
        # Atributos do campo 'codigo'
        codigo_attrs = form.fields['codigo'].widget.attrs
        self.assertEqual(codigo_attrs.get('class'), 'textinput form-control')
        self.assertEqual(codigo_attrs.get('maxlength'), '3')
        self.assertEqual(codigo_attrs.get('pattern'), '[0-9]{3}')
        self.assertEqual(codigo_attrs.get('title'), 'Código do banco. Somente números.')

        # Atributos do campo 'nome'
        nome_attrs = form.fields['nome'].widget.attrs
        self.assertEqual(nome_attrs.get('class'), 'textinput form-control')
        self.assertEqual(nome_attrs.get('maxlength'), '50')
        self.assertEqual(nome_attrs.get('title'), 'Nome do banco. Aceita letras e números.')

        # Atributos do campo 'site'
        site_attrs = form.fields['site'].widget.attrs
        self.assertEqual(site_attrs.get('class'), 'textinput form-control')
        self.assertEqual(site_attrs.get('maxlength'), '50')
        self.assertEqual(site_attrs.get('title'), 'Site do banco. Aceita letras e números.')

    def test_form_valid_data(self):
        """
        Testa se o formulário é válido com dados corretos.
        """
        form = BancoForm(data=self.valid_data)
        self.assertTrue(form.is_valid(), msg=form.errors)

        # Opcional: salva e verifica a criação do objeto
        if form.is_valid():
            banco = form.save()
            self.assertIsInstance(banco, Banco)
            self.assertEqual(banco.codigo, self.valid_data['codigo'])
            self.assertEqual(banco.nome, self.valid_data['nome'])
            self.assertEqual(banco.site, self.valid_data['site'])

    def test_form_invalid_codigo(self):
        """
        Testa se o formulário rejeita um código inválido.
        """
        form = BancoForm(data=self.invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('codigo', form.errors)

    def test_meta_configuration(self):
        """
        Testa se os labels e help_texts definidos na Meta estão corretos.
        """
        form = BancoForm()
        self.assertEqual(form.fields['codigo'].label, 'Código do Banco')
        self.assertEqual(form.fields['nome'].label, 'Nome do Banco')
        self.assertEqual(form.fields['site'].label, 'Site Oficial')

        self.assertEqual(form.fields['codigo'].help_text, 'Informe o código de 3 dígitos do banco.')
        self.assertEqual(form.fields['nome'].help_text, 'Insira o nome completo do banco.')
        self.assertEqual(form.fields['site'].help_text, 'Forneça o URL do site oficial do banco.')

