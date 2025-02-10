from extensions import db
from datetime import datetime

class LocalArmazenagem(db.Model):
    __tablename__ = 'locais_armazenagem'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    endereco = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    estoques = db.relationship('Estoque', backref='local', lazy=True)

class Estoque(db.Model):
    __tablename__ = 'estoques'
    
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=False)
    local_id = db.Column(db.Integer, db.ForeignKey('locais_armazenagem.id'), nullable=False)
    quantidade = db.Column(db.Float, nullable=False, default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Estoque {self.produto.nome} - {self.local.nome}: {self.quantidade}>'

class HistoricoEstoque(db.Model):
    __tablename__ = 'historico_estoque'
    
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=False)
    local_id = db.Column(db.Integer, db.ForeignKey('locais_armazenagem.id'), nullable=False)
    quantidade = db.Column(db.Float, nullable=False)
    tipo_movimento = db.Column(db.String(20), nullable=False)  # entrada, saida, ajuste
    observacao = db.Column(db.Text)
    data_movimento = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relacionamentos
    local = db.relationship('LocalArmazenagem', backref='historicos', lazy=True)
    usuario = db.relationship('User', backref='movimentos_estoque', lazy=True)

    def __repr__(self):
        return f'<HistoricoEstoque {self.produto.nome} - {self.tipo_movimento} - {self.quantidade}>'
