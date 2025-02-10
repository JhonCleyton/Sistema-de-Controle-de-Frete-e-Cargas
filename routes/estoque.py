from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models.produto import Produto
from models.estoque import Estoque, LocalArmazenagem, HistoricoEstoque
from extensions import db
from datetime import datetime
from functools import wraps

estoque_bp = Blueprint('estoque', __name__)

def faturamento_gerencia_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or \
           not (current_user.role == 'faturamento' or current_user.role == 'gerencia'):
            flash('Acesso não autorizado.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@estoque_bp.route('/estoque')
@login_required
@faturamento_gerencia_required
def index():
    produtos = Produto.query.all()
    locais = LocalArmazenagem.query.all()
    estoques = Estoque.query.all()
    return render_template('estoque/index.html', produtos=produtos, locais=locais, estoques=estoques)

@estoque_bp.route('/estoque/produtos', methods=['GET', 'POST'])
@login_required
@faturamento_gerencia_required
def produtos():
    if request.method == 'POST':
        codigo = request.form.get('codigo')
        nome = request.form.get('nome')
        descricao = request.form.get('descricao')
        unidade_medida = request.form.get('unidade_medida')
        
        produto = Produto(
            codigo=codigo,
            nome=nome,
            descricao=descricao,
            unidade_medida=unidade_medida
        )
        
        try:
            db.session.add(produto)
            db.session.commit()
            flash('Produto cadastrado com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Erro ao cadastrar produto.', 'error')
            
    produtos = Produto.query.all()
    return render_template('estoque/produtos.html', produtos=produtos)

@estoque_bp.route('/estoque/movimento', methods=['POST'])
@login_required
@faturamento_gerencia_required
def registrar_movimento():
    produto_id = request.form.get('produto_id')
    local_id = request.form.get('local_id')
    quantidade = float(request.form.get('quantidade'))
    tipo_movimento = request.form.get('tipo_movimento')
    observacao = request.form.get('observacao')
    
    estoque = Estoque.query.filter_by(
        produto_id=produto_id,
        local_id=local_id
    ).first()
    
    if not estoque:
        estoque = Estoque(
            produto_id=produto_id,
            local_id=local_id,
            quantidade=0
        )
        db.session.add(estoque)
    
    if tipo_movimento == 'entrada':
        estoque.quantidade += quantidade
    elif tipo_movimento == 'saida':
        if estoque.quantidade < quantidade:
            return jsonify({'error': 'Quantidade insuficiente em estoque'}), 400
        estoque.quantidade -= quantidade
    
    historico = HistoricoEstoque(
        produto_id=produto_id,
        local_id=local_id,
        quantidade=quantidade,
        tipo_movimento=tipo_movimento,
        observacao=observacao,
        usuario_id=current_user.id
    )
    
    try:
        db.session.add(historico)
        db.session.commit()
        return jsonify({'message': 'Movimento registrado com sucesso'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao registrar movimento'}), 500

@estoque_bp.route('/estoque/historico')
@login_required
@faturamento_gerencia_required
def historico():
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    produto_id = request.args.get('produto_id')
    local_id = request.args.get('local_id')
    
    query = HistoricoEstoque.query
    
    if data_inicio:
        query = query.filter(HistoricoEstoque.data_movimento >= data_inicio)
    if data_fim:
        query = query.filter(HistoricoEstoque.data_movimento <= data_fim)
    if produto_id:
        query = query.filter_by(produto_id=produto_id)
    if local_id:
        query = query.filter_by(local_id=local_id)
        
    historicos = query.order_by(HistoricoEstoque.data_movimento.desc()).all()
    produtos = Produto.query.all()
    locais = LocalArmazenagem.query.all()
    
    return render_template('estoque/historico.html', 
                         historicos=historicos, 
                         produtos=produtos, 
                         locais=locais)
