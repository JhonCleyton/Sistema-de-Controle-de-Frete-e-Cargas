from extensions import db

class Cidade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'latitude': self.latitude,
            'longitude': self.longitude
        }
