from extensions import db

class ControleFrete(db.Model):
    __tablename__ = 'controle_fretes'
    
    id = db.Column(db.Integer, primary_key=True)
    carga_id = db.Column(db.Integer, db.ForeignKey('carga.id'), nullable=False)
    tipo_frete = db.Column(db.String(50))
    origem = db.Column(db.String(100))
    km_inicial = db.Column(db.Float)
    km_final = db.Column(db.Float)
    km_rodados = db.Column(db.Float)
    valor_frete = db.Column(db.Float)
    abastecimento = db.Column(db.Float)
    impostos = db.Column(db.Float)
    adiantamento = db.Column(db.Float)
    entrega_extra = db.Column(db.Float)
    outros = db.Column(db.Float)
    preco_km = db.Column(db.Float)
    preco_kg = db.Column(db.Float)
    
    # Relacionamento
    carga = db.relationship('Carga', back_populates='controle_frete')
    
    def to_dict(self):
        return {
            'id': self.id,
            'carga_id': self.carga_id,
            'tipo_frete': self.tipo_frete,
            'origem': self.origem,
            'km_inicial': self.km_inicial,
            'km_final': self.km_final,
            'km_rodados': self.km_rodados,
            'valor_frete': self.valor_frete,
            'abastecimento': self.abastecimento,
            'impostos': self.impostos,
            'adiantamento': self.adiantamento,
            'entrega_extra': self.entrega_extra,
            'outros': self.outros,
            'preco_km': self.preco_km,
            'preco_kg': self.preco_kg
        }
