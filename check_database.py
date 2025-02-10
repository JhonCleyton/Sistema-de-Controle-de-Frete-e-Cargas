from app import app, db
from models.gerencia import Gerencia

def check_assinaturas():
    with app.app_context():
        # Busca todas as gerencias com assinatura
        gerencias = Gerencia.query.filter(Gerencia.assinatura.isnot(None)).all()
        
        print("\nGerencias com assinatura:")
        for g in gerencias:
            print(f"ID: {g.id}")
            print(f"Carga ID: {g.carga_id}")
            print(f"Assinatura: {g.assinatura}")
            print(f"Nome Assinatura: {g.nome_assinatura}")
            print("-" * 50)

if __name__ == '__main__':
    check_assinaturas()
