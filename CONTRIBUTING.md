# Guia de Contribuição - Assistente IA Corporativo

Obrigado pelo interesse em contribuir com o Assistente IA Corporativo! Este documento fornece diretrizes para contribuir com o projeto.

## Índice

1. [Código de Conduta](#código-de-conduta)
2. [Como Contribuir](#como-contribuir)
3. [Configuração do Ambiente de Desenvolvimento](#configuração-do-ambiente-de-desenvolvimento)
4. [Padrões de Código](#padrões-de-código)
5. [Processo de Pull Request](#processo-de-pull-request)
6. [Relatando Bugs](#relatando-bugs)
7. [Sugerindo Melhorias](#sugerindo-melhorias)

## Código de Conduta

Este projeto adota um Código de Conduta que esperamos que todos os participantes sigam. Por favor, leia o [Código de Conduta](CODE_OF_CONDUCT.md) para entender quais ações serão e não serão toleradas.

## Como Contribuir

Existem várias maneiras de contribuir com o Assistente IA Corporativo:

1. **Reportar bugs**: Se você encontrar um bug, por favor, reporte-o usando o sistema de issues.
2. **Sugerir melhorias**: Novas ideias são sempre bem-vindas.
3. **Melhorar a documentação**: Ajude a tornar a documentação mais clara e completa.
4. **Contribuir com código**: Implemente novos recursos ou corrija bugs existentes.

## Configuração do Ambiente de Desenvolvimento

Para configurar o ambiente de desenvolvimento:

1. Clone o repositório:
   ```bash
   git clone https://github.com/sua-empresa/assistente-ia.git
   cd assistente-ia
   ```

2. Crie e ative um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

3. Instale as dependências de desenvolvimento:
   ```bash
   pip install -r requirements-dev.txt
   ```

4. Configure o arquivo `.env` com base no `.env.example`:
   ```bash
   cp .env.example .env
   # Edite o arquivo .env com suas configurações
   ```

5. Compile o llama.cpp (se necessário para desenvolvimento):
   ```bash
   git clone https://github.com/ggerganov/llama.cpp.git
   cd llama.cpp
   make
   ```

6. Execute os testes para verificar se tudo está funcionando:
   ```bash
   python -m unittest discover
   ```

## Padrões de Código

### Estilo de Código

Seguimos o [PEP 8](https://www.python.org/dev/peps/pep-0008/) para código Python. Algumas diretrizes específicas:

- Use 4 espaços para indentação (não tabs)
- Limite as linhas a 79 caracteres para código e 72 para comentários
- Use docstrings no estilo Google para documentar funções e classes
- Use nomes descritivos para variáveis, funções e classes

### Documentação

- Mantenha a documentação atualizada quando fizer alterações
- Adicione docstrings a todas as funções, classes e métodos
- Atualize o README.md quando necessário

### Testes

- Adicione testes para novos recursos
- Certifique-se de que todos os testes passam antes de enviar um pull request
- Mantenha a cobertura de testes alta

## Processo de Pull Request

1. Crie um fork do repositório
2. Clone seu fork localmente
3. Crie um branch para suas alterações:
   ```bash
   git checkout -b feature/nome-da-feature
   ```
4. Faça suas alterações e commit:
   ```bash
   git commit -m "Descrição clara das alterações"
   ```
5. Envie seu branch para o GitHub:
   ```bash
   git push origin feature/nome-da-feature
   ```
6. Abra um Pull Request no GitHub

### Diretrizes para Pull Requests

- Descreva claramente o que suas alterações fazem
- Referencie quaisquer issues relacionadas
- Certifique-se de que todos os testes passam
- Siga os padrões de código do projeto
- Mantenha o PR focado em uma única alteração ou recurso

## Relatando Bugs

Ao relatar bugs, inclua:

- Descrição clara do bug
- Passos para reproduzir o problema
- Comportamento esperado vs. comportamento observado
- Capturas de tela, se aplicável
- Informações sobre o ambiente (sistema operacional, navegador, etc.)

## Sugerindo Melhorias

Ao sugerir melhorias:

- Descreva claramente o recurso ou melhoria
- Explique por que seria útil
- Considere como isso se integraria ao projeto existente
- Forneça exemplos de como seria usado

---

Agradecemos suas contribuições para tornar o Assistente IA Corporativo melhor para todos!