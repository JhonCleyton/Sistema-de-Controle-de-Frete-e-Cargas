from extensions import db
from datetime import datetime

class Gerencia(db.Model):
    __tablename__ = 'gerencia'
    __table_args__ = {'extend_existing': True}  # Isso força o SQLAlchemy a recriar a tabela
    
    id = db.Column(db.Integer, primary_key=True)
    carga_id = db.Column(db.Integer, db.ForeignKey('carga.id'), nullable=False)
    data_aprovacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_assinatura = db.Column(db.DateTime)  # Adicionado campo data_assinatura
    observacoes = db.Column(db.Text)
    status = db.Column(db.String(50))
    diarias = db.Column(db.Float, default=0)
    valor_total = db.Column(db.Float, default=0)  # Novo campo
    valor_a_pagar = db.Column(db.Float, default=0)  # Novo campo
    assinatura = db.Column(db.String(100))
    nome_assinatura = db.Column(db.String(100))  # Nome da pessoa que assinou
    
    # Relacionamento
    carga = db.relationship('Carga', back_populates='gerencia')
    
    def __init__(self, **kwargs):
        super(Gerencia, self).__init__(**kwargs)
        if not self.data_aprovacao:
            self.data_aprovacao = datetime.utcnow()
    
    def to_dict(self):
        return {
            'id': self.id,
            'carga_id': self.carga_id,
            'data_aprovacao': self.data_aprovacao.strftime('%Y-%m-%d %H:%M:%S') if self.data_aprovacao else None,
            'data_assinatura': self.data_assinatura.strftime('%Y-%m-%d %H:%M:%S') if self.data_assinatura else None,
            'observacoes': self.observacoes,
            'status': self.status,
            'diarias': self.diarias,
            'valor_total': self.valor_total,
            'valor_a_pagar': self.valor_a_pagar,
            'assinatura': self.assinatura,
            'nome_assinatura': self.nome_assinatura
        }
