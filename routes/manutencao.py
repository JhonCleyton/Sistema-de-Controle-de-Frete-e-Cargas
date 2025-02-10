from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from extensions import db
from models.manutencao import ManutencaoPreventiva
from datetime import datetime
from functools import wraps

manutencao_bp = Blueprint('manutencao', __name__)

def logistica_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.role in ['logistica', 'admin']:
            flash('Acesso não autorizado.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@manutencao_bp.route('/manutencoes')
@login_required
def listar_manutencoes():
    manutencoes = ManutencaoPreventiva.query.all()
    return render_template('manutencao.html', manutencoes=manutencoes)

@manutencao_bp.route('/manutencoes/criar', methods=['POST'])
@login_required
@logistica_required
def criar_manutencao():
    data = request.json
    try:
        manutencao = ManutencaoPreventiva(
            veiculo_id=data['veiculo_id'],
            tipo_manutencao=data['tipo_manutencao'],
            data_prevista=datetime.strptime(data['data_prevista'], '%Y-%m-%d'),
            km_previsto=data.get('km_previsto'),
            descricao=data['descricao'],
            prioridade=data.get('prioridade', 'normal'),
            responsavel_id=current_user.id
        )
        
        if data.get('km_proxima_manutencao'):
            manutencao.km_proxima_manutencao = data['km_proxima_manutencao']
        
        if data.get('data_proxima_manutencao'):
            manutencao.data_proxima_manutencao = datetime.strptime(data['data_proxima_manutencao'], '%Y-%m-%d')
        
        db.session.add(manutencao)
        db.session.commit()
        
        return jsonify({'message': 'Manutenção preventiva criada com sucesso!', 'manutencao': manutencao.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@manutencao_bp.route('/manutencoes/<int:manutencao_id>', methods=['PUT'])
@login_required
@logistica_required
def atualizar_manutencao(manutencao_id):
    manutencao = ManutencaoPreventiva.query.get_or_404(manutencao_id)
    data = request.json
    
    try:
        # Atualizar campos básicos
        if 'status' in data:
            manutencao.status = data['status']
            if data['status'] == 'em_andamento' and not manutencao.data_inicio:
                manutencao.data_inicio = datetime.now()
            elif data['status'] == 'concluida':
                manutencao.data_conclusao = datetime.now()
        
        # Atualizar campos de execução
        if 'km_execucao' in data:
            manutencao.km_execucao = data['km_execucao']
        if 'custo_pecas' in data:
            manutencao.custo_pecas = data['custo_pecas']
            manutencao.calcular_custo_total()
        if 'custo_mao_obra' in data:
            manutencao.custo_mao_obra = data['custo_mao_obra']
            manutencao.calcular_custo_total()
        
        # Atualizar responsáveis
        if 'mecanico_responsavel' in data:
            manutencao.mecanico_responsavel = data['mecanico_responsavel']
        if 'oficina' in data:
            manutencao.oficina = data['oficina']
        
        # Atualizar detalhes técnicos
        if 'pecas_substituidas' in data:
            manutencao.pecas_substituidas = data['pecas_substituidas']
        if 'servicos_realizados' in data:
            manutencao.servicos_realizados = data['servicos_realizados']
        if 'observacoes' in data:
            manutencao.observacoes = data['observacoes']
        
        # Atualizar próxima manutenção
        if 'km_proxima_manutencao' in data:
            manutencao.km_proxima_manutencao = data['km_proxima_manutencao']
        if 'data_proxima_manutencao' in data:
            manutencao.data_proxima_manutencao = datetime.strptime(data['data_proxima_manutencao'], '%Y-%m-%d')
        
        manutencao.verificar_status()
        db.session.commit()
        
        return jsonify({'message': 'Manutenção atualizada com sucesso!', 'manutencao': manutencao.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@manutencao_bp.route('/manutencoes/<int:manutencao_id>', methods=['DELETE'])
@login_required
@logistica_required
def excluir_manutencao(manutencao_id):
    manutencao = ManutencaoPreventiva.query.get_or_404(manutencao_id)
    
    if manutencao.status not in ['pendente', 'atrasada']:
        return jsonify({'error': 'Não é possível excluir uma manutenção que já está em andamento ou concluída'}), 400
    
    try:
        db.session.delete(manutencao)
        db.session.commit()
        return jsonify({'message': 'Manutenção excluída com sucesso!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
