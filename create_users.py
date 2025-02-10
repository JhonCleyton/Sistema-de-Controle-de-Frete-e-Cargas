from app import app, db
from models.user import User

def create_default_users():
    with app.app_context():
        # Criar usuários se não existirem
        users = [
            {
                'username': 'admin',
                'password': 'admin123',
                'role': 'admin',
                'nome': 'Administrador',
                'display_name': 'Administrador'
            },
            {
                'username': 'logistica',
                'password': 'logistica123',
                'role': 'logistica',
                'nome': 'Equipe de Logística',
                'display_name': 'Logística'
            },
            {
                'username': 'gerencia',
                'password': 'gerencia123',
                'role': 'gerencia',
                'nome': 'Gerência',
                'display_name': 'Gerência'
            }
        ]
        
        for user_data in users:
            username = user_data['username']
            if not User.query.filter_by(username=username).first():
                user = User(
                    username=username,
                    role=user_data['role'],
                    nome=user_data['nome'],
                    display_name=user_data['display_name']
                )
                user.set_password(user_data['password'])
                db.session.add(user)
                print(f"Criando usuário: {username}")
        
        db.session.commit()
        print("Usuários padrão criados com sucesso!")

if __name__ == '__main__':
    create_default_users()
