# app.py
# Aplicação web corporativa em Flask para assistente de IA privado
# Utiliza modelo LLaMA 3 8B quantizado via llama.cpp

import os
import sys
import subprocess
import tempfile
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import logging
import uuid
from flask_migrate import Migrate
from models import db, User, QueryHistory, Setting
from config import get_config

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('assistente-ia')

# Inicialização da aplicação Flask
app = Flask(__name__)
app.config.from_object(get_config())
app.secret_key = os.environ.get('SECRET_KEY', str(uuid.uuid4()))

# Inicializar o banco de dados
db.init_app(app)
migrate = Migrate(app, db)

# Criar as tabelas do banco de dados se não existirem
with app.app_context():
    db.create_all()
    
    # Verificar se existe um usuário admin, se não, criar um
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Adicionar também um usuário comum
        user = User(username='user', role='user')
        user.set_password('user123')
        db.session.add(user)
        
        db.session.commit()
        logger.info("Usuários padrão criados: admin e user")

# Configurações do modelo LLaMA
LLAMA_PATH = os.environ.get('LLAMA_PATH', '/opt/llama.cpp')
MODEL_PATH = os.environ.get('MODEL_PATH', '/opt/llama.cpp/models/llama-3-8b-instruct.Q4_K_M.gguf')
CONTEXT_SIZE = os.environ.get('CONTEXT_SIZE', '4096')
TEMPERATURE = os.environ.get('TEMPERATURE', '0.7')

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
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['username'] = username
            session['role'] = user.role
            session['user_id'] = user.id
            
            # Atualizar último login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
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
    session.pop('user_id', None)
    return render_template('login.html')

# Rota para processar perguntas
@app.route('/ask', methods=['POST'])
def ask():
    if 'username' not in session or 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    data = request.get_json()
    question = data.get('question', '')
    
    if not question:
        return jsonify({'error': 'Pergunta vazia'}), 400
    
    # Processar a pergunta com o modelo LLaMA
    response = run_llama_model(question)
    
    # Registrar a pergunta no histórico
    query_record = QueryHistory(
        user_id=session['user_id'],
        question=question,
        response=response
    )
    db.session.add(query_record)
    db.session.commit()
    
    logger.info(f"Pergunta processada: {question[:50]}...")
    
    return jsonify({
        'response': response,
        'timestamp': query_record.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    })

# Rota para visualizar histórico (apenas para administradores)
@app.route('/history')
def history():
    if 'username' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Não autorizado'}), 401
    
    # Buscar histórico de perguntas do banco de dados
    history_records = QueryHistory.query.order_by(QueryHistory.timestamp.desc()).all()
    history_list = []
    
    for record in history_records:
        user = User.query.get(record.user_id)
        history_list.append({
            'user': user.username if user else 'Usuário desconhecido',
            'question': record.question,
            'response': record.response,
            'timestamp': record.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        })
    
    return render_template('history.html', history=history_list)

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
    new_email = data.get('email')
    new_full_name = data.get('full_name')
    new_department = data.get('department')
    
    if not new_username or not new_password:
        return jsonify({'error': 'Usuário e senha são obrigatórios'}), 400
    
    # Verificar se o usuário já existe
    if User.query.filter_by(username=new_username).first():
        return jsonify({'error': 'Usuário já existe'}), 400
    
    # Criar novo usuário
    new_user = User(
        username=new_username,
        role=new_role,
        email=new_email,
        full_name=new_full_name,
        department=new_department
    )
    new_user.set_password(new_password)
    
    # Salvar no banco de dados
    db.session.add(new_user)
    db.session.commit()
    
    logger.info(f"Novo usuário adicionado: {new_username}")
    
    return jsonify({'success': True})

# Inicialização da aplicação
if __name__ == '__main__':
    # Em produção, use um servidor WSGI como Gunicorn
    app.run(host='0.0.0.0', port=5000, debug=False)