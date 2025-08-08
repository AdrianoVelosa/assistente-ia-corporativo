# integrations/__init__.py
# Pacote para integrações externas

from importlib import import_module
import logging
import os

logger = logging.getLogger(__name__)

# Dicionário de integrações disponíveis
AVAILABLE_INTEGRATIONS = {
    'sharepoint': 'integrations.sharepoint',
    'fileserver': 'integrations.fileserver'
}

# Dicionário para armazenar instâncias de integrações
_integration_instances = {}

def get_integration(integration_name):
    """Obtém uma instância de integração pelo nome
    
    Args:
        integration_name (str): Nome da integração ('sharepoint' ou 'fileserver')
        
    Returns:
        object: Instância da integração ou None se não estiver disponível
    """
    # Verificar se a integração já foi instanciada
    if integration_name in _integration_instances:
        return _integration_instances[integration_name]
    
    # Verificar se a integração está disponível
    if integration_name not in AVAILABLE_INTEGRATIONS:
        logger.warning(f"Integração '{integration_name}' não está disponível")
        return None
    
    try:
        # Importar o módulo de integração
        module_path = AVAILABLE_INTEGRATIONS[integration_name]
        module = import_module(module_path)
        
        # Obter a função de fábrica
        factory_func_name = f"get_{integration_name}_integration"
        factory_func = getattr(module, factory_func_name)
        
        # Criar instância da integração
        instance = factory_func()
        
        # Armazenar a instância para uso futuro
        _integration_instances[integration_name] = instance
        
        return instance
    except ImportError as e:
        logger.error(f"Erro ao importar integração '{integration_name}': {str(e)}")
        return None
    except AttributeError as e:
        logger.error(f"Função de fábrica não encontrada para integração '{integration_name}': {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Erro ao inicializar integração '{integration_name}': {str(e)}")
        return None

def is_integration_enabled(integration_name):
    """Verifica se uma integração está habilitada nas configurações
    
    Args:
        integration_name (str): Nome da integração
        
    Returns:
        bool: True se a integração estiver habilitada, False caso contrário
    """
    env_var = f"{integration_name.upper()}_ENABLED"
    return os.environ.get(env_var, '').lower() in ('true', '1', 'yes', 'y')