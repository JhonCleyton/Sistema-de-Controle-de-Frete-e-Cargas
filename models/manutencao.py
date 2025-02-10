from extensions import db
from datetime import datetime

class Manutencao(db.Model):
    __tablename__ = 'manutencoes'
    
    id = db.Column(db.Integer, primary_key=True)
    veiculo_id = db.Column(db.Integer, db.ForeignKey('veiculos.id'), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # preventiva, corretiva, revisao
    descricao = db.Column(db.Text, nullable=False)
    data_prevista = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pendente')  # pendente, concluída, cancelada
    
    # Dados da execução
    data_inicio = db.Column(db.DateTime)
    data_conclusao = db.Column(db.DateTime)
    custo = db.Column(db.Float)
    observacoes = db.Column(db.Text)
    
    # Responsáveis
    criado_por_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    concluido_por_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relacionamentos
    veiculo = db.relationship('Veiculo', backref='manutencoes')
    criado_por = db.relationship('User', foreign_keys=[criado_por_id])
    concluido_por = db.relationship('User', foreign_keys=[concluido_por_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'veiculo': self.veiculo.placa,
            'tipo': self.tipo,
            'descricao': self.descricao,
            'data_prevista': self.data_prevista.strftime('%Y-%m-%d'),
            'status': self.status,
            'data_inicio': self.data_inicio.strftime('%Y-%m-%d') if self.data_inicio else None,
            'data_conclusao': self.data_conclusao.strftime('%Y-%m-%d') if self.data_conclusao else None,
            'custo': self.custo,
            'observacoes': self.observacoes,
            'criado_por': self.criado_por.nome if self.criado_por else None,
            'concluido_por': self.concluido_por.nome if self.concluido_por else None
        }
