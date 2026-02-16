## Migração de dados de banco PostgreSQL para SQLite  

Criei este script para atender a uma necessidade de migração de banco de dados PostgreSQL para SQLite para o Sistema de Registro de Protocolos do meu setor. O banco de dados PostgreSQL precisa de gerenciamento frequente e não poderei mais gerenciá-lo devido ao fim do meu tempo de serviço por completar 8 anos na força. Meu setor não tem pessoas com conhecimento técnico para me substituir nessa responsabilidade, e pensando nisso, o SQLite atende muito bem essa situação por quase não precisar de gerenciamento, o backup dos dados pode ser feito literalmente copiando o arquivo .db.   

#### O script segue um fluxo em 5 passos:
- Carrega as credenciais do `.env`
- Define a ordem de migração respeitando as FKs — `usuario` e `recebedor` primeiro, depois `protocolo` que depende deles   
- Converte tipos automaticamente — JSONB vira string JSON, bool vira 1/0, date/datetime vira ISO string   
- Extrai e insere tabela por tabela com tratamento de erros por registro   
- Verifica no final usando cláusula simples comparando com a função de agregação `COUNT` de cada tabela entre PG e SQLite   
---
### Schema:
Precisei criar um schema em SQLite exatamente como o schema do PostgreSQL. Caso não lembre com detalhes o schema do banco postgreSQL, o script **[Exportador.py](https://github.com/yurivski/Schema-Change-Detector/blob/main/fonte/exportador.py)** pode ajudar: copie o script e faça pequenas edições para atender aos parâmetros do seu banco e tabelas, o script extrairá e salvará os dados em arquivo JSON, após isso, basta criar o novo schema em SQLite com as mesmas cláusulas.  

---

### Orientações/Licensa:
Caso esteja em uma situação onde precise migrar o banco de dados para SQLite, sinta-se livre para clonar o repositório e editar para atender às suas necessidades.

---

#### [LinkedIn](https://www.linkedin.com/in/yuri-pontes-4ba24a345/): Yuri Pontes
