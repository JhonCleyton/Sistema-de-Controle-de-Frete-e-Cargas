from extensions import db
from models.devolucao import Devolucao
from flask import Flask
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def test_model():
    with app.app_context():
        try:
            # Tentar buscar uma devolução
            devolucao = Devolucao.query.first()
            if devolucao:
                print("Devolução encontrada:")
                print(f"ID: {devolucao.id}")
                print(f"Número da Carga: {devolucao.numero_carga}")
                print(f"Quantidade de Embalagens: {devolucao.qtd_embalagens}")
                print(f"Tipo de Movimento: {devolucao.tipo_movimento}")
                print(f"Aprovado: {devolucao.aprovado}")
            else:
                print("Nenhuma devolução encontrada no banco de dados")
                
        except Exception as e:
            print(f"Erro ao testar modelo: {str(e)}")

if __name__ == '__main__':
    test_model()
