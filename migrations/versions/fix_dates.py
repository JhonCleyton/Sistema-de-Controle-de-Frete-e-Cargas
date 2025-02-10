"""fix_dates

Revision ID: fix_dates
Revises: c5cbc4be2cbb
Create Date: 2025-02-10 09:14:12.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'fix_dates'
down_revision = 'c5cbc4be2cbb'
branch_labels = None
depends_on = None

def upgrade():
    # Criar uma tabela temporária com a estrutura correta
    op.execute("""
        CREATE TABLE logistica_temp (
            id INTEGER PRIMARY KEY,
            carga_id INTEGER NOT NULL,
            descarga FLOAT,
            data_entrega DATE,
            observacoes TEXT,
            pendencias TEXT,
            FOREIGN KEY(carga_id) REFERENCES carga(id)
        )
    """)
    
    # Copiar os dados, convertendo as datas
    op.execute("""
        INSERT INTO logistica_temp (id, carga_id, descarga, data_entrega, observacoes, pendencias)
        SELECT 
            id, 
            carga_id, 
            descarga,
            CASE 
                WHEN data_entrega IS NOT NULL THEN date(data_entrega)
                ELSE NULL
            END,
            observacoes,
            pendencias
        FROM logistica
    """)
    
    # Remover a tabela antiga
    op.execute("DROP TABLE logistica")
    
    # Renomear a tabela temporária
    op.execute("ALTER TABLE logistica_temp RENAME TO logistica")

def downgrade():
    pass
