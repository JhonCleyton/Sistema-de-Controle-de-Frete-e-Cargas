from extensions import db
from datetime import datetime

class Motorista(db.Model):
    __tablename__ = 'motoristas'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cnh = db.Column(db.String(20), unique=True, nullable=False)
    categoria_cnh = db.Column(db.String(2))  # A, B, C, D, E
    validade_cnh = db.Column(db.Date)
    cpf = db.Column(db.String(11), unique=True)
    telefone = db.Column(db.String(20))
    endereco = db.Column(db.String(200))
    status = db.Column(db.String(20), default='disponível')  # disponível, em_viagem, folga, afastado
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'cnh': self.cnh,
            'categoria_cnh': self.categoria_cnh,
            'validade_cnh': self.validade_cnh.strftime('%Y-%m-%d') if self.validade_cnh else None,
            'cpf': self.cpf,
            'telefone': self.telefone,
            'endereco': self.endereco,
            'status': self.status
        }
