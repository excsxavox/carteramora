import logging
from pathlib import Path

from cobranzas.domain.models.sincronizacion_feriados_result import (
    SincronizacionFeriadosResult,
)
from cobranzas.domain.ports.feriado_catalogo_repository import (
    FeriadoCatalogoRepositoryPort,
)
from cobranzas.domain.ports.feriado_excel_repository import FeriadoExcelRepositoryPort

logger = logging.getLogger("cobranzas.sync.feriados")


class SincronizarFeriadosService:
    """Job 0b: sincroniza catálogo de feriados desde Excel a claves/catalogo."""

    def __init__(
        self,
        excel_repository: FeriadoExcelRepositoryPort,
        catalogo_repository: FeriadoCatalogoRepositoryPort,
        directorio_excel: Path,
        patron_excel: str,
        clave_feriados: str,
    ) -> None:
        self._excel = excel_repository
        self._catalogo = catalogo_repository
        self._directorio = directorio_excel
        self._patron = patron_excel
        self._clave = clave_feriados

    def ejecutar(self) -> SincronizacionFeriadosResult:
        resultado = SincronizacionFeriadosResult()

        archivo = self._excel.buscar_archivo(self._directorio, self._patron)
        if archivo is None:
            resultado.omitidos_sin_excel = True
            return resultado

        resultado.archivo_excel = str(archivo)
        try:
            rangos = self._excel.leer_feriados(archivo)
        except Exception as exc:
            resultado.errores.append(str(exc))
            return resultado

        resultado.registros_excel = len(rangos)
        id_clave = self._catalogo.obtener_o_crear_clave(self._clave)

        for rango in rangos:
            try:
                detalle = self._catalogo.sincronizar_rango(
                    id_clave,
                    rango.descripcion,
                    rango.fecha_inicio,
                    rango.fecha_fin,
                )
                resultado.dias_insertados += detalle.insertados
                resultado.dias_activados += detalle.activados
                resultado.dias_desactivados += detalle.desactivados
                logger.info(
                    "Feriado OK: '%s' | %s → %s | +%s ~%s -%s",
                    rango.descripcion,
                    rango.fecha_inicio,
                    rango.fecha_fin,
                    detalle.insertados,
                    detalle.activados,
                    detalle.desactivados,
                )
            except Exception as exc:
                mensaje = (
                    f"Error en '{rango.descripcion}' "
                    f"({rango.fecha_inicio}–{rango.fecha_fin}): {exc}"
                )
                logger.exception(mensaje)
                resultado.errores.append(mensaje)

        return resultado
