from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models.motorista import Motorista
from extensions import db
from datetime import datetime
from functools import wraps

motoristas_bp = Blueprint('motoristas', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.role in ['gerencia', 'logistica']:
            return jsonify({'error': 'Acesso não autorizado'}), 403
        return f(*args, **kwargs)
    return decorated_function

@motoristas_bp.route('/motoristas')
@login_required
def motoristas():
    motoristas = Motorista.query.all()
    return render_template('motoristas/motoristas.html', motoristas=motoristas)

@motoristas_bp.route('/motoristas/adicionar', methods=['POST'])
@login_required
@admin_required
def adicionar_motorista():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados inválidos'}), 400
            
        # Validar campos obrigatórios
        required_fields = ['nome', 'cnh']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'O campo {field} é obrigatório'}), 400
        
        # Verificar se já existe motorista com a mesma CNH
        if Motorista.query.filter_by(cnh=data['cnh']).first():
            return jsonify({'error': 'CNH já cadastrada'}), 400
            
        # Criar novo motorista
        motorista = Motorista(
            nome=data['nome'],
            cnh=data['cnh'],
            categoria_cnh=data.get('categoria_cnh'),
            validade_cnh=datetime.strptime(data['validade_cnh'], '%Y-%m-%d') if data.get('validade_cnh') else None,
            cpf=data.get('cpf'),
            telefone=data.get('telefone'),
            endereco=data.get('endereco'),
            status='disponível'
        )
        
        db.session.add(motorista)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Motorista cadastrado com sucesso!',
            'motorista': motorista.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@motoristas_bp.route('/motoristas/<int:id>/editar', methods=['POST'])
@login_required
@admin_required
def editar_motorista(id):
    try:
        motorista = Motorista.query.get_or_404(id)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados inválidos'}), 400
            
        # Verificar se a nova CNH já existe (se foi alterada)
        if data['cnh'] != motorista.cnh and Motorista.query.filter_by(cnh=data['cnh']).first():
            return jsonify({'error': 'CNH já cadastrada'}), 400
            
        motorista.nome = data['nome']
        motorista.cnh = data['cnh']
        motorista.categoria_cnh = data.get('categoria_cnh')
        motorista.validade_cnh = datetime.strptime(data['validade_cnh'], '%Y-%m-%d') if data.get('validade_cnh') else None
        motorista.cpf = data.get('cpf')
        motorista.telefone = data.get('telefone')
        motorista.endereco = data.get('endereco')
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Motorista atualizado com sucesso!',
            'motorista': motorista.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@motoristas_bp.route('/motoristas/<int:id>/excluir', methods=['POST'])
@login_required
@admin_required
def excluir_motorista(id):
    try:
        motorista = Motorista.query.get_or_404(id)
        db.session.delete(motorista)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Motorista excluído com sucesso!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@motoristas_bp.route('/api/motoristas', methods=['GET'])
@login_required
def listar_motoristas():
    try:
        motoristas = Motorista.query.all()
        return jsonify([m.to_dict() for m in motoristas])
    except Exception as e:
        return jsonify({'error': str(e)}), 500
