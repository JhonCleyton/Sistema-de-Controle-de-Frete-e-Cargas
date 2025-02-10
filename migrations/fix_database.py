import sys
import os

# Adicionar o diretório pai ao path do Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extensions import db
from models.transportadora import Transportadora
from models.devolucao import Devolucao
from app import create_app

def reset_database():
    app = create_app()
    with app.app_context():
        # Remover todas as tabelas
        db.drop_all()
        
        # Recriar todas as tabelas
        db.create_all()
        
        print("Banco de dados recriado com sucesso!")

if __name__ == '__main__':
    reset_database()
