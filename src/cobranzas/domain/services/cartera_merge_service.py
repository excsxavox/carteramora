from dataclasses import replace
from typing import Dict, List, Optional

from cobranzas.domain.models.credito import Credito


class CarteraMergeService:
    """Combina morosidad (mora) con TE detallado de cartera (enriquecimiento)."""

    def enriquecer_con_cartera(
        self,
        creditos_morosidad: List[Credito],
        creditos_cartera: List[Credito],
    ) -> List[Credito]:
        cartera_por_operacion: Dict[str, Credito] = {
            c.id_credito: c for c in creditos_cartera
        }
        return [
            self._merge(morosidad, cartera_por_operacion.get(morosidad.id_credito))
            for morosidad in creditos_morosidad
        ]

    def _merge(
        self,
        morosidad: Credito,
        cartera: Optional[Credito],
    ) -> Credito:
        if cartera is None:
            return morosidad

        return replace(
            morosidad,
            cedula=cartera.cedula or morosidad.cedula,
            calificacion=cartera.calificacion or morosidad.calificacion,
            total_operacion=cartera.total_operacion or morosidad.total_operacion,
            segmentacion=cartera.segmentacion or morosidad.segmentacion,
            fuente_repago=cartera.fuente_repago or morosidad.fuente_repago,
            codigo_oficial=cartera.codigo_oficial or morosidad.codigo_oficial,
            tipo_operacion=cartera.tipo_operacion or morosidad.tipo_operacion,
            oficina=morosidad.oficina or cartera.oficina,
            socio=morosidad.socio or cartera.socio,
            campos_tab=Credito.combinar_campos_tab(
                morosidad.campos_tab, cartera.campos_tab
            ),
        )
