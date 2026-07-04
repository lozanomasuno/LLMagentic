"""CLI script — seed PostgreSQL with affiliate data from BD_afiliados.xlsx."""

from __future__ import annotations

import argparse
import asyncio
import datetime
import logging
import sys
from pathlib import Path

import openpyxl
from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert

from app.config.settings import get_settings  # noqa: F401 (triggers .env load)
from app.core.database import AsyncSessionLocal
from app.domain.models.affiliate import Affiliate
from app.domain.models import affiliate, consultation, log  # noqa: F401

logger = logging.getLogger(__name__)

# Maps Excel "Sí"/"No" strings to Python booleans
_BOOL: dict[str | None, bool | None] = {
    "Sí": True,
    "Si": True,
    "SÍ": True,
    "No": False,
    "NO": False,
    "": None,
    None: None,
}


def _parse_date(value: object) -> datetime.date | None:
    if value is None:
        return None
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    if isinstance(value, str) and value.strip():
        try:
            return datetime.date.fromisoformat(value.strip())
        except ValueError:
            return None
    return None


def _map_row(headers: tuple, row: tuple) -> dict:
    d: dict = dict(zip(headers, row))
    return {
        "id_afiliado": d["id_afiliado"],
        "tipo_documento": d.get("tipo_documento"),
        "numero_documento": str(d["numero_documento"]),
        "primer_nombre": d.get("primer_nombre"),
        "primer_apellido": d.get("primer_apellido"),
        "segundo_apellido": d.get("segundo_apellido"),
        "sexo": d.get("sexo"),
        "fecha_nacimiento": _parse_date(d.get("fecha_nacimiento")),
        "edad": d.get("edad"),
        "ciudad": d.get("ciudad"),
        "departamento": d.get("departamento"),
        "tipo_afiliado": d.get("tipo_afiliado"),
        "parentesco": d.get("parentesco"),
        "plan": d.get("plan"),
        "fecha_afiliacion": _parse_date(d.get("fecha_afiliacion")),
        "antiguedad_meses": d.get("antiguedad_meses"),
        "estado_afiliacion": d.get("estado_afiliacion"),
        "estado_pagos": d.get("estado_pagos"),
        "dias_mora": int(d.get("dias_mora") or 0),
        "valor_pendiente_cop": int(d.get("valor_pendiente_cop") or 0),
        "tiene_autorizacion_previa": _BOOL.get(d.get("tiene_autorizacion_previa")),
        "servicio_autorizado": d.get("servicio_autorizado"),
        "numero_autorizacion": d.get("numero_autorizacion"),
        "fecha_autorizacion": _parse_date(d.get("fecha_autorizacion")),
        "vigencia_autorizacion": _parse_date(d.get("vigencia_autorizacion")),
        "preexistencia_declarada": _BOOL.get(d.get("preexistencia_declarada")),
        "descripcion_preexistencia": d.get("descripcion_preexistencia"),
        "correo_contacto": d.get("correo_contacto"),
        "telefono_contacto": (
            str(d["telefono_contacto"]) if d.get("telefono_contacto") else None
        ),
    }


def _load_records(file_path: Path) -> list[dict]:
    wb = openpyxl.load_workbook(file_path, data_only=True)
    ws = wb["Afiliados"]
    rows = list(ws.iter_rows(values_only=True))
    headers: tuple = rows[0]
    return [_map_row(headers, row) for row in rows[1:] if row[0] is not None]


async def seed(file_path: Path, truncate: bool = False) -> int:
    """Load records from Excel and upsert into the affiliates table."""
    records = _load_records(file_path)
    if not records:
        logger.error("No records found in %s", file_path)
        return 0

    async with AsyncSessionLocal() as session:
        if truncate:
            await session.execute(delete(Affiliate))
            await session.commit()
            logger.info("Affiliates table truncated")

        stmt = insert(Affiliate).values(records)
        upsert_stmt = stmt.on_conflict_do_update(
            index_elements=["id_afiliado"],
            set_={
                col: stmt.excluded[col]
                for col in records[0]
                if col != "id_afiliado"
            },
        )
        await session.execute(upsert_stmt)
        await session.commit()

    logger.info("Seeded %d affiliates from %s", len(records), file_path)
    return len(records)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s — %(message)s")

    parser = argparse.ArgumentParser(description="Seed affiliates table from Excel")
    parser.add_argument(
        "--file",
        type=Path,
        default=Path("data/BD_afiliados.xlsx"),
        help="Path to BD_afiliados.xlsx",
    )
    parser.add_argument(
        "--truncate",
        action="store_true",
        help="Truncate the table before inserting",
    )
    args = parser.parse_args()

    if not args.file.exists():
        print(f"ERROR: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    count = asyncio.run(seed(args.file, truncate=args.truncate))
    print(f"✓ Seeded {count} affiliates")


if __name__ == "__main__":
    main()
