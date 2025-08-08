# Changelog - Assistente IA Corporativo

Todas as alterações notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/spec/v2.0.0.html).

## [1.0.0] - 2024-06-15

### Adicionado

- Versão inicial do Assistente IA Corporativo
- Interface web com campo de entrada e área de resposta
- Integração com modelo LLaMA 3 8B quantizado via llama.cpp
- Sistema de autenticação de usuários
- Painel de administração para gerenciar usuários e configurações do modelo
- Histórico de perguntas e respostas
- Estrutura modular para futuras expansões
- Documentação completa (README, guias de usuário e administrador)
- Scripts de instalação e configuração para Ubuntu Server
- Arquivos de configuração para serviço Systemd
- Suporte a diferentes tipos de prompts (geral, técnico, RH)
- Funções utilitárias para sanitização de entrada e formatação de respostas
- Testes unitários básicos

### Segurança

- Implementação de hash de senhas
- Proteção contra injeção de comandos
- Controle de acesso baseado em funções (usuário/administrador)
- Sanitização de entrada do usuário
- Configuração segura de sessões

## [0.2.0] - 2024-06-10

### Adicionado

- Protótipo da interface web
- Integração inicial com llama.cpp
- Estrutura básica do projeto

### Alterado

- Melhorias na formatação das respostas do modelo
- Otimização do processo de carregamento do modelo

## [0.1.0] - 2024-06-01

### Adicionado

- Conceito inicial e planejamento do projeto
- Pesquisa sobre modelos LLaMA e métodos de quantização
- Definição dos requisitos e arquitetura do sistema