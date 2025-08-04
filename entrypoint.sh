#!/bin/bash

check_required_variable() {
  if [ -z "${!1}" ]; then
    echo "$1 não foi definido."
    exit 1
  fi
}

check_optional_variable() {
  local VAR_NAME="$1"
  local DEFAULT_VALUE="$2"

  if [ -z "${!VAR_NAME}" ]; then
    echo "$1 não foi definido, utilizando valor padrão $2"
    eval "$VAR_NAME=$DEFAULT_VALUE"
  fi
}

if [ -n "$DEBUG" ]; then
  echo "DEBUG habilitado."
fi

check_optional_variable "APP_PORT" "8000"
check_optional_variable "DB_PORT" "5432"
check_optional_variable "ENGINE" "django.db.backends.postgresql"

check_required_variable "DB_HOST"
check_required_variable "DB_NAME"
check_required_variable "POSTGRES_PASSWORD"
check_required_variable "POSTGRES_USER"
check_required_variable "SECRET_KEY"
check_required_variable "DJANGO_SU_NAME"
check_required_variable "DJANGO_SU_EMAIL"
check_required_variable "DJANGO_SU_PASSWORD"

echo ""
echo "INICIANDO O BANCO POSTGRES... AGUARDE..."

while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 1
done

echo ""
echo "BANCO DE DADOS DO POSTGRES INICIADO COM SUCESSO."

echo "Iniciando as migrações"

## trecho temporário para solução das migrações incompatíveis
#find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
#find . -path "*/migrations/__pycache__/*" -delete  # Primeiro remove arquivos dentro de __pycache__
#find . -path "*/migrations/__pycache__" -type d -empty -delete  # Depois remove o diretório vazio
#python manage.py makemigrations
#python manage.py migrate --fake
#
python manage.py makemigrations tabelas --skip-checks
python manage.py migrate tabelas --skip-checks

python manage.py makemigrations processos --skip-checks
python manage.py migrate processos --skip-checks
#
echo "Novos passos"
python manage.py showmigrations tabelas
python manage.py showmigrations processos
#

echo "Término das migrações"

#echo "Iniciando a coleta dos arquivos estáticos"
#python manage.py collectstatic --noinput
#echo "Término da coleta"


#echo "INICIANDO AS CARGAS BASE DAS TABELAS DO SISTEMA... "
#python manage.py initiate_admin
#python manage.py initiate_tabelasbase
#python manage.py importar_bancos
#python manage.py importar_cbo
#python manage.py importar_municipios
#python manage.py importar_bairros
#python manage.py importar_ramosatividade
#python manage.py importar_clientes
#python manage.py importar_avalistas
#python manage.py importar_empresas
#echo ""
#echo "PROCESSO DE CARGA FINALIZADO COM SUCESSO."

# inserir aqui o processo pra rodar o envio de email automático todas as manhãs ou ao final do dia
# com as movimentações dos clientes, avalistas, empresas, processos
# python enviaEmail.py

exec "$@"
