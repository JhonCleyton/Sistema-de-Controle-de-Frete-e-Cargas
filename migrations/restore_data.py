import sqlite3
import os

def restore_data():
    # Caminho para o banco de dados
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database.db')
    
    # Conectar ao banco de dados
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Inserir dados de exemplo
        cursor.execute("""
        INSERT INTO devolucoes (
            numero_carga, data_devolucao, numero_nfe,
            peso_devolvido, valor_mercadoria, tipo_mercadoria,
            qtd_embalagens, tipo_movimento, aprovado,
            observacoes, transportadora_id
        ) VALUES (
            '4568', '2025-01-02 00:00:00.000000', '5156',
            5000.0, 20500.0, 'GALINHA LEVE',
            0, NULL, 0,
            'DEGELO', 1
        )
        """)
        
        conn.commit()
        print("Dados restaurados com sucesso!")
        
    except Exception as e:
        print(f"Erro ao restaurar dados: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    restore_data()
