from extensions import db

class Romaneio(db.Model):
    __tablename__ = 'romaneios'
    
    id = db.Column(db.Integer, primary_key=True)
    carga_id = db.Column(db.Integer, db.ForeignKey('carga.id'), nullable=False)
    nota = db.Column(db.String(50))
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'))
    condicoes_pagamento = db.Column(db.String(100))
    forma_pagamento = db.Column(db.String(50))
    qtd_embalagens = db.Column(db.Integer)
    peso_bruto = db.Column(db.Float)
    valor_liquido = db.Column(db.Float)
    
    # Relacionamentos
    carga = db.relationship('Carga', back_populates='romaneios')
    cliente = db.relationship('Cliente')
    
    def to_dict(self):
        return {
            'id': self.id,
            'carga_id': self.carga_id,
            'nota': self.nota,
            'cliente_id': self.cliente_id,
            'cliente_nome': self.cliente.nome if self.cliente else None,
            'condicoes_pagamento': self.condicoes_pagamento,
            'forma_pagamento': self.forma_pagamento,
            'qtd_embalagens': self.qtd_embalagens,
            'peso_bruto': self.peso_bruto,
            'valor_liquido': self.valor_liquido
        }
