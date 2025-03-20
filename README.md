# Project-ChatBot-IA
Este projeto será disponibilizado de forma que todos desenvolvedores possam contribuir!

## Documentação

---

## Preparação da Aplicação

### Clonar Repositório
A primeira coisa a fazer é clonar o repositório caso queira testar a aplicação!

```bash
$ git clone https://github.com/anselmonhamage/Project-ChatBot-IA.git

$ cd Project-ChatBot-IA/
```

## Preparação do Ambiente de Desenvolvimento e Instalação de Dependências
Feito a clonagem, primeiro pricisamos preparar nosso ambiente virtual para evitar conflitos no momento de instalação das dependências.

Para tal vamos criar um ambiente virtual usando o virtualenv no python na raiz do projecto, então garanta que está na raiz:


### Criando e Ativando o Ambiente Virtual

```bash
$ python -m venv venv
```

### Activação do ambiente virtual venv

#### Shell do Linux
```bash
$ source venv/bin/activate
```

#### Prompt de Comando(CMD) Windowns
```bash
$ .\venv\Scripts\activate
```

### Dectivação do ambiente virtual venv
```bash
$ deactivate
```

## Instalação das Dependências do projecto

#### Shell do Linux
```bash
$ pip3 install -r requirements.txt
```

#### Prompt de Comando Windowns
```bash
$ pip install -r requirements.txt
```


## Ajustes e Configuração das API Key e Banco de Dados

### Criação de um arquivo .env

A criação de um __.env__ irá permitir que configure todas as informações sensiveis nas variáveis de ambiente.
Então, deixei a disposição um exemplo de como está estruturado no projecto real as variáveis de ambiente no arquivo, __.env.example__ .
Apenas será necessário copiar as informações de __.env.example__ para __.env__ .

```
Exemplo:
   API_KEY=some_key
   SECRET_KEY=some_secret_key
   FLASK_DEBUG=True
   FLASK_HOST=some_host
   FLASK_DEVELOPMENT_PORT=some_port
   MSSQL_SERVER=some_host_server
   MSSQL_DB=some_database
   MSSQL_DRIVER=some_driver
   TWILIO_ACCOUNT_SID=some_account_sid
   TWILIO_AUTH_TOKEN=some_auth_token
   TWILIO_WHATSAPP_NUMBER=twilio_number
   MY_WHATSAPP_NUMBER=some_your_number
```

### Configuração do Banco de Dados MS SQL Server

O banco de dados usado para o projecto, é o banco de dados MS SQL SERVER da Microsoft e dependendo do banco de dados a configuração será diferente.

#### Exemplo:

```
            server = os.environ.get("MSSQL_SERVER")
            database = os.environ.get("MSSQL_DB")
            driver = os.environ.get("MSSQL_DRIVER")

            SQLALCHEMY_DATABASE_URI = f'mssql+pyodbc://{server}/{database}?driver={driver}'
```

#### **NB:** O presente exemplo será modificado brevimente!


## Migrações das tabelas ORM do projecto para o Banco de Dados

Tendo já feito toda configuração e terminado, vamos agora fazer as migrações para o banco de dados:

#### Shell

```
    flask db init
    flask db migrate -m "initial migration."-> apenas a primeira vez, as proximas serão $ flask db migrate
    flask db upgrade
```


## Execução do Projecto

Chegou a tão esperada hora de executar o projecto!

#### Shell do Linux

```
    $ python3 run.py runserver
```

#### Prompt de Comando Windowns

```
    $ python run.py runserver
```

## Expôr o serviço na Internet, caso contrário pode testar com ngrok
### Fazer a instalação do ngrok, windows, tem para todas plataformas
[Acesse ao link](https://ngrok.com/docs/guides/device-gateway/windows/)

### Definir a porta para expôr um serviço pelo ngrok

```
    $ ngrok http <porta>
```

### Definir token de autenticação para o ngrok

```
    $ ngrok authtoken NGROK_AUTHTOKEN
```

### FIM
