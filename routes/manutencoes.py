from flask import Blueprint, request, jsonify, render_template
from extensions import db
from datetime import datetime
from flask_login import login_required, current_user
from models.veiculo import Veiculo
from models.manutencao import Manutencao
from functools import wraps

manutencoes_bp = Blueprint('manutencoes', __name__)

def check_permission(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({'error': 'Usuário não autenticado'}), 401
            if current_user.role not in allowed_roles:
                return jsonify({'error': 'Usuário não autorizado'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def logistica_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['admin', 'logistica']:
            return jsonify({'error': 'Acesso não autorizado'}), 403
        return f(*args, **kwargs)
    return decorated_function

@manutencoes_bp.route('/manutencoes')
@login_required
def manutencoes():
    manutencoes = Manutencao.query.all()
    veiculos = Veiculo.query.all()
    return render_template('manutencoes/manutencoes.html', manutencoes=manutencoes, veiculos=veiculos)

@manutencoes_bp.route('/manutencoes/criar', methods=['POST'])
@login_required
@logistica_required
def criar_manutencao():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados inválidos'}), 400
            
        veiculo_id = data.get('veiculo_id')
        tipo = data.get('tipo')
        descricao = data.get('descricao')
        data_prevista = data.get('data_prevista')
        
        if not all([veiculo_id, tipo, descricao, data_prevista]):
            return jsonify({'error': 'Todos os campos são obrigatórios'}), 400
            
        # Verificar se o veículo existe
        veiculo = Veiculo.query.get(veiculo_id)
        if not veiculo:
            return jsonify({'error': 'Veículo não encontrado'}), 404
            
        # Converter string para datetime
        try:
            data_prevista = datetime.strptime(data_prevista, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Formato de data inválido'}), 400
            
        # Verificar se a data é futura
        if data_prevista < datetime.now().date():
            return jsonify({'error': 'A data prevista deve ser futura'}), 400
            
        nova_manutencao = Manutencao(
            veiculo_id=veiculo_id,
            tipo=tipo,
            descricao=descricao,
            data_prevista=data_prevista,
            status='pendente',
            criado_por_id=current_user.id
        )
        
        db.session.add(nova_manutencao)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Manutenção agendada com sucesso!',
            'data': {
                'id': nova_manutencao.id,
                'veiculo': veiculo.placa,
                'tipo': nova_manutencao.tipo,
                'data_prevista': nova_manutencao.data_prevista.strftime('%Y-%m-%d'),
                'status': nova_manutencao.status
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@manutencoes_bp.route('/manutencoes/<int:id>/concluir', methods=['POST'])
@login_required
@logistica_required
def concluir_manutencao(id):
    try:
        manutencao = Manutencao.query.get(id)
        if not manutencao:
            return jsonify({'error': 'Manutenção não encontrada'}), 404
            
        data = request.get_json()
        observacoes = data.get('observacoes') if data else None
        
        manutencao.status = 'concluída'
        manutencao.data_conclusao = datetime.now()
        manutencao.concluido_por_id = current_user.id
        if observacoes:
            manutencao.observacoes = observacoes
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Manutenção concluída com sucesso!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@manutencoes_bp.route('/manutencoes/<int:id>/cancelar', methods=['POST'])
@login_required
@logistica_required
def cancelar_manutencao(id):
    try:
        manutencao = Manutencao.query.get(id)
        if not manutencao:
            return jsonify({'error': 'Manutenção não encontrada'}), 404
            
        data = request.get_json()
        motivo = data.get('motivo') if data else None
        
        manutencao.status = 'cancelada'
        if motivo:
            manutencao.observacoes = f"Cancelada: {motivo}"
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Manutenção cancelada com sucesso!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
