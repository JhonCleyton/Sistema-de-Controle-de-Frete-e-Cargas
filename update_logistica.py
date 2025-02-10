from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text

# Criar uma aplicação Flask mínima
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

def update_logistica_table():
    with app.app_context():
        engine = db.engine
        with engine.connect() as conn:
            # Criar backup da tabela
            conn.execute(text('CREATE TABLE logistica_backup AS SELECT * FROM logistica'))
            conn.execute(text('DROP TABLE logistica'))
            
            # Criar nova tabela com a estrutura atualizada
            conn.execute(text('''
                CREATE TABLE logistica (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    carga_id INTEGER NOT NULL,
                    descarga FLOAT,
                    data_entrega DATETIME,
                    observacoes TEXT,
                    pendencias TEXT,
                    FOREIGN KEY(carga_id) REFERENCES carga(id)
                )
            '''))
            
            # Copiar dados do backup para a nova tabela
            conn.execute(text('''
                INSERT INTO logistica (id, carga_id, descarga, data_entrega, observacoes, pendencias)
                SELECT id, carga_id, descarga, data_entrega, observacao, pendencias
                FROM logistica_backup
            '''))
            
            # Remover tabela de backup
            conn.execute(text('DROP TABLE logistica_backup'))
            
            print("Tabela logistica atualizada com sucesso!")

if __name__ == '__main__':
    update_logistica_table()
