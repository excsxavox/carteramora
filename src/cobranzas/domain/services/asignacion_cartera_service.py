"""Asignación secuencial balanceada de mora temprana (HU-GRC-01)."""

import logging
from dataclasses import replace
from datetime import date
from typing import Dict, List, Optional, Sequence, Tuple

from cobranzas.domain.models.asignacion_credito import AsignacionCredito
from cobranzas.domain.models.credito import Credito
from cobranzas.domain.ports.asignacion_mensual_port import AsignacionMensualPort
from cobranzas.domain.ports.recblue_port import RecbluePort
from cobranzas.domain.services.mora_temprana_service import saldo_capital_desde_credito

logger = logging.getLogger("cobranzas.asignacion")


class AsignacionCarteraService:
    def __init__(
        self,
        rotacion_asesores: Sequence[str],
        asignacion_mensual: Optional[AsignacionMensualPort] = None,
        recblue: Optional[RecbluePort] = None,
    ) -> None:
        self._rotacion = [c.strip().upper() for c in rotacion_asesores if c.strip()]
        self._asignacion_mensual = asignacion_mensual
        self._recblue = recblue

    def asignar(
        self,
        creditos: List[Credito],
        fecha_corte: date,
    ) -> Tuple[List[Credito], List[AsignacionCredito]]:
        if not self._rotacion:
            raise ValueError("La rotación de asesores está vacía (ASESORES_ROTACION)")

        existentes = self._cargar_asignaciones_mes(fecha_corte)
        ids_recblue = self._recblue.id_credito_por_operacion() if self._recblue else {}

        creditos_asignados: List[Credito] = []
        filas: List[AsignacionCredito] = []
        indice_rotacion = 0

        for credito in creditos:
            saldo = saldo_capital_desde_credito(credito)
            numero = credito.id_credito

            if numero in existentes:
                codigo, nombre = existentes[numero]
                reasignado = False
            else:
                codigo = self._rotacion[indice_rotacion % len(self._rotacion)]
                nombre = codigo
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

        logger.info(
            "Asignación | operaciones=%s asesores_rotacion=%s nuevas=%s",
            len(filas),
            len(self._rotacion),
            sum(1 for f in filas if f.reasignado),
        )
        return creditos_asignados, filas

    def _cargar_asignaciones_mes(self, fecha_corte: date) -> Dict[str, Tuple[str, str]]:
        if self._asignacion_mensual is None:
            return {}
        return self._asignacion_mensual.asignaciones_del_mes(
            fecha_corte.year, fecha_corte.month
        )
