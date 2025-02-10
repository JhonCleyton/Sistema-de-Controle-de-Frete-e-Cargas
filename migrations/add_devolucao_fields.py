from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import os

# Configurar o caminho do projeto
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(project_dir, 'database.db')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

def upgrade():
    # Criar uma tabela temporária com a nova estrutura
    db.session.execute(text('''
        CREATE TABLE devolucoes_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_carga VARCHAR(20) NOT NULL,
            numero_nfe VARCHAR(50) NOT NULL,
            data_devolucao DATETIME NOT NULL,
            tipo_movimento VARCHAR(10),
            transportadora_id INTEGER NOT NULL,
            qtd_embalagens INTEGER DEFAULT 0,
            peso_devolvido FLOAT NOT NULL,
            valor_mercadoria FLOAT NOT NULL,
            tipo_mercadoria VARCHAR(100) NOT NULL,
            aprovado BOOLEAN NOT NULL DEFAULT FALSE,
            data_aprovacao DATETIME,
            aprovado_por VARCHAR(100),
            observacoes TEXT,
            FOREIGN KEY(transportadora_id) REFERENCES transportadoras(id) ON DELETE CASCADE
        )
    '''))
    
    # Copiar os dados da tabela antiga para a nova
    db.session.execute(text('''
        INSERT INTO devolucoes_new (
            id, numero_carga, numero_nfe, data_devolucao, tipo_movimento,
            transportadora_id, qtd_embalagens, peso_devolvido, valor_mercadoria,
            tipo_mercadoria, aprovado, data_aprovacao, aprovado_por, observacoes
        )
        SELECT 
            id, numero_carga, numero_nfe, data_devolucao, tipo_movimento,
            transportadora_id, qtd_embalagens, peso_devolvido, valor_mercadoria,
            tipo_mercadoria, aprovado, data_aprovacao, aprovado_por, observacoes
        FROM devolucoes
    '''))
    
    # Remover a tabela antiga
    db.session.execute(text('DROP TABLE devolucoes'))
    
    # Renomear a nova tabela
    db.session.execute(text('ALTER TABLE devolucoes_new RENAME TO devolucoes'))
    
    db.session.commit()
    print("Migração concluída com sucesso!")

def downgrade():
    # Se precisar reverter a migração
    db.session.execute(text('''
        CREATE TABLE devolucoes_old (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_carga VARCHAR(50) NOT NULL,
            data_devolucao DATETIME NOT NULL,
            numero_nfe VARCHAR(50) NOT NULL,
            peso_devolvido FLOAT NOT NULL,
            valor_mercadoria FLOAT NOT NULL,
            tipo_mercadoria VARCHAR(100) NOT NULL,
            qtd_embalagens INTEGER DEFAULT 0,
            tipo_movimento VARCHAR(10),
            aprovado BOOLEAN NOT NULL DEFAULT FALSE,
            data_aprovacao DATETIME,
            aprovado_por VARCHAR(100),
            observacoes TEXT,
            transportadora_id INTEGER NOT NULL,
            FOREIGN KEY(transportadora_id) REFERENCES transportadoras(id) ON DELETE CASCADE
        )
    '''))
    
    # Copiar os dados de volta
    db.session.execute(text('''
        INSERT INTO devolucoes_old (
            id, numero_carga, data_devolucao, numero_nfe, peso_devolvido,
            valor_mercadoria, tipo_mercadoria, qtd_embalagens, tipo_movimento,
            aprovado, data_aprovacao, aprovado_por, observacoes, transportadora_id
        )
        SELECT 
            id, numero_carga, data_devolucao, numero_nfe, peso_devolvido,
            valor_mercadoria, tipo_mercadoria, qtd_embalagens, tipo_movimento,
            aprovado, data_aprovacao, aprovado_por, observacoes, transportadora_id
        FROM devolucoes
    '''))
    
    # Remover a tabela nova
    db.session.execute(text('DROP TABLE devolucoes'))
    
    # Renomear a tabela antiga
    db.session.execute(text('ALTER TABLE devolucoes_old RENAME TO devolucoes'))
    
    db.session.commit()
    print("Downgrade concluído com sucesso!")

if __name__ == '__main__':
    with app.app_context():
        upgrade()
