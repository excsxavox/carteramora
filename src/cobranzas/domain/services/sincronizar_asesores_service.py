import logging
from pathlib import Path

from cobranzas.domain.models.sincronizacion_asesores_result import (
    SincronizacionAsesoresResult,
)
from cobranzas.domain.ports.asesor_excel_repository import AsesorExcelRepositoryPort
from cobranzas.domain.ports.asesor_sync_repository import AsesorSyncRepositoryPort
from cobranzas.domain.services.validar_asesores_service import (
    ValidacionAsesoresError,
    validar_registros_asesores,
)

logger = logging.getLogger("cobranzas.sync.asesores")


class SincronizarAsesoresService:
    """Job 0: carga catálogo de asesores desde Excel a BD."""

    def __init__(
        self,
        excel_repository: AsesorExcelRepositoryPort,
        sync_repository: AsesorSyncRepositoryPort,
        rechazar_duplicados_excel: bool = True,
    ) -> None:
        self._excel = excel_repository
        self._sync = sync_repository
        self._rechazar_duplicados = rechazar_duplicados_excel

    def ejecutar(self, archivo_excel: Path) -> SincronizacionAsesoresResult:
        logger.info("Leyendo asesores desde: %s", archivo_excel.as_posix())
        registros_raw = self._excel.leer_asesores(archivo_excel)
        logger.info("Filas leídas del Excel: %s", len(registros_raw))

        try:
            registros, advertencias = validar_registros_asesores(
                registros_raw,
                rechazar_duplicados_excel=self._rechazar_duplicados,
            )
        except ValidacionAsesoresError as exc:
            logger.error("Validación fallida:\n%s", exc)
            resultado = SincronizacionAsesoresResult(
                filas_excel=len(registros_raw),
                errores=[str(exc)],
            )
            return resultado

        if advertencias:
            logger.warning("Advertencias de validación (%s):", len(advertencias))
            for aviso in advertencias:
                logger.warning("  %s", aviso)

        duplicados_omitidos = len(registros_raw) - len(registros)
        if duplicados_omitidos:
            logger.info(
                "Duplicados en Excel omitidos: %s (cédulas únicas: %s)",
                duplicados_omitidos,
                len(registros),
            )

        logger.info("Registros válidos para sincronizar: %s", len(registros))

        for registro in registros[:5]:
            logger.info(
                "  Excel → BD | cedula=%s | nombre=%s | activo=%s",
                registro.cedula,
                registro.nombre,
                registro.activo,
            )
        if len(registros) > 5:
            logger.info("  ... +%s filas más", len(registros) - 5)

        resultado = self._sync.sincronizar(registros)
        resultado.filas_excel = len(registros_raw)
        resultado.duplicados_excel_omitidos = duplicados_omitidos
        resultado.advertencias = advertencias
        logger.info(
            "Sincronización | creados=%s actualizados=%s sin_cambios=%s errores=%s",
            resultado.creados,
            resultado.actualizados,
            resultado.sin_cambios,
            len(resultado.errores),
        )
        for error in resultado.errores:
            logger.error("  %s", error)
        return resultado
