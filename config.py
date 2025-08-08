# config.py
# Configurações para a aplicação Assistente IA Corporativo

import os
import secrets
from datetime import timedelta

# Configurações básicas
class Config:
    # Segurança
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    
    # Configurações do modelo LLaMA
    LLAMA_PATH = os.environ.get('LLAMA_PATH', '/opt/llama.cpp')
    MODEL_PATH = os.environ.get('MODEL_PATH', '/opt/llama.cpp/models/llama-3-8b-instruct.Q4_K_M.gguf')
    CONTEXT_SIZE = os.environ.get('CONTEXT_SIZE', '4096')
    TEMPERATURE = os.environ.get('TEMPERATURE', '0.7')
    
    # Configurações de logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'app.log')
    
    # Configurações de upload (para futuras expansões)
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    
    # Configurações do banco de dados
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# Configurações de desenvolvimento
class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False

# Configurações de teste
class TestingConfig(Config):
    DEBUG = False
    TESTING = True
    WTF_CSRF_ENABLED = False

# Configurações de produção
class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    
    # Em produção, certifique-se de definir uma chave secreta forte
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Configurações adicionais de segurança para produção
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True

# Dicionário de configurações
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# Função para obter a configuração atual
def get_config():
    config_name = os.environ.get('FLASK_CONFIG', 'default')
    return config.get(config_name, config['default'])