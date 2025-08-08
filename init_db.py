# init_db.py
# Script para inicializar o banco de dados e executar migrações

import os
import sys
from flask_migrate import Migrate, init, migrate, upgrade
from app import app, db
from models import User, QueryHistory, Setting

def init_db():
    """Inicializa o banco de dados e cria as tabelas necessárias"""
    with app.app_context():
        # Inicializar o sistema de migrações se não existir
        if not os.path.exists(os.path.join('migrations', 'versions')):
            print("Inicializando sistema de migrações...")
            init(directory='migrations')
        
        # Criar migração inicial se não houver versões
        versions_dir = os.path.join('migrations', 'versions')
        if os.path.exists(versions_dir) and not os.listdir(versions_dir):
            print("Criando migração inicial...")
            migrate(directory='migrations', message='migração inicial')
        
        # Aplicar migrações pendentes
        print("Aplicando migrações...")
        upgrade(directory='migrations')
        
        # Verificar se existe um usuário admin, se não, criar um
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            print("Criando usuário admin padrão...")
            admin = User(username='admin', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            
            # Adicionar também um usuário comum
            user = User(username='user', role='user')
            user.set_password('user123')
            db.session.add(user)
            
            db.session.commit()
            print("Usuários padrão criados: admin e user")
        
        print("Banco de dados inicializado com sucesso!")

if __name__ == '__main__':
    init_db()