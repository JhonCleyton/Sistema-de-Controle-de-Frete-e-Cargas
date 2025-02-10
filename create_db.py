from app import app, db
import os

def reset_db():
    # Remove o banco de dados existente
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'database.db')
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Banco de dados removido: {db_path}")
    
    # Cria o banco de dados novamente
    with app.app_context():
        db.create_all()
        print("Banco de dados recriado com sucesso!")

if __name__ == '__main__':
    reset_db()
