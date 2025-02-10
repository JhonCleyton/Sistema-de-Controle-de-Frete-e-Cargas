from extensions import db
from datetime import datetime

class Mensagem(db.Model):
    __tablename__ = 'mensagens'
    
    id = db.Column(db.Integer, primary_key=True)
    remetente_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    destinatario_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    conteudo = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    lida = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'remetente_id': self.remetente_id,
            'destinatario_id': self.destinatario_id,
            'conteudo': self.conteudo,
            'tipo': self.tipo,
            'lida': self.lida,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
