from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file, session
from flask_login import login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect, generate_csrf
from functools import wraps
from extensions import db, login_manager, csrf, cache
from datetime import datetime, timedelta
import os
import traceback
import json
from flask_socketio import SocketIO, emit

# Importar modelos
from models.user import User
from models.transportadora import Transportadora
from models.veiculo import Veiculo
from models.carga import Carga
from models.motorista import Motorista
from models.cidade import Cidade
from models.cliente import Cliente
from models.romaneio import Romaneio
from models.controle_frete import ControleFrete
from models.gerencia import Gerencia
from models.devolucao import Devolucao
from models.chat import Mensagem
from models.resumo_movimento import ResumoMovimento
from models.logistica import Logistica
from models.recebimento import Recebimento
from models.despesa import Despesa

# Importar blueprints
from routes.relatorios import relatorios_bp
from routes.chat import chat_bp
from routes.folgas import folgas_bp
from routes.sislog import sislog_bp
from routes.manutencoes import manutencoes_bp
from routes.usuarios import usuarios_bp
from routes.devolucao import devolucao_bp
from routes.transportadora import transportadora_bp
from routes.estoque import estoque_bp

app = Flask(__name__)

# Configuração básica
app.config['SECRET_KEY'] = 'sua-chave-secreta-aqui'
app.config['WTF_CSRF_SECRET_KEY'] = 'outra-chave-secreta-aqui'
app.config['WTF_CSRF_ENABLED'] = True
app.config.from_object('config.Config')

# Configuração de sessão
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)

# Configuração do Flask-Login
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=7)
app.config['REMEMBER_COOKIE_SECURE'] = False
app.config['REMEMBER_COOKIE_HTTPONLY'] = True
app.config['REMEMBER_COOKIE_SAMESITE'] = 'Lax'
app.config['REMEMBER_COOKIE_REFRESH_EACH_REQUEST'] = True

# Configuração do cache
app.config['CACHE_TYPE'] = 'simple'
app.config['CACHE_DEFAULT_TIMEOUT'] = 300

# Inicializar extensões
db.init_app(app)
csrf.init_app(app)
login_manager.init_app(app)
cache.init_app(app)

# Configurar o login manager
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'info'
login_manager.refresh_view = 'login'
login_manager.needs_refresh_message = 'Por favor, faça login novamente para acessar esta página.'
login_manager.needs_refresh_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'info'
login_manager.session_protection = 'strong'

# Importar o csrf_token para os templates
@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf)

# Inicializar Flask-Migrate
migrate = Migrate(app, db)

# Context processor para variáveis globais
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# Registrar blueprints
app.register_blueprint(relatorios_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(folgas_bp)
app.register_blueprint(sislog_bp)
app.register_blueprint(manutencoes_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(devolucao_bp)
app.register_blueprint(transportadora_bp)
app.register_blueprint(estoque_bp)

# Configurar CSRF para permitir GET em rotas específicas
csrf.exempt('/api/relatorios/dados')

# Configuração de error handlers
@app.errorhandler(400)
def bad_request_error(error):
    if 'CSRF' in str(error):
        return jsonify({
            'success': False,
            'message': 'CSRF token inválido ou ausente'
        }), 400
    return jsonify({
        'success': False,
        'message': str(error)
    }), 400

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    if request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'message': 'Erro interno do servidor'
        }), 500
    return render_template('500.html'), 500

# Remover funções redundantes
def init_db():
    pass

def create_admin():
    pass

@app.route('/update_db')
@login_required
def update_db():
    try:
        # Adiciona as colunas se não existirem
        with db.engine.connect() as conn:
            # Verifica se as colunas existem
            result = conn.execute("PRAGMA table_info(gerencia)")
            colunas = [row[1] for row in result]
            
            if 'diarias' not in colunas:
                conn.execute("ALTER TABLE gerencia ADD COLUMN diarias FLOAT DEFAULT 0")
            if 'valor_total' not in colunas:
                conn.execute("ALTER TABLE gerencia ADD COLUMN valor_total FLOAT DEFAULT 0")
            if 'valor_a_pagar' not in colunas:
                conn.execute("ALTER TABLE gerencia ADD COLUMN valor_a_pagar FLOAT DEFAULT 0")
            
            return jsonify({'success': True, 'message': 'Banco de dados atualizado com sucesso!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def update_database():
    pass

# Função de inicialização do banco de dados
def create_tables():
    try:
        # Cria todas as tabelas se não existirem
        db.create_all()
        
        # Carregar cidades do arquivo JSON se a tabela estiver vazia
        if not Cidade.query.first():
            app.logger.info('Carregando cidades do arquivo JSON...')
            try:
                with open('cidades_cache.json', 'r', encoding='utf-8') as f:
                    cidades_data = json.load(f)
                    
                for cidade in cidades_data:
                    cidade_obj = Cidade(
                        id=cidade['id'],
                        nome=cidade['nome']
                    )
                    db.session.add(cidade_obj)
                
                db.session.commit()
                app.logger.info(f'Carregadas {len(cidades_data)} cidades')
            except Exception as e:
                app.logger.error(f'Erro ao carregar cidades do JSON: {str(e)}')
                db.session.rollback()
        
        return True
    except Exception as e:
        app.logger.error(f'Erro ao criar tabelas: {str(e)}')
        return False

def gerencia_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'gerencia':
            flash('Acesso restrito para usuários da gerência.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def index():
    return redirect(url_for('lista_cargas'))

@app.route('/lista_cargas')
@login_required
def lista_cargas():
    # Carregar cargas com join na tabela de logística
    cargas = db.session.query(Carga)\
        .outerjoin(Logistica)\
        .order_by(Carga.id.desc())\
        .all()
        
    # Atualizar data_chegada com data_entrega da logística se necessário
    for carga in cargas:
        try:
            if carga.logistica and carga.logistica.data_entrega:
                data_entrega = carga.logistica.data_entrega
                # Validar se a data está em um intervalo razoável
                if isinstance(data_entrega, str):
                    data_entrega = datetime.strptime(data_entrega, '%Y-%m-%d').date()
                
                # Ignorar datas fora do intervalo razoável
                if data_entrega.year < 1900 or data_entrega.year > 2100:
                    continue
                    
                if not carga.data_chegada or carga.data_chegada != data_entrega:
                    carga.data_chegada = data_entrega
                    db.session.add(carga)
        except (ValueError, TypeError, AttributeError) as e:
            # Se houver erro com a data, ignorar e continuar
            print(f"Erro ao processar data para carga {carga.id}: {str(e)}")
            continue
    
    # Commit as alterações se houver
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao atualizar datas: {str(e)}")
    
    transportadoras = Transportadora.query.all()
    return render_template('lista_cargas.html', cargas=cargas, transportadoras=transportadoras)

@app.route('/editar_carga/<int:carga_id>', methods=['GET', 'POST'])
@login_required
def editar_carga(carga_id):
    if current_user.role not in ['gerencia', 'faturamento']:
        flash('Acesso não autorizado!', 'error')
        return redirect(url_for('index'))
    
    carga = Carga.query.get_or_404(carga_id)
    
    # Buscar dados necessários
    clientes = Cliente.query.all()
    cidades = [{'id': c.id, 'nome': c.nome} for c in Cidade.query.all()]
    transportadoras = Transportadora.query.all()
    motoristas = Motorista.query.all()
    veiculos = Veiculo.query.all()
    
    # Lista de códigos de movimento e seus tipos
    codigos_movimento = {
        'T520': 'NFe DE SAÍDA - VENDA',
        'T521': 'BONIFICAÇÃO',
        'T820': 'TRANSPORTE PARA ARMAZENAGEM'
    }
    
    if request.method == 'POST':
        try:
            # Atualizar dados da carga (similar à criação)
            carga.carga = request.form['carga']
            carga.status = request.form['status']
            carga.rota = ', '.join(request.form.getlist('rota[]'))
            carga.nfs_cte = request.form.get('nfs_cte', '')
            carga.nf = request.form.get('nf', '')
            carga.observacoes = request.form.get('observacoes', '')
            
            # Processar transportadora, veículo, motorista
            carga.transportadora_id = int(request.form['transportadora']) if request.form.get('transportadora') else None
            carga.veiculo_id = int(request.form['veiculo']) if request.form.get('veiculo') else None
            carga.motorista = request.form.get('motorista', '')
            
            # Processar datas e horas
            carga.data_saida = datetime.strptime(request.form['data_saida'], '%Y-%m-%d').date() if request.form.get('data_saida') else None
            carga.hora_saida = datetime.strptime(request.form['hora_saida'], '%H:%M').time() if request.form.get('hora_saida') and ':' in request.form['hora_saida'] else None
            carga.data_chegada = datetime.strptime(request.form['data_chegada'], '%Y-%m-%d').date() if request.form.get('data_chegada') else None
            carga.hora_chegada = datetime.strptime(request.form['hora_chegada'], '%H:%M').time() if request.form.get('hora_chegada') and ':' in request.form['hora_chegada'] else None
            
            # Processar valores numéricos
            carga.km_inicial = float(request.form['km_inicial']) if request.form.get('km_inicial') else None
            carga.km_final = float(request.form['km_final']) if request.form.get('km_final') else None
            carga.km_total = float(request.form['km_total']) if request.form.get('km_total') else None
            
            # Remover romaneios existentes
            Romaneio.query.filter_by(carga_id=carga.id).delete()
            
            # Adicionar novos romaneios
            notas = request.form.getlist('nota[]')
            clientes_ids = request.form.getlist('cliente[]')
            condicoes = request.form.getlist('condicoes_pagamento[]')
            formas = request.form.getlist('forma_pagamento[]')
            qtds = request.form.getlist('qtd_embalagens[]')
            pesos = request.form.getlist('peso_bruto[]')
            valores = request.form.getlist('valor_liquido[]')

            for i in range(len(notas)):
                if notas[i].strip():
                    romaneio = Romaneio(
                        carga_id=carga.id,
                        nota=notas[i],
                        cliente_id=int(clientes_ids[i]) if clientes_ids[i] else None,
                        condicoes_pagamento=condicoes[i] if i < len(condicoes) else None,
                        forma_pagamento=formas[i] if i < len(formas) else None,
                        qtd_embalagens=int(qtds[i]) if i < len(qtds) and qtds[i] else 0,
                        peso_bruto=float(pesos[i]) if i < len(pesos) and pesos[i] else 0,
                        valor_liquido=float(valores[i]) if i < len(valores) and valores[i] else 0
                    )
                    db.session.add(romaneio)
            
            # Remover movimentos existentes
            ResumoMovimento.query.filter_by(carga_id=carga.id).delete()
            
            # Adicionar novos movimentos
            codigos = request.form.getlist('codigo_movimento[]')
            tipos = request.form.getlist('tipo_movimento[]')
            valores_movimento = request.form.getlist('valor_movimento[]')

            for i in range(len(codigos)):
                if codigos[i].strip():
                    try:
                        valor = float(valores_movimento[i]) if valores_movimento[i] and valores_movimento[i].strip() else 0.0
                    except (ValueError, IndexError):
                        valor = 0.0
                        
                    movimento = ResumoMovimento(
                        carga_id=carga.id,
                        codigo=codigos[i],
                        tipo_movimento=tipos[i] if i < len(tipos) else None,
                        valor=valor
                    )
                    db.session.add(movimento)
            
            # Processar controle de frete
            ControleFrete.query.filter_by(carga_id=carga.id).delete()
            
            if request.form.get('tipo_frete'):
                frete = ControleFrete(
                    carga_id=carga.id,
                    tipo_frete=request.form['tipo_frete'],
                    origem=request.form.get('origem', ''),
                    km_inicial=float(request.form['km_inicial_frete']) if request.form.get('km_inicial_frete') else None,
                    km_final=float(request.form['km_final_frete']) if request.form.get('km_final_frete') else None,
                    km_rodados=float(request.form['km_rodados']) if request.form.get('km_rodados') else None,
                    valor_frete=float(request.form['valor_frete']) if request.form.get('valor_frete') else None,
                    abastecimento=float(request.form['abastecimento']) if request.form.get('abastecimento') else None,
                    impostos=float(request.form['impostos']) if request.form.get('impostos') else None,
                    adiantamento=float(request.form['adiantamento']) if request.form.get('adiantamento') else None,
                    entrega_extra=float(request.form['entrega_extra']) if request.form.get('entrega_extra') else None,
                    outros=float(request.form['outros']) if request.form.get('outros') else None,
                    preco_km=float(request.form['preco_km']) if request.form.get('preco_km') else None,
                    preco_kg=float(request.form['preco_kg']) if request.form.get('preco_kg') else None
                )
                db.session.add(frete)
            
            db.session.commit()
            flash('Carga atualizada com sucesso!', 'success')
            return redirect(url_for('visualizar_carga', carga_id=carga.id))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar carga: {str(e)}', 'error')
            print(f"Erro na edição de carga: {str(e)}")
            return redirect(url_for('editar_carga', carga_id=carga_id))
    
    # GET request
    return render_template('editar_carga.html', 
                         carga=carga,
                         clientes=clientes,
                         cidades=cidades,
                         codigos_movimento=codigos_movimento,
                         transportadoras=transportadoras,
                         motoristas=motoristas,
                         veiculos=veiculos)

@app.route('/excluir_carga', methods=['POST'])
@login_required
def excluir_carga():
    if current_user.role != 'gerencia':
        flash('Acesso não autorizado!', 'error')
        return redirect(url_for('index'))
    
    carga_id = request.form.get('carga_id')
    carga = Carga.query.get_or_404(carga_id)
    
    try:
        # Primeiro, exclua todos os registros relacionados
        ControleFrete.query.filter_by(carga_id=carga_id).delete(synchronize_session=False)
        Gerencia.query.filter_by(carga_id=carga_id).delete(synchronize_session=False)
        Romaneio.query.filter_by(carga_id=carga_id).delete(synchronize_session=False)
        Recebimento.query.filter_by(carga_id=carga_id).delete(synchronize_session=False)
        Despesa.query.filter_by(carga_id=carga_id).delete(synchronize_session=False)
        ResumoMovimento.query.filter_by(carga_id=carga_id).delete(synchronize_session=False)
        Logistica.query.filter_by(carga_id=carga_id).delete(synchronize_session=False)
        
        # Depois exclua a carga
        db.session.delete(carga)
        db.session.commit()
        flash('Carga excluída com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir carga: {str(e)}', 'error')
    
    return redirect(url_for('lista_cargas'))

@csrf.exempt
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            print("Recebendo requisição de login...")
            
            # Tentar obter dados como JSON primeiro
            if request.is_json:
                data = request.get_json()
                username = data.get('username')
                password = data.get('password')
            else:
                username = request.form.get('username')
                password = request.form.get('password')
            
            if not username or not password:
                print("Campos incompletos")
                if request.is_json:
                    return jsonify({'error': 'Por favor, preencha todos os campos'}), 400
                flash('Por favor, preencha todos os campos', 'error')
                return redirect(url_for('login'))
            
            print(f"Procurando usuário: {username}")
            user = User.query.filter_by(username=username).first()
            
            if user and user.check_password(password):
                print(f"Usuário encontrado: {user.username}, role: {user.role}")
                
                # Fazer login e configurar a sessão
                login_user(user, remember=True, duration=timedelta(days=7))
                session.permanent = True
                
                print(f"Login bem-sucedido para {username}")
                
                next_page = request.args.get('next')
                if request.is_json:
                    if next_page:
                        return jsonify({'redirect': next_page})
                    return jsonify({'redirect': url_for('index')})
                if next_page:
                    return redirect(next_page)
                return redirect(url_for('index'))
            else:
                print("Usuário não encontrado ou senha incorreta")
                if request.is_json:
                    return jsonify({'error': 'Usuário ou senha inválidos'}), 401
                flash('Usuário ou senha inválidos', 'error')
                return redirect(url_for('login'))
                
        except Exception as e:
            print(f"Erro no login: {str(e)}")
            if request.is_json:
                return jsonify({'error': f'Erro ao processar login: {str(e)}'}), 500
            flash(f'Erro ao processar login: {str(e)}', 'error')
            return redirect(url_for('login'))
    
    # Se for GET, renderiza o template
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    # Registrar o logout
    if current_user.is_authenticated:
        print(f"Logout para usuário: {current_user.username}")
    
    # Fazer logout do usuário e limpar a sessão
    logout_user()
    session.clear()
    
    flash('Você foi desconectado com sucesso.', 'success')
    return redirect(url_for('login'))

@app.route('/nova_carga', methods=['GET', 'POST'])
@login_required
def nova_carga():
    if not current_user.is_authenticated or current_user.role not in ['gerencia', 'faturamento']:
        flash('Acesso não autorizado! Apenas usuários de gerência e faturamento podem criar novas cargas.', 'error')
        return redirect(url_for('index'))
    
    # Buscar dados necessários
    clientes = Cliente.query.all()
    cidades = [{'id': c.id, 'nome': c.nome} for c in Cidade.query.all()]
    transportadoras = Transportadora.query.all()
    motoristas = Motorista.query.all()
    veiculos = Veiculo.query.all()
    
    # Lista de códigos de movimento e seus tipos
    codigos_movimento = {
        'T520': 'NFe DE SAÍDA - VENDA',
        'T521': 'BONIFICAÇÃO',
        'T820': 'TRANSPORTE PARA ARMAZENAGEM'
    }
    
    if request.method == 'POST':
        try:
            print("Dados recebidos do formulário:")
            print("Form data:", request.form)
            
            # Criar nova carga
            nova_carga = Carga(
                carga=request.form['carga'],
                status='Em Andamento',
                rota=', '.join(request.form.getlist('rota[]')),  # Junta todas as rotas com vírgula
                nfs_cte=request.form.get('nfs_cte', ''),
                nf=request.form.get('nf', ''),
                transportadora_id=int(request.form['transportadora']) if request.form.get('transportadora') else None,
                veiculo_id=int(request.form['veiculo']) if request.form.get('veiculo') else None,
                motorista=request.form.get('motorista', ''),  # Agora é string
                data_saida=datetime.strptime(request.form['data_saida'], '%Y-%m-%d').date() if request.form.get('data_saida') else None,
                hora_saida=datetime.strptime(request.form['hora_saida'], '%H:%M').time() if request.form.get('hora_saida') else None,
                data_chegada=datetime.strptime(request.form['data_chegada'], '%Y-%m-%d').date() if request.form.get('data_chegada') else None,
                hora_chegada=datetime.strptime(request.form['hora_chegada'], '%H:%M').time() if request.form.get('hora_chegada') else None,
                km_inicial=float(request.form['km_inicial']) if request.form.get('km_inicial') else None,
                km_final=float(request.form['km_final']) if request.form.get('km_final') else None,
                km_total=float(request.form['km_total']) if request.form.get('km_total') else None,
                observacoes=request.form.get('observacoes', '')
            )
            
            print("Nova carga criada:", nova_carga.__dict__)
            
            db.session.add(nova_carga)
            db.session.flush()  # Obter o ID da carga sem commit

            # Adicionar romaneios
            notas = request.form.getlist('nota[]')
            clientes_ids = request.form.getlist('cliente[]')
            condicoes = request.form.getlist('condicoes_pagamento[]')
            formas = request.form.getlist('forma_pagamento[]')
            qtds = request.form.getlist('qtd_embalagens[]')
            pesos = request.form.getlist('peso_bruto[]')
            valores = request.form.getlist('valor_liquido[]')

            print("Dados dos romaneios:")
            print("Notas:", notas)
            print("Clientes:", clientes_ids)
            print("Condições:", condicoes)
            print("Formas:", formas)
            print("Qtds:", qtds)
            print("Pesos:", pesos)
            print("Valores:", valores)

            for i in range(len(notas)):
                if notas[i].strip():  # Só adiciona se houver nota
                    romaneio = Romaneio(
                        carga_id=nova_carga.id,
                        nota=notas[i],
                        cliente_id=int(clientes_ids[i]) if clientes_ids[i] else None,
                        condicoes_pagamento=condicoes[i] if i < len(condicoes) else None,
                        forma_pagamento=formas[i] if i < len(formas) else None,
                        qtd_embalagens=int(qtds[i]) if i < len(qtds) and qtds[i] else 0,
                        peso_bruto=float(pesos[i]) if i < len(pesos) and pesos[i] else 0,
                        valor_liquido=float(valores[i]) if i < len(valores) and valores[i] else 0
                    )
                    db.session.add(romaneio)
            
            # Adicionar movimentos
            codigos = request.form.getlist('codigo_movimento[]')
            tipos = request.form.getlist('tipo_movimento[]')
            valores_movimento = request.form.getlist('valor_movimento[]')

            print("Dados dos movimentos:")
            print("Códigos:", codigos)
            print("Tipos:", tipos)
            print("Valores:", valores_movimento)

            for i in range(len(codigos)):
                if codigos[i].strip():  # Só adiciona se houver código
                    try:
                        valor = float(valores_movimento[i]) if valores_movimento[i] and valores_movimento[i].strip() else 0.0
                    except (ValueError, IndexError):
                        valor = 0.0
                        
                    movimento = ResumoMovimento(
                        carga_id=nova_carga.id,
                        codigo=codigos[i],
                        tipo_movimento=tipos[i] if i < len(tipos) else None,
                        valor=valor
                    )
                    db.session.add(movimento)
            
            # Adicionar controle de frete
            if request.form.get('tipo_frete'):
                frete = ControleFrete(
                    carga_id=nova_carga.id,
                    tipo_frete=request.form['tipo_frete'],
                    origem=request.form.get('origem', ''),
                    km_inicial=float(request.form['km_inicial_frete']) if request.form.get('km_inicial_frete') else None,
                    km_final=float(request.form['km_final_frete']) if request.form.get('km_final_frete') else None,
                    km_rodados=float(request.form['km_rodados']) if request.form.get('km_rodados') else None,
                    valor_frete=float(request.form['valor_frete']) if request.form.get('valor_frete') else None,
                    abastecimento=float(request.form['abastecimento']) if request.form.get('abastecimento') else None,
                    impostos=float(request.form['impostos']) if request.form.get('impostos') else None,
                    adiantamento=float(request.form['adiantamento']) if request.form.get('adiantamento') else None,
                    entrega_extra=float(request.form['entrega_extra']) if request.form.get('entrega_extra') else None,
                    outros=float(request.form['outros']) if request.form.get('outros') else None,
                    preco_km=float(request.form['preco_km']) if request.form.get('preco_km') else None,
                    preco_kg=float(request.form['preco_kg']) if request.form.get('preco_kg') else None
                )
                db.session.add(frete)
                print(f"Controle de frete adicionado: {frete.__dict__}")

            db.session.commit()
            flash('Carga criada com sucesso!', 'success')
            return redirect(url_for('lista_cargas'))

        except Exception as e:
            db.session.rollback()
            print(f"Erro ao criar carga: {str(e)}")
            flash(f'Erro ao criar carga: {str(e)}', 'error')
            return render_template('nova_carga.html', 
                                clientes=clientes,
                                cidades=cidades,
                                transportadoras=transportadoras,
                                motoristas=motoristas,
                                veiculos=veiculos,
                                codigos_movimento=codigos_movimento)

    # Se for GET, renderiza o template com os dados necessários
    return render_template('nova_carga.html',
                         clientes=clientes,
                         cidades=cidades,
                         transportadoras=transportadoras,
                         motoristas=motoristas,
                         veiculos=veiculos,
                         codigos_movimento=codigos_movimento)

@app.route('/api/clientes')
@login_required
def get_clientes():
    try:
        app.logger.info('Buscando clientes do banco de dados...')
        clientes = Cliente.query.all()
        app.logger.info(f'Encontrados {len(clientes)} clientes')
        
        dados = []
        for cliente in clientes:
            dados.append({
                'id': cliente.id,
                'codigo': cliente.codigo,
                'nome': cliente.nome.encode('latin1').decode('utf-8', errors='ignore')
            })
        
        app.logger.info('Dados formatados com sucesso')
        return jsonify(dados)
    except Exception as e:
        app.logger.error(f'Erro ao buscar clientes: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/cidades')
@login_required
def get_cidades():
    try:
        app.logger.info('Buscando cidades do banco de dados...')
        cidades = Cidade.query.all()
        app.logger.info(f'Encontradas {len(cidades)} cidades')
        
        result = [{
            'id': cidade.id,
            'nome': cidade.nome
        } for cidade in cidades]
        
        app.logger.info('Retornando cidades:', result)
        return jsonify(result)
    except Exception as e:
        app.logger.error(f'Erro ao buscar cidades: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/cidade/<nome>', methods=['GET'])
@login_required
def get_cidade(nome):
    try:
        cidade = Cidade.query.filter_by(nome=nome).first()
        if not cidade:
            return jsonify({'error': 'Cidade não encontrada'}), 404
        
        return jsonify({
            'id': cidade.id,
            'nome': cidade.nome,
            'codigo': cidade.codigo,
            'latitude': cidade.latitude,
            'longitude': cidade.longitude
        })
    except Exception as e:
        app.logger.error(f'Erro ao buscar cidade: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/cidades', methods=['GET'])
@login_required
def list_cidades():
    try:
        cidades = Cidade.query.all()
        return jsonify({
            'data': [{
                'id': c.id,
                'nome': c.nome
            } for c in cidades]
        })
    except Exception as e:
        app.logger.error(f'Erro ao buscar cidades: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/novo_cliente', methods=['POST'])
@login_required
def novo_cliente():
    try:
        data = request.get_json()
        
        if not data or not data.get('nome') or not data.get('codigo'):
            return jsonify({'error': 'Dados inválidos'}), 400
        
        # Validar dados
        if not data.get('nome') or not data.get('codigo'):
            return jsonify({'error': 'Código e nome são obrigatórios'}), 400
        
        # Validar se o código já existe
        if Cliente.query.filter_by(codigo=data['codigo']).first():
            return jsonify({'error': 'Código já cadastrado'}), 400
        
        # Criar novo cliente
        novo_cliente = Cliente(codigo=data['codigo'], nome=data['nome'])
        db.session.add(novo_cliente)
        db.session.commit()
        
        return jsonify({'message': 'Cliente cadastrado com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/financeiro/<int:carga_id>', methods=['GET', 'POST'])
@login_required
def financeiro(carga_id):
    if current_user.role not in ['gerencia', 'financeiro']:
        flash('Acesso não autorizado!', 'error')
        return redirect(url_for('index'))
    
    carga = Carga.query.get_or_404(carga_id)
    
    if request.method == 'POST':
        try:
            data = request.form
            print("Dados recebidos:", dict(data))
            
            # Limpar recebimentos e despesas existentes
            Recebimento.query.filter_by(carga_id=carga_id).delete()
            Despesa.query.filter_by(carga_id=carga_id).delete()
            
            # Processar recebimentos
            formas = data.getlist('forma_pagamento[]')
            valores_recebimento = data.getlist('valor_recebimento[]')
            observacoes_recebimento = data.getlist('observacoes_recebimento[]')
            
            print("Formas:", formas)
            print("Valores:", valores_recebimento)
            print("Observações recebimento:", observacoes_recebimento)
            
            for i in range(len(formas)):
                if formas[i] and valores_recebimento[i]:
                    try:
                        valor = float(valores_recebimento[i])
                        recebimento = Recebimento(
                            carga_id=carga_id,
                            forma_pagamento=formas[i],
                            observacoes=observacoes_recebimento[i] if i < len(observacoes_recebimento) else '',
                            valor=valor
                        )
                        db.session.add(recebimento)
                        print(f"Recebimento adicionado: forma={formas[i]}, valor={valor}")
                    except ValueError as e:
                        print(f"Erro ao converter valor: {str(e)}")
                        db.session.rollback()
                        return jsonify({'error': f'Valor inválido para recebimento {i+1}'}), 400
                    except Exception as e:
                        print(f"Erro ao criar recebimento: {str(e)}")
                        db.session.rollback()
                        return jsonify({'error': str(e)}), 400
            
            # Processar despesas
            tipos = data.getlist('descricao[]')
            valores_despesa = data.getlist('valor_despesa[]')
            observacoes_despesa = data.getlist('observacoes_despesa[]')
            
            print("Tipos:", tipos)
            print("Valores despesa:", valores_despesa)
            print("Observações despesa:", observacoes_despesa)
            
            for i in range(len(tipos)):
                if tipos[i] and valores_despesa[i]:
                    try:
                        valor = float(valores_despesa[i])
                        despesa = Despesa(
                            carga_id=carga_id,
                            descricao=tipos[i],
                            observacoes=observacoes_despesa[i] if i < len(observacoes_despesa) else '',
                            valor=valor
                        )
                        db.session.add(despesa)
                        print(f"Despesa adicionada: tipo={tipos[i]}, valor={valor}")
                    except ValueError as e:
                        print(f"Erro ao converter valor: {str(e)}")
                        db.session.rollback()
                        return jsonify({'error': f'Valor inválido para despesa {i+1}'}), 400
                    except Exception as e:
                        print(f"Erro ao criar despesa: {str(e)}")
                        db.session.rollback()
                        return jsonify({'error': str(e)}), 400
            
            db.session.commit()
            flash('Dados financeiros salvos com sucesso!', 'success')
            
            # Enviar notificação para gerentes
            gerentes = User.query.filter_by(role='gerencia').all()
            for gerente in gerentes:
                socketio.emit('notificacao_financeiro', {
                    'carga_numero': carga.carga,
                    'usuario': current_user.nome,
                    'data': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                }, room=f'user_{gerente.id}')
            
            # Se a requisição espera JSON, retorna JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True})
            # Senão, redireciona
            return redirect(url_for('visualizar_carga', carga_id=carga_id))
            
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao salvar dados financeiros: {str(e)}")
            return jsonify({'error': str(e)}), 400
    
    # Carregar dados existentes
    recebimentos = Recebimento.query.filter_by(carga_id=carga_id).all()
    despesas = Despesa.query.filter_by(carga_id=carga_id).all()
    
    return render_template('financeiro.html', 
                         carga=carga,
                         recebimentos=recebimentos,
                         despesas=despesas)

@app.route('/logistica/<int:carga_id>', methods=['GET', 'POST'])
@login_required
def logistica(carga_id):
    if not current_user.is_authenticated or current_user.role not in ['gerencia', 'logistica']:
        flash('Acesso não autorizado! Apenas usuários de gerência e logística podem acessar esta página.', 'error')
        return redirect(url_for('index'))
    
    carga = Carga.query.get_or_404(carga_id)
    
    if request.method == 'POST':
        try:
            # Tratar o valor de descarga formatado em R$
            descarga_str = request.form.get('descarga', '0')
            descarga_str = descarga_str.replace('R$', '').replace('.', '').replace(',', '.').strip()
            descarga = float(descarga_str) if descarga_str else 0
            
            # Obter e converter a data de entrega para Date
            data_entrega = datetime.strptime(request.form['data_entrega'], '%Y-%m-%d').date()
            
            # Atualizar a data de chegada da carga
            carga.data_chegada = data_entrega
            
            # Criar ou atualizar logística
            if carga.logistica:
                carga.logistica.descarga = descarga
                carga.logistica.data_entrega = data_entrega
                carga.logistica.observacoes = request.form.get('observacoes', '')
                carga.logistica.pendencias = request.form.get('pendencias', '')
            else:
                logistica = Logistica(
                    carga_id=carga.id,
                    descarga=descarga,
                    data_entrega=data_entrega,
                    observacoes=request.form.get('observacoes', ''),
                    pendencias=request.form.get('pendencias', '')
                )
                db.session.add(logistica)
            
            db.session.commit()
            flash('Dados da logística salvos com sucesso!', 'success')
            return redirect(url_for('visualizar_carga', carga_id=carga.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao salvar dados da logística: {str(e)}', 'error')
            return render_template('logistica.html', carga=carga)
    
    return render_template('logistica.html', carga=carga)

@app.route('/gerencia/<int:carga_id>', methods=['GET', 'POST'])
@login_required
def gerencia(carga_id):
    carga = Carga.query.get_or_404(carga_id)
    total_despesas = sum(despesa.valor for despesa in carga.despesas)
    
    if request.method == 'POST':
        try:
            diarias = float(request.form.get('diarias', 0)) if request.form.get('diarias') else 0
            observacoes = request.form.get('observacoes', '')
            assinatura = request.form.get('assinatura', '')
            nome_assinatura = request.form.get('nome_assinatura', '')
            
            # Calcula o valor total
            valor_total = (
                (carga.controle_frete.valor_frete if carga.controle_frete and carga.controle_frete.valor_frete is not None else 0) +
                (carga.controle_frete.impostos if carga.controle_frete and carga.controle_frete.impostos is not None else 0) +
                (carga.controle_frete.entrega_extra if carga.controle_frete and carga.controle_frete.entrega_extra is not None else 0) +
                (carga.logistica.descarga if carga.logistica and carga.logistica.descarga is not None else 0) +
                diarias -
                (
                    (carga.controle_frete.adiantamento if carga.controle_frete and carga.controle_frete.adiantamento is not None else 0) +
                    (carga.controle_frete.abastecimento if carga.controle_frete and carga.controle_frete.abastecimento is not None else 0) +
                    (carga.controle_frete.outros if carga.controle_frete and carga.controle_frete.outros is not None else 0)
                )
            )
            
            # Calcula o valor a pagar
            valor_a_pagar = valor_total - total_despesas
            
            if not carga.gerencia:
                gerencia = Gerencia(
                    carga_id=carga_id,
                    diarias=diarias,
                    valor_total=valor_total,
                    valor_a_pagar=valor_a_pagar,
                    observacoes=observacoes,
                    status='Assinado' if assinatura else 'Pendente',
                    assinatura=assinatura,
                    nome_assinatura=nome_assinatura,
                    data_assinatura=datetime.now() if assinatura else None
                )
                db.session.add(gerencia)
            else:
                carga.gerencia.diarias = diarias
                carga.gerencia.valor_total = valor_total
                carga.gerencia.valor_a_pagar = valor_a_pagar
                carga.gerencia.observacoes = observacoes
                if assinatura and not carga.gerencia.assinatura:
                    carga.gerencia.status = 'Assinado'
                    carga.gerencia.assinatura = assinatura
                    carga.gerencia.nome_assinatura = nome_assinatura
                    carga.gerencia.data_assinatura = datetime.now()
            
            db.session.commit()
            flash('Dados da gerência salvos com sucesso!', 'success')
            return redirect(url_for('visualizar_carga', carga_id=carga_id))
        
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Erro ao salvar gerência: {str(e)}")
            flash(f'Erro ao salvar gerência: {str(e)}', 'error')
    
    return render_template('gerencia.html', carga=carga, total_despesas=total_despesas)

@app.route('/usuarios', methods=['GET', 'POST'])
@login_required
def usuarios():
    if current_user.role != 'gerencia':
        flash('Acesso não autorizado!', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Verificar se é uma exclusão
        excluir_id = request.form.get('excluir_id')
        if excluir_id:
            user = User.query.get(excluir_id)
            if user and user.username != 'admin':
                db.session.delete(user)
                try:
                    db.session.commit()
                    print("Commit realizado com sucesso!")
                    flash('Usuário excluído com sucesso!', 'success')
                except Exception as e:
                    db.session.rollback()
                    print(f"Erro ao salvar: {str(e)}")
                    flash('Erro ao excluir usuário!', 'error')
                return redirect(url_for('usuarios'))
        
        # Processar criação/edição de usuário
        usuario_id = request.form.get('usuario_id')
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        
        if usuario_id:  # Edição
            user = User.query.get(usuario_id)
            if user:
                if User.query.filter(User.username == username, User.id != user.id).first():
                    flash('Nome de usuário já existe!', 'error')
                else:
                    user.username = username
                    if password:
                        user.set_password(password)
                    user.role = role
                    try:
                        db.session.commit()
                        print("Commit realizado com sucesso!")
                        flash('Usuário atualizado com sucesso!', 'success')
                    except Exception as e:
                        db.session.rollback()
                        print(f"Erro ao salvar: {str(e)}")
                        flash('Erro ao atualizar usuário!', 'error')
        else:  # Novo usuário
            if User.query.filter_by(username=username).first():
                flash('Nome de usuário já existe!', 'error')
            else:
                user = User(username=username, role=role)
                user.set_password(password)
                db.session.add(user)
                try:
                    db.session.commit()
                    print("Commit realizado com sucesso!")
                    flash('Usuário criado com sucesso!', 'success')
                except Exception as e:
                    db.session.rollback()
                    print(f"Erro ao salvar: {str(e)}")
                    flash('Erro ao criar usuário!', 'error')
        
        return redirect(url_for('usuarios'))
    
    users = User.query.all()
    return render_template('usuarios.html', users=users)

@app.route('/verificar_senha', methods=['POST'])
@login_required
def verificar_senha():
    data = request.get_json()
    if not data or 'senha' not in data:
        return jsonify({'error': 'Senha não fornecida'}), 400
        
    senha = data.get('senha')
    user = User.query.get(current_user.id)
    
    if user and user.check_password(senha):
        return jsonify({'success': True}), 200
    else:
        return jsonify({'error': 'Senha incorreta'}), 401

@app.route('/check_users')
def check_users():
    users = User.query.all()
    return jsonify([{'username': user.username, 'role': user.role} for user in users])

@app.route('/visualizar_carga/<int:carga_id>')
@login_required
def visualizar_carga(carga_id):
    try:
        carga = Carga.query.get_or_404(carga_id)
        total_despesas = sum(despesa.valor for despesa in carga.despesas)
        
        # Calcula o valor total dos romaneios
        total_romaneios = sum(romaneio.valor_liquido for romaneio in carga.romaneios)
        
        # Buscar devoluções da carga
        devolucoes = Devolucao.query.filter_by(numero_carga=carga.carga).all()
        
        # Calcula o valor total usando o total dos romaneios
        valor_total = total_romaneios
        
        return render_template('visualizar_carga.html', 
                             carga=carga, 
                             total_despesas=total_despesas,
                             total_romaneios=total_romaneios,
                             devolucoes=devolucoes,
                             valor_total=valor_total)
    except Exception as e:
        app.logger.error(f"Erro ao visualizar carga: {str(e)}")
        flash(f'Erro ao visualizar carga: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/adicionar_cidade', methods=['POST'])
@login_required
def adicionar_cidade():
    try:
        data = request.get_json()
        
        if not data or not data.get('nome') or not data.get('codigo'):
            return jsonify({'error': 'Dados inválidos'}), 400
        
        # Verificar se a cidade já existe
        cidade_existente = Cidade.query.filter_by(nome=data['nome']).first()
        if cidade_existente:
            return jsonify({'error': 'Cidade já cadastrada'}), 400
        
        # Criar nova cidade
        cidade = Cidade(
            nome=data['nome'],
            codigo=data['codigo'],
            latitude=data.get('latitude', 0),  # Valor padrão 0 se não fornecido
            longitude=data.get('longitude', 0)  # Valor padrão 0 se não fornecido
        )
        
        db.session.add(cidade)
        db.session.commit()
        
        return jsonify({'message': 'Cidade adicionada com sucesso'})
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Erro ao adicionar cidade: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/resumos')
@login_required
def resumos():
    # Buscar dados para os resumos
    cargas = Carga.query.all()
    total_cargas = len(cargas)
    
    # Calcular totais
    total_valor = sum([sum([r.valor_liquido for r in c.romaneios]) for c in cargas if c.romaneios])
    total_peso = sum([sum([r.peso_bruto for r in c.romaneios]) for c in cargas if c.romaneios])
    total_embalagens = sum([sum([r.qtd_embalagens for r in c.romaneios]) for c in cargas if c.romaneios])
    
    # Agrupar por status
    status_counts = {}
    for c in cargas:
        status_counts[c.status] = status_counts.get(c.status, 0) + 1
    
    # Agrupar por transportadora
    transportadora_counts = {}
    for c in cargas:
        if c.transportadora:
            nome = c.transportadora.nome
            transportadora_counts[nome] = transportadora_counts.get(nome, 0) + 1
    
    return render_template('gerencia/resumos.html',
                         total_cargas=total_cargas,
                         total_valor=total_valor,
                         total_peso=total_peso,
                         total_embalagens=total_embalagens,
                         status_counts=status_counts,
                         transportadora_counts=transportadora_counts,
                         cargas=cargas)

@app.route('/relatorios')
@login_required
def relatorios():
    # Buscar dados para os filtros
    transportadoras = db.session.query(Carga.transportadora).distinct().all()
    transportadoras = [t[0] for t in transportadoras if t[0]]
    
    clientes = db.session.query(Cliente.nome).distinct().all()
    clientes = [c[0] for c in clientes if c[0]]
    
    cidades = db.session.query(Cidade.nome).distinct().all()
    cidades = [c[0] for c in cidades if c[0]]
    
    status = db.session.query(Carga.status).distinct().all()
    status = [s[0] for s in status if s[0]]
    
    return render_template('gerencia/relatorios.html',
                         transportadoras=transportadoras,
                         clientes=clientes,
                         cidades=cidades,
                         status=status)

@app.route('/api/relatorios/transportadoras', methods=['GET'])
@login_required
def get_relatorios_transportadoras():
    try:
        transportadoras = db.session.query(Carga.transportadora).distinct().all()
        return jsonify({'data': [t[0] for t in transportadoras if t[0]]})
    except Exception as e:
        app.logger.error(f'Erro ao buscar transportadoras: {str(e)}')
        return jsonify({'error': 'Erro ao buscar transportadoras'}), 500

@app.route('/api/relatorios/clientes', methods=['GET'])
@login_required
def get_relatorios_clientes():
    try:
        clientes = db.session.query(Cliente.nome).distinct().all()
        return jsonify({'data': [c[0] for c in clientes if c[0]]})
    except Exception as e:
        app.logger.error(f'Erro ao buscar clientes: {str(e)}')
        return jsonify({'error': 'Erro ao buscar clientes'}), 500

@app.route('/api/relatorios/cidades', methods=['GET'])
@login_required
def get_relatorios_cidades():
    try:
        # Buscar cidades únicas das rotas das cargas
        cargas = Carga.query.all()
        cidades = set()
        for carga in cargas:
            if carga.rota:
                cidades.update(cidade.strip() for cidade in carga.rota.split(','))
        
        return jsonify({'data': sorted(list(cidades))})
    except Exception as e:
        app.logger.error(f'Erro ao buscar cidades: {str(e)}')
        return jsonify({'error': 'Erro ao buscar cidades'}), 500

@app.route('/api/relatorios/dados', methods=['GET'])
@login_required
def get_relatorios_dados():
    try:
        # Obter parâmetros da query
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        transportadora_id = request.args.get('transportadora')
        status = request.args.get('status')
        cliente_nome = request.args.get('cliente')
        cidade = request.args.get('cidade')

        # Log para debug
        app.logger.info(f'Filtros recebidos: data_inicio={data_inicio}, data_fim={data_fim}, transportadora={transportadora_id}, status={status}, cliente={cliente_nome}, cidade={cidade}')

        # Construir query base
        query = Carga.query

        # Aplicar joins necessários
        query = query.outerjoin(ControleFrete)
        query = query.outerjoin(Gerencia)
        query = query.outerjoin(Romaneio)

        # Aplicar filtros
        if data_inicio:
            query = query.filter(Carga.data_saida >= datetime.strptime(data_inicio, '%Y-%m-%d'))
        if data_fim:
            query = query.filter(Carga.data_saida <= datetime.strptime(data_fim, '%Y-%m-%d'))
        if transportadora_id:
            query = query.filter(Carga.transportadora_id == transportadora_id)
        if status:
            query = query.filter(Carga.status == status)
        if cliente_nome:
            query = query.join(Cliente).filter(Cliente.nome == cliente_nome)
        if cidade:
            query = query.filter(Carga.rota.like(f'%{cidade}%'))

        # Executar query
        cargas = query.all()
        app.logger.info(f'Total de cargas encontradas: {len(cargas)}')
        
        if not cargas:
            return jsonify({
                'frete': {'media': 0, 'total': 0},
                'valor_por_kg': 0,
                'valor_por_km': 0,
                'diarias': {'media': 0, 'total': 0},
                'total_entregas_adicionais': 0,
                'resumo_kg': {'total': 0, 'media': 0, 'minimo': 0, 'maximo': 0},
                'localizacoes': []
            })

        # Inicializar variáveis para métricas
        total_frete = 0
        total_peso = 0
        total_km = 0
        total_diarias = 0
        total_extras = 0
        pesos = []

        # Calcular métricas
        for carga in cargas:
            if carga.controle_frete:
                total_frete += carga.controle_frete.valor_frete or 0
                total_km += carga.controle_frete.km_rodados or 0
                total_extras += carga.controle_frete.entrega_extra or 0
            
            if carga.gerencia:
                total_diarias += carga.gerencia.diarias or 0
            
            for romaneio in carga.romaneios:
                if romaneio and romaneio.peso_bruto:
                    peso = float(romaneio.peso_bruto)
                    total_peso += peso
                    pesos.append(peso)

        num_cargas = len(cargas)
        
        # Calcular médias e estatísticas
        valor_medio_frete = total_frete / num_cargas if num_cargas > 0 else 0
        valor_medio_kg = total_frete / total_peso if total_peso > 0 else 0
        valor_medio_km = total_frete / total_km if total_km > 0 else 0
        valor_medio_diaria = total_diarias / num_cargas if num_cargas > 0 else 0
        peso_medio = sum(pesos) / len(pesos) if pesos else 0
        peso_minimo = min(pesos) if pesos else 0
        peso_maximo = max(pesos) if pesos else 0

        # Preparar dados para gráficos
        evolucao_data = defaultdict(int)
        status_data = defaultdict(int)
        localizacoes = []

        # Buscar todas as cidades do banco de dados
        cidades_db = {cidade.nome: cidade for cidade in Cidade.query.all()}

        for carga in cargas:
            if carga.data_saida:
                data_str = carga.data_saida.strftime('%Y-%m-%d')
                evolucao_data[data_str] += 1
            status_data[carga.status] += 1
            
            # Adicionar todas as cidades da rota como localizações
            if carga.rota:
                cidades = [cidade.strip() for cidade in carga.rota.split(',')]
                for cidade_nome in cidades:
                    cidade = cidades_db.get(cidade_nome)
                    if cidade and cidade.latitude and cidade.longitude:
                        # Verificar se já existe um marcador para esta cidade
                        cidade_existe = False
                        for loc in localizacoes:
                            if loc['cidade'] == cidade_nome:
                                if str(carga.carga) not in loc['cargas']:
                                    loc['cargas'].append(str(carga.carga))
                                cidade_existe = True
                                break
                        
                        if not cidade_existe:
                            localizacoes.append({
                                'lat': cidade.latitude,
                                'lng': cidade.longitude,
                                'cidade': cidade_nome,
                                'cargas': [str(carga.carga)]
                            })

        evolucao_ordenada = dict(sorted(evolucao_data.items()))

        response_data = {
            'frete': {
                'media': valor_medio_frete,
                'total': total_frete
            },
            'valor_por_kg': valor_medio_kg,
            'valor_por_km': valor_medio_km,
            'diarias': {
                'media': valor_medio_diaria,
                'total': total_diarias
            },
            'total_entregas_adicionais': total_extras,
            'resumo_kg': {
                'total': total_peso,
                'media': peso_medio,
                'minimo': peso_minimo,
                'maximo': peso_maximo
            },
            'localizacoes': localizacoes
        }

        app.logger.info('Dados calculados com sucesso')
        return jsonify(response_data)

    except Exception as e:
        app.logger.error(f'Erro ao gerar relatórios: {str(e)}')
        import traceback
        app.logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/transportadoras/', methods=['POST'])
@login_required
def criar_transportadora():
    try:
        if not request.is_json:
            return jsonify({
                'success': False,
                'message': 'Tipo de conteúdo deve ser application/json'
            }), 400

        data = request.get_json()
        
        if not data or 'nome' not in data:
            return jsonify({
                'success': False,
                'message': 'Nome da transportadora é obrigatório'
            }), 400

        app.logger.info(f'Criando transportadora com dados: {data}')
        
        nova_transportadora = Transportadora(
            nome=data['nome'],
            cnpj=data.get('cnpj', ''),
            endereco=data.get('endereco', ''),
            telefone=data.get('telefone', ''),
            email=data.get('email', '')
        )
        
        db.session.add(nova_transportadora)
        db.session.commit()
        
        app.logger.info(f'Transportadora criada com sucesso: {nova_transportadora.id}')
        
        return jsonify({
            'success': True,
            'message': 'Transportadora criada com sucesso',
            'transportadora': {
                'id': nova_transportadora.id,
                'nome': nova_transportadora.nome
            }
        })
    except Exception as e:
        db.session.rollback()
        error_msg = f'Erro ao criar transportadora: {str(e)}'
        app.logger.error(error_msg)
        app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': error_msg
        }), 500

@app.route('/api/transportadoras/<int:id>', methods=['PUT'])
@login_required
def atualizar_transportadora(id):
    try:
        transportadora = Transportadora.query.get_or_404(id)
        data = request.json
        
        transportadora.nome = data.get('nome', transportadora.nome)
        transportadora.cnpj = data.get('cnpj', transportadora.cnpj)
        transportadora.endereco = data.get('endereco', transportadora.endereco)
        transportadora.telefone = data.get('telefone', transportadora.telefone)
        transportadora.email = data.get('email', transportadora.email)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Transportadora atualizada com sucesso'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao atualizar transportadora: {str(e)}'
        }), 400

@app.route('/api/transportadoras/<int:id>', methods=['DELETE'])
@login_required
def excluir_transportadora(id):
    try:
        transportadora = Transportadora.query.get_or_404(id)
        db.session.delete(transportadora)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Transportadora excluída com sucesso'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao excluir transportadora: {str(e)}'
        }), 400

@app.route('/api/transportadoras/', methods=['GET'])
@login_required
def listar_transportadoras():
    try:
        transportadoras = Transportadora.query.all()
        return jsonify({
            'success': True,
            'transportadoras': [{
                'id': t.id,
                'nome': t.nome,
                'cnpj': t.cnpj,
                'endereco': t.endereco,
                'telefone': t.telefone,
                'email': t.email
            } for t in transportadoras]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar transportadoras: {str(e)}'
        }), 500

@app.route('/api/transportadoras/<int:transportadora_id>/veiculos', methods=['GET'])
@login_required
def get_veiculos_transportadora(transportadora_id):
    try:
        transportadora = Transportadora.query.get_or_404(transportadora_id)
        veiculos = Veiculo.query.filter_by(transportadora_id=transportadora_id).all()
        
        return jsonify({
            'success': True,
            'message': f'Veículos da transportadora {transportadora.nome}',
            'veiculos': [{
                'id': v.id,
                'placa': v.placa,
                'modelo': v.modelo,
                'marca': v.marca,
                'tipo': v.tipo,
                'ano': v.ano,
                'capacidade': v.capacidade
            } for v in veiculos]
        })
    except Exception as e:
        error_msg = f'Erro ao listar veículos: {str(e)}'
        app.logger.error(error_msg)
        app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': error_msg
        }), 500

@app.route('/api/transportadoras/<int:transportadora_id>/veiculos', methods=['POST'])
@login_required
def criar_veiculo(transportadora_id):
    try:
        if not request.is_json:
            return jsonify({
                'success': False,
                'message': 'Tipo de conteúdo deve ser application/json'
            }), 400

        transportadora = Transportadora.query.get_or_404(transportadora_id)
        data = request.get_json()

        if not data or 'placa' not in data:
            return jsonify({
                'success': False,
                'message': 'Placa do veículo é obrigatória'
            }), 400

        # Verificar se já existe um veículo com essa placa
        existing = Veiculo.query.filter_by(placa=data['placa']).first()
        if existing:
            return jsonify({
                'success': False,
                'message': 'Já existe um veículo com essa placa'
            }), 400

        app.logger.info(f'Criando veículo para transportadora {transportadora_id}: {data}')

        try:
            capacidade = float(data['capacidade']) if data.get('capacidade') else None
        except (ValueError, TypeError):
            capacidade = None

        try:
            ano = int(data['ano']) if data.get('ano') else None
        except (ValueError, TypeError):
            ano = None

        novo_veiculo = Veiculo(
            transportadora_id=transportadora_id,
            placa=data['placa'].strip().upper(),
            modelo=data.get('modelo', '').strip(),
            marca=data.get('marca', '').strip(),
            tipo=data.get('tipo', '').strip(),
            ano=ano,
            capacidade=capacidade
        )

        db.session.add(novo_veiculo)
        db.session.commit()

        app.logger.info(f'Veículo criado com sucesso: {novo_veiculo.id}')

        return jsonify({
            'success': True,
            'message': 'Veículo criado com sucesso',
            'veiculo': {
                'id': novo_veiculo.id,
                'placa': novo_veiculo.placa,
                'modelo': novo_veiculo.modelo,
                'marca': novo_veiculo.marca,
                'tipo': novo_veiculo.tipo,
                'ano': novo_veiculo.ano,
                'capacidade': novo_veiculo.capacidade
            }
        })
    except Exception as e:
        db.session.rollback()
        error_msg = f'Erro ao criar veículo: {str(e)}'
        app.logger.error(error_msg)
        app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': error_msg
        }), 500

@app.route('/api/transportadoras/<int:transportadora_id>/veiculos/<int:veiculo_id>', methods=['GET'])
@login_required
def get_veiculo(transportadora_id, veiculo_id):
    try:
        veiculo = Veiculo.query.filter_by(
            transportadora_id=transportadora_id,
            id=veiculo_id
        ).first_or_404()
        
        return jsonify({
            'success': True,
            'veiculo': {
                'id': veiculo.id,
                'placa': veiculo.placa,
                'modelo': veiculo.modelo,
                'marca': veiculo.marca,
                'tipo': veiculo.tipo,
                'ano': veiculo.ano,
                'capacidade': veiculo.capacidade
            }
        })
    except Exception as e:
        error_msg = f'Erro ao buscar veículo: {str(e)}'
        app.logger.error(error_msg)
        app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': error_msg
        }), 500

@app.route('/api/transportadoras/<int:transportadora_id>/veiculos/<int:veiculo_id>', methods=['PUT'])
@login_required
def atualizar_veiculo(transportadora_id, veiculo_id):
    try:
        if not request.is_json:
            return jsonify({
                'success': False,
                'message': 'Tipo de conteúdo deve ser application/json'
            }), 400

        veiculo = Veiculo.query.filter_by(
            transportadora_id=transportadora_id,
            id=veiculo_id
        ).first_or_404()
        
        data = request.get_json()
        
        if not data or 'placa' not in data:
            return jsonify({
                'success': False,
                'message': 'Placa do veículo é obrigatória'
            }), 400

        # Verificar se já existe outro veículo com essa placa
        existing = Veiculo.query.filter(
            Veiculo.placa == data['placa'],
            Veiculo.id != veiculo_id
        ).first()
        if existing:
            return jsonify({
                'success': False,
                'message': 'Já existe outro veículo com essa placa'
            }), 400
        
        veiculo.placa = data['placa']
        veiculo.modelo = data.get('modelo', veiculo.modelo)
        veiculo.marca = data.get('marca', veiculo.marca)
        veiculo.tipo = data.get('tipo', veiculo.tipo)
        veiculo.ano = data.get('ano', veiculo.ano)
        veiculo.capacidade = float(data['capacidade']) if data.get('capacidade') else None
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Veículo atualizado com sucesso',
            'veiculo': {
                'id': veiculo.id,
                'placa': veiculo.placa,
                'modelo': veiculo.modelo,
                'tipo': veiculo.tipo,
                'capacidade': veiculo.capacidade
            }
        })
    except Exception as e:
        db.session.rollback()
        error_msg = f'Erro ao atualizar veículo: {str(e)}'
        app.logger.error(error_msg)
        app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': error_msg
        }), 500

@app.route('/api/transportadoras/<int:transportadora_id>/veiculos/<int:veiculo_id>', methods=['DELETE'])
@login_required
def excluir_veiculo(transportadora_id, veiculo_id):
    try:
        veiculo = Veiculo.query.filter_by(
            transportadora_id=transportadora_id,
            id=veiculo_id
        ).first_or_404()
        
        db.session.delete(veiculo)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Veículo excluído com sucesso'
        })
    except Exception as e:
        db.session.rollback()
        error_msg = f'Erro ao excluir veículo: {str(e)}'
        app.logger.error(error_msg)
        app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': error_msg
        }), 500

@app.route('/api/carga/<int:carga_id>/valores')
@login_required
def get_valores_carga(carga_id):
    try:
        carga = Carga.query.get_or_404(carga_id)
        total_despesas = sum(despesa.valor for despesa in carga.despesas)
        
        return jsonify({
            'success': True,
            'total_despesas': total_despesas,
            'carga_id': carga_id
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/assinatura/<int:carga_id>')
@login_required
def get_assinatura(carga_id):
    carga = Carga.query.get_or_404(carga_id)
    if carga.gerencia and carga.gerencia.assinatura:
        return carga.gerencia.assinatura
    return '', 404

@app.route('/atualizar_status/<int:carga_id>', methods=['POST'])
@login_required
def atualizar_status(carga_id):
    if not current_user.is_authenticated or current_user.role != 'gerencia':
        return jsonify({'success': False, 'message': 'Acesso não autorizado!'}), 403
    
    try:
        data = request.get_json()
        novo_status = data.get('status')
        
        if novo_status not in ['Em Andamento', 'Fechado']:
            return jsonify({'success': False, 'message': 'Status inválido!'}), 400
            
        carga = Carga.query.get_or_404(carga_id)
        carga.status = novo_status
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Status atualizado com sucesso!'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao atualizar status: {str(e)}'}), 500

def initialize_database():
    """Inicializa o banco de dados com as tabelas e dados iniciais"""
    try:
        with app.app_context():
            # Verifica se as tabelas já existem antes de criar
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            # Só cria as tabelas se não existirem
            if not existing_tables:
                db.create_all()
                print("Tabelas criadas com sucesso!")
            
            # Criar usuário admin se não existir
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(
                    username='admin',
                    role='admin',
                    nome='Administrador',
                    display_name='Administrador'
                )
                admin.set_password('admin')
                db.session.add(admin)
            
            # Criar usuário gerencia se não existir
            gerencia = User.query.filter_by(username='gerencia').first()
            if not gerencia:
                gerencia = User(
                    username='gerencia',
                    role='gerencia',
                    nome='Gerência',
                    display_name='Gerência'
                )
                gerencia.set_password('gerencia')
                db.session.add(gerencia)
            
            # Criar usuário logistica se não existir
            logistica = User.query.filter_by(username='logistica').first()
            if not logistica:
                logistica = User(
                    username='logistica',
                    role='logistica',
                    nome='Logística',
                    display_name='Logística'
                )
                logistica.set_password('logistica')
                db.session.add(logistica)
            
            # Criar usuário financeiro se não existir
            financeiro = User.query.filter_by(username='financeiro').first()
            if not financeiro:
                financeiro = User(
                    username='financeiro',
                    role='financeiro',
                    nome='Financeiro',
                    display_name='Financeiro'
                )
                financeiro.set_password('financeiro')
                db.session.add(financeiro)
            
            # Criar usuário operacional se não existir
            operacional = User.query.filter_by(username='operacional').first()
            if not operacional:
                operacional = User(
                    username='operacional',
                    role='operacional',
                    nome='Operacional',
                    display_name='Operacional'
                )
                operacional.set_password('operacional')
                db.session.add(operacional)
            
            # Criar usuário visualizador se não existir
            visualizador = User.query.filter_by(username='visualizador').first()
            if not visualizador:
                visualizador = User(
                    username='visualizador',
                    role='visualizador',
                    nome='Visualizador',
                    display_name='Visualizador'
                )
                visualizador.set_password('visualizador')
                db.session.add(visualizador)
            
            db.session.commit()
            print("Banco de dados inicializado com sucesso!")
            
    except Exception as e:
        print(f"Erro ao inicializar banco de dados: {str(e)}")
        traceback.print_exc()

socketio = SocketIO(app)

@socketio.on('connect')
def handle_connect():
    if current_user.is_authenticated:
        # Criar uma sala específica para o usuário
        socketio.join_room(f'user_{current_user.id}')

if __name__ == '__main__':
    initialize_database()
    socketio.run(app, host='10.0.0.222', port=3000, debug=True)
