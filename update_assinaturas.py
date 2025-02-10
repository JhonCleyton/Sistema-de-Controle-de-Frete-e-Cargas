from app import app, db
from models.gerencia import Gerencia

def update_assinaturas():
    with app.app_context():
        # Busca todas as gerencias com assinatura
        gerencias = Gerencia.query.filter(Gerencia.assinatura.isnot(None)).all()
        
        for g in gerencias:
            # Troca os valores
            nome_antigo = g.assinatura
            g.assinatura = 'X'
            g.nome_assinatura = nome_antigo
        
        db.session.commit()
        print("Assinaturas atualizadas com sucesso!")

if __name__ == '__main__':
    update_assinaturas()
