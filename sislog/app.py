from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import requests
import json
from unidecode import unidecode

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fleet.db'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plate = db.Column(db.String(20), unique=True, nullable=False)
    model = db.Column(db.String(50), nullable=False)
    trips = db.relationship('Trip', back_populates='vehicle')

class Driver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    license_number = db.Column(db.String(20), unique=True, nullable=False)
    trips = db.relationship('Trip', back_populates='driver')

class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'), nullable=False)
    destination = db.Column(db.String(200), nullable=False)
    destination_lat = db.Column(db.Float)
    destination_lng = db.Column(db.Float)
    initial_km = db.Column(db.Float, nullable=False)
    final_km = db.Column(db.Float, nullable=False)
    fuel_liters = db.Column(db.Float, nullable=False)
    
    vehicle = db.relationship('Vehicle', back_populates='trips')
    driver = db.relationship('Driver', back_populates='trips')
    
    @property
    def total_km(self):
        return self.final_km - self.initial_km
    
    @property
    def fuel_consumption(self):
        if self.fuel_liters > 0:
            return self.total_km / self.fuel_liters
        return 0

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Usuário ou senha inválidos')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/veiculos')
@login_required
def veiculos():
    if not current_user.is_admin:
        flash('Acesso negado. Apenas administradores podem acessar esta página.')
        return redirect(url_for('dashboard'))
    veiculos = Vehicle.query.all()
    return render_template('veiculos.html', veiculos=veiculos)

@app.route('/veiculos/adicionar', methods=['POST'])
@login_required
def adicionar_veiculo():
    if not current_user.is_admin:
        return jsonify({'error': 'Acesso negado'}), 403
    
    data = request.json
    veiculo = Vehicle(
        plate=data['plate'],
        model=data['model']
    )
    db.session.add(veiculo)
    db.session.commit()
    return jsonify({'message': 'Veículo adicionado com sucesso'})

@app.route('/veiculos/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_veiculo(id):
    if not current_user.is_admin:
        return jsonify({'error': 'Acesso negado'}), 403
    
    veiculo = Vehicle.query.get_or_404(id)
    db.session.delete(veiculo)
    db.session.commit()
    return jsonify({'message': 'Veículo excluído com sucesso'})

@app.route('/veiculos/<int:id>', methods=['GET'])
@login_required
def obter_veiculo(id):
    veiculo = Vehicle.query.get_or_404(id)
    return jsonify({
        'id': veiculo.id,
        'plate': veiculo.plate,
        'model': veiculo.model
    })

@app.route('/veiculos/editar/<int:id>', methods=['POST'])
@login_required
def editar_veiculo(id):
    if not current_user.is_admin:
        return jsonify({'error': 'Acesso negado'}), 403
    
    veiculo = Vehicle.query.get_or_404(id)
    data = request.json
    veiculo.plate = data['plate']
    veiculo.model = data['model']
    db.session.commit()
    return jsonify({'message': 'Veículo atualizado com sucesso'})

@app.route('/motoristas')
@login_required
def motoristas():
    if not current_user.is_admin:
        flash('Acesso negado. Apenas administradores podem acessar esta página.')
        return redirect(url_for('dashboard'))
    motoristas = Driver.query.all()
    return render_template('motoristas.html', motoristas=motoristas)

@app.route('/motoristas/adicionar', methods=['POST'])
@login_required
def adicionar_motorista():
    if not current_user.is_admin:
        return jsonify({'error': 'Acesso negado'}), 403
    
    data = request.json
    motorista = Driver(
        name=data['name'],
        license_number=data['license']
    )
    db.session.add(motorista)
    db.session.commit()
    return jsonify({'message': 'Motorista adicionado com sucesso'})

@app.route('/motoristas/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_motorista(id):
    if not current_user.is_admin:
        return jsonify({'error': 'Acesso negado'}), 403
    
    motorista = Driver.query.get_or_404(id)
    db.session.delete(motorista)
    db.session.commit()
    return jsonify({'message': 'Motorista excluído com sucesso'})

@app.route('/motoristas/<int:id>', methods=['GET'])
@login_required
def obter_motorista(id):
    motorista = Driver.query.get_or_404(id)
    return jsonify({
        'id': motorista.id,
        'name': motorista.name,
        'license_number': motorista.license_number
    })

@app.route('/motoristas/editar/<int:id>', methods=['POST'])
@login_required
def editar_motorista(id):
    if not current_user.is_admin:
        return jsonify({'error': 'Acesso negado'}), 403
    
    motorista = Driver.query.get_or_404(id)
    data = request.json
    motorista.name = data['name']
    motorista.license_number = data['license']
    db.session.commit()
    return jsonify({'message': 'Motorista atualizado com sucesso'})

@app.route('/usuarios')
@login_required
def usuarios():
    if not current_user.is_admin:
        flash('Acesso negado. Apenas administradores podem acessar esta página.')
        return redirect(url_for('dashboard'))
    usuarios = User.query.all()
    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/usuarios/adicionar', methods=['POST'])
@login_required
def adicionar_usuario():
    if not current_user.is_admin:
        return jsonify({'error': 'Acesso negado'}), 403
    
    data = request.json
    usuario = User(
        username=data['username'],
        password_hash=generate_password_hash(data['password']),
        is_admin=data.get('is_admin', False)
    )
    db.session.add(usuario)
    db.session.commit()
    return jsonify({'message': 'Usuário adicionado com sucesso'})

@app.route('/usuarios/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_usuario(id):
    if not current_user.is_admin:
        return jsonify({'error': 'Acesso negado'}), 403
    
    if id == current_user.id:
        return jsonify({'error': 'Não é possível excluir seu próprio usuário'}), 400
    
    usuario = User.query.get_or_404(id)
    db.session.delete(usuario)
    db.session.commit()
    return jsonify({'message': 'Usuário excluído com sucesso'})

@app.route('/usuarios/<int:id>', methods=['GET'])
@login_required
def obter_usuario(id):
    if not current_user.is_admin:
        return jsonify({'error': 'Acesso negado'}), 403
    
    usuario = User.query.get_or_404(id)
    return jsonify({
        'id': usuario.id,
        'username': usuario.username,
        'is_admin': usuario.is_admin
    })

@app.route('/usuarios/editar/<int:id>', methods=['POST'])
@login_required
def editar_usuario(id):
    if not current_user.is_admin:
        return jsonify({'error': 'Acesso negado'}), 403
    
    usuario = User.query.get_or_404(id)
    data = request.json
    usuario.username = data['username']
    if data.get('password'):
        usuario.password_hash = generate_password_hash(data['password'])
    usuario.is_admin = data.get('is_admin', False)
    db.session.commit()
    return jsonify({'message': 'Usuário atualizado com sucesso'})

@app.route('/viagens')
@login_required
def viagens():
    viagens = Trip.query.all()
    veiculos = Vehicle.query.all()
    motoristas = Driver.query.all()
    return render_template('viagens.html', viagens=viagens, veiculos=veiculos, motoristas=motoristas)

@app.route('/viagens/adicionar', methods=['POST'])
@login_required
def adicionar_viagem():
    try:
        data = request.json
        
        # Validação dos dados
        required_fields = ['date', 'vehicle_id', 'driver_id', 'destination', 'initial_km', 'final_km', 'fuel_liters']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'Campo {field} é obrigatório'}), 400
        
        # Parse do destino
        try:
            destino = json.loads(data['destination'])
            if not isinstance(destino, dict) or 'nome' not in destino:
                return jsonify({'message': 'Formato do destino inválido'}), 400
        except json.JSONDecodeError:
            return jsonify({'message': 'Erro ao processar o destino'}), 400
        
        # Validação dos números
        try:
            initial_km = float(data['initial_km'])
            final_km = float(data['final_km'])
            fuel_liters = float(data['fuel_liters'])
            
            if final_km <= initial_km:
                return jsonify({'message': 'Quilometragem final deve ser maior que a inicial'}), 400
            
            if fuel_liters <= 0:
                return jsonify({'message': 'Quantidade de combustível deve ser maior que zero'}), 400
        except ValueError:
            return jsonify({'message': 'Valores numéricos inválidos'}), 400
        
        # Cria a viagem
        viagem = Trip(
            date=datetime.strptime(data['date'], '%Y-%m-%d'),
            vehicle_id=int(data['vehicle_id']),
            driver_id=int(data['driver_id']),
            destination=destino['nome'],
            destination_lat=float(destino.get('lat', 0)),
            destination_lng=float(destino.get('lng', 0)),
            initial_km=initial_km,
            final_km=final_km,
            fuel_liters=fuel_liters
        )
        
        db.session.add(viagem)
        db.session.commit()
        
        return jsonify({'message': 'Viagem adicionada com sucesso'})
    except Exception as e:
        db.session.rollback()
        print('Erro ao adicionar viagem:', str(e))  # Log do erro
        return jsonify({'message': 'Erro ao adicionar viagem'}), 500

@app.route('/viagens/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_viagem(id):
    if not current_user.is_admin:
        return jsonify({'error': 'Acesso negado'}), 403
    
    viagem = Trip.query.get_or_404(id)
    db.session.delete(viagem)
    db.session.commit()
    return jsonify({'message': 'Viagem excluída com sucesso'})

@app.route('/viagens/<int:id>', methods=['GET'])
@login_required
def obter_viagem(id):
    viagem = Trip.query.get_or_404(id)
    return jsonify({
        'id': viagem.id,
        'date': viagem.date.strftime('%Y-%m-%d'),
        'vehicle_id': viagem.vehicle_id,
        'driver_id': viagem.driver_id,
        'destination': json.dumps({
            'nome': viagem.destination,
            'lat': viagem.destination_lat,
            'lng': viagem.destination_lng
        }),
        'initial_km': viagem.initial_km,
        'final_km': viagem.final_km,
        'fuel_liters': viagem.fuel_liters
    })

@app.route('/viagens/editar/<int:id>', methods=['POST'])
@login_required
def editar_viagem(id):
    if not current_user.is_admin:
        return jsonify({'error': 'Acesso negado'}), 403
    
    viagem = Trip.query.get_or_404(id)
    data = request.json
    
    # Parse o destino que vem como string JSON
    destino = json.loads(data['destination'])
    
    viagem.date = datetime.strptime(data['date'], '%Y-%m-%d')
    viagem.vehicle_id = data['vehicle_id']
    viagem.driver_id = data['driver_id']
    viagem.destination = destino['nome']  # Salva apenas o nome da cidade
    viagem.destination_lat = destino['lat']
    viagem.destination_lng = destino['lng']
    viagem.initial_km = float(data['initial_km'])
    viagem.final_km = float(data['final_km'])
    viagem.fuel_liters = float(data['fuel_liters'])
    
    db.session.commit()
    return jsonify({'message': 'Viagem atualizada com sucesso'})

@app.route('/dashboard/filtros')
@login_required
def get_filtros():
    # Busca apenas destinos, veículos e motoristas que têm viagens registradas
    destinos = db.session.query(Trip.destination).distinct().all()
    veiculos = db.session.query(Vehicle).join(Trip).distinct().all()
    motoristas = db.session.query(Driver).join(Trip).distinct().all()
    
    return jsonify({
        'destinos': [d[0] for d in destinos],
        'veiculos': [{'id': v.id, 'plate': v.plate} for v in veiculos],
        'motoristas': [{'id': m.id, 'name': m.name} for m in motoristas]
    })

@app.route('/dashboard/dados')
@login_required
def dashboard_dados():
    # Pega os parâmetros dos filtros
    veiculo_id = request.args.get('veiculo')
    motorista_id = request.args.get('motorista')
    destino = request.args.get('destino')
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    
    # Query base
    query = Trip.query
    
    # Aplica os filtros
    if veiculo_id:
        query = query.filter(Trip.vehicle_id == veiculo_id)
    if motorista_id:
        query = query.filter(Trip.driver_id == motorista_id)
    if destino:
        query = query.filter(Trip.destination == destino)
    if data_inicio:
        query = query.filter(Trip.date >= datetime.strptime(data_inicio, '%Y-%m-%d'))
    if data_fim:
        query = query.filter(Trip.date <= datetime.strptime(data_fim, '%Y-%m-%d'))
    
    # Executa a query
    viagens = query.all()
    
    # Calcula totais
    total_km = sum(viagem.total_km for viagem in viagens)
    total_fuel = sum(viagem.fuel_liters for viagem in viagens)
    avg_consumption = total_km / total_fuel if total_fuel > 0 else 0

    # Dados para o gráfico de evolução
    dados_evolucao = []
    for viagem in sorted(viagens, key=lambda x: x.date):
        dados_evolucao.append({
            'data': viagem.date.strftime('%d/%m/%Y'),
            'consumo': viagem.fuel_consumption
        })

    # Dados para o gráfico de consumo por veículo
    consumo_por_veiculo = {}
    for viagem in viagens:
        placa = viagem.vehicle.plate
        if placa not in consumo_por_veiculo:
            consumo_por_veiculo[placa] = {
                'total_km': 0,
                'total_fuel': 0
            }
        consumo_por_veiculo[placa]['total_km'] += viagem.total_km
        consumo_por_veiculo[placa]['total_fuel'] += viagem.fuel_liters

    dados_veiculo = []
    for placa, dados in consumo_por_veiculo.items():
        consumo = dados['total_km'] / dados['total_fuel'] if dados['total_fuel'] > 0 else 0
        dados_veiculo.append({
            'veiculo': placa,
            'consumo': round(consumo, 2)
        })

    # Dados para o mapa
    dados_mapa = []
    for viagem in viagens:
        dados_mapa.append({
            'destino': viagem.destination,
            'lat': viagem.destination_lat,
            'lng': viagem.destination_lng
        })
    
    return jsonify({
        'total_km': round(total_km, 2),
        'avg_km': round(total_km / len(viagens), 2) if viagens else 0,
        'total_fuel': round(total_fuel, 2),
        'avg_consumption': round(avg_consumption, 2),
        'evolucao': dados_evolucao,
        'consumo_veiculo': dados_veiculo,
        'destinos': dados_mapa
    })

@app.route('/cidades')
def get_cidades():
    import requests
    import json
    from unidecode import unidecode
    
    # Verifica se já temos o arquivo de cidades em cache
    cache_file = 'cidades_cache.json'
    if os.path.exists(cache_file):
        with open(cache_file, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    
    # Se não tiver em cache, busca da API do IBGE
    url = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
    response = requests.get(url)
    
    if response.status_code == 200:
        cidades = []
        for municipio in response.json():
            # Busca coordenadas no OpenStreetMap
            cidade_nome = municipio['nome']
            estado_sigla = municipio['microrregiao']['mesorregiao']['UF']['sigla']
            nome_busca = f"{cidade_nome}, {estado_sigla}, Brazil"
            
            try:
                # Usa o Nominatim do OpenStreetMap para obter coordenadas
                nominatim_url = f"https://nominatim.openstreetmap.org/search?q={nome_busca}&format=json&limit=1"
                headers = {'User-Agent': 'Sistema de Controle de Frota/1.0'}
                coord_response = requests.get(nominatim_url, headers=headers)
                
                if coord_response.status_code == 200 and coord_response.json():
                    location = coord_response.json()[0]
                    cidades.append({
                        'id': municipio['id'],
                        'nome': f"{cidade_nome} - {estado_sigla}",
                        'latitude': float(location['lat']),
                        'longitude': float(location['lon'])
                    })
            except Exception as e:
                print(f"Erro ao buscar coordenadas para {nome_busca}: {str(e)}")
                continue
            
        # Salva em cache
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cidades, f, ensure_ascii=False)
        
        return jsonify(cidades)
    
    return jsonify([])

# Initialize the database
def init_db():
    with app.app_context():
        # Recria todas as tabelas
        db.drop_all()
        db.create_all()
        
        # Cria usuário admin se não existir
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', is_admin=True)
            admin.set_password('admin123')  # Volta para a senha original
            db.session.add(admin)
            db.session.commit()

if __name__ == '__main__':
    init_db()  # Recria o banco de dados
    app.run(debug=True, host='0.0.0.0', port=2000)
