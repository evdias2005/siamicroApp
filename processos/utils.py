import requests

from django.http import JsonResponse
from django.shortcuts import render
from .models import Bairro  # Certifique-se de que o modelo está importado corretamente
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from num2words import num2words
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="download.pdf"'        # jogar direto para download
    pdf_status = pisa.CreatePDF(html, dest=response)
    if pdf_status.err:
        return HttpResponse('Alguns erros foram encontrados. Contacte o Setor de Desenvolvimento <pre>' + html + '</pre>')
    return response

def valor_por_extenso(number_p):
    """
    Converte um valor monetário para extenso.
    Ex: 123,45 -> "cento e vinte e três reais e quarenta e cinco centavos"
    """
    try:
        integer_part, decimal_part = map(int, number_p.replace('.', '').split(','))
    except ValueError:
        integer_part, decimal_part = int(number_p.replace('.', '')), 0

    aux1 = ' real' if integer_part == 1 else ' reais'
    aux2 = ' centavo' if decimal_part == 1 else ' centavos'

    text1 = num2words(integer_part, lang='pt_BR') + aux1 if integer_part else ''
    text2 = num2words(decimal_part, lang='pt_BR') + aux2 if decimal_part else ''

    return f"{text1} e {text2}".strip(' e ')

def numero_para_ordinal(numero):
    """
    Converte um número inteiro em seu ordinal por extenso em português.
    Exemplo: 1 -> 'primeiro', 2 -> 'segundo', 21 -> 'vigésimo primeiro'
    """
    unidades = [
        "", "primeira", "segunda", "terceira", "quarta", "quinta",
        "sexta", "sétima", "oitava", "nona"
    ]
    dezenas = [
        "", "", "vigésima", "trigésima", "quadragésima", "quinquagésima",
        "sexagésima", "septuagésima", "octogésima", "nonagésima"
    ]
    centenas = [
        "", "centésima", "ducentésima", "trecentésima", "quadringentésima",
        "quingentésima", "sexcentésima", "septingentésima",
        "octingentésima", "nongentésima"
    ]

    if numero <= 0 or numero > 999:
        return "Número fora do alcance suportado (1-999)."

    partes = []

    # Extrai a centena
    centena = numero // 100
    if centena > 0:
        partes.append(centenas[centena])
    numero %= 100

    # Extrai a dezena
    dezena = numero // 10
    if dezena > 0:
        partes.append(dezenas[dezena])
    numero %= 10

    # Extrai a unidade
    if numero > 0:
        partes.append(unidades[numero])

    return " ".join(partes)

def showmessages_error(form):
    """
    Formata as mensagens de erro de um formulário para exibição amigável.
    """
    error_messages = []

    for field, errors in form.errors.items():
        if field == '__all__':
            # Trata erros gerais do formulário
            error_messages.extend(errors)  # Adiciona diretamente as mensagens gerais
        else:
            # Obtém o rótulo do campo ou usa o nome do campo caso não tenha rótulo
            field_label = form.fields[field].label or field
            for error in errors:
                error_messages.append(f"{field_label}: {error}")

    return " | ".join(error_messages)

def consultar_cnpj(request):
    cnpj = request.GET.get('cnpj')  # Captura o CNPJ enviado via GET
    if not cnpj:
        return error_response('CNPJ não informado', 400)

    data, status_code = fetch_cnpj_data(cnpj)
    if status_code == 200:
        if 'erro' not in data:
            return JsonResponse(data)  # Retorna os dados JSON diretamente
        return error_response('CNPJ não encontrado', 404)

    return error_response('Erro ao consultar o CNPJ.ws', 500)

def fetch_cnpj_data(cnpj):
    """Faz a requisição à API do CNPJ.ws e retorna os dados e o status HTTP."""
    url = f'https://publica.cnpj.ws/cnpj/{cnpj}'
    try:
        response = requests.get(url)
        return response.json(), response.status_code
    except requests.RequestException:
        return {'error': 'Falha na conexão com a API'}, 500

def error_response(message, status_code):
    """Gera uma resposta JSON para erros."""
    return JsonResponse({'error': message}, status=status_code)

def load_bairros(request):
    """Carrega os bairros com base na cidade informada."""
    cidade_id = get_integer_from_request(request, 'cidade')
    bairros = Bairro.objects.filter(cidade_id=cidade_id).order_by('nome') if cidade_id else Bairro.objects.none()
    context = {'bairros': bairros}
    return render(request, 'pessoasfisicas/bairro_dropdown_list_options.html', context)

def get_integer_from_request(request, param_name):
    """Converte um parâmetro GET para inteiro, retornando None se inválido."""
    try:
        value = request.GET.get(param_name)
        return int(value) if value else None
    except (ValueError, TypeError):
        return None

def consultar_cep(request):
    """Consulta informações de um endereço com base no CEP."""
    cep = request.GET.get('cep')  # Captura o CEP enviado via GET
    if not cep:
        return error_response('CEP não informado', 400)

    data, status_code = fetch_cep_data(cep)
    if status_code == 200:
        if 'erro' not in data:
            return JsonResponse(data)
        return error_response('CEP não encontrado', 404)

    return error_response('Erro ao consultar o ViaCEP', 500)

def fetch_cep_data(cep):
    """Faz a requisição à API do ViaCEP e retorna os dados e o status HTTP."""
    url = f'https://viacep.com.br/ws/{cep}/json/'
    try:
        response = requests.get(url)
        return response.json(), response.status_code
    except requests.RequestException:
        return {'error': 'Falha na conexão com a API'}, 500

def error_response(message, status_code):
    """Função auxiliar para padronizar respostas de erro JSON."""
    return JsonResponse({"error": message, "latitude": None, "longitude": None, "level": "error"}, status=status_code)

def consultar_geolocalizacao(request):
    # O Javascript já envia o número junto com o logradouro
    logradouro_completo = request.GET.get('logradouro')
    bairro = request.GET.get('bairro')
    cidade = request.GET.get('cidade')

    # Validações básicas dos parâmetros recebidos
    if not logradouro_completo:
        # Mantém a validação do logradouro que agora inclui o número
        return error_response('Logradouro (com número) não informado', 400)
    if not bairro:
        return error_response('Bairro não informado', 400)
    if not cidade:
        return error_response('Cidade não informada', 400)

    # Inicializa o geolocator (idealmente, configure um user_agent único para sua aplicação)
    # Substitua "evdias2005@gmail.com" por um identificador da sua aplicação ou email de contato
    geolocator = Nominatim(user_agent="evdias2005@gmail.com")

    enderecos_para_tentar = [
        {"query": f"{logradouro_completo}, {bairro}, {cidade}, Brasil", "level": "exact"},
        {"query": f"{bairro}, {cidade}, Brasil", "level": "bairro"},
        {"query": f"{cidade}, Brasil", "level": "cidade"}
    ]

    location = None
    found_level = None

    for tentativa in enderecos_para_tentar:
        print(f"Tentando geolocalizar ({tentativa['level']}): {tentativa['query']}")
        try:
            location = geolocator.geocode(tentativa["query"], timeout=10)
            if location:
                found_level = tentativa["level"]
                print(f"Localização encontrada ({found_level}): Lat={location.latitude}, Lon={location.longitude}")
                break # Para o loop na primeira localização encontrada
            else:
                print(f"Não encontrado para: {tentativa['query']}")
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            print(f"Erro no geocoder ({tentativa['level']}): {e}")
            # Pode decidir continuar para a próxima tentativa ou retornar erro imediatamente
            # return error_response(f"Erro de serviço de geolocalização: {e}", 503)
            continue # Tenta o próximo nível de fallback
        except Exception as e:
            # Captura outros erros inesperados
            print(f"Erro inesperado durante geolocalização ({tentativa['level']}): {e}")
            return error_response(f"Erro interno inesperado: {e}", 500)

    if location and found_level:
        # Retorna JSON com latitude, longitude e o nível de precisão
        return JsonResponse({
            "latitude": location.latitude,
            "longitude": location.longitude,
            "level": found_level, # Indica se é 'exact', 'bairro' ou 'cidade'
            "error": None
        })
    else:
        print("Localização não encontrada após todas as tentativas.")
        # Retorna JSON com erro após tentar todos os fallbacks
        return error_response("Localização não encontrada para o endereço ou proximidades.", 404)

#
# from django.http import JsonResponse
# from geopy.geocoders import Nominatim
# from geopy.exc import GeocoderTimedOut, GeocoderServiceError
#
# def error_response(message, status_code):
#     """Função auxiliar para padronizar respostas de erro JSON."""
#     return JsonResponse({"error": message, "latitude": None, "longitude": None, "level": "error"}, status=status_code)
#
# def consultar_geolocalizacao(request):
#     logradouro_completo = request.GET.get("logradouro")
#     bairro = request.GET.get("bairro")
#     cidade = request.GET.get("cidade")
#
#     if not logradouro_completo:
#         return error_response("Logradouro (com número) não informado", 400)
#     if not bairro:
#         return error_response("Bairro não informado", 400)
#     if not cidade:
#         return error_response("Cidade não informada", 400)
#
#     geolocator = Nominatim(user_agent="sua_aplicacao_ou_email_contato_v2") # Use um user agent descritivo
#
#     enderecos_para_tentar = [
#         {"query": f"{logradouro_completo}, {bairro}, {cidade}, Brasil", "level": "exact"},
#         {"query": f"{bairro}, {cidade}, Brasil", "level": "bairro"},
#         {"query": f"{cidade}, Brasil", "level": "cidade"}
#     ]
#
#     location = None
#     found_level = None
#
#     for tentativa in enderecos_para_tentar:
#         print(f"Tentando geolocalizar ({tentativa['level']}): {tentativa['query']}")
#         try:
#             location = geolocator.geocode(tentativa["query"], timeout=10)
#             if location:
#                 found_level = tentativa["level"]
#                 print(f"Localização encontrada ({found_level}): Lat={location.latitude}, Lon={location.longitude}")
#                 break # Para o loop na primeira localização encontrada
#             else:
#                 print(f"Não encontrado para: {tentativa['query']}")
#         except (GeocoderTimedOut, GeocoderServiceError) as e:
#             print(f"Erro no geocoder ({tentativa['level']}): {e}")
#             # Pode decidir continuar para a próxima tentativa ou retornar erro imediatamente
#             # return error_response(f"Erro de serviço de geolocalização: {e}", 503)
#             continue # Tenta o próximo nível de fallback
#         except Exception as e:
#             # Captura outros erros inesperados
#             print(f"Erro inesperado durante geolocalização ({tentativa['level']}): {e}")
#             return error_response(f"Erro interno inesperado: {e}", 500)
#
#     if location and found_level:
#         # Retorna JSON com latitude, longitude e o nível de precisão
#         return JsonResponse({
#             "latitude": location.latitude,
#             "longitude": location.longitude,
#             "level": found_level, # Indica se é 'exact', 'bairro' ou 'cidade'
#             "error": None
#         })
#     else:
#         print("Localização não encontrada após todas as tentativas.")
#         # Retorna JSON com erro após tentar todos os fallbacks
#         return error_response("Localização não encontrada para o endereço ou proximidades.", 404)
#
# ```