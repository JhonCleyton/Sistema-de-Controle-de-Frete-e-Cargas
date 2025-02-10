"""Criar tabelas do sistema de estoque

Revision ID: estoque_tables
Revises: None
Create Date: 2025-01-28 15:21:21.000000

"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Criar tabela de produtos
    op.create_table(
        'produtos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('codigo', sa.String(length=50), nullable=False),
        sa.Column('nome', sa.String(length=100), nullable=False),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.Column('unidade_medida', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('codigo')
    )

    # Criar tabela de locais de armazenagem
    op.create_table(
        'locais_armazenagem',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(length=100), nullable=False),
        sa.Column('endereco', sa.String(length=200), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Criar tabela de estoque
    op.create_table(
        'estoques',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('produto_id', sa.Integer(), nullable=False),
        sa.Column('local_id', sa.Integer(), nullable=False),
        sa.Column('quantidade', sa.Float(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['local_id'], ['locais_armazenagem.id'], ),
        sa.ForeignKeyConstraint(['produto_id'], ['produtos.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Criar tabela de histórico de estoque
    op.create_table(
        'historico_estoque',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('produto_id', sa.Integer(), nullable=False),
        sa.Column('local_id', sa.Integer(), nullable=False),
        sa.Column('quantidade', sa.Float(), nullable=False),
        sa.Column('tipo_movimento', sa.String(length=20), nullable=False),
        sa.Column('observacao', sa.Text(), nullable=True),
        sa.Column('data_movimento', sa.DateTime(), nullable=False),
        sa.Column('usuario_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['local_id'], ['locais_armazenagem.id'], ),
        sa.ForeignKeyConstraint(['produto_id'], ['produtos.id'], ),
        sa.ForeignKeyConstraint(['usuario_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('historico_estoque')
    op.drop_table('estoques')
    op.drop_table('locais_armazenagem')
    op.drop_table('produtos')
