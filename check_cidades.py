from app import app, db
from models.cidade import Cidade

with app.app_context():
    cidades = Cidade.query.all()
    print(f"Total de cidades: {len(cidades)}")
    if len(cidades) > 0:
        print(f"Primeira cidade: {cidades[0].nome}")
        print(f"Última cidade: {cidades[-1].nome}")
