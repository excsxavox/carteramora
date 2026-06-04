from datetime import datetime, timezone

from cobranzas.domain.models.credito import Credito, EstadoMora


class CobranzasService:
    """Lógica de dominio pura: filtrado y agregación de cartera en mora."""

    def filtrar_en_mora(
        self, creditos: list[Credito], dias_mora_minimo: int
    ) -> list[Credito]:
        return [c for c in creditos if c.esta_en_mora(dias_mora_minimo)]

    def construir_reporte(
        self,
        creditos_mora: list[Credito],
        dias_mora_minimo: int,
    ) -> dict:
        por_estado: dict[EstadoMora, list[dict]] = {
            EstadoMora.MORA_LEVE: [],
            EstadoMora.MORA_GRAVE: [],
        }

        for credito in creditos_mora:
            estado = credito.clasificar_mora(dias_mora_minimo)
            if estado == EstadoMora.AL_DIA:
                continue
            por_estado[estado].append(
                {
                    "no_operacion": credito.id_credito,
                    "nombre_socio": credito.cliente,
                    "cedula": credito.cedula,
                    "socio": credito.socio,
                    "oficina": credito.oficina,
                    "estado_operacion": credito.estado_operacion,
                    "calificacion": credito.calificacion,
                    "dias_atraso": credito.dias_mora,
                    "saldo_capital_atrasado": credito.saldo_pendiente,
                    "total_atrasado": credito.total_atrasado,
                    "total_operacion": credito.total_operacion,
                    "segmentacion": credito.segmentacion,
                    "fuente_repago": credito.fuente_repago,
                    "clasificacion_mora": estado.value,
                }
            )

        total_saldo = sum(c.saldo_pendiente for c in creditos_mora)

        return {
            "generado_en": datetime.now(timezone.utc).isoformat(),
            "fecha_corte": creditos_mora[0].fecha_corte.isoformat()
            if creditos_mora
            else None,
            "dias_mora_minimo": dias_mora_minimo,
            "total_creditos": len(creditos_mora),
            "total_saldo_mora": round(total_saldo, 2),
            "mora_leve": por_estado[EstadoMora.MORA_LEVE],
            "mora_grave": por_estado[EstadoMora.MORA_GRAVE],
        }
