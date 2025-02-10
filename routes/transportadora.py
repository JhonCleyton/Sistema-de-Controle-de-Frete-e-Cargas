from flask import Blueprint, request, jsonify, render_template
from models.transportadora import Transportadora
from models.veiculo import Veiculo
from extensions import db, csrf
from flask_login import login_required, current_user
from functools import wraps
import traceback

# Blueprint para todas as rotas de transportadora
transportadora_bp = Blueprint('transportadora', __name__, url_prefix='/transportadora')

def check_permission(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({'error': 'Não autorizado'}), 401
            if current_user.role not in allowed_roles:
                return jsonify({'error': 'Acesso negado'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Rota para a página web
@transportadora_bp.route('/')
@login_required
@check_permission(['faturamento', 'logistica'])
def index():
    return render_template('transportadora.html')

# Rotas da API
@transportadora_bp.route('/api/transportadoras', methods=['GET'])
@login_required
@check_permission(['faturamento', 'logistica', 'gerencia'])
@csrf.exempt
def get_transportadoras():
    try:
        transportadoras = Transportadora.query.all()
        return jsonify([{
            'id': t.id,
            'nome': t.nome,
            'cnpj': t.cnpj,
            'telefone': t.telefone,
            'email': t.email
        } for t in transportadoras])
    except Exception as e:
        print(f"Erro ao listar transportadoras: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Erro ao listar transportadoras'}), 500

@transportadora_bp.route('/api/transportadoras/<int:id>', methods=['GET'])
@login_required
@check_permission(['faturamento', 'logistica'])
@csrf.exempt
def get_transportadora(id):
    try:
        transportadora = Transportadora.query.get_or_404(id)
        return jsonify({
            'id': transportadora.id,
            'nome': transportadora.nome,
            'cnpj': transportadora.cnpj,
            'telefone': transportadora.telefone,
            'email': transportadora.email
        })
    except Exception as e:
        print(f"Erro ao buscar transportadora: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Erro ao buscar transportadora'}), 500

@transportadora_bp.route('/api/transportadoras', methods=['POST'])
@login_required
@check_permission(['faturamento', 'logistica'])
@csrf.exempt
def create_transportadora():
    try:
        data = request.get_json()
        
        # Validar dados
        if not data.get('nome'):
            return jsonify({'error': 'Nome é obrigatório'}), 400
        if not data.get('cnpj'):
            return jsonify({'error': 'CNPJ é obrigatório'}), 400
            
        # Verificar se já existe transportadora com mesmo CNPJ
        existing = Transportadora.query.filter_by(cnpj=data['cnpj']).first()
        if existing:
            return jsonify({'error': 'Já existe uma transportadora com este CNPJ'}), 400
        
        transportadora = Transportadora(
            nome=data['nome'],
            cnpj=data['cnpj'],
            telefone=data.get('telefone'),
            email=data.get('email')
        )
        
        db.session.add(transportadora)
        db.session.commit()
        
        return jsonify({
            'message': 'Transportadora criada com sucesso',
            'transportadora': {
                'id': transportadora.id,
                'nome': transportadora.nome,
                'cnpj': transportadora.cnpj,
                'telefone': transportadora.telefone,
                'email': transportadora.email
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao criar transportadora: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Erro ao criar transportadora'}), 500

@transportadora_bp.route('/api/transportadoras/<int:id>', methods=['PUT'])
@login_required
@check_permission(['faturamento', 'logistica'])
@csrf.exempt
def update_transportadora(id):
    try:
        transportadora = Transportadora.query.get_or_404(id)
        data = request.get_json()
        
        # Validar dados
        if not data.get('nome'):
            return jsonify({'error': 'Nome é obrigatório'}), 400
        if not data.get('cnpj'):
            return jsonify({'error': 'CNPJ é obrigatório'}), 400
            
        # Verificar se já existe outra transportadora com mesmo CNPJ
        existing = Transportadora.query.filter_by(cnpj=data['cnpj']).first()
        if existing and existing.id != id:
            return jsonify({'error': 'Já existe uma transportadora com este CNPJ'}), 400
        
        transportadora.nome = data['nome']
        transportadora.cnpj = data['cnpj']
        transportadora.telefone = data.get('telefone')
        transportadora.email = data.get('email')
        
        db.session.commit()
        
        return jsonify({'message': 'Transportadora atualizada com sucesso'})
        
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao atualizar transportadora: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Erro ao atualizar transportadora'}), 500

# Rotas para veículos
@transportadora_bp.route('/api/transportadoras/<int:transportadora_id>/veiculos', methods=['GET'])
@login_required
@check_permission(['faturamento', 'logistica'])
@csrf.exempt
def get_veiculos(transportadora_id):
    try:
        veiculos = Veiculo.query.filter_by(transportadora_id=transportadora_id).all()
        return jsonify([{
            'id': v.id,
            'placa': v.placa,
            'modelo': v.modelo,
            'capacidade': v.capacidade,
            'tipo': v.tipo
        } for v in veiculos])
    except Exception as e:
        print(f"Erro ao listar veículos: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Erro ao listar veículos'}), 500

@transportadora_bp.route('/api/transportadoras/<int:transportadora_id>/veiculos', methods=['POST'])
@login_required
@check_permission(['faturamento', 'logistica'])
@csrf.exempt
def create_veiculo(transportadora_id):
    try:
        # Verificar se a transportadora existe
        transportadora = Transportadora.query.get_or_404(transportadora_id)
        
        data = request.get_json()
        
        # Validar dados
        if not data.get('placa'):
            return jsonify({'error': 'Placa é obrigatória'}), 400
        if not data.get('modelo'):
            return jsonify({'error': 'Modelo é obrigatório'}), 400
        if not data.get('tipo'):
            return jsonify({'error': 'Tipo é obrigatório'}), 400
            
        # Verificar se já existe veículo com mesma placa
        existing = Veiculo.query.filter_by(placa=data['placa']).first()
        if existing:
            return jsonify({'error': 'Já existe um veículo com esta placa'}), 400
        
        veiculo = Veiculo(
            transportadora_id=transportadora_id,
            placa=data['placa'],
            modelo=data['modelo'],
            capacidade=data.get('capacidade'),
            tipo=data['tipo']
        )
        
        db.session.add(veiculo)
        db.session.commit()
        
        return jsonify({
            'message': 'Veículo criado com sucesso',
            'id': veiculo.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao criar veículo: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Erro ao criar veículo'}), 500

@transportadora_bp.route('/api/transportadoras/<int:transportadora_id>/veiculos/<int:id>', methods=['GET'])
@login_required
@check_permission(['faturamento', 'logistica'])
@csrf.exempt
def get_veiculo(transportadora_id, id):
    try:
        veiculo = Veiculo.query.filter_by(
            transportadora_id=transportadora_id,
            id=id
        ).first_or_404()
        
        return jsonify({
            'id': veiculo.id,
            'placa': veiculo.placa,
            'modelo': veiculo.modelo,
            'capacidade': veiculo.capacidade,
            'tipo': veiculo.tipo
        })
    except Exception as e:
        print(f"Erro ao buscar veículo: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Erro ao buscar veículo'}), 500

@transportadora_bp.route('/api/transportadoras/<int:transportadora_id>/veiculos/<int:id>', methods=['PUT'])
@login_required
@check_permission(['faturamento', 'logistica'])
@csrf.exempt
def update_veiculo(transportadora_id, id):
    try:
        veiculo = Veiculo.query.filter_by(
            transportadora_id=transportadora_id,
            id=id
        ).first_or_404()
        
        data = request.get_json()
        
        # Validar dados
        if not data.get('placa'):
            return jsonify({'error': 'Placa é obrigatória'}), 400
        if not data.get('modelo'):
            return jsonify({'error': 'Modelo é obrigatório'}), 400
        if not data.get('tipo'):
            return jsonify({'error': 'Tipo é obrigatório'}), 400
            
        # Verificar se já existe outro veículo com mesma placa
        existing = Veiculo.query.filter_by(placa=data['placa']).first()
        if existing and existing.id != id:
            return jsonify({'error': 'Já existe um veículo com esta placa'}), 400
        
        veiculo.placa = data['placa']
        veiculo.modelo = data['modelo']
        veiculo.capacidade = data.get('capacidade')
        veiculo.tipo = data['tipo']
        
        db.session.commit()
        
        return jsonify({'message': 'Veículo atualizado com sucesso'})
        
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao atualizar veículo: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Erro ao atualizar veículo'}), 500
