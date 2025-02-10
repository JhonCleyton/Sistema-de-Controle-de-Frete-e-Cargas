from app import app, db
import os
from models.user import User
from models.chat import Mensagem
from models.folga import Folga
from models.manutencao import Manutencao
from models.viagem import Viagem

def reset_db():
    with app.app_context():
        # Remove o banco de dados existente
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'database.db')
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"Banco de dados removido: {db_path}")
        
        # Cria o banco de dados novamente
        db.create_all()
        print("Banco de dados recriado com sucesso!")
        
        # Cria o usuário gerencia
        gerencia = User(
            username='gerencia',
            nome='Gerência',
            role='gerencia',
            display_name='Gerência'
        )
        gerencia.set_password('gerencia')
        
        # Cria o usuário logistica
        logistica = User(
            username='logistica',
            nome='Logística',
            role='logistica',
            display_name='Logística'
        )
        logistica.set_password('logistica')
        
        # Cria o usuário financeiro
        financeiro = User(
            username='financeiro',
            nome='Financeiro',
            role='financeiro',
            display_name='Financeiro'
        )
        financeiro.set_password('financeiro')
        
        # Cria o usuário faturamento
        faturamento = User(
            username='faturamento',
            nome='Faturamento',
            role='faturamento',
            display_name='Faturamento'
        )
        faturamento.set_password('faturamento')
        
        # Adiciona todos os usuários
        db.session.add(gerencia)
        db.session.add(logistica)
        db.session.add(financeiro)
        db.session.add(faturamento)
        db.session.commit()
        
        print("Usuários padrão criados com sucesso!")

if __name__ == '__main__':
    reset_db()
