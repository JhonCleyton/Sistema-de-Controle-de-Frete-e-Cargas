// Funções para atualizar o dashboard
async function updateDashboardData() {
    try {
        // Constrói a URL com os filtros
        const params = new URLSearchParams();
        
        const veiculo = document.getElementById('veiculo_filtro')?.value;
        const motorista = document.getElementById('motorista_filtro')?.value;
        const destino = document.getElementById('destino_filtro')?.value;
        const dataInicio = document.getElementById('data_inicio')?.value;
        const dataFim = document.getElementById('data_fim')?.value;
        
        if (veiculo) params.append('veiculo', veiculo);
        if (motorista) params.append('motorista', motorista);
        if (destino) params.append('destino', destino);
        if (dataInicio) params.append('data_inicio', dataInicio);
        if (dataFim) params.append('data_fim', dataFim);
        
        const response = await fetch(`/dashboard/dados?${params.toString()}`);
        const data = await response.json();
        
        // Atualiza cards
        const elements = {
            'totalKm': data.total_km.toFixed(2),
            'avgKm': data.avg_km.toFixed(2),
            'totalFuel': data.total_fuel.toFixed(2),
            'avgConsumption': data.avg_consumption.toFixed(2)
        };

        for (const [id, value] of Object.entries(elements)) {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        }

        // Atualiza gráfico de evolução
        const consumptionCtx = document.getElementById('consumptionChart');
        if (consumptionCtx) {
            const chart = Chart.getChart(consumptionCtx);
            if (chart) {
                chart.destroy();
            }

            new Chart(consumptionCtx, {
                type: 'line',
                data: {
                    labels: data.evolucao.map(item => item.data),
                    datasets: [{
                        label: 'Consumo Médio (km/L)',
                        data: data.evolucao.map(item => item.consumo),
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }

        // Atualiza gráfico de consumo por veículo
        const vehicleCtx = document.getElementById('vehicleConsumptionChart');
        if (vehicleCtx) {
            const chart = Chart.getChart(vehicleCtx);
            if (chart) {
                chart.destroy();
            }

            new Chart(vehicleCtx, {
                type: 'pie',
                data: {
                    labels: data.consumo_veiculo.map(item => item.veiculo),
                    datasets: [{
                        data: data.consumo_veiculo.map(item => item.consumo),
                        backgroundColor: [
                            'rgb(255, 99, 132)',
                            'rgb(54, 162, 235)',
                            'rgb(255, 205, 86)',
                            'rgb(75, 192, 192)',
                            'rgb(153, 102, 255)'
                        ]
                    }]
                },
                options: {
                    responsive: true
                }
            });
        }

        // Atualiza mapa
        atualizarMapa(data.destinos);
    } catch (error) {
        console.error('Erro ao atualizar dashboard:', error);
    }
}

// Variável global para armazenar a instância do mapa
let tripMap = null;

// Função para atualizar o mapa
function atualizarMapa(destinos) {
    const mapElement = document.getElementById('tripMap');
    if (mapElement) {
        // Se já existe um mapa, remove ele
        if (tripMap) {
            tripMap.remove();
            tripMap = null;
        }
        
        // Cria novo mapa
        tripMap = L.map('tripMap').setView([-14.235, -51.925], 4);
        
        // Adiciona o layer do OpenStreetMap
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(tripMap);

        // Cria um grupo para os marcadores
        const markers = L.featureGroup();
        
        // Adiciona marcadores
        destinos.forEach(destino => {
            if (destino.lat && destino.lng) {
                // Cria um círculo vermelho como marcador
                const marker = L.circleMarker([destino.lat, destino.lng], {
                    radius: 8,
                    fillColor: "#ff4444",
                    color: "#000",
                    weight: 1,
                    opacity: 1,
                    fillOpacity: 0.8
                });
                
                // Adiciona popup com o nome do destino
                marker.bindPopup(destino.destino);
                markers.addLayer(marker);
            }
        });
        
        // Adiciona os marcadores ao mapa
        markers.addTo(tripMap);
        
        // Ajusta o zoom para mostrar todos os marcadores
        if (markers.getLayers().length > 0) {
            tripMap.fitBounds(markers.getBounds(), { padding: [50, 50] });
        }
    }
}

async function carregarFiltros() {
    try {
        const response = await fetch('/dashboard/filtros');
        const data = await response.json();
        
        // Preenche os selects
        const selectVeiculo = document.getElementById('veiculo_filtro');
        const selectMotorista = document.getElementById('motorista_filtro');
        const selectDestino = document.getElementById('destino_filtro');
        
        if (selectVeiculo) {
            data.veiculos.forEach(veiculo => {
                const option = document.createElement('option');
                option.value = veiculo.id;
                option.textContent = veiculo.plate;
                selectVeiculo.appendChild(option);
            });
        }
        
        if (selectMotorista) {
            data.motoristas.forEach(motorista => {
                const option = document.createElement('option');
                option.value = motorista.id;
                option.textContent = motorista.name;
                selectMotorista.appendChild(option);
            });
        }
        
        if (selectDestino) {
            data.destinos.forEach(destino => {
                const option = document.createElement('option');
                option.value = destino;
                option.textContent = destino;
                selectDestino.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Erro ao carregar filtros:', error);
    }
}

function aplicarFiltros() {
    updateDashboardData();
}

function limparFiltros() {
    // Limpa os campos
    document.getElementById('data_inicio').value = '';
    document.getElementById('data_fim').value = '';
    document.getElementById('veiculo_filtro').value = '';
    document.getElementById('motorista_filtro').value = '';
    document.getElementById('destino_filtro').value = '';
    
    // Atualiza o dashboard
    updateDashboardData();
}

// Função para carregar cidades
async function carregarCidades() {
    try {
        const response = await fetch('/cidades');
        const cidades = await response.json();
        
        const select = document.getElementById('destination');
        if (select) {
            select.innerHTML = '<option value="">Selecione uma cidade</option>';
            
            cidades.forEach(cidade => {
                const option = document.createElement('option');
                option.value = JSON.stringify({
                    nome: cidade.nome,
                    lat: cidade.lat,
                    lng: cidade.lng
                });
                option.textContent = cidade.nome;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Erro ao carregar cidades:', error);
    }
}

async function salvarVeiculo() {
    const plate = document.getElementById('plate').value;
    const model = document.getElementById('model').value;

    try {
        const response = await fetch('/veiculos/adicionar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ plate, model })
        });

        const data = await response.json();
        if (response.ok) {
            alert('Veículo salvo com sucesso!');
            window.location.reload();
        } else {
            alert(data.error || 'Erro ao salvar veículo');
        }
    } catch (error) {
        alert('Erro ao salvar veículo');
        console.error(error);
    }
}

async function salvarMotorista() {
    const name = document.getElementById('name').value;
    const license = document.getElementById('license').value;

    try {
        const response = await fetch('/motoristas/adicionar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, license })
        });

        const data = await response.json();
        if (response.ok) {
            alert('Motorista salvo com sucesso!');
            window.location.reload();
        } else {
            alert(data.error || 'Erro ao salvar motorista');
        }
    } catch (error) {
        alert('Erro ao salvar motorista');
        console.error(error);
    }
}

async function salvarUsuario() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const isAdmin = document.getElementById('isAdmin').checked;

    try {
        const response = await fetch('/usuarios/adicionar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password, is_admin: isAdmin })
        });

        const data = await response.json();
        if (response.ok) {
            alert('Usuário salvo com sucesso!');
            window.location.reload();
        } else {
            alert(data.error || 'Erro ao salvar usuário');
        }
    } catch (error) {
        alert('Erro ao salvar usuário');
        console.error(error);
    }
}

async function salvarViagem() {
    try {
        const date = document.getElementById('date').value;
        const vehicle = document.getElementById('vehicle').value;
        const driver = document.getElementById('driver').value;
        const destination = document.getElementById('destination').value;
        const initial_km = document.getElementById('initial_km').value;
        const final_km = document.getElementById('final_km').value;
        const fuel_liters = document.getElementById('fuel_liters').value;
        
        // Validação básica
        if (!date || !vehicle || !driver || !destination || !initial_km || !final_km || !fuel_liters) {
            alert('Por favor, preencha todos os campos');
            return;
        }
        
        // Converte os valores para números
        const initialKm = parseFloat(initial_km);
        const finalKm = parseFloat(final_km);
        const fuelLiters = parseFloat(fuel_liters);
        
        // Validação dos números
        if (finalKm <= initialKm) {
            alert('Quilometragem final deve ser maior que a inicial');
            return;
        }
        
        if (fuelLiters <= 0) {
            alert('Quantidade de combustível deve ser maior que zero');
            return;
        }
        
        // Parse do destino
        let destinoObj;
        try {
            destinoObj = JSON.parse(destination);
        } catch (e) {
            alert('Erro ao processar o destino selecionado');
            return;
        }
        
        const data = {
            date: date,
            vehicle_id: vehicle,
            driver_id: driver,
            destination: JSON.stringify(destinoObj),
            initial_km: initialKm,
            final_km: finalKm,
            fuel_liters: fuelLiters
        };
        
        const response = await fetch('/viagens/adicionar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('addTripModal'));
            modal.hide();
            window.location.reload();
        } else {
            const error = await response.json();
            alert(error.message || 'Erro ao salvar viagem');
        }
    } catch (error) {
        console.error('Erro ao salvar viagem:', error);
        alert('Erro ao salvar viagem. Verifique o console para mais detalhes.');
    }
}

async function editarVeiculo(id) {
    try {
        const response = await fetch(`/veiculos/${id}`);
        const veiculo = await response.json();
        
        document.getElementById('plate').value = veiculo.plate;
        document.getElementById('model').value = veiculo.model;
        
        const modal = new bootstrap.Modal(document.getElementById('addVehicleModal'));
        modal.show();
        
        const btnSalvar = document.querySelector('#addVehicleModal .btn-primary');
        btnSalvar.onclick = async () => {
            const data = {
                plate: document.getElementById('plate').value,
                model: document.getElementById('model').value
            };
            
            const response = await fetch(`/veiculos/editar/${id}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            if (response.ok) {
                modal.hide();
                window.location.reload();
            } else {
                alert('Erro ao editar veículo');
            }
        };
    } catch (error) {
        console.error('Erro ao carregar veículo:', error);
    }
}

async function editarMotorista(id) {
    try {
        const response = await fetch(`/motoristas/${id}`);
        const motorista = await response.json();
        
        document.getElementById('name').value = motorista.name;
        document.getElementById('license').value = motorista.license_number;
        
        const modal = new bootstrap.Modal(document.getElementById('addDriverModal'));
        modal.show();
        
        const btnSalvar = document.querySelector('#addDriverModal .btn-primary');
        btnSalvar.onclick = async () => {
            const data = {
                name: document.getElementById('name').value,
                license: document.getElementById('license').value
            };
            
            const response = await fetch(`/motoristas/editar/${id}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            if (response.ok) {
                modal.hide();
                window.location.reload();
            } else {
                alert('Erro ao editar motorista');
            }
        };
    } catch (error) {
        console.error('Erro ao carregar motorista:', error);
    }
}

async function editarUsuario(id) {
    try {
        const response = await fetch(`/usuarios/${id}`);
        const usuario = await response.json();
        
        document.getElementById('username').value = usuario.username;
        document.getElementById('password').value = '';
        document.getElementById('is_admin').checked = usuario.is_admin;
        
        const modal = new bootstrap.Modal(document.getElementById('addUserModal'));
        modal.show();
        
        const btnSalvar = document.querySelector('#addUserModal .btn-primary');
        btnSalvar.onclick = async () => {
            const data = {
                username: document.getElementById('username').value,
                password: document.getElementById('password').value,
                is_admin: document.getElementById('is_admin').checked
            };
            
            const response = await fetch(`/usuarios/editar/${id}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            if (response.ok) {
                modal.hide();
                window.location.reload();
            } else {
                alert('Erro ao editar usuário');
            }
        };
    } catch (error) {
        console.error('Erro ao carregar usuário:', error);
    }
}

async function editarViagem(id) {
    try {
        const response = await fetch(`/viagens/${id}`);
        const viagem = await response.json();
        
        document.getElementById('date').value = viagem.date;
        document.getElementById('vehicle').value = viagem.vehicle_id;
        document.getElementById('driver').value = viagem.driver_id;
        
        // Parse o destino salvo
        const destino = JSON.parse(viagem.destination);
        document.getElementById('destination').value = JSON.stringify({
            nome: destino.nome,
            lat: destino.lat,
            lng: destino.lng
        });
        
        document.getElementById('initial_km').value = viagem.initial_km;
        document.getElementById('final_km').value = viagem.final_km;
        document.getElementById('fuel_liters').value = viagem.fuel_liters;
        
        // Atualiza o consumo médio
        calcularConsumo();
        
        const modal = new bootstrap.Modal(document.getElementById('addTripModal'));
        modal.show();
        
        // Remove o evento anterior se existir
        const btnSalvar = document.querySelector('#addTripModal .btn-primary');
        btnSalvar.onclick = null;
        
        // Adiciona o novo evento
        btnSalvar.onclick = async () => {
            const destinoSelecionado = JSON.parse(document.getElementById('destination').value);
            
            const data = {
                date: document.getElementById('date').value,
                vehicle_id: document.getElementById('vehicle').value,
                driver_id: document.getElementById('driver').value,
                destination: JSON.stringify(destinoSelecionado),
                initial_km: document.getElementById('initial_km').value,
                final_km: document.getElementById('final_km').value,
                fuel_liters: document.getElementById('fuel_liters').value
            };
            
            const response = await fetch(`/viagens/editar/${id}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            if (response.ok) {
                modal.hide();
                window.location.reload();
            } else {
                alert('Erro ao editar viagem');
            }
        };
    } catch (error) {
        console.error('Erro ao carregar viagem:', error);
    }
}

// Funções para excluir registros
async function excluirVeiculo(id) {
    if (confirm('Tem certeza que deseja excluir este veículo?')) {
        try {
            const response = await fetch(`/veiculos/excluir/${id}`, {
                method: 'POST'
            });
            
            if (response.ok) {
                window.location.reload();
            } else {
                alert('Erro ao excluir veículo');
            }
        } catch (error) {
            console.error('Erro ao excluir veículo:', error);
        }
    }
}

async function excluirMotorista(id) {
    if (confirm('Tem certeza que deseja excluir este motorista?')) {
        try {
            const response = await fetch(`/motoristas/excluir/${id}`, {
                method: 'POST'
            });
            
            if (response.ok) {
                window.location.reload();
            } else {
                alert('Erro ao excluir motorista');
            }
        } catch (error) {
            console.error('Erro ao excluir motorista:', error);
        }
    }
}

async function excluirUsuario(id) {
    if (confirm('Tem certeza que deseja excluir este usuário?')) {
        try {
            const response = await fetch(`/usuarios/excluir/${id}`, {
                method: 'POST'
            });
            
            if (response.ok) {
                window.location.reload();
            } else {
                const data = await response.json();
                alert(data.error || 'Erro ao excluir usuário');
            }
        } catch (error) {
            console.error('Erro ao excluir usuário:', error);
        }
    }
}

async function excluirViagem(id) {
    if (confirm('Tem certeza que deseja excluir esta viagem?')) {
        try {
            const response = await fetch(`/viagens/excluir/${id}`, {
                method: 'POST'
            });
            
            if (response.ok) {
                window.location.reload();
            } else {
                alert('Erro ao excluir viagem');
            }
        } catch (error) {
            console.error('Erro ao excluir viagem:', error);
        }
    }
}

// Funções para o formulário de viagem
function calcularKmRodados() {
    const kmInicial = parseFloat(document.getElementById('initial_km').value) || 0;
    const kmFinal = parseFloat(document.getElementById('final_km').value) || 0;
    const kmRodados = kmFinal - kmInicial;
    
    // Atualiza o campo de km rodados se existir
    const kmRodadosElement = document.getElementById('km_rodados');
    if (kmRodadosElement) {
        kmRodadosElement.value = kmRodados.toFixed(2);
    }

    // Calcula consumo médio se tiver o campo de litros preenchido
    const litros = parseFloat(document.getElementById('fuel_liters').value) || 0;
    const consumoMedio = litros > 0 ? kmRodados / litros : 0;
    
    const consumoMedioElement = document.getElementById('consumo_medio');
    if (consumoMedioElement) {
        consumoMedioElement.value = consumoMedio.toFixed(2);
    }
}

// Função para calcular o consumo médio
function calcularConsumo() {
    const initialKm = parseFloat(document.getElementById('initial_km').value) || 0;
    const finalKm = parseFloat(document.getElementById('final_km').value) || 0;
    const fuelLiters = parseFloat(document.getElementById('fuel_liters').value) || 0;
    
    const totalKm = finalKm - initialKm;
    const consumo = fuelLiters > 0 ? totalKm / fuelLiters : 0;
    
    document.getElementById('consumo').value = consumo.toFixed(2);
}

// Inicialização quando o documento estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    // Atualiza dados do dashboard se estiver na página correta
    if (document.getElementById('totalKm')) {
        carregarFiltros();
        updateDashboardData();
    }

    // Carrega cidades
    carregarCidades();

    // Adiciona listeners aos botões de salvar
    const btnSalvarVeiculo = document.querySelector('#addVehicleModal .btn-primary');
    if (btnSalvarVeiculo) {
        btnSalvarVeiculo.addEventListener('click', salvarVeiculo);
    }

    const btnSalvarMotorista = document.querySelector('#addDriverModal .btn-primary');
    if (btnSalvarMotorista) {
        btnSalvarMotorista.addEventListener('click', salvarMotorista);
    }

    const btnSalvarUsuario = document.querySelector('#addUserModal .btn-primary');
    if (btnSalvarUsuario) {
        btnSalvarUsuario.addEventListener('click', salvarUsuario);
    }

    const btnSalvarViagem = document.querySelector('#addTripModal .btn-primary');
    if (btnSalvarViagem) {
        btnSalvarViagem.addEventListener('click', salvarViagem);
    }

    // Adiciona listeners para cálculo automático de km rodados
    const kmInicial = document.getElementById('initial_km');
    const kmFinal = document.getElementById('final_km');
    const litros = document.getElementById('fuel_liters');

    if (kmInicial && kmFinal) {
        kmInicial.addEventListener('input', calcularKmRodados);
        kmFinal.addEventListener('input', calcularKmRodados);
        if (litros) {
            litros.addEventListener('input', calcularKmRodados);
        }
    }
});
