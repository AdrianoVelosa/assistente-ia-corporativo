# Assistente IA Corporativo

Uma aplicação web corporativa em Flask que funciona como um assistente de IA privado, utilizando o modelo LLaMA 3 8B quantizado rodando localmente via llama.cpp.

## Características

- Interface web simples com campo de entrada e área de resposta
- Execução do modelo LLaMA 3 8B quantizado via llama.cpp
- Autenticação de usuários
- Histórico de perguntas
- Painel de administração
- Preparado para expansão com integração com SharePoint e File Server

## Requisitos do Sistema

- Ubuntu Server (recomendado 20.04 LTS ou superior)
- Python 3.8 ou superior
- llama.cpp compilado e instalado
- Modelo LLaMA 3 8B quantizado (formato GGUF)
- Pelo menos 8GB de RAM (16GB recomendado)
- Pelo menos 10GB de espaço em disco

## Instalação

### 1. Instalar dependências do sistema

```bash
sudo apt update
sudo apt install -y build-essential python3-dev python3-pip python3-venv git cmake
```

### 2. Clonar e compilar llama.cpp

```bash
git clone https://github.com/ggerganov/llama.cpp.git /opt/llama.cpp
cd /opt/llama.cpp
make
```

### 3. Baixar o modelo LLaMA 3 8B quantizado

```bash
mkdir -p /opt/llama.cpp/models
cd /opt/llama.cpp/models

# Baixar o modelo (exemplo usando wget)
wget https://huggingface.co/TheBloke/Llama-3-8B-Instruct-GGUF/resolve/main/llama-3-8b-instruct.Q4_K_M.gguf
```

### 4. Configurar a aplicação

```bash
# Clonar este repositório ou copiar os arquivos para o servidor
git clone https://github.com/AdrianoVelosa/assistente-ia-corporativo.git /opt/assistente-ia
cd /opt/assistente-ia

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente (opcional)
cat > .env << EOL
FLASK_APP=app.py
FLASK_ENV=production
FLASK_CONFIG=production
SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
LLAMA_PATH=/opt/llama.cpp
MODEL_PATH=/opt/llama.cpp/models/llama-3-8b-instruct.Q4_K_M.gguf
EOL
```

## Executando a Aplicação

### Modo de Desenvolvimento

```bash
cd /opt/assistente-ia
source venv/bin/activate
export FLASK_APP=app.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000
```

### Modo de Produção (com Gunicorn)

```bash
cd /opt/assistente-ia
source venv/bin/activate
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Configurar como Serviço Systemd

Crie um arquivo de serviço systemd para executar a aplicação como um serviço:

```bash
sudo nano /etc/systemd/system/assistente-ia.service
```

Adicione o seguinte conteúdo:

```ini
[Unit]
Description=Assistente IA Corporativo
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/assistente-ia
Environment="PATH=/opt/assistente-ia/venv/bin"
EnvironmentFile=/opt/assistente-ia/.env
ExecStart=/opt/assistente-ia/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Ative e inicie o serviço:

```bash
sudo systemctl daemon-reload
sudo systemctl enable assistente-ia
sudo systemctl start assistente-ia
```

## Acessando a Aplicação

Acesse a aplicação através do navegador:

```
http://[IP_DO_SERVIDOR]:5000
```

Credenciais padrão:
- Usuário: admin
- Senha: admin123

**IMPORTANTE:** Altere a senha padrão após o primeiro login!

## Estrutura do Projeto

```
/
├── app.py              # Aplicação principal Flask
├── config.py           # Configurações da aplicação
├── requirements.txt    # Dependências Python
├── static/             # Arquivos estáticos
│   ├── css/            # Folhas de estilo
│   │   └── style.css   # Estilo principal
│   └── js/             # JavaScript
│       └── main.js     # Script principal
└── templates/          # Templates HTML
    ├── admin.html      # Página de administração
    ├── base.html       # Template base
    ├── history.html    # Histórico de perguntas
    ├── index.html      # Página principal
    └── login.html      # Página de login
```

## Expansões Futuras

### Integração com SharePoint

Para integrar com o SharePoint, você precisará:

1. Instalar as dependências adicionais:
   ```bash
   pip install office365-rest-python-client msal
   ```

2. Configurar as credenciais do SharePoint no arquivo `.env`:
   ```
   SHAREPOINT_URL=https://seudominio.sharepoint.com
   SHAREPOINT_SITE=sites/seusite
   SHAREPOINT_CLIENT_ID=seu_client_id
   SHAREPOINT_CLIENT_SECRET=seu_client_secret
   ```

### Integração com File Server

Para integrar com File Server, você precisará:

1. Instalar as dependências adicionais:
   ```bash
   pip install pysmb
   ```

2. Configurar as credenciais do File Server no arquivo `.env`:
   ```
   FILESERVER_HOST=seu_servidor
   FILESERVER_SHARE=nome_do_compartilhamento
   FILESERVER_USER=usuario
   FILESERVER_PASSWORD=senha
   ```

## Segurança

- A aplicação utiliza autenticação básica de usuário/senha
- As senhas são armazenadas com hash seguro
- Sessões são gerenciadas com cookies seguros
- Em produção, recomenda-se usar HTTPS com certificado SSL/TLS

## Suporte

Para suporte, entre em contato com a equipe de TI.

## Licença

Este projeto é proprietário e de uso interno da empresa.