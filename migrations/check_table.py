import sqlite3
import os

def check_table():
    # Caminho para o banco de dados
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database.db')
    
    # Conectar ao banco de dados
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Verificar estrutura da tabela
        cursor.execute("PRAGMA table_info(devolucoes)")
        columns = cursor.fetchall()
        
        print("Estrutura atual da tabela devolucoes:")
        for col in columns:
            print(f"Coluna: {col[1]}, Tipo: {col[2]}, NotNull: {col[3]}, Default: {col[4]}")
            
        # Se a tabela não tiver as colunas necessárias, vamos recriá-la do zero
        needed_columns = {
            'qtd_embalagens',
            'tipo_movimento',
            'aprovado',
            'data_aprovacao',
            'aprovado_por'
        }
        
        existing_columns = {col[1] for col in columns}
        missing_columns = needed_columns - existing_columns
        
        if missing_columns:
            print(f"\nColunas faltando: {missing_columns}")
            print("\nRecriando a tabela...")
            
            # Criar tabela temporária com a estrutura correta
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS devolucoes_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_carga VARCHAR(50) NOT NULL,
                data_devolucao DATETIME NOT NULL,
                numero_nfe VARCHAR(50) NOT NULL,
                peso_devolvido FLOAT NOT NULL,
                valor_mercadoria FLOAT NOT NULL,
                tipo_mercadoria VARCHAR(100) NOT NULL,
                qtd_embalagens INTEGER DEFAULT 0,
                tipo_movimento VARCHAR(10),
                aprovado BOOLEAN DEFAULT FALSE,
                data_aprovacao DATETIME,
                aprovado_por VARCHAR(100),
                observacoes TEXT,
                transportadora_id INTEGER NOT NULL,
                FOREIGN KEY (transportadora_id) REFERENCES transportadoras (id) ON DELETE CASCADE
            )
            """)
            
            # Copiar dados existentes
            cursor.execute("""
            INSERT INTO devolucoes_new (
                id, numero_carga, data_devolucao, numero_nfe,
                peso_devolvido, valor_mercadoria, tipo_mercadoria,
                observacoes, transportadora_id
            )
            SELECT 
                id, numero_carga, data_devolucao, numero_nfe,
                peso_devolvido, valor_mercadoria, tipo_mercadoria,
                observacoes, transportadora_id
            FROM devolucoes
            """)
            
            # Remover tabela antiga e renomear a nova
            cursor.execute("DROP TABLE devolucoes")
            cursor.execute("ALTER TABLE devolucoes_new RENAME TO devolucoes")
            
            conn.commit()
            print("Tabela recriada com sucesso!")
            
            # Verificar nova estrutura
            cursor.execute("PRAGMA table_info(devolucoes)")
            new_columns = cursor.fetchall()
            print("\nNova estrutura da tabela devolucoes:")
            for col in new_columns:
                print(f"Coluna: {col[1]}, Tipo: {col[2]}, NotNull: {col[3]}, Default: {col[4]}")
        
    except Exception as e:
        print(f"Erro: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    check_table()
