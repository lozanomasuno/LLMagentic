"""initial_schema

Revision ID: d8f24a01d6ad
Revises: 
Create Date: 2026-07-03 18:51:03.675360

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd8f24a01d6ad'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- affiliates ---
    op.create_table(
        "affiliates",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("id_afiliado", sa.String(length=50), nullable=False),
        sa.Column("tipo_documento", sa.String(length=10), nullable=True),
        sa.Column("numero_documento", sa.String(length=30), nullable=False),
        sa.Column("primer_nombre", sa.String(length=100), nullable=True),
        sa.Column("primer_apellido", sa.String(length=100), nullable=True),
        sa.Column("segundo_apellido", sa.String(length=100), nullable=True),
        sa.Column("sexo", sa.String(length=1), nullable=True),
        sa.Column("fecha_nacimiento", sa.Date(), nullable=True),
        sa.Column("edad", sa.Integer(), nullable=True),
        sa.Column("ciudad", sa.String(length=100), nullable=True),
        sa.Column("departamento", sa.String(length=100), nullable=True),
        sa.Column("tipo_afiliado", sa.String(length=50), nullable=True),
        sa.Column("parentesco", sa.String(length=50), nullable=True),
        sa.Column("plan", sa.String(length=50), nullable=True),
        sa.Column("fecha_afiliacion", sa.Date(), nullable=True),
        sa.Column("antiguedad_meses", sa.Integer(), nullable=True),
        sa.Column("estado_afiliacion", sa.String(length=30), nullable=True),
        sa.Column("estado_pagos", sa.String(length=30), nullable=True),
        sa.Column("dias_mora", sa.Integer(), nullable=True),
        sa.Column("valor_pendiente_cop", sa.BigInteger(), nullable=True),
        sa.Column("tiene_autorizacion_previa", sa.Boolean(), nullable=True),
        sa.Column("servicio_autorizado", sa.String(length=200), nullable=True),
        sa.Column("numero_autorizacion", sa.String(length=50), nullable=True),
        sa.Column("fecha_autorizacion", sa.Date(), nullable=True),
        sa.Column("vigencia_autorizacion", sa.Date(), nullable=True),
        sa.Column("preexistencia_declarada", sa.Boolean(), nullable=True),
        sa.Column("descripcion_preexistencia", sa.Text(), nullable=True),
        sa.Column("correo_contacto", sa.String(length=200), nullable=True),
        sa.Column("telefono_contacto", sa.String(length=30), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id_afiliado"),
        sa.UniqueConstraint("numero_documento"),
    )
    op.create_index("ix_affiliates_id_afiliado", "affiliates", ["id_afiliado"])
    op.create_index("ix_affiliates_numero_documento", "affiliates", ["numero_documento"])
    op.create_index("ix_affiliates_plan", "affiliates", ["plan"])
    op.create_index("ix_affiliates_estado_afiliacion", "affiliates", ["estado_afiliacion"])
    op.create_index("ix_affiliates_estado_pagos", "affiliates", ["estado_pagos"])

    # --- consultations ---
    op.create_table(
        "consultations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("affiliate_id", sa.Integer(), nullable=False),
        sa.Column("query_text", sa.Text(), nullable=False),
        sa.Column("response_text", sa.Text(), nullable=True),
        sa.Column("coverage_result", sa.String(length=50), nullable=True),
        sa.Column("sources_used", sa.JSON(), nullable=True),
        sa.Column("agent_trace", sa.JSON(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["affiliate_id"], ["affiliates.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_consultations_coverage_result", "consultations", ["coverage_result"])

    # --- logs ---
    op.create_table(
        "logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("level", sa.String(length=20), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("module", sa.String(length=200), nullable=True),
        sa.Column("extra", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_logs_level", "logs", ["level"])
    op.create_index("ix_logs_module", "logs", ["module"])
    op.create_index("ix_logs_created_at", "logs", ["created_at"])


def downgrade() -> None:
    op.drop_table("logs")
    op.drop_table("consultations")
    op.drop_index("ix_affiliates_estado_pagos", table_name="affiliates")
    op.drop_index("ix_affiliates_estado_afiliacion", table_name="affiliates")
    op.drop_index("ix_affiliates_plan", table_name="affiliates")
    op.drop_index("ix_affiliates_numero_documento", table_name="affiliates")
    op.drop_index("ix_affiliates_id_afiliado", table_name="affiliates")
    op.drop_table("affiliates")
