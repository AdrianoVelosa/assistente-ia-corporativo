# Migrações do Banco de Dados

Este diretório contém os arquivos de migração do banco de dados gerenciados pelo Flask-Migrate.

## Como usar

Para inicializar o sistema de migrações (primeira vez):
```
flask db init
```

Para criar uma nova migração após alterar os modelos:
```
flask db migrate -m "descrição da migração"
```

Para aplicar as migrações pendentes ao banco de dados:
```
flask db upgrade
```

Para reverter a última migração:
```
flask db downgrade
```

## Importante

- Sempre revise os arquivos de migração gerados antes de aplicá-los
- Faça backup do banco de dados antes de aplicar migrações em produção
- Mantenha este diretório sob controle de versão