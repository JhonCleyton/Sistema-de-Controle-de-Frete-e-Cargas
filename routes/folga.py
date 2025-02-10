from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from extensions import db
from models.folga import Folga
from datetime import datetime
from functools import wraps

folga_bp = Blueprint('folga', __name__)

def gerencia_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.role in ['gerencia', 'admin']:
            flash('Acesso não autorizado.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@folga_bp.route('/folgas')
@login_required
def listar_folgas():
    if current_user.role in ['gerencia', 'admin']:
        folgas = Folga.query.all()
    else:
        folgas = Folga.query.filter_by(motorista_id=current_user.id).all()
    return render_template('folga.html', folgas=folgas)

@folga_bp.route('/folgas/solicitar', methods=['POST'])
@login_required
def solicitar_folga():
    data = request.json
    try:
        folga = Folga(
            motorista_id=current_user.id,
            data_inicio=datetime.strptime(data['data_inicio'], '%Y-%m-%d %H:%M'),
            data_fim=datetime.strptime(data['data_fim'], '%Y-%m-%d %H:%M'),
            motivo=data['motivo'],
            observacoes=data.get('observacoes')
        )
        db.session.add(folga)
        db.session.commit()
        return jsonify({'message': 'Solicitação de folga enviada com sucesso!', 'folga': folga.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@folga_bp.route('/folgas/<int:folga_id>', methods=['PUT'])
@login_required
@gerencia_required
def avaliar_folga(folga_id):
    data = request.json
    folga = Folga.query.get_or_404(folga_id)
    
    try:
        folga.status = data['status']
        folga.aprovada_por_id = current_user.id
        folga.data_aprovacao = datetime.now()
        folga.observacoes = data.get('observacoes', folga.observacoes)
        
        db.session.commit()
        return jsonify({'message': 'Folga atualizada com sucesso!', 'folga': folga.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@folga_bp.route('/folgas/<int:folga_id>', methods=['DELETE'])
@login_required
def cancelar_folga(folga_id):
    folga = Folga.query.get_or_404(folga_id)
    
    if folga.motorista_id != current_user.id and current_user.role not in ['gerencia', 'admin']:
        return jsonify({'error': 'Não autorizado'}), 403
    
    if folga.status != 'pendente':
        return jsonify({'error': 'Não é possível cancelar uma folga que já foi avaliada'}), 400
    
    try:
        db.session.delete(folga)
        db.session.commit()
        return jsonify({'message': 'Solicitação de folga cancelada com sucesso!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
