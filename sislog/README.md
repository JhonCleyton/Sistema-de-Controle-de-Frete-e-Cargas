# Sistema de Controle de Frota

Sistema web para monitoramento de consumo médio de combustível de frota.

## Funcionalidades

- Login com níveis de acesso (admin e usuário comum)
- Cadastro de veículos e motoristas
- Registro de viagens com:
  - Data
  - Veículo
  - Motorista
  - Origem/Destino
  - Quilometragem
  - Abastecimento
- Dashboard com:
  - Indicadores de consumo
  - Gráficos de evolução
  - Mapa de destinos
  - Filtros personalizados

## Instalação

1. Instale o Python 3.8 ou superior
2. Clone este repositório
3. Crie um ambiente virtual:
```bash
python -m venv venv
```

4. Ative o ambiente virtual:
```bash
venv\Scripts\activate
```

5. Instale as dependências:
```bash
pip install -r requirements.txt
```

6. Execute a aplicação:
```bash
python app.py
```

7. Acesse http://localhost:5000 no navegador

## Credenciais Iniciais

- Usuário: admin
- Senha: admin123

## Tecnologias Utilizadas

- Backend: Python/Flask
- Frontend: HTML, CSS, JavaScript
- Banco de Dados: SQLite
- Bibliotecas:
  - Chart.js para gráficos
  - Leaflet.js para mapas
  - Bootstrap para interface
