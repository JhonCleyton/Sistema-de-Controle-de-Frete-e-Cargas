from extensions import db
from datetime import datetime

class Carga(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    carga = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    rota = db.Column(db.String(100))
    nfs_cte = db.Column(db.String(50))
    nf = db.Column(db.String(50))
    transportadora_id = db.Column(db.Integer, db.ForeignKey('transportadoras.id'))
    veiculo_id = db.Column(db.Integer, db.ForeignKey('veiculos.id'))
    motorista = db.Column(db.String(100))
    data_saida = db.Column(db.Date)
    hora_saida = db.Column(db.Time)
    data_chegada = db.Column(db.Date)
    hora_chegada = db.Column(db.Time)
    km_inicial = db.Column(db.Float)
    km_final = db.Column(db.Float)
    km_total = db.Column(db.Float)
    peso_total = db.Column(db.Float)
    distancia_total = db.Column(db.Float)
    valor_frete = db.Column(db.Float)
    valor_diaria = db.Column(db.Float)
    valor_entrega_adicional = db.Column(db.Float)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'))
    observacoes = db.Column(db.String(200))  # Campo para observações curtas

    # Relacionamentos
    transportadora = db.relationship('Transportadora', back_populates='cargas')
    veiculo = db.relationship('Veiculo', back_populates='cargas')
    resumo_movimentos = db.relationship('ResumoMovimento', back_populates='carga', lazy='select')
    controle_frete = db.relationship('ControleFrete', back_populates='carga', uselist=False)
    romaneios = db.relationship('Romaneio', back_populates='carga', lazy='select')
    gerencia = db.relationship('Gerencia', back_populates='carga', uselist=False)
    logistica = db.relationship('Logistica', back_populates='carga', uselist=False)
    recebimentos = db.relationship('Recebimento', back_populates='carga', lazy='select')
    despesas = db.relationship('Despesa', back_populates='carga', lazy='select')

    def calcular_preco_por_kg(self):
        # Calcular o peso total dos romaneios
        peso_total = sum(romaneio.peso_bruto for romaneio in self.romaneios) if self.romaneios else 0
        
        if not peso_total or peso_total == 0:
            return 0
            
        # Valor do frete e entrega extra do controle de frete
        valor_total = 0
        if self.controle_frete:
            valor_total += self.controle_frete.valor_frete or 0
            valor_total += self.controle_frete.entrega_extra or 0
        
        # Adicionar diária da gerência
        if self.gerencia and self.gerencia.diarias:
            valor_total += self.gerencia.diarias
        
        # Adicionar valor de descarga da logística
        if hasattr(self, 'logistica') and self.logistica and self.logistica.descarga:
            valor_total += self.logistica.descarga
            
        return valor_total / peso_total if peso_total > 0 else 0

    def to_dict(self):
        return {
            'id': self.id,
            'carga': self.carga,
            'status': self.status,
            'rota': self.rota,
            'nfs_cte': self.nfs_cte,
            'nf': self.nf,
            'transportadora_id': self.transportadora_id,
            'transportadora': self.transportadora.nome if self.transportadora else None,
            'veiculo_id': self.veiculo_id,
            'veiculo': self.veiculo.placa if self.veiculo else None,
            'motorista': self.motorista,
            'data_saida': self.data_saida.strftime('%Y-%m-%d') if self.data_saida else None,
            'hora_saida': self.hora_saida.strftime('%H:%M') if self.hora_saida else None,
            'data_chegada': self.data_chegada.strftime('%Y-%m-%d') if self.data_chegada else None,
            'hora_chegada': self.hora_chegada.strftime('%H:%M') if self.hora_chegada else None,
            'km_inicial': self.km_inicial,
            'km_final': self.km_final,
            'km_total': self.km_total,
            'peso_total': self.peso_total,
            'distancia_total': self.distancia_total,
            'valor_frete': self.valor_frete,
            'valor_diaria': self.valor_diaria,
            'valor_entrega_adicional': self.valor_entrega_adicional,
            'cliente_id': self.cliente_id,
            'observacoes': self.observacoes,
            'resumo_movimentos': [movimento.to_dict() for movimento in self.resumo_movimentos],
            'controle_frete': self.controle_frete.to_dict() if self.controle_frete else None,
            'romaneios': [romaneio.to_dict() for romaneio in self.romaneios],
            'gerencia': self.gerencia.to_dict() if self.gerencia else None,
            'logistica': self.logistica.to_dict() if self.logistica else None,
            'recebimentos': [recebimento.to_dict() for recebimento in self.recebimentos],
            'despesas': [despesa.to_dict() for despesa in self.despesas]
        }
