"""create tables clientes pedidos detalles_pedido

Revision ID: a1b2c3d4e5f6
Revises: 431b92af8bdb
Create Date: 2026-02-24 02:50:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '431b92af8bdb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Enum estado_pedido (idempotente: no falla si ya existe) ─────────────
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE estado_pedido_enum AS ENUM ('pendiente', 'en_bodega', 'enviado');
        EXCEPTION
            WHEN duplicate_object THEN NULL;
        END $$;
    """)

    # ── Tabla clientes ──────────────────────────────────────────────────────
    op.create_table(
        'clientes',
        sa.Column('id',         postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('nombre',     sa.String(150),  nullable=False),
        sa.Column('telefono',   sa.String(30),   nullable=False),
        sa.Column('email',      sa.String(254),  nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_clientes_email',    'clientes', ['email'])
    op.create_index('ix_clientes_telefono', 'clientes', ['telefono'])

    # ── Tabla pedidos ───────────────────────────────────────────────────────
    # Usamos postgresql.ENUM con create_type=False para que SQLAlchemy
    # NO intente crear el tipo (ya lo creamos arriba con DO $$)
    estado_type = postgresql.ENUM(
        'pendiente', 'en_bodega', 'enviado',
        name='estado_pedido_enum',
        create_type=False,
    )
    op.create_table(
        'pedidos',
        sa.Column('id',          postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('cliente_id',  postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('clientes.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('estado',      estado_type, nullable=False),
        sa.Column('subtotal_usd', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('total_usd',    sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('valor_dolar',  sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('total_clp',    sa.Numeric(precision=14, scale=0), nullable=False),
        sa.Column('created_at',   sa.DateTime(timezone=True),        nullable=False),
    )
    op.create_index('ix_pedidos_cliente_id', 'pedidos', ['cliente_id'])
    op.create_index('ix_pedidos_estado',     'pedidos', ['estado'])
    op.create_index('ix_pedidos_created_at', 'pedidos', ['created_at'])

    # ── Tabla detalles_pedido ───────────────────────────────────────────────
    op.create_table(
        'detalles_pedido',
        sa.Column('id',                  postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('pedido_id',           postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('pedidos.id', ondelete='CASCADE'), nullable=False),
        sa.Column('nombre_producto',     sa.String(255),               nullable=False),
        sa.Column('cantidad',            sa.Integer(),                 nullable=False),
        sa.Column('precio_base_usd',     sa.Numeric(precision=12, scale=4), nullable=False),
        sa.Column('porcentaje_tax',      sa.Numeric(precision=5,  scale=2), nullable=False),
        sa.Column('porcentaje_comision', sa.Numeric(precision=5,  scale=2), nullable=False),
        sa.Column('tax_usd',             sa.Numeric(precision=12, scale=4), nullable=False),
        sa.Column('comision_usd',        sa.Numeric(precision=12, scale=4), nullable=False),
        sa.Column('precio_final_usd',    sa.Numeric(precision=12, scale=4), nullable=False),
        sa.Column('subtotal_usd',        sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('created_at',          sa.DateTime(timezone=True),        nullable=False),
    )
    op.create_index('ix_detalles_pedido_pedido_id',       'detalles_pedido', ['pedido_id'])
    op.create_index('ix_detalles_pedido_nombre_producto', 'detalles_pedido', ['nombre_producto'])


def downgrade() -> None:
    op.drop_table('detalles_pedido')
    op.drop_table('pedidos')
    op.drop_table('clientes')
    op.execute("DROP TYPE IF EXISTS estado_pedido_enum")
