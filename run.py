#!/usr/bin/env python
# run.py
# Script para iniciar o Assistente IA Corporativo em modo de desenvolvimento

import os
import logging
from app import app
from config import DevelopmentConfig

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    # Verificar se o diretório de templates existe
    if not os.path.exists('templates'):
        logger.warning('Diretório de templates não encontrado. Criando...')
        os.makedirs('templates')
    
    # Verificar se o diretório de arquivos estáticos existe
    if not os.path.exists('static'):
        logger.warning('Diretório de arquivos estáticos não encontrado. Criando...')
        os.makedirs('static/css', exist_ok=True)
        os.makedirs('static/js', exist_ok=True)
    
    # Verificar se o arquivo .env existe
    if not os.path.exists('.env'):
        logger.warning('Arquivo .env não encontrado. Criando com valores padrão...')
        with open('.env', 'w') as f:
            f.write("# Configurações do Assistente IA Corporativo\n")
            f.write("FLASK_APP=app.py\n")
            f.write("FLASK_ENV=development\n")
            f.write("FLASK_DEBUG=1\n")
            f.write("SECRET_KEY=chave-secreta-de-desenvolvimento\n")
            f.write("# Configurações do modelo LLaMA\n")
            f.write("LLAMA_EXEC_PATH=/caminho/para/llama.cpp/main\n")
            f.write("LLAMA_MODEL_PATH=/caminho/para/modelo/llama-3-8b-instruct.Q4_K_M.gguf\n")
            f.write("LLAMA_CONTEXT_SIZE=4096\n")
            f.write("LLAMA_TEMPERATURE=0.7\n")
    
    # Iniciar a aplicação
    logger.info('Iniciando o Assistente IA Corporativo em modo de desenvolvimento')
    app.config.from_object(DevelopmentConfig)
    app.run(host='0.0.0.0', port=5000)