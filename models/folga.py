from extensions import db
from datetime import datetime

class Folga(db.Model):
    __tablename__ = 'folgas'
    
    id = db.Column(db.Integer, primary_key=True)
    motorista_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    data_inicio = db.Column(db.DateTime, nullable=False)
    data_fim = db.Column(db.DateTime, nullable=False)
    motivo = db.Column(db.String(200))
    status = db.Column(db.String(20), default='ativa')  # ativa, cancelada
    observacoes = db.Column(db.Text)
    
    # Relacionamentos
    motorista = db.relationship('User', foreign_keys=[motorista_id], backref='folgas')
    
    def to_dict(self):
        return {
            'id': self.id,
            'motorista': self.motorista.nome,
            'data_inicio': self.data_inicio.strftime('%Y-%m-%d %H:%M'),
            'data_fim': self.data_fim.strftime('%Y-%m-%d %H:%M'),
            'motivo': self.motivo,
            'status': self.status,
            'observacoes': self.observacoes
        }
