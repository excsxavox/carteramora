from pathlib import Path
from typing import List, Sequence

from cobranzas.domain.models.credito import Credito
from cobranzas.domain.schemas.tab_schema import COL_CLASIFICACION_MORA, encabezado_tab, fila_tab


class TabDetalleExportService:
    """Exporta detalle TAB (cabecera genérica + filas) a archivo .lis."""

    def exportar_morosidad(
        self,
        file_path: Path,
        columnas: Sequence[str],
        creditos: List[Credito],
    ) -> None:
        lineas = [encabezado_tab(columnas)]
        for credito in creditos:
            lineas.append(credito.fila_tab(columnas))
        self._escribir(file_path, lineas)

    def exportar_mora(
        self,
        file_path: Path,
        columnas: Sequence[str],
        creditos: List[Credito],
        dias_mora_minimo: int,
    ) -> None:
        lineas = [encabezado_tab(columnas)]
        for credito in creditos:
            lineas.append(self._linea_mora(credito, columnas, dias_mora_minimo))
        self._escribir(file_path, lineas)

    def _linea_mora(
        self,
        credito: Credito,
        columnas: Sequence[str],
        dias_mora_minimo: int,
    ) -> str:
        valores = credito.campos_tab_dict()
        valores[COL_CLASIFICACION_MORA] = credito.clasificar_mora(
            dias_mora_minimo
        ).value
        return fila_tab(valores.get(columna, "") for columna in columnas)

    def _escribir(self, file_path: Path, lineas: List[str]) -> None:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text("\n".join(lineas) + "\n", encoding="utf-8")
