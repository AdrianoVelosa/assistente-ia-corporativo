# app.py
# Aplicação web corporativa em Flask para assistente de IA privado
# Utiliza modelo LLaMA 3 8B quantizado via llama.cpp

import os
import subprocess
import tempfile
from flask import Flask, render_template, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import logging
import uuid

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Inicialização da aplicação Flask
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', str(uuid.uuid4()))

# Configurações do modelo LLaMA
LLAMA_PATH = os.environ.get('LLAMA_PATH', '/opt/llama.cpp')
MODEL_PATH = os.environ.get('MODEL_PATH', '/opt/llama.cpp/models/llama-3-8b-instruct.Q4_K_M.gguf')
CONTEXT_SIZE = os.environ.get('CONTEXT_SIZE', '4096')
TEMPERATURE = os.environ.get('TEMPERATURE', '0.7')

# Simulação de banco de dados de usuários (em produção, use um banco de dados real)
users_db = {
    'admin': {
        'password': generate_password_hash('admin123'),
        'role': 'admin'
    }
}

# Histórico de perguntas (em produção, use um banco de dados real)
query_history = []

# Função para executar o modelo LLaMA
def run_llama_model(prompt):
    try:
        # Criar arquivo temporário para o prompt
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
            temp_file.write(prompt)
            temp_file_path = temp_file.name
        
        # Comando para executar o modelo LLaMA
        cmd = [
            f"{LLAMA_PATH}/main",
            "-m", MODEL_PATH,
            "-c", CONTEXT_SIZE,
            "-t", TEMPERATURE,
            "-n", "1024",
            "--color", "0",
            "--temp", TEMPERATURE,
            "--repeat_penalty", "1.1",
            "--in-prefix", "[INST]",
            "--in-suffix", "[/INST]",
            "-f", temp_file_path
        ]
        
        # Executar o comando e capturar a saída
        logger.info(f"Executando comando: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Limpar o arquivo temporário
        os.unlink(temp_file_path)
        
        # Processar a saída
        output = result.stdout
        
        # Extrair apenas a resposta do modelo (após o prompt)
        response_parts = output.split('[/INST]')
        if len(response_parts) > 1:
            response = response_parts[1].strip()
        else:
            response = output.strip()
            
        return response
    
    except Exception as e:
        logger.error(f"Erro ao executar o modelo: {str(e)}")
        return f"Erro ao processar sua pergunta: {str(e)}"

# Rota principal
@app.route('/')
def index():
    if 'username' not in session:
        return render_template('login.html')
    return render_template('index.html')

# Rota de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in users_db and check_password_hash(users_db[username]['password'], password):
            session['username'] = username
            session['role'] = users_db[username]['role']
            logger.info(f"Usuário {username} logado com sucesso")
            return jsonify({'success': True, 'redirect': '/'})
        else:
            logger.warning(f"Tentativa de login falhou para o usuário {username}")
            return jsonify({'success': False, 'message': 'Usuário ou senha inválidos'})
    
    return render_template('login.html')

# Rota de logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return render_template('login.html')

# Rota para processar perguntas
@app.route('/ask', methods=['POST'])
def ask():
    if 'username' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    data = request.get_json()
    question = data.get('question', '')
    
    if not question:
        return jsonify({'error': 'Pergunta vazia'}), 400
    
    # Registrar a pergunta no histórico
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    query_record = {
        'user': session['username'],
        'question': question,
        'timestamp': timestamp
    }
    
    # Processar a pergunta com o modelo LLaMA
    response = run_llama_model(question)
    
    # Adicionar resposta ao registro
    query_record['response'] = response
    query_history.append(query_record)
    
    logger.info(f"Pergunta processada: {question[:50]}...")
    
    return jsonify({
        'response': response,
        'timestamp': timestamp
    })

# Rota para visualizar histórico (apenas para administradores)
@app.route('/history')
def history():
    if 'username' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Não autorizado'}), 401
    
    return render_template('history.html', history=query_history)

# Rota para administração (apenas para administradores)
@app.route('/admin')
def admin():
    if 'username' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Não autorizado'}), 401
    
    return render_template('admin.html')

# Rota para adicionar usuários (apenas para administradores)
@app.route('/admin/add_user', methods=['POST'])
def add_user():
    if 'username' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Não autorizado'}), 401
    
    data = request.get_json()
    new_username = data.get('username')
    new_password = data.get('password')
    new_role = data.get('role', 'user')
    
    if not new_username or not new_password:
        return jsonify({'error': 'Usuário e senha são obrigatórios'}), 400
    
    if new_username in users_db:
        return jsonify({'error': 'Usuário já existe'}), 400
    
    users_db[new_username] = {
        'password': generate_password_hash(new_password),
        'role': new_role
    }
    
    logger.info(f"Novo usuário adicionado: {new_username}")
    
    return jsonify({'success': True})

# Inicialização da aplicação
if __name__ == '__main__':
    # Em produção, use um servidor WSGI como Gunicorn
    app.run(host='0.0.0.0', port=5000, debug=False)