# integrations/fileserver.py
# Módulo para integração com File Server via SMB/CIFS

import os
import logging
import tempfile
from smb.SMBConnection import SMBConnection
from datetime import datetime

logger = logging.getLogger(__name__)

class FileServerIntegration:
    """Classe para integração com File Server via SMB/CIFS"""
    
    def __init__(self):
        """Inicializa a integração com File Server usando variáveis de ambiente"""
        self.host = os.environ.get('FILESERVER_HOST')
        self.share = os.environ.get('FILESERVER_SHARE')
        self.username = os.environ.get('FILESERVER_USER')
        self.password = os.environ.get('FILESERVER_PASSWORD')
        self.domain = os.environ.get('FILESERVER_DOMAIN', '')
        self.client_name = os.environ.get('FILESERVER_CLIENT_NAME', 'AssistenteIA')
        self.server_name = os.environ.get('FILESERVER_SERVER_NAME', self.host)
        
        if not all([self.host, self.share, self.username, self.password]):
            logger.warning("Configurações de File Server incompletas. A integração não estará disponível.")
            self.is_configured = False
        else:
            self.is_configured = True
            self.conn = None
    
    def connect(self):
        """Estabelece conexão com o File Server
        
        Returns:
            bool: True se a conexão foi estabelecida com sucesso, False caso contrário
        """
        if not self.is_configured:
            logger.warning("Integração com File Server não configurada")
            return False
        
        try:
            # Criar conexão SMB
            self.conn = SMBConnection(
                self.username,
                self.password,
                self.client_name,
                self.server_name,
                domain=self.domain,
                use_ntlm_v2=True
            )
            
            # Conectar ao servidor
            connected = self.conn.connect(self.host, 139)  # Porta padrão SMB
            
            if connected:
                logger.info(f"Conexão estabelecida com o File Server {self.host}")
                return True
            else:
                logger.error(f"Falha ao conectar ao File Server {self.host}")
                return False
        except Exception as e:
            logger.error(f"Erro ao conectar ao File Server: {str(e)}")
            self.conn = None
            return False
    
    def disconnect(self):
        """Encerra a conexão com o File Server"""
        if self.conn:
            self.conn.close()
            self.conn = None
            logger.info("Conexão com File Server encerrada")
    
    def list_files(self, path="/", pattern="*"):
        """Lista arquivos em um diretório do File Server
        
        Args:
            path (str): Caminho relativo dentro do compartilhamento
            pattern (str): Padrão para filtrar arquivos
            
        Returns:
            list: Lista de arquivos encontrados
        """
        if not self.is_configured:
            logger.warning("Integração com File Server não configurada")
            return []
        
        if not self.conn and not self.connect():
            return []
        
        try:
            # Listar arquivos no diretório
            file_list = self.conn.listPath(self.share, path, pattern=pattern)
            
            results = []
            for item in file_list:
                # Ignorar entradas . e ..
                if item.filename in ['.', '..']:
                    continue
                
                # Formatar data de criação
                create_time = datetime.fromtimestamp(item.create_time)
                
                results.append({
                    'name': item.filename,
                    'path': os.path.join(path, item.filename).replace('\\', '/'),
                    'size': item.file_size,
                    'is_directory': item.isDirectory,
                    'created': create_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'attributes': {
                        'read_only': bool(item.file_attributes & 0x1),
                        'hidden': bool(item.file_attributes & 0x2),
                        'system': bool(item.file_attributes & 0x4),
                        'archive': bool(item.file_attributes & 0x20)
                    }
                })
            
            return results
        except Exception as e:
            logger.error(f"Erro ao listar arquivos no File Server: {str(e)}")
            return []
    
    def read_file(self, file_path):
        """Lê o conteúdo de um arquivo do File Server
        
        Args:
            file_path (str): Caminho relativo do arquivo dentro do compartilhamento
            
        Returns:
            str: Conteúdo do arquivo
        """
        if not self.is_configured:
            logger.warning("Integração com File Server não configurada")
            return ""
        
        if not self.conn and not self.connect():
            return ""
        
        try:
            # Criar arquivo temporário para armazenar o conteúdo
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Baixar o arquivo para o arquivo temporário
            with open(temp_path, 'wb') as file_obj:
                self.conn.retrieveFile(self.share, file_path, file_obj)
            
            # Ler o conteúdo do arquivo temporário
            with open(temp_path, 'r', encoding='utf-8', errors='ignore') as file_obj:
                content = file_obj.read()
            
            # Remover o arquivo temporário
            os.unlink(temp_path)
            
            return content
        except Exception as e:
            logger.error(f"Erro ao ler arquivo do File Server: {str(e)}")
            return ""
    
    def search_files(self, search_path="/", keyword="", max_depth=3):
        """Pesquisa arquivos no File Server que contenham uma palavra-chave no nome
        
        Args:
            search_path (str): Caminho base para a pesquisa
            keyword (str): Palavra-chave para pesquisar nos nomes dos arquivos
            max_depth (int): Profundidade máxima de diretórios para pesquisar
            
        Returns:
            list: Lista de arquivos encontrados
        """
        if not self.is_configured:
            logger.warning("Integração com File Server não configurada")
            return []
        
        if not self.conn and not self.connect():
            return []
        
        results = []
        
        def search_directory(path, current_depth=0):
            if current_depth > max_depth:
                return
            
            try:
                # Listar arquivos no diretório atual
                items = self.conn.listPath(self.share, path)
                
                for item in items:
                    # Ignorar entradas . e ..
                    if item.filename in ['.', '..']:
                        continue
                    
                    # Caminho completo do item
                    item_path = os.path.join(path, item.filename).replace('\\', '/')
                    
                    # Verificar se o nome do arquivo contém a palavra-chave
                    if keyword.lower() in item.filename.lower():
                        create_time = datetime.fromtimestamp(item.create_time)
                        
                        results.append({
                            'name': item.filename,
                            'path': item_path,
                            'size': item.file_size,
                            'is_directory': item.isDirectory,
                            'created': create_time.strftime('%Y-%m-%d %H:%M:%S')
                        })
                    
                    # Se for um diretório, pesquisar recursivamente
                    if item.isDirectory:
                        search_directory(item_path, current_depth + 1)
            except Exception as e:
                logger.error(f"Erro ao pesquisar em {path}: {str(e)}")
        
        # Iniciar pesquisa recursiva
        search_directory(search_path)
        
        return results

# Exemplo de uso
def get_fileserver_integration():
    """Função de fábrica para obter uma instância da integração com File Server"""
    return FileServerIntegration()