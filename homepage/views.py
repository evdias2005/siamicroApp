import os

from django.shortcuts import render
from django.views.generic import View, TemplateView
from tabelas.models import Config
from processos.models import PessoaFisica, PessoaJuridica, Processo, Financeiro

from django.db.models import Q, Count, Sum
from django.db.models.functions import Extract

from datetime import datetime, timedelta

from dotenv import load_dotenv

from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, reverse

class CustomLoginView(LoginView):
    template_name = 'login.html'

    def form_valid(self, form):
        """Verifica se é o primeiro login antes de redirecionar"""
        response = super().form_valid(form)

        # Se o usuário marcou o checkbox para atualizar a senha
        if self.request.POST.get('atualizar_senha'):
            return redirect(reverse('password_change'))  # ou o nome da sua view de troca de senha

        return response


class HomeView(View):
    template_name = "home.html"

    def get(self, request):

        # # Check if the .env file exists
        # if os.path.isfile('.env'):
        #     load_dotenv()

        # if 'production' in os.getenv('DB_NAME'):
        #     nomebase = '[PRODUÇÃO]'
        # elif 'staging' in os.getenv('DB_NAME'):
        #     nomebase = '[TESTE]'
        # else:
        #     nomebase = '[LOCAL]'

        nomebase = '[BASE TESTE]'

        # informações para montagem do gráfico de barras (qtde processos por Mẽs)
        meses = ['JAN', 'FEV', 'MAR', 'ABR', 'MAI', 'JUN', 'JUL', 'AGO', 'SET', 'OUT', 'NOV', 'DEZ']

        labels1 = []
        data1 = []

        exercicio = Config.objects.filter(is_deleted=False).last().exercicio          # pega o exercício atual da tabela Config

        qsprocessos = Processo.objects.filter(Q(is_deleted=False) & ~Q(status='C') & Q(dtprocesso__year=exercicio))

        qsprocessosmes = qsprocessos.annotate(mes=Extract('dtprocesso', 'month')).values('mes').annotate(qtde=Count('id')).order_by('mes')
        for item in qsprocessosmes:
            indice = item['mes'] - 1                    # utilizado para converter o mês para
            labels1.append(meses[indice])                # extenso. 1=jan, 2=fev, ...
            data1.append(item['qtde'])


        # informações para montagem do gráfico de barras (processo por agente)
        labels2 = []
        data2 = []

        # qsparametro = Parametro.objects.filter(is_deleted=False).last()          # pega o último registro da tabela (default)
        # exercicio = qsparametro.exercicio               # pega o exercício atual

        # qsprocessos = Processo.objects.filter(Q(is_deleted=False) & ~Q(status='C') & Q(dtprocesso__year=exercicio))
        qsprocessosagente = qsprocessos.values('criado_por__first_name').annotate(qtde=Count('id'))

        for item in qsprocessosagente:
            # indice = item['criado_por__first_name'] - 1
            labels2.append(item['criado_por__first_name'])
            data2.append(item['qtde'])


        # informações para montagem do segundo gráfico de barras (processo por linha de crédito)
        labels4 = []
        data4 = []

        # qsparametro = Parametro.objects.filter(is_deleted=False).last()          # pega o último registro da tabela (default)
        # exercicio = qsparametro.exercicio               # pega o exercício atual

        # qsprocessos = Processo.objects.filter(Q(is_deleted=False) & ~Q(status='C') & Q(dtprocesso__year=exercicio))
        qsprocessoslincred = qsprocessos.values('linhacredito__grupo').annotate(qtde=Count('id'))

        for item in qsprocessoslincred:
            # indice = item['criado_por__first_name'] - 1
            labels4.append(item['linhacredito__grupo'])
            data4.append(item['qtde'])


        # informações para montagem do segundo gráfico de barras (processo por finalidade de crédito)
        labels5 = []
        data5 = []
        # qsparametro = Parametro.objects.filter(is_deleted=False).last()          # pega o último registro da tabela (default)
        # exercicio = qsparametro.exercicio               # pega o exercício atual
        # qsprocessos = Processo.objects.filter(Q(is_deleted=False) & ~Q(status='C') & Q(dtprocesso__year=exercicio))
        qsprocessosfincred = qsprocessos.values('finalidadecredito__nome').annotate(qtde=Count('id'))
        for item in qsprocessosfincred:
            # indice = item['criado_por__first_name'] - 1
            labels5.append(item['finalidadecredito__nome'])
            data5.append(item['qtde'])


        # informações para montagem do gráfico de barras (total dos processos em reais por linha de crédito)
        labels6 = []
        data6 = []
        qsvlrprocessoslincred = qsprocessos.values('linhacredito__grupo').annotate(total=Sum('valorsolicitado'))
        for item in qsvlrprocessoslincred:
            # indice = item['criado_por__first_name'] - 1
            # print (item['linhacredito__nome'])
            # print (int(item['total']))
            labels6.append(item['linhacredito__grupo'])
            data6.append(int(item['total']))

        # informações para montagem do gráfico de barras (total dos processos em reais por finalidade de crédito)
        labels7 = []
        data7 = []
        qsvlrprocessosfincred = qsprocessos.values('finalidadecredito__nome').annotate(total=Sum('valorsolicitado'))
        for item in qsvlrprocessosfincred:
            # indice = item['criado_por__first_name'] - 1
            # print (item['linhacredito__nome'])
            # print (int(item['total']))
            labels7.append(item['finalidadecredito__nome'])
            data7.append(int(item['total']))


        # informações para montagem do gráfico de barras (representatividade dos processos por agente)
        labels3 = []
        data3 = []
        qsprocessosuser = qsprocessos.values('criado_por__first_name').annotate(qtde=Count('id'))
        for item in qsprocessosuser:
            labels3.append(item['criado_por__first_name'])
            data3.append(item['qtde'])
        exercicio = Config.objects.filter(is_deleted=False).last().exercicio          # pega o exercício atual (default)
        tmpconclusao = Config.objects.filter(is_deleted=False).last().tmpconclusaoprocesso
        # tmpconclusao = 10   # corrigir posterioemnte pois não está funcionando no docker


        # informações para montagem do gráfico de barras (total dos processos em reais por agente)
        labels8 = []
        data8 = []
        qsvlrprocessosagente = qsprocessos.values('criado_por__first_name').annotate(total=Sum('valorsolicitado'))
        for item in qsvlrprocessosagente:
            # indice = item['criado_por__first_name'] - 1
            # print (item['linhacredito__nome'])
            # print (int(item['total']))
            labels8.append(item['criado_por__first_name'])
            data8.append(int(item['total']))

        # informações para montagem do gráfico de barras (qtde processos por Ano)
        labels9 = []
        data9 = []

        qsprocessos1 = Processo.objects.filter(Q(is_deleted=False) & ~Q(status='C'))
        qsprocessosano = qsprocessos1.annotate(ano=Extract('dtprocesso', 'year')).values('ano').annotate(qtde=Count('id')).order_by('ano')
        for item in qsprocessosano:
            labels9.append(item['ano'])
            data9.append(item['qtde'])

        # informações para montagem do gráfico de barras (total dos processos por segmento de negócio)
        labels10 = []
        data10 = []

        qsprocessossegmento = qsprocessos.values('empresa__setornegocio__nome').annotate(qtde=Count('id'))
        for item in qsprocessossegmento:
            labels10.append(item['empresa__setornegocio__nome'])
            data10.append(int(item['qtde']))


        # informações para montagem do gráfico de barras (total em R$ dos processos por segmento de negócio)
        labels11 = []
        data11 = []

        qsvlrprocessossegmento = qsprocessos.values('empresa__setornegocio__nome').annotate(total=Sum('valorsolicitado'))
        for item in qsvlrprocessossegmento:
            labels11.append(item['empresa__setornegocio__nome'])
            data11.append(int(item['total']))

        context = {
           'labels1': labels1, 'data1': data1, 'labels2': labels2, 'data2': data2, 'labels3': labels3, 'data3': data3,
            'labels4': labels4, 'data4': data4, 'labels5': labels5, 'data5': data5, 'labels6': labels6, 'data6': data6,
            'labels7': labels7, 'data7': data7, 'labels8': labels8, 'data8': data8, 'labels9': labels9, 'data9': data9,
            'labels10': labels10, 'data10': data10, 'labels11': labels11, 'data11': data11, 'nomebase': nomebase
        }

        # informações para montagem dos números informativos
        quantidade_cadastro = {}
        # agenda_hoje = {}
        # alertas = {}

        data_atual = datetime.now().date()
        context['data_atual'] = data_atual.strftime('%d/%m/%Y')
        context['exercicio'] = exercicio

        quantidade_cadastro['pessoasfisicas'] = PessoaFisica.objects.filter(Q(is_deleted=False) &
                                                                            Q(data_criacao__year=exercicio)).count()
            # PessoaFisica.objects.filter(is_deleted=False).count()

        quantidade_cadastro['pessoasjuridicas'] = PessoaJuridica.objects.filter(Q(is_deleted=False) &
                                                                                Q(data_criacao__year=exercicio)).count()
            # PessoaJuridica.objects.filter(is_deleted=False).count()

        quantidade_cadastro['processos'] = Processo.objects.filter(Q(is_deleted=False) & ~Q(status='C')
                                                                   & Q(dtprocesso__year=exercicio)).count()
            # is_deleted=False, status__in=['A', 'F', 'P'], dtprocesso__year=exercicio).count()

        quantidade_cadastro['processos_em_andamento'] = Processo.objects.filter(Q(is_deleted=False)
                                                                                & Q(status__in=['P', 'A', 'R', '1', '2'])
                                                                                & Q(dtprocesso__year=exercicio)).count()
            # Q(is_deleted=False) & Q(status='A') & Q(dtprocesso__year=exercicio)).count()

        quantidade_cadastro['titulos'] = Financeiro.objects.filter(Q(is_deleted=False) & ~Q(status='C')
                                                                   & Q(data_criacao__year=exercicio)).count()
            # Q(is_deleted=False) & Q(data_criacao__year=exercicio) & ~Q(status='C')).count()

        context['quantidade_cadastro'] = quantidade_cadastro

        datalimite = datetime.today() - timedelta(tmpconclusao)
        qsprocessospendentes = Processo.objects.filter(Q(is_deleted=False) & ~Q(status='F') & ~Q(status='N')
                                                       & ~Q(status='C') & Q(dtprocesso__lte=datalimite))
        processos_pendentes = ''
        for i in qsprocessospendentes:
            processos_pendentes = processos_pendentes + str(i.numprocesso) + ' | '
        context['processos_pendentes'] = processos_pendentes

        return render(request, self.template_name, context)


class AboutView(TemplateView):
    template_name = "about.html"


class RelatoriosView(TemplateView):
    template_name = "relatorios.html"
