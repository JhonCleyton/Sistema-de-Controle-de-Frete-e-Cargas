from app import app, db
from models.chat import Mensagem

with app.app_context():
    # SQLite não suporta ALTER COLUMN, então vamos recriar a tabela
    db.session.execute('''
    CREATE TABLE mensagens_new (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        remetente_id INTEGER NOT NULL,
        destinatario_id INTEGER,
        conteudo TEXT NOT NULL,
        data_envio DATETIME NOT NULL,
        lida BOOLEAN NOT NULL,
        tipo VARCHAR(20) NOT NULL,
        FOREIGN KEY(remetente_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY(destinatario_id) REFERENCES users(id) ON DELETE CASCADE
    )
    ''')
    
    # Copiar dados da tabela antiga
    db.session.execute('''
    INSERT INTO mensagens_new 
    SELECT * FROM mensagens
    ''')
    
    # Remover tabela antiga
    db.session.execute('DROP TABLE mensagens')
    
    # Renomear nova tabela
    db.session.execute('ALTER TABLE mensagens_new RENAME TO mensagens')
    
    db.session.commit()
