import sqlite3
import os

def check_data():
    # Caminho para o banco de dados
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database.db')
    
    # Conectar ao banco de dados
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Verificar se há dados na tabela
        cursor.execute("SELECT * FROM devolucoes LIMIT 1")
        row = cursor.fetchone()
        
        if row:
            # Pegar os nomes das colunas
            cursor.execute("PRAGMA table_info(devolucoes)")
            columns = [col[1] for col in cursor.fetchall()]
            
            print("Dados da primeira devolução:")
            for i, value in enumerate(row):
                print(f"{columns[i]}: {value}")
        else:
            print("Nenhuma devolução encontrada no banco de dados")
            
        # Verificar se há algum problema com a tabela
        cursor.execute("PRAGMA integrity_check")
        integrity = cursor.fetchone()[0]
        print(f"\nIntegridade do banco de dados: {integrity}")
        
        # Verificar as foreign keys
        cursor.execute("PRAGMA foreign_key_check")
        fk_issues = cursor.fetchall()
        if fk_issues:
            print("\nProblemas com chaves estrangeiras encontrados:")
            for issue in fk_issues:
                print(issue)
        else:
            print("\nNenhum problema com chaves estrangeiras encontrado")
            
    except Exception as e:
        print(f"Erro: {str(e)}")
    finally:
        conn.close()

if __name__ == '__main__':
    check_data()
