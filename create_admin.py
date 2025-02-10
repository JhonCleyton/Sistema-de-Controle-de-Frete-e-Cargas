from app import app, db
from models.user import User

def create_admin():
    with app.app_context():
        # Verifica se já existe um admin
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print("Usuário admin já existe!")
            return
        
        # Cria o usuário admin
        admin = User(
            username='admin',
            nome='Administrador',
            role='admin',
            display_name='Administrador'
        )
        admin.set_password('admin123')
        
        db.session.add(admin)
        db.session.commit()
        print("Usuário admin criado com sucesso!")

if __name__ == '__main__':
    create_admin()
