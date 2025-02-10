from datetime import datetime
from extensions import db

class Mensagem(db.Model):
    __tablename__ = 'mensagens'
    
    id = db.Column(db.Integer, primary_key=True)
    remetente_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    destinatario_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=True)  # Nullable para mensagens de grupo
    conteudo = db.Column(db.Text, nullable=False)
    data_envio = db.Column(db.DateTime, default=datetime.utcnow)
    lida = db.Column(db.Boolean, default=False)
    tipo = db.Column(db.String(20), default='individual')  # 'individual' ou 'grupo'
    
    # Relacionamentos
    remetente = db.relationship('User', foreign_keys=[remetente_id], backref='mensagens_enviadas')
    destinatario = db.relationship('User', foreign_keys=[destinatario_id], backref='mensagens_recebidas')

    def to_dict(self):
        return {
            'id': self.id,
            'remetente_id': self.remetente_id,
            'remetente_nome': self.remetente.username if self.remetente else None,
            'destinatario_id': self.destinatario_id,
            'conteudo': self.conteudo,
            'data_envio': self.data_envio.strftime('%Y-%m-%d %H:%M:%S'),
            'lida': self.lida,
            'tipo': self.tipo
        }
