from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models.carga import Carga
from models.motorista import Motorista
from models.cidade import Cidade
from models.transportadora import Transportadora
from models.cliente import Cliente
from extensions import db, cache
from sqlalchemy import func, and_
from datetime import datetime
import traceback
from functools import wraps

relatorios_bp = Blueprint('relatorios', __name__)

def gerencia_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Não autenticado'}), 401
        if current_user.role != 'gerencia':
            return jsonify({'error': 'Acesso negado'}), 403
        return f(*args, **kwargs)
    return decorated_function

@relatorios_bp.route('/relatorios')
@login_required
def index():
    return render_template('gerencia/relatorios.html')

@relatorios_bp.route('/api/relatorios/dados')
@login_required
def get_dados_relatorio():
    try:
        if not current_user.is_authenticated:
            return jsonify({'error': 'Não autenticado'}), 401
            
        # Obter datas do filtro
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        cidade = request.args.get('cidade')
        transportadora = request.args.get('transportadora')
        cliente = request.args.get('cliente')
        status = request.args.get('status')
        
        print(f"[{current_user.username}] Filtros: data_inicio={data_inicio}, data_fim={data_fim}, cidade={cidade}, transportadora={transportadora}, cliente={cliente}, status={status}")
        
        # Query base com joins otimizados
        query = db.session.query(Carga).options(
            db.joinedload(Carga.romaneios),
            db.joinedload(Carga.controle_frete),
            db.joinedload(Carga.gerencia)
        )
        
        # Aplicar filtros
        if data_inicio and data_fim:
            data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
            data_fim = datetime.strptime(data_fim, '%Y-%m-%d')
            query = query.filter(Carga.data_saida >= data_inicio, Carga.data_saida <= data_fim)
        
        if cidade and cidade != "Todas as cidades":
            query = query.filter(Carga.rota.like(f'%{cidade}%'))
        if transportadora:
            query = query.filter(Carga.transportadora_id == transportadora)
        if cliente and cliente != "Todos os clientes":
            query = query.filter(Carga.cliente_id == cliente)
        if status and status != "Todos os status":
            query = query.filter(Carga.status == status)
            
        # Executar a query principal
        cargas = query.all()
        print(f"[{current_user.username}] Total de cargas encontradas: {len(cargas)}")
        
        # Se não houver resultados, retornar zeros
        if not cargas:
            return jsonify({
                'frete': {'media': 0, 'total': 0},
                'valor_por_kg': 0,
                'valor_por_km': 0,
                'diarias': {'media': 0, 'total': 0},
                'total_entregas_adicionais': 0,
                'resumo_kg': {'total': 0, 'media': 0, 'minimo': 0, 'maximo': 0},
                'localizacoes': [],
                'evolucao': [],
                'status': {'Em andamento': 0, 'Concluído': 0, 'Cancelado': 0}
            })
        
        # Inicializar variáveis para métricas
        total_frete = 0
        total_peso = 0
        total_km = 0
        total_diarias = 0
        total_extras = 0
        pesos = []
        
        # Dicionário para contagem de status
        status_count = {'Em andamento': 0, 'Concluído': 0, 'Cancelado': 0}
        
        # Dicionário para evolução diária
        evolucao_diaria = {}
        
        # Calcular métricas
        for carga in cargas:
            # Contagem de status
            if carga.status in status_count:
                status_count[carga.status] += 1
            
            # Evolução diária
            data_saida = carga.data_saida.strftime('%Y-%m-%d') if carga.data_saida else None
            if data_saida:
                if data_saida not in evolucao_diaria:
                    evolucao_diaria[data_saida] = 0
                evolucao_diaria[data_saida] += 1
            
            if carga.controle_frete:
                total_frete += float(carga.controle_frete.valor_frete or 0)
                total_km += float(carga.controle_frete.km_rodados or 0)
                total_extras += float(carga.controle_frete.entrega_extra or 0)
            
            if carga.gerencia:
                total_diarias += float(carga.gerencia.diarias or 0)
            
            for romaneio in carga.romaneios:
                if romaneio and romaneio.peso_bruto:
                    peso = float(romaneio.peso_bruto)
                    total_peso += peso
                    pesos.append(peso)
        
        num_cargas = len(cargas)
        
        # Preparar dados de evolução
        evolucao = []
        for data in sorted(evolucao_diaria.keys()):
            evolucao.append({
                'data': data,
                'quantidade': evolucao_diaria[data]
            })
        
        # Calcular médias e estatísticas
        valor_medio_frete = total_frete / num_cargas if num_cargas > 0 else 0
        valor_medio_kg = total_frete / total_peso if total_peso > 0 else 0
        valor_medio_km = total_frete / total_km if total_km > 0 else 0
        valor_medio_diaria = total_diarias / num_cargas if num_cargas > 0 else 0
        peso_medio = sum(pesos) / len(pesos) if pesos else 0
        peso_minimo = min(pesos) if pesos else 0
        peso_maximo = max(pesos) if pesos else 0
        
        # Preparar dados para localização
        localizacoes = []
        cidades_db = {cidade.nome: cidade for cidade in Cidade.query.all()}
        
        for carga in cargas:
            if carga.rota:
                cidades = [cidade.strip() for cidade in carga.rota.split(',')]
                for cidade_nome in cidades:
                    cidade = cidades_db.get(cidade_nome)
                    if cidade and cidade.latitude and cidade.longitude:
                        # Verificar se já existe um marcador para esta cidade
                        cidade_existe = False
                        for loc in localizacoes:
                            if loc['cidade'] == cidade_nome:
                                if str(carga.id) not in loc['cargas']:
                                    loc['cargas'].append(str(carga.id))
                                cidade_existe = True
                                break
                        
                        if not cidade_existe:
                            localizacoes.append({
                                'lat': cidade.latitude,
                                'lng': cidade.longitude,
                                'cidade': cidade_nome,
                                'cargas': [str(carga.id)]
                            })
        
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
            'localizacoes': localizacoes,
            'evolucao': evolucao,
            'status': status_count
        }
        
        print(f"[{current_user.username}] Dados calculados com sucesso:", response_data)
        return jsonify(response_data)
    
    except Exception as e:
        print(f"[{current_user.username}] Erro ao gerar relatórios: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@relatorios_bp.route('/api/relatorios/cidades')
@login_required
def get_cidades():
    try:
        cidades = db.session.query(Cidade.nome).distinct().all()
        return jsonify({'data': [c[0] for c in cidades if c[0]]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@relatorios_bp.route('/api/relatorios/clientes')
@login_required
def get_clientes():
    try:
        clientes = db.session.query(Cliente.nome).distinct().all()
        return jsonify({'data': [c[0] for c in clientes if c[0]]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@relatorios_bp.route('/api/relatorios/transportadoras')
@login_required
def get_transportadoras():
    try:
        transportadoras = db.session.query(Transportadora.nome).distinct().all()
        return jsonify({'data': [t[0] for t in transportadoras if t[0]]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@relatorios_bp.route('/api/relatorios/clientes-list')
@login_required
@gerencia_required
def get_clientes_list():
    try:
        print("Iniciando busca de clientes...")
        clientes = db.session.query(
            Cliente.id,
            Cliente.nome,
            Cliente.codigo
        ).all()
        
        print(f"Encontrados {len(clientes)} clientes")
        
        resultado = [{
            'id': cliente.id,
            'nome': cliente.nome,
            'codigo': cliente.codigo
        } for cliente in clientes]
        
        return jsonify(resultado)
    except Exception as e:
        print(f"Erro ao carregar clientes: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': f"Erro ao carregar clientes: {str(e)}"}), 500
