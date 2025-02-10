from extensions import db
from datetime import datetime

class Recebimento(db.Model):
    __tablename__ = 'recebimentos'
    
    id = db.Column(db.Integer, primary_key=True)
    carga_id = db.Column(db.Integer, db.ForeignKey('carga.id'), nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    valor = db.Column(db.Float)
    forma_pagamento = db.Column(db.String(50))
    observacoes = db.Column(db.Text)
    
    # Relacionamento
    carga = db.relationship('Carga', back_populates='recebimentos')
    
    def to_dict(self):
        return {
            'id': self.id,
            'carga_id': self.carga_id,
            'data': self.data.strftime('%Y-%m-%d %H:%M:%S') if self.data else None,
            'valor': self.valor,
            'forma_pagamento': self.forma_pagamento,
            'observacoes': self.observacoes
        }
