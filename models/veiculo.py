from extensions import db
from datetime import datetime

class Veiculo(db.Model):
    __tablename__ = 'veiculos'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.String(10), unique=True, nullable=False)
    modelo = db.Column(db.String(100))
    marca = db.Column(db.String(100))
    tipo = db.Column(db.String(50))
    ano = db.Column(db.Integer)
    capacidade = db.Column(db.Float)  # em kg
    transportadora_id = db.Column(db.Integer, db.ForeignKey('transportadoras.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relacionamentos
    transportadora = db.relationship('Transportadora', back_populates='veiculos')
    cargas = db.relationship('Carga', back_populates='veiculo')
    
    def to_dict(self):
        return {
            'id': self.id,
            'placa': self.placa,
            'modelo': self.modelo,
            'marca': self.marca,
            'tipo': self.tipo,
            'ano': self.ano,
            'capacidade': self.capacidade,
            'transportadora_id': self.transportadora_id
        }

    def __repr__(self):
        return f'<Veiculo {self.placa}>'

class VeiculoSislog(db.Model):
    __tablename__ = 'veiculos_sislog'
    
    id = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.String(8), unique=True, nullable=False)
    modelo = db.Column(db.String(50), nullable=False)
    marca = db.Column(db.String(50), nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    capacidade = db.Column(db.Float, nullable=False)  # em kg
    tipo = db.Column(db.String(20), nullable=False)  # truck, carreta, van, utilitario
    status = db.Column(db.String(20), default='disponível', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'placa': self.placa,
            'modelo': self.modelo,
            'marca': self.marca,
            'ano': self.ano,
            'capacidade': self.capacidade,
            'tipo': self.tipo,
            'status': self.status
        }
