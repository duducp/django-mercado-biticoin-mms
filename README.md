# Médias Móveis Simples

O objetivo do projeto é entregar variações de médias móveis simples,
de 20, 50 e 200 dias, das moedas Bitcoin e Etherium que são listadas no
Mercado Bitcoin via api Rest. Para isso temos que calcular diariamente a
média móvel simples das moedas sendo isso feito por workers desenvolvidos
utilizando o Celery.

Principais dependências:
- [Django](https://www.djangoproject.com/)
- [Django Ninja](https://django-ninja.rest-framework.com/) (async)
- [Celery](https://docs.celeryproject.org/en/stable/getting-started/introduction.html)

Compatibilidade:
- Python 3.10.0
- Django 3.2.9

## Índice
- [Sobre o projeto](#about)
  - [Api rest](#about_api)
  - [Beat](#about_beat)
  - [Worker](#about_worker)
- [Primeiros passos para executar o projeto localmente](#first_steps)
- [Modo de desenvolvimento](#development_mode)
- [Modo de produção](#deploying_prod)
- [Scripts de carga inicial no banco de dados](#initial_charge)
- [Docker](#docker)
- [Celery](#celery)
- [Testes](#tests)
- [Logs](#logs)
- [Correlation ID](#correlation_id)
- [Criando um novo aplicativo Django](#create_app)
- [Changelog e versionamento do código](#app_versioning)
  - [Changelog](#changelog)
  - [Versionamento](#versioning)
- [Migrate e migration](#migrate_migration)
- [Commits](#commits)

<a id="about"></a>
### Sobre o projeto
O projeto está dividido em três aplicações: api web rest, worker e beat.

<a id="about_api"></a>
#### Api Rest
A api rest é o ponto de entrada principal que expõe as rotas de acesso externo.

A rota principal da API é a de indicadores de média móvel simples. Ela é
responsável por filtrar as variações das médias no banco de dados.

Para evitar alto número de requisições ao banco de dados, essa rota tem um
cache com duração de 10 minutos.

```shell
curl --location --request GET 'http://localhost:8000/v1/indicators/BRLBTC/mms?range=20&from=1622469710&to=1622401310'
```

Os parâmetros que podem ser informados são:

|Parâmetro  |Local  |Tipo   |Obrigatório|Opções         |Descrição                                          |
|-----------|-------|-------|-----------|---------------|---------------------------------------------------|
|pair       |path   |texto  |Sim        |BRLBTC, BRLETH |Pair da moeda que deve ser pesquisado.             |
|range      |query  |número |Sim        |20, 50, 200    |Quantidade de dias da média móvel.                 |
|from       |query  |número |Sim        |               |Data inicial de pesquisa.                          |
|to         |query  |número |Não        |               |Data final de pesquisa. Padrão é o dia anterior.   |
|precision  |query  |texto  |Não        |1d             |Precisão da média móvel. Padrão é 1d.              |

Mais informações podem ser obtidos na documentação: http://localhost:8000/v1/docs

<a id="about_beat"></a>
#### Beat
O _beat_ é uma aplicação schedule, de tempos em tempos ele chama as tasks que
está programado. Essa configuração pode ser feita pelo Django Admin ou pelo
próprio settings do projeto.

Se acessar `src/project/core/settings/base.py` e procurar pela variável de ambiente
_CELERY_BEAT_SCHEDULE_ verá que existe uma configuração para ele. Essa
configuração diz que a task _task_beat_select_pairs_to_mms_ deve ser chamada
a cada uma hora. Com isso a cada uma hora o _beat_ irá publicar uma mensagem
na fila _indicator-mms-select-pairs_ e o _worker_ irá consumir essa mensagem
e começar a executar a task.

<a id="about_worker"></a>
#### Worker
O _worker_ é uma aplicação que consome uma ou mais filas e redireciona a mensagem
da fila para a _task_ responsável. Atualmente existem duas tasks no projeto:

- **task_beat_select_pairs_to_mms**

Essa task consome a fila _indicator-mms-select-pairs_ e é responsável
diariamente por distribuir os pairs das moedas para a task que calcula a média
móvel simples.

Para garantir que a task não será executada mais de uma vez no dia, existe um
cache lock com duração de 24 horas e caso a task já tenha sido executada no dia,
a executação atual é descartada. Se ocorrer erro na primeira execução do dia o
cache lock não é setado.

- **task_calculate_simple_moving_average**

Essa task consome a fila _indicator-mms-calculate_ e é responsável por calcular
a média móvel simples de cada pair que ela recebe.

A task recebe três parâmetros para execução:
- pair: pair da moeda;
- precision: precisão para cálculo da média móvel simples, por enquanto é somente 1 dia;
- datetime_started: data e hora que a mensagem foi colocada na fila da task;

Assim que a task começa a processar ela cria um cache lock para garantir que
outro worker não irá processar o mesmo pair que ela esta processando e esse
cache lock é removido assim que a task é finalizada.

Ela identifica os parâmetros para cálculo da média e faz uma request para a API
de Candles a fim de buscar os dados de fechamento do pair. Assim que recebe o
retorno da API ela começa a calcular a média móvel simples salvando os dados no
banco de dados.

Caso haja algum erro durante o processamento da task, é definido um retry de 30
minutos. Esse retry pode ocorrer inúmeras vezes ao dia e caso a data inicial de
processamento task for menor que a data de processamento atual da task o
processamento do pair é descartado.

<a id="first_steps"></a>
### Primeiros passos para executar o projeto localmente
1- Configure o ambiente virtual:
```shell script
python -m venv venv
```

2- Ative o ambiente virtual:
```shell script
source venv/bin/activate
```

3- Execute o comando para instalar as dependências:
```shell script
make dependencies
```

<a id="development_mode"></a>
### Modo de desenvolvimento
O modo de desenvolvimento por padrão utiliza o Postgres como banco de dados e
Redis para cache e filas do Celery.

1- Copie o arquivo _.env-sample_ e renomeie para _.env-development_.
Aproveite e faça os ajustes necessários nas variáveis de ambiente:
```shell script
cp .env-sample .env-development
```

2- Execute o comando para criar as tabelas no banco de dados:
```shell script
make migrate
```

Ao executar o comando acima será criados os containers docker com as dependências.

3- Para acessar o Django Admin é necessário criar o super usuário e isso pode
ser feito com o seguinte comando:
```shell script
make superuser
```

4- Agora basta executar o comando abaixo para iniciar o aplicativo.
O comando abaixo irá subir as dependências no docker e irá executar a aplicação no shell.
```shell script
make run
```

Você também pode executar a aplicação em um container docker. Consulte a seção [Docker](#docker).

Após executar os comandos acima, você poderá acessar a documentação e o painel administrativo:
```
http://localhost:8000/admin
http://localhost:8000/ping
http://localhost:8000/v1/docs
```

<a id="deploying_prod"></a>
### Modo de produção
O modo de produção utilizamos o servidor [gunicorn](https://gunicorn.org/)
junto com o servidor ASGI [uvicorn](https://www.uvicorn.org/).

Para implantar em produção, as seguintes variáveis de ambiente devem ser definidas na aplicação da api, worker e beat:
```shell script
export SIMPLE_SETTINGS=project.core.settings.production
export GUNICORN_WORKERS=1
export CELERY_WORKER_CONCURRENCY=1
export SECRET_KEY="your_key_here"
export DATABASE_URL="sqlite:///db.sqlite3"
export DATABASE_READ_URL="sqlite:///db.sqlite3"
export CELERY_BROKER_URL="redis://127.0.0.1:6379/1"
export REDIS_URL=redis://127.0.0.1:6379/0
export REDIS_URL_LOCK=redis://127.0.0.1:6379/0
```

Opcional:
```shell script
export ALLOWED_HOSTS="*;"
```

Se esta é a primeira vez que executa o aplicativo em um banco de dados de
produção, você deve aplicar a migração e criar o super usuário.

Como opcional você pode desativar o Django Admin setando a variável **ADMIN_ENABLED** como **false**. Caso queira
desativar a documentação você deve setar **docs_url** igual a **None** no NinjaAPI em **project.urls**.

Consulte o arquivo `core/settings/base.py` para ver todas as variáveis de ambiente disponíveis.

<a id="initial_charge"></a>
### Scripts de carga inicial no banco de dados
Se a primeira vez que o projeto está sendo executado normalmente queremos fazer
uma carga inicial no banco de dados.

Os scripts são configurados no [management](https://docs.djangoproject.com/pt-br/3.0/howto/custom-management-commands/)
do Django. Veja que no app `src/project/indicators/mms` existe o diretório
`management/commands` com o arquivo _mms_initial_charge.py_. Esse arquivo é o
script de carga inicial das variações de média móvel simples.

Se você for executar o script localmente, primeiramente deve-se iniciar as
dependências do projeto `make docker-dependencies-up`.

Para executar o script basta executar o comando abaixo:
```shell script
python src/manage.py mms_initial_charge --days=365
```

Ao executar o comando será publicado na fila _indicator-mms-calculate_
mensagens com data para cálculo da quantidade de dias informado no comando.
Com isso a task _task_calculate_simple_moving_average_ irá consumir as mensagens
e começar a calcular a média móvel do dia e pair recebido.

Para que a task começa a capturar as mensagens para executar o cálculo os workers
do Celery devem estar ligados. Se estiver executando o script localmente basta
rodar o comando `make docker-celery-up`.

<a id="docker"></a>
### Docker
Esta aplicação faz uso do Docker para facilitar durante o desenvolvimento.
Certifique-se de ter o docker instalado em seu dispositivo.

Veja os comandos disponíveis no Makefile:

|Comando                        |Descrição                                                      |
|-------------------------------|---------------------------------------------------------------|
|docker-up-all                  |Inicia todos os containers docker.                             |
|docker-down-all                |Remove todos os containers criados.                            |
|docker-restart-all             |Reinicia todos os containers criados.                          |
|docker-dependencies-up         |Cria os containers docker de dependências da aplicação.        |
|docker-dependencies-down       |Remove os containers de dependências da aplicação.             |
|docker-dependencies-downclear  |Remove os containers e os volumes de dependências da aplicação.|
|docker-app-up                  |Cria os containers docker da aplicação rest.                   |
|docker-app-down                |Remove os containers da aplicação rest.                        |
|docker-app-logs                |Visualiza os logs dos containers da aplicação rest.            |
|docker-app-migrate             |Aplicada as migrações no banco de dados.                       |
|docker-app-superuser           |Cria o super usuário para acesso ao admin.                     |
|docker-celery-run              |Cria os containers docker do Celery (_worker_ e _beat_).       |
|docker-celery-down             |Remove os containers do Celery (_worker_ e _beat_).            |
|docker-celery-logs             |Visualiza os logs dos containers do Celery (_worker_ e _beat_).|

<a id="celery"></a>
### Celery
Nesse projeto é possível criar tarefas (_tasks_) que podem ser executadas de
tempo em tempo ou quando solicitadas. Toda essa lógica é feita usando a
biblioteca [Celery] (https://docs.celeryproject.org/en/stable).

Seu funcionamento consiste em dois aplicativos, sendo o _worker_ e o _beat_:
- O [_beat_](#about_beat) é apenas uma aplicação que de vez em quando chama uma _task_ para ser
  executada, isso de acordo com a configuração definida em `core/settings/base.py`.
- O [_worker_](#about_worker) é o aplicativo que recebe a mensagem do _beat_ ou de algum comando
  interno do aplicativo e começa a processar a tarefa de acordo com o que está
  definido nele.

Dentro de cada aplicativo, configuramos um arquivo chamado _tasks.py_ e nesse
arquivo escrevemos o código da tarefa.

Na seção [Docker](#docker) você encontrará alguns comandos para criar os
containers docker do Celery.

<a id="tests"></a>
### Testes
Para a criação de testes unitários o projeto utiliza o [pytest](https://pytest.org/).

Dentro de cada _app_ que fica no diretório `src/project` existe uma pasta chamada _tests_.
Cada arquivo python de teste tem seu nome começado com **test_** e cada função
de teste começa com **test_**.

Existe alguns comandos para você rodar os testes:

|Comando                    |Descrição                                                                                                      |
|---------------------------|---------------------------------------------------------------------------------------------------------------|
|test                       |Irá rodar os testes unitários da aplicação.                                                                    |
|test-coverage              |Irá rodar os testes unitários e medir a cobertura do testes.                                                   |
|test-coverage-html-server  |Irá rodar os testes unitários, medir a cobertura, gerar uma página html estática e iniciará um servidor local .|

<a id="logs"></a>
### Logs
Os logs do aplicativo são mais poderosos e menos dolorosos com a ajuda de
**structlog** que é intermediado por `structlog`. Todos os logs feitos são
convertidos para JSON, facilitando assim a análise e busca.

Para utiliza-los basta seguir o código abaixo:
```python
import structlog
logger = structlog.get_logger()

logger.info("User logged in", user="test-user")
```

Todos os logs gerados utilizando o _structlog_ contém o Correlation-ID.
Para mais detalhes sobre [Correlation-ID](#correlation_id) acesse a seção.

<a id="correlation_id"></a>
### Correlation ID
Correlation ID é um código UUID que amarra todos os logs gerados pela aplicação,
facilitando assim a busca de logs gerados em uma requisição, por exemplo.
Este aplicativo faz uso do [django-cid](https://pypi.org/project/django-cid/)
para fazer a gestão dos Correlation ID.

Ele é injetado nos logs e retornado no cabeçalho de cada solicitação.
O usuário pode também enviá-lo no cabeçalho da solicitação (X-Correlation-ID)
ou se não for encontrado, o aplicativo irá gerar automaticamente.

<a id="create_app"></a>
### Criando um novo aplicativo Django dentro do projeto
Quando precisamos criar novas rotas ou novas tasks para a aplicação devemos
criar um novo app Django.

Todos os novos aplicativos são criados no diretório _src/project_ e para criar
um novo aplicativo, você deve executar o seguinte comando:
```shell script
make app name=clients
```

Observe que o parâmetro _name_ foi passado. Ele é usado para informar o nome
do novo aplicativo.

<a id="app_versioning"></a>
### Changelog e versionamento do código
Esse projeto está configurado para gerar um arquivo de _changelog_ toda vez que
haver a nescessidade de gerar uma nova versão do projeto.

<a id="changelog"></a>
#### Changelog
Uma boa prática é sempre criar um arquivo _changelog_ em cada tarefa
(pull/merge request) concluída a fim de manter um histórico da mudança.
Para isso temos alguns comandos:

|Comando                |Descrição                                              |
|-----------------------|-------------------------------------------------------|
|changelog-feature      |Significa um novo recurso.                             |
|changelog-improvement  |Significa que uma melhoria foi implementada no projeto.|
|changelog-bugfix       |Significa uma correção de um problema.                 |
|changelog-doc          |Significa uma melhoria na documentação.                |
|changelog-removal      |Significa uma suspensão ou remoção de uma rota de API. |

Cada um desses comandos espera o parâmetro **message**. Você pode usá-lo da seguinte forma:

```shell script
make changelog-feature message="Adds CRUD for clients management"
```

Para mais detalhes sobre a criação desses arquivos de changelog você pode ver
na [documentação](https://towncrier.readthedocs.io/en/actual-freaking-docs/)
da biblioteca _towncrier_.

<a id="versioning"></a>
#### Versionamento
Quando uma história termina, é hora de criar uma nova versão do projeto.
Todos os arquivos de _changelog_ existentes serão convertidos em uma única
mensagem que ficará disponível no arquivo _CHANGELOG.md_.

Existem três comandos que podemos usar para fechar uma versão. São eles:

|Comando        |Descrição                              |
|---------------|---------------------------------------|
|release-patch  |Cria uma versão de patch. Ex.: 0.0.1   |
|release-minor  |Cria uma versão de minor. Ex.: 0.1.0   |
|release-major  |Cria uma versão de major. Ex.: 1.0.0   |

Você pode usá-los da seguinte maneira:
```shell script
make release-patch
```

Depois de executar o comando específico, dois novos _commits_ serão criados, um
referindo-se à geração do arquivo _changelog_ e o outro referindo-se a geração
da nova versão do aplicativo. Além desses novos _commits_, uma tag específica
para a versão do aplicativo também é gerada.

Finalmente, você pode enviar todas as alterações para o seu repositório git
com o comando `make push`.

Para mais detalhes sobre o versionamento, você pode conferir a
[documentação](https://github.com/c4urself/bump2version)
oficial da biblioteca _bump2version_.

<a id="migrate_migration"></a>
### Migrate e migration
Se você acabou de configurar seu modelo (model), é hora de criar o esquema a
ser aplicado no banco de dados no futuro. Observe que em seu aplicativo há uma
pasta com o nome de **migrations**, é aqui que fica o esquema do seu _model_.
Para mais detalhes sobre esses comandos acesse a
[documentação](https://docs.djangoproject.com/en/3.2/topics/migrations/) oficial.

Para criar o esquema, precisamos executar o seguinte comando:
```shell script
make migration
```

Você também pode criar um layout em branco, que por sua vez não será relacionado
a nenhum modelo em primeiro momento:
```shell script
make migration-empty app=clients
```

Observe que o parâmetro _app_ foi informado. Ele é usado para informar em qual
aplicativo o _model_ deverá ser criado.

Agora precisamos aplicar este _model_ ao banco de dados e para isso executamos
o seguinte comando:
```shell script
make migrate
```

<a id="commits"></a>
### Commits
Ao criar o commit, é comum apenas falar o que foi feito ou o que está sendo feito, utilizando para isso verbos no
passado ou no gerúndio:
```
Fixed bug with Y
Changing behavior of X
Refatorou classe de autenticação
Atualizando biblioteca xpto
```

Escrever desse modo pode parecer mais natural na hora de compor a mensagem do commit, mas isso pode dificultar a leitura
do histórico de commits de um projeto.

Ao fazer commits em inglês, escreva o título no modo imperativo:
```
Refactor subsystem X for readability
Update getting started documentation
Remove deprecated methods
Release version 1.0.0
```

Isso vai de acordo com o padrão que o próprio Git segue quando gera uma mensagens de commit automaticamente em casos
como no `git merge`:
```
Merge branch 'myfeature'
```

Ou como no git revert:
```
Revert "Add the thing with the stuff"

This reverts commit cc87791524aedd593cff5a74532befe7ab69ce9d.
```

Uma dica ao fazer mensagens de commit em inglês, é que um bom título sempre deve completar a frase:
_if applied, this commit will_. Por exemplo:
```
if applied, this commit will refactor subsystem X for readability
if applied, this commit will update getting started documentation
if applied, this commit will remove deprecated methods
if applied, this commit will release version 1.0.0
```

Já quando for escrever a mensagem do commit em português conjugue o verbo no presente do indicativo, utilizando a terceira pessoa do singular:
```
Refatora sistema X para melhorar legibilidade
Atualiza documentação de instalação do projeto
Remove métodos obsoletos
```

O conteúdo acima foi retirado do site [Ruan Brandão](https://ruanbrandao.com.br/2020/02/04/como-fazer-um-bom-commit/).
