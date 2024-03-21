# Travellers API

Este projeto é o backend para o projeto travellers.app.br

## Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- [Python v3.12](https://www.python.org/downloads/)
- [Docker 25.0.1](https://www.docker.com/get-started/)
- [Docker Compose v2.24.2](https://docs.docker.com/compose/install/)
- [Direnv 2.21.2](https://direnv.net/docs/installation.html)

## Variáveis de ambiente

Para a gestão das variaveis de ambiente, vamos usar o Direnv.
Devemos ter um arquivo no raiz do projeto chamado `.envrc`

```bash
export ENVIRONMENT="local"
export DB_USER="traveleradmin"
export DB_PASSWORD="password"
export DB_NAME="travelerdb"

export JWT_SECRET_KEY="jwt_secret_key"
export APP_SECRET_KEY="app_secret_key"
export SQLALCHEMY_DATABASE_URI="postgresql://${DB_USER}:${DB_PASSWORD}@localhost/${DB_NAME}"
export UPLOAD_BUCKET="prd-uploads-bucket"
export UPLOAD_FOLDER="uploads"

export IUGU_API_TOKEN="IUGU_TOKEN"

export AWS_ACCESS_KEY_ID="aws_access_key"
export AWS_SECRET_ACCESS_KEY="aws_secret_access_key"
export AWS_DEFAULT_REGION=sa-east-1

```

## Local database up

Estamos usando docker-compose para subir o banco de dados local, é importante
que as variavies de ambiente tenham sido carregadas com o usdo o Direnv.

No raiz do projeto execute:

```
docker compose up
```

## Configuração do ambiente virtual python (venv)

Você precisa instalar o venv e instalar a dependencias de desenvolvimento:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Executando o ambiente local

Com o database rodando, você pode rodar o projeto com:

```bash
source venv/bin/activate
pip install -r requirements.txt
flask run
```

## Validando se o ambiente local esta rodando

Ao subir o ambiente é criado um usuário padrão: `admin@localhost` com a senha `admin@2024`

Então teste se localmente o sistema esta fucional com essas duas chamadas:

Login:

```bash
curl --location 'http://localhost:5000/api/admin/login' \
--header 'Content-Type: application/json' \
--data-raw '{
    "username": "admin@localhost",
    "password": "admin@2024"
}'
```

Listar Roteiros:

```bash
curl --location 'http://localhost:5000/api/admin/itinerary' \
--header 'Authorization: Bearer ACCESS_TOKEN_RETORNADO_NO_LOGIN'
```

## Collections Postman

- [Travellers API - Postman Collecton](./postman/Travelers%20-%20API.postman_collection.json)
- [travellers-local - Environment](./postman/travelers-local.postman_environment.json)

## Subindo Debbug no VsCode

Adicione o arquvo ./.vscode/launch.json no raiz do projeto e pressione F5

```json
{
  // Use IntelliSense to learn about possible attributes.
  // Hover to view descriptions of existing attributes.
  // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Flask",
      "type": "debugpy",
      "request": "launch",
      "module": "flask",
      "env": {
        "FLASK_APP": "app.py",
        "FLASK_DEBUG": "1"
      },
      "args": ["run", "--no-debugger", "--no-reload"],
      "jinja": true,
      "justMyCode": true
    }
  ]
}
```

## Configurando o python interpreter no VsCode

```vscode
Ctrl+P -> Python: Select Interpreter -> Python 3.X ('.venv': venv)
```

## Contribuições

Pull requests são bem-vindos.

Por favor observe tanto quanto possivel a conveção de commits [Conventional Commits](https://www.conventionalcommits.org/pt-br/v1.0.0/)
