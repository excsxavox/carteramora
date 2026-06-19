"""Resuelve rutas docsmora/destino por fecha de corte (MMDDYYYY)."""

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Optional, Set

from cobranzas.infrastructure.config.entregables_mensuales import (
    ruta_asignacion_desde_fecha_archivo,
)
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
    archivo_morosidad: Optional[Path]
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


# Nombres oficiales del core (HU): camorosico_{MMDDYYYY}_{HHMM}_of_0.lis
PATRONES_CAMOROSICO = (
    "camorosico_{fecha}_*_of_0.lis",
    "camorosico_{fecha}*.lis",
)

# cadetacaco_cie{MMDDYYYY}_{HHMM}_of_0.lis
PATRONES_CADETACACO = (
    "cadetacaco_cie{fecha}_*_of_0.lis",
    "cadetacaco_cie{fecha}*.lis",
)

# Compatibilidad con exportaciones antiguas (cobra en lugar de cie)
PATRONES_CADETACACO_LEGACY = (
    "cadetacaco_cobra{fecha}*_of_0.lis",
    "cadetacaco_cobra{fecha}*.lis",
)


def _mensaje_carpeta_inexistente(
    fecha_mmddyyyy: str,
    carpeta_lote: Path,
    directorio_docsmora: Optional[Path],
) -> str:
    sugerencia = ""
    if directorio_docsmora is not None:
        disponibles = _listar_fechas_lote_disponibles(directorio_docsmora)
        if disponibles:
            ultimas = ", ".join(disponibles[-5:])
            sugerencia = (
                f" Fechas con lote en docsmora: {ultimas}."
                f" Defina FECHA_CORTE en .env o envíe fecha en POST /pipeline."
            )
    return (
        f"No existe carpeta de lote para {fecha_mmddyyyy}: "
        f"{carpeta_lote.as_posix()}.{sugerencia}"
    )


def _buscar_lis_en_lote(
    carpeta_lote: Path,
    patrones: tuple[str, ...],
    fecha_mmddyyyy: str,
    descripcion: str,
    patrones_legacy: Optional[tuple[str, ...]] = None,
    directorio_docsmora: Optional[Path] = None,
    opcional: bool = False,
) -> Optional[Path]:
    if not carpeta_lote.is_dir():
        if opcional:
            return None
        raise FileNotFoundError(
            _mensaje_carpeta_inexistente(
                fecha_mmddyyyy, carpeta_lote, directorio_docsmora
            )
        )

    candidatos: list[Path] = []
    for plantilla in patrones:
        candidatos.extend(
            _candidatos_lis(carpeta_lote, plantilla.format(fecha=fecha_mmddyyyy))
        )

    if not candidatos and patrones_legacy:
        for plantilla in patrones_legacy:
            candidatos.extend(
                _candidatos_lis(
                    carpeta_lote, plantilla.format(fecha=fecha_mmddyyyy)
                )
            )

    if not candidatos:
        if opcional:
            return None
        ejemplos = ", ".join(
            p.format(fecha=fecha_mmddyyyy) for p in patrones[:2]
        )
        raise FileNotFoundError(
            f"No se encontró {descripcion} en {carpeta_lote.as_posix()} "
            f"(patrones: {ejemplos})"
        )

    candidatos = list({p.resolve(): p for p in candidatos}.values())
    candidatos.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidatos[0]


def resolver_rutas_cartera(
    directorio_docsmora: Path,
    directorio_destino: Path,
    fecha: Optional[date] = None,
    fecha_mmddyyyy: Optional[str] = None,
    feriados: Optional[Set[date]] = None,
    morosidad_opcional: bool = False,
) -> RutasCarteraDia:
    """
    Busca entradas y define salidas para la fecha indicada (hoy por defecto).

    Estructura:
      docsmora/2026/05042026/cartera05042026b/camorosico_05042026_2327_of_0.lis
      docsmora/2026/05042026/cartera05042026b/cadetacaco_cie05042026_0148_of_0.lis
      destino/2026/05042026/cartera05042026b/...
    """
    ftxt = fecha_mmddyyyy or fecha_corte_mmddyyyy(fecha)
    fecha_date = fecha or parsear_fecha_corte(ftxt)
    carpeta_entrada = carpeta_lote_docsmora(directorio_docsmora, ftxt)
    carpeta_salida = carpeta_lote_destino(directorio_destino, ftxt)
    carpeta_salida.mkdir(parents=True, exist_ok=True)
    archivo_asignacion = ruta_asignacion_desde_fecha_archivo(
        directorio_destino, fecha_date, feriados
    )
    carpeta_entregables = archivo_asignacion.parent
    carpeta_entregables.mkdir(parents=True, exist_ok=True)

    morosidad = _buscar_lis_en_lote(
        carpeta_entrada,
        PATRONES_CAMOROSICO,
        ftxt,
        "camorosico",
        directorio_docsmora=directorio_docsmora,
        opcional=morosidad_opcional,
    )
    cartera = _buscar_lis_en_lote(
        carpeta_entrada,
        PATRONES_CADETACACO,
        ftxt,
        "cadetacaco",
        patrones_legacy=PATRONES_CADETACACO_LEGACY,
        directorio_docsmora=directorio_docsmora,
    )

    return RutasCarteraDia(
        fecha_corte=ftxt,
        carpeta_lote=carpeta_entrada,
        archivo_morosidad=morosidad,
        archivo_cartera=cartera,
        archivo_salida_morosidad=carpeta_salida / "detalle_morosidad.lis",
        archivo_salida_mora=carpeta_salida / "reporte_mora.lis",
        archivo_salida_asignacion=archivo_asignacion,
    )
