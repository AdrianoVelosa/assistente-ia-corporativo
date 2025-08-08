# utils.py
# Funções utilitárias para o Assistente IA Corporativo

import os
import re
import json
import logging
from datetime import datetime
from functools import wraps
from flask import session, redirect, url_for, request, jsonify

logger = logging.getLogger(__name__)

# Decorador para verificar autenticação
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            # Se for uma requisição AJAX, retornar erro 401
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': 'Não autorizado'}), 401
            # Caso contrário, redirecionar para a página de login
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Decorador para verificar se o usuário é administrador
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session or session.get('role') != 'admin':
            # Se for uma requisição AJAX, retornar erro 403
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': 'Acesso negado'}), 403
            # Caso contrário, redirecionar para a página principal
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Função para sanitizar entrada do usuário
def sanitize_input(text):
    """Sanitiza a entrada do usuário para evitar injeção de comandos
    
    Args:
        text (str): Texto a ser sanitizado
        
    Returns:
        str: Texto sanitizado
    """
    if not text:
        return ""
    
    # Remover caracteres potencialmente perigosos
    sanitized = re.sub(r'[;&|`$><]', '', text)
    
    # Limitar o tamanho da entrada
    max_length = 1000
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized

# Função para formatar o prompt para o modelo LLaMA
def format_prompt(question, system_prompt=None):
    """Formata o prompt para o modelo LLaMA
    
    Args:
        question (str): Pergunta do usuário
        system_prompt (str, optional): Prompt de sistema para contextualizar o modelo
        
    Returns:
        str: Prompt formatado
    """
    # Sanitizar a entrada
    question = sanitize_input(question)
    
    # Prompt de sistema padrão se não for fornecido
    if not system_prompt:
        system_prompt = (
            "Você é um assistente de IA corporativo útil e conciso. "
            "Responda às perguntas de forma profissional e objetiva, "
            "fornecendo informações precisas e relevantes para o ambiente corporativo."
        )
    
    # Formatar o prompt no formato esperado pelo LLaMA
    formatted_prompt = f"<s>[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\n{question} [/INST]\n"
    
    return formatted_prompt

# Função para registrar consultas no histórico
def log_query(username, question, response):
    """Registra uma consulta no histórico
    
    Args:
        username (str): Nome do usuário
        question (str): Pergunta do usuário
        response (str): Resposta do modelo
        
    Returns:
        dict: Registro da consulta
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    query_record = {
        'user': username,
        'question': question,
        'response': response,
        'timestamp': timestamp
    }
    
    # Em uma implementação real, isso seria salvo em um banco de dados
    # Aqui, apenas retornamos o registro
    
    return query_record

# Função para validar configurações do modelo
def validate_model_config(config):
    """Valida as configurações do modelo
    
    Args:
        config (dict): Configurações do modelo
        
    Returns:
        tuple: (bool, str) - (válido, mensagem de erro)
    """
    # Verificar se o caminho do modelo existe
    model_path = config.get('model_path')
    if not model_path or not os.path.exists(model_path):
        return False, f"Caminho do modelo inválido: {model_path}"
    
    # Verificar se o tamanho do contexto é válido
    context_size = config.get('context_size')
    try:
        context_size = int(context_size)
        if context_size < 512 or context_size > 8192:
            return False, f"Tamanho de contexto inválido: {context_size}. Deve estar entre 512 e 8192."
    except (ValueError, TypeError):
        return False, f"Tamanho de contexto inválido: {context_size}"
    
    # Verificar se a temperatura é válida
    temperature = config.get('temperature')
    try:
        temperature = float(temperature)
        if temperature < 0.0 or temperature > 2.0:
            return False, f"Temperatura inválida: {temperature}. Deve estar entre 0.0 e 2.0."
    except (ValueError, TypeError):
        return False, f"Temperatura inválida: {temperature}"
    
    return True, ""

# Função para processar a resposta do modelo
def process_model_response(response):
    """Processa a resposta do modelo para melhorar a formatação
    
    Args:
        response (str): Resposta bruta do modelo
        
    Returns:
        str: Resposta processada
    """
    if not response:
        return "Desculpe, não foi possível gerar uma resposta."
    
    # Remover o prompt da resposta (se presente)
    if '[/INST]' in response:
        response = response.split('[/INST]', 1)[1].strip()
    
    # Remover tokens de fim de sequência
    response = response.replace('<s>', '').replace('</s>', '').strip()
    
    # Limpar linhas em branco repetidas
    response = re.sub(r'\n{3,}', '\n\n', response)
    
    return response