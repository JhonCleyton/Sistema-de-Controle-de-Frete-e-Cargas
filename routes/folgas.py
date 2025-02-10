from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models.user import User
from models.folga import Folga
from extensions import db
from datetime import datetime
from functools import wraps

folgas_bp = Blueprint('folga', __name__)

@folgas_bp.route('/folga')
@login_required
def folgas():
    if current_user.role == 'motorista':
        folgas = Folga.query.filter_by(motorista_id=current_user.id).all()
    else:
        folgas = Folga.query.all()
    
    motoristas = None
    if current_user.role == 'logistica':
        motoristas = User.query.filter_by(role='motorista').all()
    
    return render_template('folgas/folgas.html', folgas=folgas, motoristas=motoristas)

@folgas_bp.route('/folga/adicionar', methods=['POST'])
@login_required
def adicionar_folga():
    if current_user.role != 'logistica':
        return jsonify({'error': 'Acesso não autorizado'}), 403
        
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados inválidos'}), 400
            
        motorista_id = data.get('motorista_id')
        data_inicio = data.get('data_inicio')
        data_fim = data.get('data_fim')
        motivo = data.get('motivo')
        
        if not motorista_id or not data_inicio or not data_fim or not motivo:
            return jsonify({'error': 'Todos os campos são obrigatórios'}), 400
            
        # Verificar se o motorista existe
        motorista = User.query.filter_by(id=motorista_id, role='motorista').first()
        if not motorista:
            return jsonify({'error': 'Motorista não encontrado'}), 404
            
        # Converter strings para datetime
        try:
            data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
            data_fim = datetime.strptime(data_fim, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Formato de data inválido'}), 400
            
        # Verificar se a data de início é menor que a data de fim
        if data_inicio > data_fim:
            return jsonify({'error': 'A data de início deve ser anterior à data de fim'}), 400
            
        # Criar nova folga
        folga = Folga(
            motorista_id=motorista_id,
            data_inicio=data_inicio,
            data_fim=data_fim,
            motivo=motivo,
            status='ativa'
        )
        
        db.session.add(folga)
        db.session.commit()
        
        return jsonify({
            'message': 'Folga adicionada com sucesso',
            'success': True
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@folgas_bp.route('/folga/<int:id>/cancelar', methods=['POST'])
@login_required
def cancelar_folga(id):
    if current_user.role != 'logistica':
        return jsonify({'error': 'Acesso não autorizado'}), 403
        
    try:
        folga = Folga.query.get_or_404(id)
        folga.status = 'cancelada'
        db.session.commit()
        
        return jsonify({
            'message': 'Folga cancelada com sucesso',
            'success': True
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
