from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    nome = db.Column(db.String(120))
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'gerencia', 'financeiro', 'logistica', 'visualizador', 'motorista'
    display_name = db.Column(db.String(80))
    profile_icon = db.Column(db.String(200))
    
    # Campos específicos para motoristas
    license_number = db.Column(db.String(20), unique=True)  # CNH
    license_category = db.Column(db.String(2))  # Categoria da CNH
    license_expiry = db.Column(db.Date)  # Data de validade da CNH
    cpf = db.Column(db.String(11), unique=True)
    telefone = db.Column(db.String(20))
    endereco = db.Column(db.String(200))
    status = db.Column(db.String(20), default='disponível')  # disponível, em_viagem, folga
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_gerente(self):
        return self.role == 'gerencia'
    
    @property
    def is_financeiro(self):
        return self.role == 'financeiro'
    
    @property
    def is_logistica(self):
        return self.role == 'logistica'
    
    @property
    def is_visualizador(self):
        return self.role == 'visualizador'
    
    @property
    def is_motorista(self):
        return self.role == 'motorista'
    
    @property
    def can_edit(self):
        return self.role in ['admin', 'gerencia', 'financeiro', 'logistica']
    
    def to_dict(self):
        base_dict = {
            'id': self.id,
            'username': self.username,
            'nome': self.nome,
            'display_name': self.display_name or self.username,
            'profile_icon': self.profile_icon,
            'role': self.role
        }
        
        if self.role == 'motorista':
            base_dict.update({
                'license_number': self.license_number,
                'license_category': self.license_category,
                'license_expiry': self.license_expiry.strftime('%Y-%m-%d') if self.license_expiry else None,
                'cpf': self.cpf,
                'telefone': self.telefone,
                'endereco': self.endereco,
                'status': self.status
            })
            
        return base_dict
