"""clean_invalid_dates

Revision ID: clean_invalid_dates
Revises: fix_dates
Create Date: 2025-02-10 09:17:16.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'clean_invalid_dates'
down_revision = 'fix_dates'
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
    
    # Copiar os dados, ignorando datas inválidas
    op.execute("""
        INSERT INTO logistica_temp (id, carga_id, descarga, data_entrega, observacoes, pendencias)
        SELECT 
            id, 
            carga_id, 
            descarga,
            CASE 
                WHEN data_entrega IS NULL THEN NULL
                WHEN data_entrega < '1900-01-01' THEN NULL
                WHEN data_entrega > '2100-01-01' THEN NULL
                ELSE date(data_entrega)
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
