"""Convierte los .lis del lote (camorosico + cadetacaco) a Excel (.xlsx).

Independiente del pipeline: no limpia, no fusiona, no asigna ni persiste.
"""

import logging
from pathlib import Path
from typing import List, Optional

from cobranzas.domain.models.lis_excel_run_result import (
    ArchivoConvertido,
    LisExcelRunResult,
)
from cobranzas.infrastructure.adapters.lis_excel_writer import LisExcelWriter
from cobranzas.infrastructure.config.fecha_corte import fecha_corte_mmddyyyy
from cobranzas.infrastructure.config.settings import Settings
from cobranzas.jobs.pipeline_runner import build_settings
from cobranzas.jobs.runner import _configure_logging

logger = logging.getLogger("cobranzas.lis_excel")

SUBCARPETA_DESTINO = "excel_lis"


def ejecutar_lis_a_excel(
    fecha: Optional[str] = None,
    settings: Optional[Settings] = None,
    configurar_logs: bool = True,
) -> LisExcelRunResult:
    """
    Convierte camorosico + cadetacaco del lote de ``fecha`` a .xlsx en
    ``destino/excel_lis/`` (un Excel por archivo, mismo nombre base).
    """
    cfg = settings or build_settings(fecha)
    if configurar_logs:
        _configure_logging(cfg.log_level)

    fecha_txt = cfg.fecha_corte or fecha_corte_mmddyyyy()
    salida_dir = cfg.directorio_destino / SUBCARPETA_DESTINO
    writer = LisExcelWriter()

    # (etiqueta, ruta) — camorosico y cadetacaco del lote.
    origenes = (
        ("camorosico", cfg.archivo_morosidad),
        ("cadetacaco", cfg.archivo_cartera),
    )

    convertidos: List[ArchivoConvertido] = []
    faltantes: List[str] = []
    for etiqueta, origen in origenes:
        if origen is None or not Path(origen).is_file():
            faltantes.append(f"{etiqueta}={origen}")
            logger.warning("LIS→Excel | %s no encontrado: %s", etiqueta, origen)
            continue
        ruta = Path(origen)
        destino = salida_dir / f"{ruta.stem}.xlsx"
        filas = writer.convertir(ruta, destino)
        convertidos.append(ArchivoConvertido(str(ruta), str(destino), filas))
        logger.info("LIS→Excel | %s | %s → %s | filas=%s", etiqueta, ruta, destino, filas)

    if not convertidos:
        msg = f"No se encontraron .lis para la fecha {fecha_txt}: {faltantes}"
        logger.error(msg)
        return LisExcelRunResult(
            ok=False, codigo_salida=1, fecha=fecha_txt, archivos=(), mensajes=(msg,)
        )

    mensajes = tuple(f"No encontrado: {f}" for f in faltantes)
    logger.info(
        "LIS→Excel OK | fecha=%s | convertidos=%s | destino=%s",
        fecha_txt,
        len(convertidos),
        salida_dir,
    )
    return LisExcelRunResult(
        ok=True,
        codigo_salida=0,
        fecha=fecha_txt,
        archivos=tuple(convertidos),
        mensajes=mensajes,
    )


def main() -> int:
    return ejecutar_lis_a_excel().codigo_salida


if __name__ == "__main__":
    raise SystemExit(main())
