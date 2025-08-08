# Guia do Administrador - Assistente IA Corporativo

Este guia fornece instruções detalhadas para administradores do Assistente IA Corporativo, incluindo configuração avançada, manutenção e solução de problemas.

## Índice

1. [Configuração Avançada](#configuração-avançada)
2. [Gerenciamento de Usuários](#gerenciamento-de-usuários)
3. [Configuração do Modelo LLaMA](#configuração-do-modelo-llama)
4. [Monitoramento e Logs](#monitoramento-e-logs)
5. [Backup e Restauração](#backup-e-restauração)
6. [Segurança](#segurança)
7. [Solução de Problemas](#solução-de-problemas)
8. [Integrações](#integrações)

## Configuração Avançada

### Variáveis de Ambiente

Além das variáveis básicas no arquivo `.env`, você pode configurar as seguintes opções avançadas:

```
# Configurações avançadas do servidor
MAX_CONTENT_LENGTH=16777216  # Tamanho máximo de upload (16MB)
SESSION_TYPE=filesystem  # Tipo de armazenamento da sessão
SESSION_PERMANENT=true  # Sessões permanentes
PERMANENT_SESSION_LIFETIME=2592000  # Duração da sessão em segundos (30 dias)

# Configurações avançadas do modelo
LLAMA_NUM_THREADS=4  # Número de threads para inferência
LLAMA_MAX_TOKENS=1024  # Número máximo de tokens na resposta
LLAMA_TOP_K=40  # Parâmetro top_k para amostragem
LLAMA_TOP_P=0.9  # Parâmetro top_p para amostragem
LLAMA_REPEAT_PENALTY=1.1  # Penalidade para repetição de tokens
```

### Configuração do Servidor Web

Para ambientes de produção, recomendamos usar o Nginx como proxy reverso na frente do Gunicorn. Exemplo de configuração do Nginx:

```nginx
server {
    listen 80;
    server_name assistente.seudominio.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Configuração para arquivos estáticos
    location /static/ {
        alias /opt/assistente-ia/static/;
        expires 30d;
    }
}
```

Para habilitar HTTPS, use o Certbot para obter certificados Let's Encrypt:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d assistente.seudominio.com
```

## Gerenciamento de Usuários

### Estrutura do Banco de Dados de Usuários

Em uma implementação completa, você deve usar um banco de dados SQL para armazenar usuários. A estrutura recomendada é:

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,
    email TEXT,
    full_name TEXT,
    department TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    active BOOLEAN DEFAULT 1
);
```

### Integração com LDAP/Active Directory

Para integrar com o Active Directory da sua empresa, adicione as seguintes variáveis ao `.env`:

```
LDAP_ENABLED=true
LDAP_SERVER=ldap://seu-servidor-ad.com
LDAP_PORT=389
LDAP_BASE_DN=DC=empresa,DC=com
LDAP_USER_DN=CN=Users,DC=empresa,DC=com
LDAP_BIND_USER=CN=ldap-bind,CN=Users,DC=empresa,DC=com
LDAP_BIND_PASSWORD=senha-segura
LDAP_USER_FILTER=(sAMAccountName=%s)
LDAP_GROUP_ADMIN=CN=AI-Admins,CN=Groups,DC=empresa,DC=com
```

E implemente a autenticação LDAP no código.

## Configuração do Modelo LLaMA

### Otimização de Desempenho

Para melhorar o desempenho do modelo LLaMA:

1. **Quantização Adequada**: Use modelos quantizados em Q4_K_M para um bom equilíbrio entre velocidade e qualidade.

2. **Ajuste de Threads**: Configure `LLAMA_NUM_THREADS` de acordo com o número de núcleos disponíveis.

3. **Tamanho de Contexto**: Ajuste `LLAMA_CONTEXT_SIZE` conforme a memória disponível:
   - 4GB RAM: máximo de 2048 tokens
   - 8GB RAM: máximo de 4096 tokens
   - 16GB RAM: máximo de 8192 tokens

4. **GPU Acceleration**: Se disponível, compile o llama.cpp com suporte a CUDA ou OpenCL:

   ```bash
   # Para CUDA
   make -j LLAMA_CUBLAS=1
   
   # Para OpenCL
   make -j LLAMA_CLBLAST=1
   ```

### Modelos Alternativos

Além do LLaMA 3 8B, você pode experimentar outros modelos compatíveis com llama.cpp:

- Mistral 7B
- Phi-2
- Gemma 7B
- Falcon 7B

Baixe os modelos quantizados do Hugging Face e ajuste o caminho no arquivo `.env`.

## Monitoramento e Logs

### Configuração de Logs

Os logs da aplicação são armazenados em `/var/log/assistente-ia/app.log` por padrão. Para configurar a rotação de logs, crie um arquivo `/etc/logrotate.d/assistente-ia` com o seguinte conteúdo:

```
/var/log/assistente-ia/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload assistente-ia.service >/dev/null 2>&1 || true
    endscript
}
```

### Monitoramento de Desempenho

Para monitorar o desempenho da aplicação, você pode usar ferramentas como Prometheus e Grafana. Adicione a extensão `prometheus-flask-exporter` ao projeto e configure métricas para:

- Tempo de resposta do modelo
- Uso de memória
- Número de requisições
- Taxa de erros

## Backup e Restauração

### Backup Regular

Crie um script de backup para salvar regularmente:

1. Banco de dados de usuários
2. Histórico de perguntas
3. Configurações (arquivo `.env`)
4. Logs importantes

Exemplo de script de backup:

```bash
#!/bin/bash
BACKUP_DIR=/var/backups/assistente-ia
DATE=$(date +%Y%m%d)

# Criar diretório de backup
mkdir -p $BACKUP_DIR

# Backup do banco de dados
sqlite3 /opt/assistente-ia/instance/assistente.db .dump > $BACKUP_DIR/db_$DATE.sql

# Backup das configurações
cp /opt/assistente-ia/.env $BACKUP_DIR/env_$DATE.bak

# Compactar tudo
tar -czf $BACKUP_DIR/backup_$DATE.tar.gz $BACKUP_DIR/db_$DATE.sql $BACKUP_DIR/env_$DATE.bak

# Limpar arquivos temporários
rm $BACKUP_DIR/db_$DATE.sql $BACKUP_DIR/env_$DATE.bak

# Manter apenas os últimos 30 backups
find $BACKUP_DIR -name "backup_*.tar.gz" -type f -mtime +30 -delete
```

## Segurança

### Melhores Práticas

1. **Atualizações Regulares**: Mantenha o sistema operacional e todas as dependências atualizadas.

2. **Firewall**: Configure o firewall para permitir apenas o tráfego necessário:

   ```bash
   sudo ufw allow 22/tcp  # SSH
   sudo ufw allow 80/tcp   # HTTP
   sudo ufw allow 443/tcp  # HTTPS
   sudo ufw enable
   ```

3. **Fail2Ban**: Instale o Fail2Ban para proteger contra tentativas de força bruta:

   ```bash
   sudo apt install fail2ban
   sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
   sudo systemctl enable fail2ban
   sudo systemctl start fail2ban
   ```

4. **Permissões de Arquivos**: Verifique se os arquivos têm as permissões corretas:

   ```bash
   sudo chown -R www-data:www-data /opt/assistente-ia
   sudo chmod -R 750 /opt/assistente-ia
   sudo chmod 640 /opt/assistente-ia/.env
   ```

5. **Auditoria de Segurança**: Realize auditorias regulares de segurança e mantenha registros de acesso.

## Solução de Problemas

### Problemas Comuns e Soluções

#### O modelo não carrega

**Sintoma**: Erro ao iniciar o modelo LLaMA.

**Soluções**:
1. Verifique se o caminho do modelo está correto no arquivo `.env`
2. Verifique se o executável `main` do llama.cpp tem permissão de execução
3. Verifique se há memória suficiente disponível
4. Tente reduzir o tamanho do contexto

#### Respostas muito lentas

**Sintoma**: O modelo demora muito para responder.

**Soluções**:
1. Aumente o número de threads (`LLAMA_NUM_THREADS`)
2. Use um modelo mais quantizado (Q4_0 é mais rápido, mas menos preciso)
3. Reduza o tamanho do contexto
4. Verifique se o servidor tem recursos suficientes

#### Erros de autenticação

**Sintoma**: Usuários não conseguem fazer login.

**Soluções**:
1. Verifique se o banco de dados de usuários está íntegro
2. Reinicie o serviço para limpar o cache de sessões
3. Se usando LDAP, verifique a conectividade com o servidor AD

## Integrações

### SharePoint

Para configurar a integração com o SharePoint:

1. Registre um aplicativo no Azure AD com permissões para acessar o SharePoint
2. Configure as variáveis de ambiente no arquivo `.env`
3. Ative a integração definindo `SHAREPOINT_ENABLED=true`

Consulte o arquivo `integrations/sharepoint.py` para mais detalhes.

### File Server

Para configurar a integração com o File Server:

1. Crie um usuário com permissões de leitura para os compartilhamentos
2. Configure as variáveis de ambiente no arquivo `.env`
3. Ative a integração definindo `FILESERVER_ENABLED=true`

Consulte o arquivo `integrations/fileserver.py` para mais detalhes.

---

## Suporte

Para suporte adicional, entre em contato com a equipe de TI ou consulte a documentação interna da empresa.