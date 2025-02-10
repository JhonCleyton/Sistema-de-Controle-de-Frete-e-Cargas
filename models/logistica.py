from extensions import db
from datetime import datetime

class Logistica(db.Model):
    __tablename__ = 'logistica'
    
    id = db.Column(db.Integer, primary_key=True)
    carga_id = db.Column(db.Integer, db.ForeignKey('carga.id'), nullable=False)
    descarga = db.Column(db.Float)
    data_entrega = db.Column(db.Date)
    observacoes = db.Column(db.Text)
    pendencias = db.Column(db.Text)
    
    # Relacionamentos
    carga = db.relationship('Carga', back_populates='logistica')
    
    def to_dict(self):
        return {
            'id': self.id,
            'carga_id': self.carga_id,
            'descarga': self.descarga,
            'data_entrega': self.data_entrega.strftime('%Y-%m-%d') if self.data_entrega else None,
            'observacoes': self.observacoes,
            'pendencias': self.pendencias
        }
