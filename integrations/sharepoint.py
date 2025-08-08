# integrations/sharepoint.py
# Módulo para integração com SharePoint

import os
import logging
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File

logger = logging.getLogger(__name__)

class SharePointIntegration:
    """Classe para integração com SharePoint Online"""
    
    def __init__(self):
        """Inicializa a integração com SharePoint usando variáveis de ambiente"""
        self.sharepoint_url = os.environ.get('SHAREPOINT_URL')
        self.site_url = os.environ.get('SHAREPOINT_SITE')
        self.client_id = os.environ.get('SHAREPOINT_CLIENT_ID')
        self.client_secret = os.environ.get('SHAREPOINT_CLIENT_SECRET')
        
        if not all([self.sharepoint_url, self.site_url, self.client_id, self.client_secret]):
            logger.warning("Configurações de SharePoint incompletas. A integração não estará disponível.")
            self.is_configured = False
        else:
            self.is_configured = True
            self._init_context()
    
    def _init_context(self):
        """Inicializa o contexto de autenticação do SharePoint"""
        if not self.is_configured:
            return None
        
        try:
            # Criar contexto de autenticação
            auth_context = AuthenticationContext(self.sharepoint_url)
            auth_context.acquire_token_for_app(self.client_id, self.client_secret)
            
            # Criar contexto do cliente
            self.ctx = ClientContext(self.site_url, auth_context)
            logger.info("Conexão com SharePoint estabelecida com sucesso")
            return self.ctx
        except Exception as e:
            logger.error(f"Erro ao inicializar contexto do SharePoint: {str(e)}")
            self.is_configured = False
            return None
    
    def search_documents(self, query, max_results=10):
        """Pesquisa documentos no SharePoint
        
        Args:
            query (str): Termo de pesquisa
            max_results (int): Número máximo de resultados
            
        Returns:
            list: Lista de documentos encontrados
        """
        if not self.is_configured:
            logger.warning("Integração com SharePoint não configurada")
            return []
        
        try:
            search_results = self.ctx.search.query(query_text=query).execute_query()
            
            results = []
            for result in search_results.value[:max_results]:
                results.append({
                    'title': result.Title,
                    'url': result.Url,
                    'author': result.Author,
                    'last_modified': result.LastModifiedTime,
                    'summary': result.HitHighlightedSummary
                })
            
            return results
        except Exception as e:
            logger.error(f"Erro ao pesquisar documentos no SharePoint: {str(e)}")
            return []
    
    def get_document_content(self, file_url):
        """Obtém o conteúdo de um documento do SharePoint
        
        Args:
            file_url (str): URL do arquivo
            
        Returns:
            str: Conteúdo do documento
        """
        if not self.is_configured:
            logger.warning("Integração com SharePoint não configurada")
            return ""
        
        try:
            # Obter o arquivo
            file = File.from_url(file_url).get().execute_query()
            
            # Ler o conteúdo do arquivo
            response = File.open_binary(self.ctx, file.serverRelativeUrl)
            
            # Retornar o conteúdo como texto
            return response.content.decode('utf-8')
        except Exception as e:
            logger.error(f"Erro ao obter conteúdo do documento: {str(e)}")
            return ""
    
    def get_recent_documents(self, library_name, max_results=10):
        """Obtém documentos recentes de uma biblioteca
        
        Args:
            library_name (str): Nome da biblioteca de documentos
            max_results (int): Número máximo de resultados
            
        Returns:
            list: Lista de documentos recentes
        """
        if not self.is_configured:
            logger.warning("Integração com SharePoint não configurada")
            return []
        
        try:
            # Obter a biblioteca de documentos
            library = self.ctx.web.lists.get_by_title(library_name)
            
            # Consultar os itens mais recentes
            items = library.items.top(max_results).order_by('Modified', ascending=False).get().execute_query()
            
            results = []
            for item in items:
                results.append({
                    'id': item.id,
                    'title': item.properties.get('Title', ''),
                    'url': item.properties.get('FileRef', ''),
                    'modified': item.properties.get('Modified', ''),
                    'created': item.properties.get('Created', ''),
                    'author': item.properties.get('Author', {}).get('Title', '')
                })
            
            return results
        except Exception as e:
            logger.error(f"Erro ao obter documentos recentes: {str(e)}")
            return []

# Exemplo de uso
def get_sharepoint_integration():
    """Função de fábrica para obter uma instância da integração com SharePoint"""
    return SharePointIntegration()