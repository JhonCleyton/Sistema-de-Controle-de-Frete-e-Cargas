from extensions import db
from datetime import datetime

class Viagem(db.Model):
    __tablename__ = 'viagens'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('veiculos.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    destination = db.Column(db.String(200), nullable=False)
    initial_km = db.Column(db.Float, nullable=False)
    final_km = db.Column(db.Float)
    fuel_liters = db.Column(db.Float)
    fuel_cost = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    vehicle = db.relationship('Veiculo', backref=db.backref('viagens', lazy=True))
    driver = db.relationship('User', backref=db.backref('viagens', lazy=True))
