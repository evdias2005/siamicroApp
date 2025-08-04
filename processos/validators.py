from django.core.exceptions import ValidationError

from validate_docbr import CPF, CNPJ

def validate_cpf(value):
    cpf = CPF()
    if not cpf.validate(value):
        raise ValidationError('CPF incorreto... Verifique!!!')      # verificar o motivo do não display da mensagem

def validate_cnpj(value):
    cnpj = CNPJ()
    if cnpj:
        if not cnpj.validate(value):
            raise ValidationError('CNPJ incorreto... Verifique!!!')      # verificar o motivo do não display da mensagem

def validar_tamanho_arquivo(pdf):
    tamanho_maximo = 0.5 * 1024 * 1024  # 0,5MB
    if pdf.size > tamanho_maximo:
        raise ValidationError(f"O tamanho máximo permitido para o arquivo é de {tamanho_maximo / 1024 / 1024}MB.")