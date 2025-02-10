import sqlite3
import os

def recreate_table():
    # Caminho para o banco de dados
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database.db')
    
    # Conectar ao banco de dados
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Backup dos dados existentes
        cursor.execute("SELECT * FROM devolucoes")
        existing_data = cursor.fetchall()
        existing_columns = [description[0] for description in cursor.description]
        
        # Criar tabela temporária com a nova estrutura
        cursor.execute("""
        CREATE TABLE devolucoes_new (
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
        
        # Transferir dados existentes
        for row in existing_data:
            # Criar dicionário com dados existentes
            data = dict(zip(existing_columns, row))
            
            # Definir valores padrão para novas colunas
            data['qtd_embalagens'] = data.get('qtd_embalagens', 0)
            data['tipo_movimento'] = data.get('tipo_movimento', None)
            data['aprovado'] = data.get('aprovado', False)
            data['data_aprovacao'] = data.get('data_aprovacao', None)
            data['aprovado_por'] = data.get('aprovado_por', None)
            
            # Inserir na nova tabela
            cursor.execute("""
            INSERT INTO devolucoes_new (
                id, numero_carga, data_devolucao, numero_nfe, 
                peso_devolvido, valor_mercadoria, tipo_mercadoria,
                qtd_embalagens, tipo_movimento, aprovado,
                data_aprovacao, aprovado_por, observacoes,
                transportadora_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data['id'], data['numero_carga'], data['data_devolucao'],
                data['numero_nfe'], data['peso_devolvido'], data['valor_mercadoria'],
                data['tipo_mercadoria'], data['qtd_embalagens'], data['tipo_movimento'],
                data['aprovado'], data['data_aprovacao'], data['aprovado_por'],
                data.get('observacoes'), data['transportadora_id']
            ))
        
        # Remover tabela antiga e renomear a nova
        cursor.execute("DROP TABLE devolucoes")
        cursor.execute("ALTER TABLE devolucoes_new RENAME TO devolucoes")
        
        conn.commit()
        print("Tabela recriada com sucesso!")
        
    except Exception as e:
        print(f"Erro durante a recriação da tabela: {str(e)}")
        conn.rollback()
        
    finally:
        conn.close()

if __name__ == '__main__':
    recreate_table()
