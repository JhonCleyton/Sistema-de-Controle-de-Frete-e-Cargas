from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from sqlalchemy import text

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)

def update_database():
    with app.app_context():
        with db.engine.connect() as conn:
            # Verifica se as colunas existem
            result = conn.execute(text("PRAGMA table_info(gerencia)"))
            colunas = [row[1] for row in result]
            
            # Adiciona as novas colunas
            if 'valor_total' not in colunas:
                conn.execute(text("ALTER TABLE gerencia ADD COLUMN valor_total FLOAT DEFAULT 0"))
                print("Coluna valor_total adicionada com sucesso!")
            
            if 'valor_a_pagar' not in colunas:
                conn.execute(text("ALTER TABLE gerencia ADD COLUMN valor_a_pagar FLOAT DEFAULT 0"))
                print("Coluna valor_a_pagar adicionada com sucesso!")
            
            # Adiciona a coluna nome_assinatura se não existir
            if 'nome_assinatura' not in colunas:
                conn.execute(text("ALTER TABLE gerencia ADD COLUMN nome_assinatura VARCHAR(100)"))
                print("Coluna nome_assinatura adicionada com sucesso!")
            else:
                print("Coluna nome_assinatura já existe.")
            
            # Remove a coluna antiga se existir
            if 'saldo_a_pagar' in colunas:
                # SQLite não suporta DROP COLUMN diretamente, então precisamos criar uma nova tabela
                conn.execute(text("""
                    CREATE TABLE gerencia_new (
                        id INTEGER PRIMARY KEY,
                        carga_id INTEGER NOT NULL,
                        data_aprovacao DATETIME,
                        data_assinatura DATETIME,
                        observacoes TEXT,
                        status VARCHAR(50),
                        diarias FLOAT DEFAULT 0,
                        valor_total FLOAT DEFAULT 0,
                        valor_a_pagar FLOAT DEFAULT 0,
                        nome_assinatura VARCHAR(100),
                        assinatura VARCHAR(100),
                        FOREIGN KEY(carga_id) REFERENCES carga(id)
                    )
                """))
                
                # Copia os dados, exceto a coluna saldo_a_pagar
                conn.execute(text("""
                    INSERT INTO gerencia_new 
                    SELECT id, carga_id, data_aprovacao, data_assinatura, observacoes, 
                           status, diarias, 0, 0, '', assinatura 
                    FROM gerencia
                """))
                
                # Remove a tabela antiga e renomeia a nova
                conn.execute(text("DROP TABLE gerencia"))
                conn.execute(text("ALTER TABLE gerencia_new RENAME TO gerencia"))
                print("Coluna saldo_a_pagar removida com sucesso!")
            
            # Commit as alterações
            conn.commit()

if __name__ == '__main__':
    update_database()
    print("Atualização do banco de dados concluída!")
