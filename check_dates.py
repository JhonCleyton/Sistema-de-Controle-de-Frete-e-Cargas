from app import app, db
from models.logistica import Logistica
from datetime import datetime

with app.app_context():
    print('Dados da logística:')
    for l in Logistica.query.all():
        print(f'ID: {l.id}, Data: {l.data_entrega}, Tipo: {type(l.data_entrega)}')
