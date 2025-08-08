#!/bin/bash
# Script de instalação para o Assistente IA Corporativo

set -e

echo "=== Instalação do Assistente IA Corporativo ==="
echo "Este script irá instalar todas as dependências necessárias e configurar a aplicação."
echo

# Verificar se está rodando como root
if [ "$(id -u)" -ne 0 ]; then
    echo "Este script deve ser executado como root ou com sudo."
    exit 1
 fi

# Definir diretório de instalação
INSTALL_DIR="/opt/assistente-ia"
LLAMA_DIR="/opt/llama.cpp"
MODEL_DIR="$LLAMA_DIR/models"

echo "=== Atualizando o sistema ==="
apt update
apt upgrade -y

echo "=== Instalando dependências do sistema ==="
apt install -y build-essential python3-dev python3-pip python3-venv git cmake wget

echo "=== Clonando e compilando llama.cpp ==="
if [ -d "$LLAMA_DIR" ]; then
    echo "Diretório llama.cpp já existe. Atualizando..."
    cd "$LLAMA_DIR"
    git pull
else
    echo "Clonando llama.cpp..."
    git clone https://github.com/ggerganov/llama.cpp.git "$LLAMA_DIR"
    cd "$LLAMA_DIR"
fi

echo "Compilando llama.cpp..."
make clean
make -j$(nproc)

echo "=== Baixando o modelo LLaMA 3 8B quantizado ==="
mkdir -p "$MODEL_DIR"
cd "$MODEL_DIR"

MODEL_FILE="llama-3-8b-instruct.Q4_K_M.gguf"
MODEL_URL="https://huggingface.co/TheBloke/Llama-3-8B-Instruct-GGUF/resolve/main/$MODEL_FILE"

if [ -f "$MODEL_FILE" ]; then
    echo "Modelo já existe. Pulando download..."
else
    echo "Baixando modelo $MODEL_FILE..."
    wget -O "$MODEL_FILE" "$MODEL_URL"
fi

echo "=== Configurando a aplicação ==="
mkdir -p "$INSTALL_DIR"

# Copiar arquivos da aplicação
echo "Copiando arquivos da aplicação..."
cp -r . "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Criar ambiente virtual
echo "Criando ambiente virtual Python..."
python3 -m venv venv
source venv/bin/activate

# Instalar dependências Python
echo "Instalando dependências Python..."
pip install --upgrade pip
pip install -r requirements.txt

# Criar arquivo .env
echo "Criando arquivo de configuração .env..."
SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')

cat > .env << EOL
FLASK_APP=app.py
FLASK_ENV=production
FLASK_CONFIG=production
SECRET_KEY=$SECRET_KEY
LLAMA_PATH=$LLAMA_DIR
MODEL_PATH=$MODEL_DIR/$MODEL_FILE
EOL

# Criar serviço systemd
echo "Criando serviço systemd..."
cat > /etc/systemd/system/assistente-ia.service << EOL
[Unit]
Description=Assistente IA Corporativo
After=network.target

[Service]
User=www-data
WorkingDirectory=$INSTALL_DIR
Environment="PATH=$INSTALL_DIR/venv/bin"
EnvironmentFile=$INSTALL_DIR/.env
ExecStart=$INSTALL_DIR/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
EOL

# Configurar permissões
echo "Configurando permissões..."
chown -R www-data:www-data "$INSTALL_DIR"
chmod -R 755 "$INSTALL_DIR"

# Habilitar e iniciar o serviço
echo "Habilitando e iniciando o serviço..."
systemctl daemon-reload
systemctl enable assistente-ia
systemctl start assistente-ia

echo
echo "=== Instalação concluída! ==="
echo "O Assistente IA Corporativo está instalado e rodando em http://$(hostname -I | awk '{print $1}'):5000"
echo "Credenciais padrão:"
echo "  Usuário: admin"
echo "  Senha: admin123"
echo
echo "IMPORTANTE: Altere a senha padrão após o primeiro login!"
echo