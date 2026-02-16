## Migração de dados de banco PostgreSQL para SQLite  

Criei este script para atender a uma necessidade de migração de banco de dados PostgreSQL para SQLite para o Sistema de Registro de Protocolos do meu setor. O banco de dados PostgreSQL precisa de gerenciamento frequente e não poderei mais gerenciá-lo devido ao fim do meu tempo de serviço por completar 8 anos na força. Meu setor não tem pessoas com conhecimento técnico para me substituir nessa responsabilidade, e pensando nisso, o SQLite atende muito bem essa situação por quase não precisar de gerenciamento, o backup dos dados pode ser feito literalmente copiando o arquivo .db.   

#### O script segue um fluxo em 5 passos:
- Carrega as credenciais do `.env`
- Define a ordem de migração respeitando as FKs — `usuario` e `recebedor` primeiro, depois `protocolo` que depende deles   
- Converte tipos automaticamente — JSONB vira string JSON, bool vira 1/0, date/datetime vira ISO string   
- Extrai e insere tabela por tabela com tratamento de erros por registro   
- Verifica no final comparando `COUNT` de cada tabela entre PG e SQLite