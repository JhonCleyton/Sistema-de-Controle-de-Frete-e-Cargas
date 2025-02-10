from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models.user import User
from extensions import db
from werkzeug.security import generate_password_hash
from functools import wraps

usuarios_bp = Blueprint('usuarios', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.role == 'gerencia':
            return jsonify({'error': 'Acesso não autorizado'}), 403
        return f(*args, **kwargs)
    return decorated_function

@usuarios_bp.route('/usuarios')
@login_required
@admin_required
def usuarios():
    users = User.query.all()
    return render_template('usuarios.html', users=users)

@usuarios_bp.route('/usuarios/adicionar', methods=['POST'])
@login_required
@admin_required
def adicionar_usuario():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados inválidos'}), 400
            
        # Validar campos obrigatórios
        required_fields = ['username', 'password', 'nome', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'O campo {field} é obrigatório'}), 400
        
        # Verificar se o usuário já existe
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Nome de usuário já existe'}), 400
            
        # Verificar se a função é válida
        funcoes_validas = ['gerencia', 'faturamento', 'logistica', 'financeiro']
        if data['role'] not in funcoes_validas:
            return jsonify({'error': 'Função inválida'}), 400
            
        # Criar novo usuário
        usuario = User(
            username=data['username'],
            nome=data['nome'],
            role=data['role'],
            password=generate_password_hash(data['password'])
        )
        
        db.session.add(usuario)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Usuário criado com sucesso!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@usuarios_bp.route('/usuarios/<int:id>/editar', methods=['POST'])
@login_required
@admin_required
def editar_usuario(id):
    try:
        usuario = User.query.get_or_404(id)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados inválidos'}), 400
            
        # Verificar se o novo username já existe (se foi alterado)
        if data['username'] != usuario.username and User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Nome de usuário já existe'}), 400
            
        usuario.username = data['username']
        usuario.nome = data['nome']
        usuario.role = data['role']
        
        if data.get('password'):
            usuario.password = generate_password_hash(data['password'])
            
        if data['role'] == 'motorista':
            if not data.get('license_number'):
                return jsonify({'error': 'CNH é obrigatória para motoristas'}), 400
            usuario.license_number = data['license_number']
        else:
            usuario.license_number = None
            
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Usuário atualizado com sucesso!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@usuarios_bp.route('/usuarios/<int:id>/excluir', methods=['POST'])
@login_required
@admin_required
def excluir_usuario(id):
    try:
        if id == current_user.id:
            return jsonify({'error': 'Não é possível excluir seu próprio usuário'}), 400
            
        usuario = User.query.get_or_404(id)
        db.session.delete(usuario)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Usuário excluído com sucesso!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@usuarios_bp.route('/api/usuario/perfil')
@login_required
def get_perfil():
    """Retorna os dados do usuário logado"""
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'nome': current_user.nome,
        'display_name': current_user.display_name or current_user.username,
        'profile_icon': current_user.profile_icon,
        'role': current_user.role
    })
