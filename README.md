# Microcrédito v2

[[_TOC_]]

Descrever o Microcrédito... (TODO)

## Executando o projeto localmente

Primeiramente, configure as variáveis de ambiente.

```
cp .env.example .env
```

### Diretamente pelo python

Na raiz do projeto execute.

```
python manage.py runserver 0.0.0.0:8000
```

### Usando Docker

Construa a imagem.

```
docker-compose build
```

Execute o projeto com o comando a seguir.

```
docker-compose up
```

### Acessando a aplicação

Depois que a aplicação estiver executando através de um dos métodos acima, acesse http://localhost:8000.

## Solução de problemas

### "Building wheel for pycairo (pyproject.toml) did not run successfully" no Docker com image baseada no Alpine Linux

**Problema:** Ao construir uma imagem Docker da aplicação, ocorreu o erro para compilar de dependência `pycairo` com a seguinte mensagem `Building wheel for pycairo (pyproject.toml) did not run successfully`. Isso se deve ao fato do sistema (imagem Docker) não possui as libs necessárias para compilar o `pycairo`.

**Solução:** O Dockerfile foi modificado para instalar as libs `build-base cairo-dev cairo cairo-tools` na imagem Docker. 

Fonte: https://phauer.com/2018/install-cairo-cairosvg-alpine-docker/

## Referências
- [Django and Docker, one "how to" make the things happen](https://medium.com/@gastonmaron/django-and-docker-one-how-to-make-the-things-happen-8413c671f4e1)
- [malaman/aiohttp-supervisord-nginx-docker](https://github.com/malaman/aiohttp-supervisord-nginx-docker)
- [Dockerizing a Python Django Web Application](https://semaphoreci.com/community/tutorials/dockerizing-a-python-django-web-application)
- http://supervisord.org/
- https://hub.docker.com/_/python/
# siamicroApp
