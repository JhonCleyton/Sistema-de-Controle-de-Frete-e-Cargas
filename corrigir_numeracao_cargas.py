from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

# Criar uma aplicação Flask mínima
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

def corrigir_numeracao_cargas():
    with app.app_context():
        engine = db.engine
        with engine.connect() as conn:
            # Consulta para verificar as últimas cargas
            resultado = conn.execute(text('SELECT id, carga_id FROM carga ORDER BY id DESC LIMIT 3'))
            cargas = resultado.fetchall()
            
            # Verificar se temos 3 cargas para corrigir
            if len(cargas) == 3:
                # Atualizar a numeração das cargas
                conn.execute(text('UPDATE carga SET carga_id = 5170 WHERE id = :id1'), {'id1': cargas[2][0]})
                conn.execute(text('UPDATE carga SET carga_id = 5171 WHERE id = :id2'), {'id2': cargas[1][0]})
                conn.execute(text('UPDATE carga SET carga_id = 5172 WHERE id = :id3'), {'id3': cargas[0][0]})
                
                print("Numeração das cargas corrigida com sucesso!")
                print(f"Carga 1 (mais antiga): {cargas[2][0]} - Novo número: 5170")
                print(f"Carga 2 (intermediária): {cargas[1][0]} - Novo número: 5171")
                print(f"Carga 3 (mais recente): {cargas[0][0]} - Novo número: 5172")
            else:
                print("Não foram encontradas 3 cargas para corrigir.")

if __name__ == '__main__':
    corrigir_numeracao_cargas()