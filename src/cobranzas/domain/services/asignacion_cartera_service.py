"""Asignación secuencial balanceada de mora temprana (HU-GRC-01)."""

import logging
from dataclasses import replace
from datetime import date
from typing import Dict, List, Optional, Tuple

from cobranzas.domain.models.asignacion_credito import AsignacionCredito
from cobranzas.domain.models.credito import Credito
from cobranzas.domain.ports.asignacion_mensual_port import AsignacionMensualPort
from cobranzas.domain.ports.asesores_rotacion_port import AsesoresRotacionPort
from cobranzas.domain.ports.recblue_port import RecbluePort
from cobranzas.domain.services.asignacion_calendario import (
    debe_asignar_asesores,
    es_primer_dia_mes,
)
from cobranzas.domain.services.mora_temprana_service import saldo_capital_desde_credito

logger = logging.getLogger("cobranzas.asignacion")


def _normalizar_operacion(numero: str) -> str:
    return (numero or "").strip()


def _mes_anterior(anio: int, mes: int) -> Tuple[int, int]:
    if mes == 1:
        return anio - 1, 12
    return anio, mes - 1


class AsignacionCarteraService:
    def __init__(
        self,
        asesores_rotacion: AsesoresRotacionPort,
        asignacion_mensual: Optional[AsignacionMensualPort] = None,
        recblue: Optional[RecbluePort] = None,
    ) -> None:
        self._asesores_rotacion = asesores_rotacion
        self._asignacion_mensual = asignacion_mensual
        self._recblue = recblue

    def _cargar_rotacion(self) -> List[Tuple[str, str]]:
        activos = self._asesores_rotacion.listar_activos()
        if activos:
            logger.info(
                "Rotación asesores desde BD | activos=%s | %s",
                len(activos),
                ", ".join(c for c, _ in activos[:8]),
            )
            return activos

        raise ValueError(
            "No hay asesores activos en tabla asesores. "
            "Cargue data/catalogo/asesores.xlsx (Job 0) antes de asignar."
        )

    def asignar(
        self,
        creditos: List[Credito],
        fecha_corte: date,
        es_fin_de_mes: bool = False,
    ) -> Tuple[List[Credito], List[AsignacionCredito]]:
        if es_fin_de_mes:
            logger.info(
                "Asignación omitida | %s | fin de mes | solo se almacena sin asesor",
                fecha_corte.isoformat(),
            )
            return list(creditos), []
        if not debe_asignar_asesores(fecha_corte):
            logger.info(
                "Asignación omitida | %s | último día del mes | solo historial en BD",
                fecha_corte.isoformat(),
            )
            return list(creditos), []

        rotacion = self._cargar_rotacion()
        existentes = self._cargar_asignaciones_arrastre(fecha_corte)
        logger.info(
            "Asignación | %s | día %s | conservar previas + rotar solo nuevas | previas=%s",
            fecha_corte.isoformat(),
            fecha_corte.day,
            len(existentes),
        )
        ids_recblue = self._recblue.id_credito_por_operacion() if self._recblue else {}

        creditos_asignados: List[Credito] = []
        filas: List[AsignacionCredito] = []
        indice_rotacion = len(existentes) % len(rotacion) if rotacion else 0

        for credito in creditos:
            saldo = saldo_capital_desde_credito(credito)
            numero = _normalizar_operacion(credito.id_credito)

            if numero in existentes:
                codigo, nombre = existentes[numero]
                reasignado = False
            else:
                codigo, nombre = rotacion[indice_rotacion % len(rotacion)]
                indice_rotacion += 1
                existentes[numero] = (codigo, nombre)
                reasignado = True

            id_recblue = ids_recblue.get(numero, "")

            filas.append(
                AsignacionCredito(
                    fecha_corte=fecha_corte,
                    numero_operacion=numero,
                    identificacion=credito.cedula,
                    socio=credito.socio,
                    nombre=credito.cliente,
                    saldo_capital=saldo,
                    dias_mora=credito.dias_mora,
                    codigo_asesor=codigo,
                    nombre_asesor=nombre,
                    id_credito_recblue=id_recblue,
                    reasignado=reasignado,
                )
            )

            creditos_asignados.append(
                replace(
                    credito,
                    codigo_oficial=codigo,
                    nombre_oficial=nombre,
                    id_credito_recblue=id_recblue,
                )
            )

        nuevas = sum(1 for f in filas if f.reasignado)
        conservadas = len(filas) - nuevas
        logger.info(
            "Asignación | pool_mora_temprana=%s | conservadas_mes=%s | nuevas=%s | asesores=%s",
            len(filas),
            conservadas,
            nuevas,
            len(rotacion),
        )
        return creditos_asignados, filas

    def _cargar_asignaciones_arrastre(
        self, fecha_corte: date
    ) -> Dict[str, Tuple[str, str]]:
        """
        Asignaciones a conservar para no reasignar lo ya gestionado.

        - Día 1 del mes: base = cierre del mes anterior (lo que se tenía a fin de
          mes); así solo se rotan las operaciones NUEVAS.
        - Otros días: asignaciones ya registradas del mes en curso.
        """
        existentes: Dict[str, Tuple[str, str]] = {}
        if es_primer_dia_mes(fecha_corte):
            anio_prev, mes_prev = _mes_anterior(fecha_corte.year, fecha_corte.month)
            existentes.update(self._cargar_asignaciones_mes(anio_prev, mes_prev))
        # Mes en curso, excluyendo el propio corte: al re-procesar un corte su
        # asignación previa no debe contar como conservada (si no, saldrían 0
        # nuevas y no se regeneraría el ASIGNACION del día).
        existentes.update(
            self._cargar_asignaciones_mes(
                fecha_corte.year, fecha_corte.month, excluir_fecha=fecha_corte
            )
        )
        return existentes

    def _cargar_asignaciones_mes(
        self, anio: int, mes: int, excluir_fecha: Optional[date] = None
    ) -> Dict[str, Tuple[str, str]]:
        if self._asignacion_mensual is None:
            return {}
        crudo = self._asignacion_mensual.asignaciones_del_mes(
            anio, mes, excluir_fecha=excluir_fecha
        )
        return {
            _normalizar_operacion(numero): asesor
            for numero, asesor in crudo.items()
            if _normalizar_operacion(numero)
        }
