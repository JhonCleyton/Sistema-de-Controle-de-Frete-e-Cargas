from extensions import db
from datetime import datetime

class Despesa(db.Model):
    __tablename__ = 'despesas'
    
    id = db.Column(db.Integer, primary_key=True)
    carga_id = db.Column(db.Integer, db.ForeignKey('carga.id'), nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    descricao = db.Column(db.String(200))
    valor = db.Column(db.Float)
    forma_pagamento = db.Column(db.String(50))
    observacoes = db.Column(db.Text)
    
    # Relacionamento
    carga = db.relationship('Carga', back_populates='despesas')
    
    def to_dict(self):
        return {
            'id': self.id,
            'carga_id': self.carga_id,
            'data': self.data.strftime('%Y-%m-%d %H:%M:%S') if self.data else None,
            'descricao': self.descricao,
            'valor': self.valor,
            'forma_pagamento': self.forma_pagamento,
            'observacoes': self.observacoes
        }
