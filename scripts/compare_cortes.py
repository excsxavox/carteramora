"""Compara clasificación mora temprana entre cortes."""
from collections import defaultdict

from sqlalchemy.orm import sessionmaker

from cobranzas.domain.services.cartera_merge_service import CarteraMergeService
from cobranzas.domain.services.dias_habiles_service import (
    calcular_cuota_mora,
    dias_max_mora_temprana_efectivo,
    vencimiento_efectivo,
)
from cobranzas.domain.services.mora_temprana_service import (
    _mora_cruza_mes_cuota,
    debe_excluir_operacion,
    dia_pago_desde_credito,
    dias_atraso_camorosico,
)
from cobranzas.infrastructure.adapters.cuadro_morosidad_parser import (
    leer_cuadro_morosidad,
)
from cobranzas.infrastructure.adapters.te_detallado_cartera_parser import (
    leer_te_detallado_cartera,
)
from cobranzas.infrastructure.persistence.database import create_engine_from_settings
from cobranzas.infrastructure.persistence.repositories.feriados_calendario_repository import (
    SqlAlchemyFeriadosCalendarioRepository,
)
from cobranzas.jobs.pipeline_runner import build_settings

FECHAS = ("06032026", "06042026", "06052026")


def analizar(fecha: str) -> dict:
    cfg = build_settings(fecha)
    engine = create_engine_from_settings(cfg)
    session_factory = sessionmaker(bind=engine, future=True)
    feriados = SqlAlchemyFeriadosCalendarioRepository(
        session_factory, cfg.clave_feriados
    ).fechas_vigentes()

    _, _, mora_list = leer_cuadro_morosidad(cfg.archivo_morosidad)
    _, _, cart_list = leer_te_detallado_cartera(cfg.archivo_cartera)
    creditos = CarteraMergeService().enriquecer_con_cartera(mora_list, cart_list)
    fc = creditos[0].fecha_corte
    dias_min = cfg.mora_temprana_dias_min
    dias_max = cfg.mora_temprana_dias_max
    estados = [x.strip() for x in cfg.estados_excluidos.split(",") if x.strip()]
    tipos = [x.strip() for x in cfg.tipos_oper_excluidos.split(",") if x.strip()]

    buckets: dict[str, int] = defaultdict(int)
    ejemplos_acum_d1: list[str] = []
    ejemplos_fuera_ref_bajo: list[str] = []

    for credito in creditos:
        ref = dias_atraso_camorosico(credito)
        if ref <= 0:
            buckets["sin_ref"] += 1
            continue
        excluir, _ = debe_excluir_operacion(credito, estados, tipos)
        if excluir:
            buckets["excluido"] += 1
            continue
        dia_pago = dia_pago_desde_credito(credito)
        if dia_pago <= 0:
            buckets["sin_dia_pago"] += 1
            continue
        cuota = calcular_cuota_mora(fc, dia_pago, feriados, ultimo_pago=None)
        mes_corte = f"{fc.year:04d}-{fc.month:02d}"
        mes_cuota = f"{cuota.anio_cuota:04d}-{cuota.mes_cuota:02d}"

        if cuota.clasificacion == "al_dia":
            v_mes = vencimiento_efectivo(fc.year, fc.month, dia_pago, feriados)
            if v_mes > fc:
                buckets["al_dia_cuota_mes_no_vencida"] += 1
            else:
                buckets["al_dia_otro"] += 1
            continue
        if _mora_cruza_mes_cuota(mes_cuota, mes_corte):
            buckets["madura_cruce_mes"] += 1
            continue
        plazo_max = dias_max_mora_temprana_efectivo(
            cuota.vencimiento_efectivo,
            cuota.anio_cuota,
            cuota.mes_cuota,
            dia_pago,
            feriados,
            dias_max,
        )
        if cuota.dias < dias_min:
            buckets["fuera_bajo"] += 1
            continue
        if plazo_max <= 0 or cuota.dias > plazo_max:
            buckets["fuera_alto"] += 1
            if ref <= 3 and len(ejemplos_fuera_ref_bajo) < 5:
                ejemplos_fuera_ref_bajo.append(
                    f"{credito.id_credito} ref={ref} dias={cuota.dias} dp={dia_pago}"
                )
            if ref <= 3:
                buckets["fuera_alto_ref_bajo"] += 1
            continue
        buckets["elegible"] += 1

    return {
        "fecha": fecha,
        "corte": fc,
        "buckets": dict(buckets),
        "ejemplos_acum_d1": ejemplos_acum_d1,
        "ejemplos_fuera_ref_bajo": ejemplos_fuera_ref_bajo,
    }


def main() -> None:
    for item in map(analizar, FECHAS):
        print()
        print("=" * 60)
        print(f"CORTE {item['fecha']} ({item['corte']})")
        for key, count in sorted(
            item["buckets"].items(), key=lambda kv: -kv[1]
        ):
            print(f"  {key:32s} {count:5d}")
        b = item["buckets"]
        print(f"  --> elegibles: {b.get('elegible', 0)}")
        print(f"  --> perdidos dias=1 por ref>3: {b.get('madura_acum_dias1', 0)}")
        print(f"  --> perdidos ref<=3 por dias>1: {b.get('fuera_alto_ref_bajo', 0)}")
        print(f"  --> AL_DIA porque marzo aun no vence: {b.get('al_dia_cuota_mes_no_vencida', 0)}")
        if item["ejemplos_acum_d1"]:
            print("  ej. madura_acum con dias=1:", ", ".join(item["ejemplos_acum_d1"]))
        if item["ejemplos_fuera_ref_bajo"]:
            print("  ej. fuera_rango ref bajo:", ", ".join(item["ejemplos_fuera_ref_bajo"]))


if __name__ == "__main__":
    main()
