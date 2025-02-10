from extensions import db
from datetime import datetime

class Devolucao(db.Model):
    __tablename__ = 'devolucoes'

    id = db.Column(db.Integer, primary_key=True)
    numero_carga = db.Column(db.String(20), nullable=False)
    numero_nfe = db.Column(db.String(50), nullable=False)
    data_devolucao = db.Column(db.DateTime, nullable=False, default=datetime.now)
    tipo_movimento = db.Column(db.String(10), nullable=True)
    transportadora_id = db.Column(db.Integer, db.ForeignKey('transportadoras.id'), nullable=False)
    qtd_embalagens = db.Column(db.Integer, nullable=True, default=0)
    peso_devolvido = db.Column(db.Float, nullable=False)
    valor_mercadoria = db.Column(db.Float, nullable=False)
    tipo_mercadoria = db.Column(db.String(100), nullable=False)
    aprovado = db.Column(db.Boolean, nullable=False, default=False)
    data_aprovacao = db.Column(db.DateTime, nullable=True)
    aprovado_por = db.Column(db.String(100), nullable=True)
    observacoes = db.Column(db.Text, nullable=True)

    transportadora = db.relationship('Transportadora', backref='devolucoes')

    def __repr__(self):
        return f'<Devolucao {self.id} - Carga {self.numero_carga}>'
