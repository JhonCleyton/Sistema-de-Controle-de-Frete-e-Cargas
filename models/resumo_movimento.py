from extensions import db

class ResumoMovimento(db.Model):
    __tablename__ = 'resumo_movimentos'
    
    id = db.Column(db.Integer, primary_key=True)
    carga_id = db.Column(db.Integer, db.ForeignKey('carga.id'), nullable=False)
    codigo = db.Column(db.String(50))
    tipo_movimento = db.Column(db.String(50))
    valor = db.Column(db.Float)
    
    # Relacionamento
    carga = db.relationship('Carga', back_populates='resumo_movimentos')
    
    def to_dict(self):
        return {
            'id': self.id,
            'carga_id': self.carga_id,
            'codigo': self.codigo,
            'tipo_movimento': self.tipo_movimento,
            'valor': self.valor
        }
