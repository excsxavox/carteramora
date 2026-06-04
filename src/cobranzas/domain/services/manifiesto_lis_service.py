from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from cobranzas.domain.models.credito import Credito

TAB = "\t"


class ManifiestoLisService:
    """Construye el contenido del archivo .lis (leídos y generados)."""

    def construir(
        self,
        archivo_morosidad: Path,
        archivo_cartera: Path,
        archivo_reporte: Path,
        archivo_lis: Path,
        creditos_morosidad: List[Credito],
        total_cartera_leidas: int,
        total_enriquecidos: int,
        creditos_mora: List[Credito],
        reporte: Dict[str, Any],
    ) -> str:
        lineas: List[str] = []
        ahora = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        fecha_corte = reporte.get("fecha_corte") or ""

        lineas.extend(
            [
                "*" * 78,
                "* MANIFIESTO COBRANZAS - JOB",
                "*" * 78,
                f"FECHA EJECUCION{TAB}{ahora}",
                f"FECHA CORTE{TAB}{fecha_corte}",
                f"DIAS MORA MINIMO{TAB}{reporte.get('dias_mora_minimo', '')}",
                "",
                f"--- ARCHIVOS LEIDOS ---",
                self._linea_archivo(
                    "ENTRADA",
                    archivo_morosidad,
                    "CUADRO DE MOROSIDAD - CONSOLIDADO",
                    len(creditos_morosidad),
                ),
                self._linea_archivo(
                    "ENTRADA",
                    archivo_cartera,
                    "TE DETALLADO DE CARTERA - CONSOLIDADO",
                    total_cartera_leidas,
                ),
                f"OPERACIONES ENRIQUECIDAS CON CARTERA{TAB}{total_enriquecidos}",
                "",
                f"--- ARCHIVOS GENERADOS ---",
                self._linea_archivo(
                    "SALIDA",
                    archivo_reporte,
                    "REPORTE MORA JSON",
                    reporte.get("total_creditos", 0),
                ),
                self._linea_archivo(
                    "SALIDA",
                    archivo_lis,
                    "MANIFIESTO LIS",
                    1,
                ),
                f"TOTAL SALDO MORA{TAB}{reporte.get('total_saldo_mora', 0)}",
                "",
                f"--- DETALLE LEIDO (MOROSIDAD) ---",
                f"NO.OPERACION{TAB}NOMBRE SOCIO{TAB}DIAS ATRASO{TAB}ESTADO{TAB}SALDO ATRASADO",
            ]
        )

        for credito in creditos_morosidad:
            lineas.append(self._linea_operacion(credito))

        lineas.extend(
            [
                "",
                f"--- DETALLE GENERADO (EN MORA) ---",
                f"NO.OPERACION{TAB}NOMBRE SOCIO{TAB}DIAS ATRASO{TAB}CLASIFICACION{TAB}SALDO ATRASADO",
            ]
        )

        for credito in creditos_mora:
            clasificacion = credito.clasificar_mora(
                int(reporte.get("dias_mora_minimo", 30))
            ).value
            lineas.append(
                f"{credito.id_credito}{TAB}{credito.cliente}{TAB}"
                f"{credito.dias_mora}{TAB}{clasificacion}{TAB}{credito.saldo_pendiente}"
            )

        lineas.extend(["", "*" * 78, "* FIN MANIFIESTO", "*" * 78, ""])
        return "\n".join(lineas)

    def _linea_archivo(
        self, tipo: str, ruta: Path, descripcion: str, registros: int
    ) -> str:
        return (
            f"{tipo}{TAB}{ruta.as_posix()}{TAB}{descripcion}{TAB}{registros}"
        )

    def _linea_operacion(self, credito: Credito) -> str:
        return (
            f"{credito.id_credito}{TAB}{credito.cliente}{TAB}"
            f"{credito.dias_mora}{TAB}{credito.estado_operacion}{TAB}"
            f"{credito.saldo_pendiente}"
        )
