from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models.user import User
from models.veiculo import VeiculoSislog
from models.transportadora import Transportadora
from models.motorista import Motorista
from models.viagem import Viagem
from models.manutencao import Manutencao
from models.folga import Folga
from extensions import db
from datetime import datetime
from functools import wraps

sislog_bp = Blueprint('sislog', __name__, url_prefix='/sislog')

def logistica_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.role in ['logistica', 'admin']:
            flash('Acesso não autorizado.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@sislog_bp.route('/')
@login_required
@logistica_required
def index():
    # Obter informações para o dashboard
    folgas_ativas = Folga.query.filter_by(status='ativa').count()
    manutencoes_pendentes = Manutencao.query.filter_by(status='pendente').count()
    manutencoes_atrasadas = Manutencao.query.filter_by(status='atrasada').count()
    
    # Estatísticas de veículos
    veiculos_disponiveis = VeiculoSislog.query.filter_by(status='disponível').count()
    veiculos_em_viagem = VeiculoSislog.query.filter_by(status='em_viagem').count()
    veiculos_manutencao = VeiculoSislog.query.filter_by(status='manutencao').count()
    
    return render_template('sislog/index.html', 
                         folgas_ativas=folgas_ativas,
                         manutencoes_pendentes=manutencoes_pendentes,
                         manutencoes_atrasadas=manutencoes_atrasadas,
                         veiculos_disponiveis=veiculos_disponiveis,
                         veiculos_em_viagem=veiculos_em_viagem,
                         veiculos_manutencao=veiculos_manutencao)

@sislog_bp.route('/dashboard')
@login_required
def dashboard():
    veiculos = VeiculoSislog.query.all()
    return render_template('sislog/dashboard.html', veiculos=veiculos)

@sislog_bp.route('/motoristas')
@login_required
@logistica_required
def motoristas():
    motoristas = User.query.filter_by(role='motorista').all()
    return render_template('sislog/motoristas.html', motoristas=motoristas)

@sislog_bp.route('/motoristas/adicionar', methods=['POST'])
@login_required
@logistica_required
def adicionar_motorista():
    try:
        print("Recebendo requisição para adicionar motorista...")
        data = request.get_json()
        if not data:
            print("Dados inválidos")
            return jsonify({'error': 'Dados inválidos'}), 400
            
        nome = data.get('name')  # Recebe como 'name' do frontend
        license_number = data.get('license_number')
        
        print(f"Dados recebidos: nome={nome}, license_number={license_number}")
        
        if not nome or not license_number:
            print("Campos obrigatórios faltando")
            return jsonify({'error': 'Nome e CNH são obrigatórios'}), 400
            
        # Verificar se já existe um motorista com esta CNH
        motorista_existente = User.query.filter_by(license_number=license_number).first()
        if motorista_existente:
            print(f"Já existe motorista com CNH {license_number}")
            return jsonify({'error': 'Já existe um motorista com esta CNH'}), 400
            
        # Verificar se já existe um usuário com este username
        username = nome.lower().replace(' ', '_')
        user_existente = User.query.filter_by(username=username).first()
        if user_existente:
            # Se já existe, adiciona um número ao final
            base_username = username
            counter = 1
            while user_existente:
                username = f"{base_username}_{counter}"
                user_existente = User.query.filter_by(username=username).first()
                counter += 1
        
        # Criar novo usuário com role de motorista
        novo_motorista = User(
            username=username,
            nome=nome,
            role='motorista',
            display_name=nome,
            license_number=license_number,
            status='disponível'  # Status inicial
        )
        
        # Definir uma senha padrão (pode ser alterada depois)
        novo_motorista.set_password('123456')
        
        print("Adicionando novo motorista ao banco de dados...")
        db.session.add(novo_motorista)
        db.session.commit()
        print("Motorista adicionado com sucesso!")
        
        return jsonify({
            'success': True,
            'message': 'Motorista adicionado com sucesso',
            'data': novo_motorista.to_dict()
        })
            
    except Exception as e:
        print(f"Erro ao adicionar motorista: {str(e)}")
        db.session.rollback()
        return jsonify({
            'error': f'Erro ao adicionar motorista: {str(e)}'
        }), 500

@sislog_bp.route('/veiculos')
@login_required
@logistica_required
def veiculos():
    veiculos = VeiculoSislog.query.all()
    return render_template('sislog/veiculos.html', veiculos=veiculos)

@sislog_bp.route('/veiculos/adicionar', methods=['GET', 'POST'])
@login_required
@logistica_required
def adicionar_veiculo():
    if request.method == 'POST':
        try:
            # Obter dados do formulário
            placa = request.form.get('placa')
            modelo = request.form.get('modelo')
            marca = request.form.get('marca')
            ano = request.form.get('ano')
            capacidade = request.form.get('capacidade')
            tipo = request.form.get('tipo')
            status = request.form.get('status', 'disponível')  # Valor padrão se não fornecido
            
            # Validar dados
            if not all([placa, modelo, marca, ano, capacidade, tipo]):
                flash('Todos os campos são obrigatórios.', 'error')
                return redirect(url_for('sislog.adicionar_veiculo'))
            
            # Converter tipos
            try:
                ano = int(ano)
                capacidade = float(capacidade)
            except ValueError:
                flash('Ano e capacidade devem ser números válidos.', 'error')
                return redirect(url_for('sislog.adicionar_veiculo'))
            
            # Verificar se já existe um veículo com esta placa
            veiculo_existente = VeiculoSislog.query.filter_by(placa=placa).first()
            if veiculo_existente:
                flash('Já existe um veículo cadastrado com esta placa.', 'error')
                return redirect(url_for('sislog.adicionar_veiculo'))
            
            # Criar novo veículo
            novo_veiculo = VeiculoSislog(
                placa=placa,
                modelo=modelo,
                marca=marca,
                ano=ano,
                capacidade=capacidade,
                tipo=tipo,
                status=status
            )
            
            db.session.add(novo_veiculo)
            db.session.commit()
            
            flash('Veículo adicionado com sucesso!', 'success')
            return redirect(url_for('sislog.veiculos'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao adicionar veículo: {str(e)}', 'error')
            return redirect(url_for('sislog.adicionar_veiculo'))
    
    return render_template('sislog/adicionar_veiculo.html')

@sislog_bp.route('/viagens')
@login_required
@logistica_required
def viagens():
    viagens = Viagem.query.all()
    veiculos = VeiculoSislog.query.all()
    motoristas = User.query.filter_by(role='motorista').all()
    print("Motoristas encontrados:", [{"id": m.id, "nome": m.nome} for m in motoristas])  # Debug
    return render_template('sislog/viagens.html', 
                         viagens=viagens,
                         veiculos=veiculos,
                         motoristas=motoristas)

@sislog_bp.route('/viagens/adicionar', methods=['POST'])
@login_required
@logistica_required
def adicionar_viagem():
    if request.method == 'POST':
        try:
            # Converter a data do formato string para datetime
            date_str = request.form.get('date')
            date = datetime.strptime(date_str, '%Y-%m-%d')
            
            nova_viagem = Viagem(
                date=date,
                vehicle_id=request.form.get('vehicle_id'),
                driver_id=request.form.get('driver_id'),
                destination=request.form.get('destination'),
                initial_km=float(request.form.get('initial_km')),
                final_km=float(request.form.get('final_km')) if request.form.get('final_km') else None,
                fuel_liters=float(request.form.get('fuel_liters')) if request.form.get('fuel_liters') else None,
                fuel_cost=float(request.form.get('fuel_cost')) if request.form.get('fuel_cost') else None
            )
            
            db.session.add(nova_viagem)
            db.session.commit()
            flash('Viagem adicionada com sucesso!', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash('Erro ao adicionar viagem: ' + str(e), 'error')
            
        return redirect(url_for('sislog.viagens'))

@sislog_bp.route('/viagens/<int:id>', methods=['DELETE'])
@login_required
@logistica_required
def excluir_viagem(id):
    try:
        viagem = Viagem.query.get_or_404(id)
        db.session.delete(viagem)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@sislog_bp.route('/motoristas/<int:id>', methods=['DELETE'])
@login_required
@logistica_required
def excluir_motorista(id):
    try:
        motorista = User.query.filter_by(id=id, role='motorista').first()
        if not motorista:
            return jsonify({'error': 'Motorista não encontrado'}), 404
            
        db.session.delete(motorista)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Motorista excluído com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@sislog_bp.route('/veiculos/<int:id>', methods=['DELETE'])
@login_required
@logistica_required
def excluir_veiculo(id):
    try:
        veiculo = VeiculoSislog.query.get(id)
        if not veiculo:
            return jsonify({'error': 'Veículo não encontrado'}), 404
            
        db.session.delete(veiculo)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Veículo excluído com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# API Endpoints
@sislog_bp.route('/api/dashboard/stats')
@login_required
def get_dashboard_stats():
    try:
        # Obter parâmetros dos filtros
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        veiculo_id = request.args.get('veiculo_id')
        
        # Converter datas se fornecidas
        if data_inicio:
            data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
        if data_fim:
            data_fim = datetime.strptime(data_fim, '%Y-%m-%d')
            # Ajustar para o final do dia
            data_fim = data_fim.replace(hour=23, minute=59, second=59)
        
        # Base query para veículos
        veiculos_query = VeiculoSislog.query
        if veiculo_id:
            veiculos_query = veiculos_query.filter(VeiculoSislog.id == veiculo_id)
        veiculos = veiculos_query.all()
        total_veiculos = len(veiculos)
        
        # Query base para viagens
        viagens_base_query = Viagem.query
        if data_inicio:
            viagens_base_query = viagens_base_query.filter(Viagem.date >= data_inicio)
        if data_fim:
            viagens_base_query = viagens_base_query.filter(Viagem.date <= data_fim)
        if veiculo_id:
            viagens_base_query = viagens_base_query.filter(Viagem.vehicle_id == veiculo_id)
        
        # Veículos em viagem
        veiculos_em_viagem = viagens_base_query.filter(
            Viagem.final_km.is_(None)
        ).count()
        
        # Query base para manutenções
        manutencoes_base_query = Manutencao.query
        if data_inicio:
            manutencoes_base_query = manutencoes_base_query.filter(Manutencao.data_prevista >= data_inicio)
        if data_fim:
            manutencoes_base_query = manutencoes_base_query.filter(Manutencao.data_prevista <= data_fim)
        if veiculo_id:
            manutencoes_base_query = manutencoes_base_query.filter(Manutencao.veiculo_id == veiculo_id)
        
        # Veículos em manutenção
        veiculos_em_manutencao = manutencoes_base_query.filter(
            Manutencao.status.in_(['pendente', 'em_andamento'])
        ).count()
        
        veiculos_disponiveis = total_veiculos - veiculos_em_viagem - veiculos_em_manutencao

        # Dados para o gráfico de consumo médio por veículo
        consumo_por_veiculo = []
        for veiculo in veiculos:
            viagens = viagens_base_query.filter(
                Viagem.vehicle_id == veiculo.id,
                Viagem.final_km.isnot(None),
                Viagem.fuel_liters.isnot(None)
            ).all()
            
            if viagens:
                total_km = sum(v.final_km - v.initial_km for v in viagens)
                total_litros = sum(v.fuel_liters for v in viagens)
                if total_litros > 0:
                    consumo_medio = total_km / total_litros
                    consumo_por_veiculo.append({
                        'placa': veiculo.placa,
                        'consumo': round(consumo_medio, 2)
                    })

        # Dados para o gráfico de quilometragem por veículo
        km_por_veiculo = []
        for veiculo in veiculos:
            viagens = viagens_base_query.filter(
                Viagem.vehicle_id == veiculo.id,
                Viagem.final_km.isnot(None)
            ).all()
            
            total_km = sum(v.final_km - v.initial_km for v in viagens)
            km_por_veiculo.append({
                'placa': veiculo.placa,
                'km': round(total_km, 2)
            })

        # Dados para o gráfico de custos por veículo
        custos_por_veiculo = []
        for veiculo in veiculos:
            # Custos de combustível
            viagens = viagens_base_query.filter(
                Viagem.vehicle_id == veiculo.id,
                Viagem.fuel_cost.isnot(None)
            ).all()
            custo_combustivel = sum(v.fuel_cost for v in viagens)
            
            # Custos de manutenção
            manutencoes = manutencoes_base_query.filter(
                Manutencao.veiculo_id == veiculo.id,
                Manutencao.custo.isnot(None)
            ).all()
            custo_manutencao = sum(m.custo for m in manutencoes)
            
            custos_por_veiculo.append({
                'placa': veiculo.placa,
                'combustivel': round(custo_combustivel, 2),
                'manutencao': round(custo_manutencao, 2),
                'total': round(custo_combustivel + custo_manutencao, 2)
            })

        return jsonify({
            'status': 'success',
            'data': {
                'frota': {
                    'total': total_veiculos,
                    'em_viagem': veiculos_em_viagem,
                    'em_manutencao': veiculos_em_manutencao,
                    'disponiveis': veiculos_disponiveis
                },
                'consumo_por_veiculo': consumo_por_veiculo,
                'km_por_veiculo': km_por_veiculo,
                'custos_por_veiculo': custos_por_veiculo
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
