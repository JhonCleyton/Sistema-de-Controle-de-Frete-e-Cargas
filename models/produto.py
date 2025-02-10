from extensions import db
from datetime import datetime

class Produto(db.Model):
    __tablename__ = 'produtos'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    unidade_medida = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    estoques = db.relationship('Estoque', backref='produto', lazy=True)
    historicos = db.relationship('HistoricoEstoque', backref='produto', lazy=True)

    def __repr__(self):
        return f'<Produto {self.codigo} - {self.nome}>'
