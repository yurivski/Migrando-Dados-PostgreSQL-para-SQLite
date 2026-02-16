import os
import json
import sqlite3
import sys
from datetime import date, datetime
from dotenv import load_dotenv

load_dotenv()

PG_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

SQLITE_PATH = r"S:\Microfilme\banco de dados\db_sqlite\protocolos_microfilme.db"

TABELAS_EM_ORDEM = [
    "usuario",
    "recebedor",
    "protocolo",
    "protocolo_backup",
    "auditoria",
]

def conectar_postgresql():
    """Conecta ao PostgreSQL e retorna a conexão."""
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        print("[OK] Conectado ao PostgreSQL")
        return conn
    except Exception as e:
        print(f"[ERRO] Falha ao conectar no PostgreSQL: {e}")
        sys.exit(1)


def conectar_sqlite():
    """Conecta ao SQLite e retorna a conexão."""
    if not os.path.exists(SQLITE_PATH):
        print(f"ERRO: Banco SQLite não encontrado em: {SQLITE_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(SQLITE_PATH)
    conn.execute("PRAGMA foreign_keys = ON") 
    conn.execute("PRAGMA journal_mode = WAL")  
    print(f"Conectado ao SQLite: {SQLITE_PATH}")
    return conn


def converter_valor(valor):
    """
    Converte tipos PostgreSQL para tipos compatíveis com SQLite.
    """
    if valor is None:
        return None
    if isinstance(valor, dict) or isinstance(valor, list):
        return json.dumps(valor, ensure_ascii=False, default=str)
    if isinstance(valor, datetime):
        return valor.isoformat()
    if isinstance(valor, date):
        return valor.isoformat()
    if isinstance(valor, bool):
        return 1 if valor else 0
    return valor

def extrair_dados_pg(pg_conn, tabela):
    """Extrai todos os registros de uma tabela do PostgreSQL."""
    cursor = pg_conn.cursor()
    cursor.execute(f"SELECT * FROM {tabela} ORDER BY id")

    colunas = [desc[0] for desc in cursor.description]
    registros = cursor.fetchall()
    cursor.close()

    return colunas, registros


def inserir_dados_sqlite(sqlite_conn, tabela, colunas, registros):
    """Insere registros no SQLite com tratamento de tipos."""
    if not registros:
        print(f"Tabela '{tabela}' está vazia no PostgreSQL. Pulando.")
        return 0

    placeholders = ", ".join(["?"] * len(colunas))
    colunas_str = ", ".join(colunas)
    sql = f"INSERT INTO {tabela} ({colunas_str}) VALUES ({placeholders})"

    cursor = sqlite_conn.cursor()
    inseridos = 0
    erros = 0

    for registro in registros:
        valores_convertidos = [converter_valor(v) for v in registro]

        try:
            cursor.execute(sql, valores_convertidos)
            inseridos += 1
        except sqlite3.IntegrityError as e:
            erros += 1
            print(f"ERRO: Registro id={registro[0]} na tabela '{tabela}': {e}")
        except Exception as e:
            erros += 1
            print(f"ERRO: Registro id={registro[0]} na tabela '{tabela}': {e}")

    sqlite_conn.commit()

    if erros > 0:
        print(f"AVISO: {erros} registro(s) com erro na tabela '{tabela}'")

    return inseridos

def migrar():
    """Executa a migração completa PostgreSQL → SQLite."""
    print("\n" + "=" * 50)
    print("Mirando PostgreSQL para SQLite")
    print()

    pg_conn = conectar_postgresql()
    sqlite_conn = conectar_sqlite()

    total_geral = 0

    for tabela in TABELAS_EM_ORDEM:
        print(f"\n--- Migrando tabela: {tabela} ---")

        colunas, registros = extrair_dados_pg(pg_conn, tabela)
        print(f"PostgreSQL: {len(registros)} registros encontrados")

        inseridos = inserir_dados_sqlite(sqlite_conn, tabela, colunas, registros)
        print(f"SQLite: {inseridos} registros inseridos")

        total_geral += inseridos

    print()
    print("VERIFICAÇÃO FINAL")
    print()

    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()

    tudo_ok = True

    for tabela in TABELAS_EM_ORDEM:
        pg_cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
        qtd_pg = pg_cursor.fetchone()[0]

        sqlite_cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
        qtd_sqlite = sqlite_cursor.fetchone()[0]

        status = "OK" if qtd_pg == qtd_sqlite else "DIVERGENTE"
        if status == "DIVERGENTE":
            tudo_ok = False

        print(f"  {tabela}: PG={qtd_pg} | SQLite={qtd_sqlite} [{status}]")

    pg_cursor.close()
    sqlite_cursor.close()

    pg_conn.close()
    sqlite_conn.close()

    print()
    if tudo_ok:
        print(f"MIGRAÇÃO CONCLUÍDA COM SUCESSO! Total: {total_geral} registros")
    else:
        print("MIGRAÇÃO CONCLUÍDA COM DIVERGÊNCIAS. Verificar erros.")
    print("=" * 50)

if __name__ == "__main__":
    migrar()