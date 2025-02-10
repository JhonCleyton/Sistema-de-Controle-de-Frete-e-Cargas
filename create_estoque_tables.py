from app import app, db
from models.produto import Produto
from models.estoque import LocalArmazenagem, Estoque, HistoricoEstoque

with app.app_context():
    # Criar todas as tabelas
    db.create_all()
    
    # Criar locais de armazenagem iniciais
    locais = [
        LocalArmazenagem(nome='P&S', endereco='Rua Principal, 123'),
        LocalArmazenagem(nome='ESTRELA', endereco='Rua Secundária, 456'),
        LocalArmazenagem(nome='FRIOZEM', endereco='Rua Terceária, 789')
    ]
    
    for local in locais:
        try:
            db.session.add(local)
            db.session.commit()
            print(f'Local {local.nome} criado com sucesso!')
        except Exception as e:
            db.session.rollback()
            print(f'Erro ao criar local {local.nome}: {str(e)}')
