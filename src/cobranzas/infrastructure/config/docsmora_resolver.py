"""Resuelve rutas docsmora/destino por fecha de corte (MMDDYYYY)."""

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Optional

from cobranzas.infrastructure.config.fecha_corte import (
    fecha_corte_mmddyyyy,
    parsear_fecha_corte,
)

__all__ = [
    "RutasCarteraDia",
    "carpeta_lote_destino",
    "carpeta_lote_docsmora",
    "fecha_corte_mmddyyyy",
    "parsear_fecha_corte",
    "resolver_rutas_cartera",
]


@dataclass(frozen=True)
class RutasCarteraDia:
    fecha_corte: str
    carpeta_lote: Path
    archivo_morosidad: Path
    archivo_cartera: Path
    archivo_salida_morosidad: Path
    archivo_salida_mora: Path
    archivo_salida_asignacion: Path


def carpeta_lote_docsmora(
    directorio_docsmora: Path,
    fecha_mmddyyyy: str,
) -> Path:
    """docsmora/{año}/{MMDDYYYY}/cartera{MMDDYYYY}b"""
    anio = fecha_mmddyyyy[4:8]
    return (
        directorio_docsmora
        / anio
        / fecha_mmddyyyy
        / f"cartera{fecha_mmddyyyy}b"
    )


def carpeta_lote_destino(
    directorio_destino: Path,
    fecha_mmddyyyy: str,
) -> Path:
    anio = fecha_mmddyyyy[4:8]
    return (
        directorio_destino
        / anio
        / fecha_mmddyyyy
        / f"cartera{fecha_mmddyyyy}b"
    )


def _listar_fechas_lote_disponibles(directorio_docsmora: Path) -> list[str]:
    """Fechas MMDDYYYY con carpeta cartera{fecha}b bajo docsmora/{año}/."""
    fechas: list[str] = []
    if not directorio_docsmora.is_dir():
        return fechas
    for carpeta_anio in directorio_docsmora.iterdir():
        if not carpeta_anio.is_dir():
            continue
        for carpeta_fecha in carpeta_anio.iterdir():
            if not carpeta_fecha.is_dir():
                continue
            nombre = carpeta_fecha.name
            if len(nombre) == 8 and nombre.isdigit():
                lote = carpeta_fecha / f"cartera{nombre}b"
                if lote.is_dir():
                    fechas.append(nombre)
    return sorted(set(fechas))


def _candidatos_lis(carpeta_lote: Path, patron: str) -> list[Path]:
    return [
        p
        for p in carpeta_lote.glob(patron)
        if p.is_file() and not p.name.startswith("~$")
    ]


def _buscar_lis_en_lote(
    carpeta_lote: Path,
    prefijo: str,
    fecha_mmddyyyy: str,
    directorio_docsmora: Optional[Path] = None,
) -> Path:
    if not carpeta_lote.is_dir():
        sugerencia = ""
        if directorio_docsmora is not None:
            disponibles = _listar_fechas_lote_disponibles(directorio_docsmora)
            if disponibles:
                ultimas = ", ".join(disponibles[-5:])
                sugerencia = (
                    f" Fechas con lote en docsmora: {ultimas}."
                    f" Defina FECHA_CORTE en .env o envíe fecha en POST /pipeline."
                )
        raise FileNotFoundError(
            f"No existe carpeta de lote para {fecha_mmddyyyy}: "
            f"{carpeta_lote.as_posix()}.{sugerencia}"
        )

    patrones_con_fecha = (
        f"{prefijo}*{fecha_mmddyyyy}*.lis",
        f"{prefijo}_*{fecha_mmddyyyy}*.lis",
        f"{prefijo}_cie{fecha_mmddyyyy}*.lis",
    )
    patrones_genericos = (
        f"{prefijo}*.lis",
        f"{prefijo}_*.lis",
        f"{prefijo}_cie*.lis",
    )

    candidatos: list[Path] = []
    for patron in patrones_con_fecha:
        candidatos.extend(_candidatos_lis(carpeta_lote, patron))

    if not candidatos:
        for patron in patrones_genericos:
            candidatos.extend(_candidatos_lis(carpeta_lote, patron))

    if not candidatos:
        raise FileNotFoundError(
            f"No se encontró {prefijo}*.lis en {carpeta_lote.as_posix()}"
        )

    candidatos = list({p.resolve(): p for p in candidatos}.values())
    candidatos.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidatos[0]


def resolver_rutas_cartera(
    directorio_docsmora: Path,
    directorio_destino: Path,
    fecha: Optional[date] = None,
    fecha_mmddyyyy: Optional[str] = None,
) -> RutasCarteraDia:
    """
    Busca entradas y define salidas para la fecha indicada (hoy por defecto).

    Estructura:
      docsmora/2026/05052026/cartera05052026b/camorosico_05052026_....lis
      destino/2026/05052026/cartera05052026b/...
    """
    ftxt = fecha_mmddyyyy or fecha_corte_mmddyyyy(fecha)
    carpeta_entrada = carpeta_lote_docsmora(directorio_docsmora, ftxt)
    carpeta_salida = carpeta_lote_destino(directorio_destino, ftxt)
    carpeta_salida.mkdir(parents=True, exist_ok=True)

    morosidad = _buscar_lis_en_lote(
        carpeta_entrada, "camorosico", ftxt, directorio_docsmora
    )
    cartera = _buscar_lis_en_lote(
        carpeta_entrada, "cadetacaco", ftxt, directorio_docsmora
    )

    return RutasCarteraDia(
        fecha_corte=ftxt,
        carpeta_lote=carpeta_entrada,
        archivo_morosidad=morosidad,
        archivo_cartera=cartera,
        archivo_salida_morosidad=carpeta_salida / "detalle_morosidad.lis",
        archivo_salida_mora=carpeta_salida / "reporte_mora.lis",
        archivo_salida_asignacion=carpeta_salida / "ASIGNACION.csv",
    )
