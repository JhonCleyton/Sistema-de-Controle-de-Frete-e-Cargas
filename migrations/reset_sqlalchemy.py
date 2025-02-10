import os
import sys

# Adicionar o diretório pai ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from flask import Flask
from extensions import db
from models.devolucao import Devolucao

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def reset_sqlalchemy():
    with app.app_context():
        try:
            # Remover todas as tabelas
            db.drop_all()
            print("Tabelas removidas com sucesso")
            
            # Recriar todas as tabelas
            db.create_all()
            print("Tabelas recriadas com sucesso")
            
        except Exception as e:
            print(f"Erro: {str(e)}")

if __name__ == '__main__':
    reset_sqlalchemy()
