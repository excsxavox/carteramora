"""Seguimiento de un crédito (ID Recblue u operación core) en el pipeline."""

from __future__ import annotations

import argparse
import csv
import logging
import sys
from datetime import date
from pathlib import Path
from typing import List, Optional, Sequence

from cobranzas.domain.models.credito import Credito
from cobranzas.domain.services.cartera_merge_service import CarteraMergeService
from cobranzas.domain.services.dias_habiles_service import (
    clasificar_mora_camorosico,
)
from cobranzas.domain.services.mora_temprana_service import (
    MoraTempranaService,
    debe_excluir_operacion,
    dia_pago_desde_credito,
    dias_atraso_camorosico,
)
from cobranzas.domain.services.resolver_reglas_mora_service import (
    ResolverReglasMoraService,
)
from cobranzas.infrastructure.adapters.cuadro_morosidad_parser import (
    leer_cuadro_morosidad,
)
from cobranzas.infrastructure.adapters.recblue_archivo_adapter import (
    RecblueArchivoAdapter,
)
from cobranzas.infrastructure.adapters.te_detallado_cartera_parser import (
    leer_te_detallado_cartera,
)
from cobranzas.infrastructure.config.docsmora_resolver import resolver_rutas_cartera
from cobranzas.infrastructure.config.entregables_mensuales import (
    ruta_asignacion_desde_fecha_archivo,
)
from cobranzas.infrastructure.config.fecha_corte import parsear_fecha_corte
from cobranzas.infrastructure.config.settings import Settings
from cobranzas.jobs.pipeline_runner import build_settings
from cobranzas.infrastructure.persistence.database import create_engine_from_settings
from cobranzas.infrastructure.persistence.repositories.feriados_calendario_repository import (
    SqlAlchemyFeriadosCalendarioRepository,
)
from cobranzas.infrastructure.persistence.repositories.reglas_repository import (
    SqlAlchemyReglasRepository,
)
from cobranzas.jobs.runner import _configure_logging

logger = logging.getLogger("cobranzas.seguir_credito")


def _buscar_credito(
    creditos: Sequence[Credito], numero_operacion: str
) -> Optional[Credito]:
    op = numero_operacion.strip()
    for credito in creditos:
        if credito.id_credito.strip() == op:
            return credito
    return None


def _leer_asignacion(ruta: Path, id_recblue: str) -> List[dict]:
    if not ruta.is_file():
        return []
    filas = []
    with ruta.open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            id_col = (row.get("ID_CREDITO") or row.get("id_credito") or "").strip()
            if id_col.replace(".0", "") == id_recblue.replace(".0", ""):
                filas.append(dict(row))
    return filas


def _imprimir_credito(etiqueta: str, credito: Credito) -> None:
    print(f"  [{etiqueta}]")
    print(f"    operacion core : {credito.id_credito}")
    print(f"    cliente        : {credito.cliente}")
    print(f"    estado         : {credito.estado_operacion}")
    print(f"    tipo oper      : {credito.tipo_operacion}")
    print(f"    dias_atraso CAMOROSICO (S): {credito.dias_mora}")
    print(f"    saldo          : {credito.saldo_pendiente}")
    print(f"    dia_pago (AG)  : {dia_pago_desde_credito(credito) or '-'}")
    fup = (
        credito.valor_campo("fecha_ultimo_pago_ultimo_abono")
        or credito.valor_campo("fecha_ultimo_pago")
    )
    if fup:
        print(f"    ultimo pago    : {fup}")
    fv = credito.valor_campo("fecha_de_vencimiento")
    if fv:
        print(f"    fecha venc.    : {fv}")


def ejecutar_seguimiento(
    identificador: str,
    fecha: Optional[str] = None,
    settings: Optional[Settings] = None,
) -> int:
    cfg = settings or (build_settings(fecha) if fecha else Settings(DEFERIR_RESOLUCION_RUTAS=True))
    _configure_logging(cfg.log_level)

    id_busqueda = identificador.strip()
    fecha_txt = fecha or cfg.fecha_corte
    fecha_corte = parsear_fecha_corte(fecha_txt) if fecha_txt else date.today()
    fecha_mmddyyyy = (
        fecha_txt
        if fecha_txt
        else f"{fecha_corte.month:02d}{fecha_corte.day:02d}{fecha_corte.year}"
    )

    print("=== Seguimiento crédito ===")
    print(f"  Buscar         : {id_busqueda}")
    print(f"  Fecha corte    : {fecha_corte} ({fecha_mmddyyyy})")

    # --- Recblue ---
    archivo_rb = cfg.archivo_recblue
    if archivo_rb is None or not archivo_rb.is_file():
        print(f"\n[Recblue] NO CONFIGURADO o archivo ausente: {archivo_rb}")
        print("  Defina ARCHIVO_RECBLUE en .env")
        return 1

    adapter = RecblueArchivoAdapter(archivo_rb)
    por_id = adapter.operaciones_por_id_credito(id_busqueda)
    por_op = adapter.registro_por_operacion(id_busqueda)

    if por_id:
        operaciones = [r["numero_operacion"] for r in por_id]
        id_recblue = por_id[0]["id_credito_recblue"]
        print(f"\n[Recblue] ID Crédito {id_recblue}")
        for r in por_id:
            print(f"  -> operacion core: {r['numero_operacion']}")
    elif por_op:
        operaciones = [por_op["numero_operacion"]]
        id_recblue = por_op["id_credito_recblue"]
        print(f"\n[Recblue] Entrada es operacion core -> ID Credito {id_recblue}")
    else:
        print(f"\n[Recblue] No se encontró ID ni operación '{id_busqueda}'")
        print(f"  Archivo: {archivo_rb.resolve()}")
        return 1

    if len(operaciones) > 1:
        print("  AVISO: varias operaciones con el mismo ID Recblue")

    numero_operacion = operaciones[0]

    # --- Archivos .lis ---
    try:
        rutas = resolver_rutas_cartera(
            cfg.directorio_docsmora,
            cfg.directorio_destino,
            fecha_mmddyyyy=fecha_mmddyyyy,
        )
    except FileNotFoundError as exc:
        print(f"\n[Archivos] {exc}")
        return 1

    print("\n[Archivos]")
    print(f"  CAMOROSICO : {rutas.archivo_morosidad}")
    print(f"  CADETACACO : {rutas.archivo_cartera}")

    _, _, morosidad = leer_cuadro_morosidad(
        rutas.archivo_morosidad, fecha_corte_override=fecha_corte
    )
    _, _, cartera = leer_te_detallado_cartera(
        rutas.archivo_cartera, fecha_corte_override=fecha_corte
    )

    cred_mora = _buscar_credito(morosidad, numero_operacion)
    cred_cartera = _buscar_credito(cartera, numero_operacion)

    if cred_mora is None:
        print(f"\n[CAMOROSICO] Operación {numero_operacion} NO está en morosidad")
        print("  No entra al pipeline de mora (no figura en el cuadro del día).")
        return 0

    print(f"\n[CAMOROSICO] Encontrada operación {numero_operacion}")
    _imprimir_credito("morosidad", cred_mora)

    if cred_cartera is None:
        print("\n[CADETACACO] Sin match (no enriquecida con día de pago)")
        credito = cred_mora
    else:
        print("\n[CADETACACO] Encontrada")
        _imprimir_credito("cartera", cred_cartera)
        credito = CarteraMergeService()._merge(cred_mora, cred_cartera)

    # --- Reglas y feriados ---
    from sqlalchemy.orm import sessionmaker

    engine = create_engine_from_settings(cfg)
    session_factory = sessionmaker(bind=engine, future=True)
    feriados_repo = SqlAlchemyFeriadosCalendarioRepository(
        session_factory, cfg.clave_feriados
    )
    feriados = feriados_repo.fechas_vigentes()
    reglas = ResolverReglasMoraService(
        SqlAlchemyReglasRepository(session_factory)
    ).resolver(
        dias_min=cfg.mora_temprana_dias_min,
        dias_max=cfg.mora_temprana_dias_max,
        estados_excluidos=tuple(
            p.strip() for p in cfg.estados_excluidos.split(",") if p.strip()
        ),
        tipos_oper_excluidos=tuple(
            p.strip() for p in cfg.tipos_oper_excluidos.split(",") if p.strip()
        ),
    )

    print(f"\n[Reglas] origen={reglas.origen} | días {reglas.dias_min}-{reglas.dias_max}")
    print(f"  feriados vigentes: {len(feriados)}")

    excluir, motivo = debe_excluir_operacion(
        credito, reglas.estados_excluidos, reglas.tipos_oper_excluidos
    )
    if excluir:
        print(f"\n[Mora] EXCLUIDO | {motivo}")
        print("  No entra a mora temprana ni ASIGNACION.csv")
        return 0

    dias_atraso = dias_atraso_camorosico(credito)
    dia_pago = dia_pago_desde_credito(credito)
    print("\n[Mora] Reglas (DIAS ATRASO de CAMOROSICO = mandatario)")
    print(f"  fecha archivo (corte)      : {credito.fecha_corte}")
    print(f"  DIAS ATRASO (CAMOROSICO)   : {dias_atraso}")
    if dias_atraso <= 0:
        print("\n  -> AL DIA (sin mora en CAMOROSICO).")
    elif dia_pago <= 0:
        print("  dia_pago (CADETACACO)      : sin dato")
        print("\n  -> NO elegible (se requiere DIA PAGO).")
    else:
        clasif = clasificar_mora_camorosico(
            credito.fecha_corte, dias_atraso, dia_pago, feriados
        )
        mes_cuota = f"{clasif.anio_cuota:04d}-{clasif.mes_cuota:02d}"
        print(f"  dia_pago (CADETACACO)      : {dia_pago}")
        print(f"  dias mora (CAMOROSICO)     : {clasif.dias}")
        print(f"  mes_cuota en mora          : {mes_cuota}")
        print(f"  vencimiento cuota en mora  : {clasif.vencimiento_cuota}")
        print(f"  limite pago mes siguiente  : {clasif.limite_mes_siguiente}")
        print(f"  clasificacion              : {clasif.clasificacion}")
        if clasif.clasificacion == "mora_madura":
            print(
                "\n  -> MORA MADURA (la fecha de corte ya pasó el día de pago "
                "del mes siguiente; no asignación temprana)."
            )
        else:
            print("\n  -> ELEGIBLE mora temprana (iría a asignación)")

    # --- Simulación pipeline ---
    servicio = MoraTempranaService()
    elegibles, _ = servicio.procesar(
        [credito],
        feriados=feriados,
        dias_min=reglas.dias_min,
        dias_max=reglas.dias_max,
        estados_excluidos=reglas.estados_excluidos,
        tipos_oper_excluidos=reglas.tipos_oper_excluidos,
        log_muestra=-1,
    )
    print(f"\n[Pipeline simulado] elegible_temprana={'SI' if elegibles else 'NO'}")

    # --- ASIGNACION.csv ---
    asignacion_path = ruta_asignacion_desde_fecha_archivo(
        cfg.directorio_destino, fecha_corte, feriados
    )
    filas_asig = _leer_asignacion(asignacion_path, id_recblue)
    print(f"\n[ASIGNACION.csv] {asignacion_path}")
    if filas_asig:
        for f in filas_asig:
            print(f"  ID_CREDITO={f.get('ID_CREDITO')} | USUARIO={f.get('USUARIO')}")
    else:
        print("  No aparece (no elegible o pipeline no ejecutado para esta fecha)")

    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Seguimiento de crédito por ID Recblue u operación core",
    )
    parser.add_argument(
        "identificador",
        help="ID Crédito Recblue (ej. 27854) o número de operación core",
    )
    parser.add_argument(
        "--fecha",
        help="Fecha corte MMDDYYYY o YYYY-MM-DD (default: FECHA_CORTE o hoy)",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        return ejecutar_seguimiento(args.identificador, fecha=args.fecha)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        logger.exception("Error en seguimiento")
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
