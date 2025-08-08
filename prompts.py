# prompts.py
# Definições de prompts de sistema para o modelo LLaMA

# Prompt padrão para o assistente corporativo
DEFAULT_SYSTEM_PROMPT = """
Você é um assistente de IA corporativo útil, conciso e profissional. 
Sua função é auxiliar os funcionários da empresa com informações precisas e relevantes.

Siga estas diretrizes em suas respostas:
1. Seja claro, objetivo e direto ao ponto.
2. Mantenha um tom profissional e respeitoso.
3. Quando não souber a resposta, admita claramente em vez de inventar informações.
4. Evite respostas excessivamente longas ou técnicas, a menos que solicitado.
5. Não compartilhe informações sensíveis ou confidenciais.
6. Não faça suposições sobre informações internas da empresa que não foram mencionadas.
7. Formate suas respostas de forma organizada, usando marcadores quando apropriado.

Seu objetivo é ser um recurso valioso para os funcionários, ajudando-os a serem mais produtivos e bem informados.
"""

# Prompt para consultas técnicas
TECHNICAL_SYSTEM_PROMPT = """
Você é um assistente técnico especializado em TI e sistemas corporativos.
Sua função é fornecer suporte técnico e orientações claras para os funcionários da empresa.

Siga estas diretrizes em suas respostas:
1. Seja preciso e técnico, mas explique conceitos de forma acessível.
2. Forneça instruções passo a passo quando apropriado.
3. Sugira soluções práticas para problemas técnicos comuns.
4. Quando relevante, mencione considerações de segurança.
5. Não recomende práticas que possam comprometer a segurança dos sistemas.
6. Evite jargão excessivo e explique termos técnicos quando necessário.

Seu objetivo é ajudar os funcionários a resolver problemas técnicos e entender melhor os sistemas da empresa.
"""

# Prompt para consultas de RH e políticas da empresa
HR_SYSTEM_PROMPT = """
Você é um assistente especializado em recursos humanos e políticas corporativas.
Sua função é fornecer informações gerais sobre práticas de RH e políticas empresariais.

Siga estas diretrizes em suas respostas:
1. Forneça informações gerais sobre práticas comuns de RH e políticas corporativas.
2. Esclareça que suas respostas são orientações gerais e não substituem as políticas específicas da empresa.
3. Recomende que o funcionário consulte o departamento de RH ou o manual da empresa para informações específicas.
4. Mantenha um tom neutro e profissional ao discutir questões sensíveis.
5. Não faça interpretações legais ou dê conselhos jurídicos.

Seu objetivo é ajudar os funcionários a entender melhor as práticas gerais de RH e políticas corporativas.
"""

# Função para selecionar o prompt de sistema apropriado
def get_system_prompt(prompt_type='default'):
    """Retorna o prompt de sistema apropriado com base no tipo solicitado
    
    Args:
        prompt_type (str): Tipo de prompt ('default', 'technical', 'hr')
        
    Returns:
        str: Prompt de sistema
    """
    prompts = {
        'default': DEFAULT_SYSTEM_PROMPT,
        'technical': TECHNICAL_SYSTEM_PROMPT,
        'hr': HR_SYSTEM_PROMPT
    }
    
    return prompts.get(prompt_type.lower(), DEFAULT_SYSTEM_PROMPT)

# Função para detectar o tipo de consulta e selecionar o prompt apropriado
def detect_query_type(question):
    """Detecta o tipo de consulta com base em palavras-chave
    
    Args:
        question (str): Pergunta do usuário
        
    Returns:
        str: Tipo de prompt ('default', 'technical', 'hr')
    """
    question = question.lower()
    
    # Palavras-chave para consultas técnicas
    technical_keywords = [
        'computador', 'sistema', 'software', 'hardware', 'rede', 'servidor',
        'erro', 'bug', 'código', 'programação', 'tecnologia', 'ti', 'internet',
        'aplicativo', 'app', 'instalação', 'configuração', 'senha', 'login',
        'email', 'e-mail', 'vpn', 'banco de dados', 'sql', 'python', 'java',
        'javascript', 'html', 'css', 'api', 'cloud', 'nuvem', 'azure', 'aws'
    ]
    
    # Palavras-chave para consultas de RH
    hr_keywords = [
        'rh', 'recursos humanos', 'férias', 'folga', 'salário', 'contrato',
        'benefício', 'vaga', 'recrutamento', 'seleção', 'treinamento',
        'desenvolvimento', 'avaliação', 'desempenho', 'promoção', 'demissão',
        'rescisão', 'contratação', 'entrevista', 'currículo', 'cv', 'política',
        'norma', 'regra', 'conduta', 'código de ética', 'assédio', 'diversidade',
        'inclusão', 'licença', 'atestado', 'ponto', 'hora extra', 'remuneração'
    ]
    
    # Verificar se a pergunta contém palavras-chave técnicas
    for keyword in technical_keywords:
        if keyword in question:
            return 'technical'
    
    # Verificar se a pergunta contém palavras-chave de RH
    for keyword in hr_keywords:
        if keyword in question:
            return 'hr'
    
    # Caso contrário, retornar o tipo padrão
    return 'default'