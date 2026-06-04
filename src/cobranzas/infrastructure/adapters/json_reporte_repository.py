import json
from pathlib import Path
from typing import Any

from cobranzas.domain.ports.reporte_repository import ReporteRepositoryPort


class JsonReporteRepository(ReporteRepositoryPort):
    """Adaptador: guarda el reporte en un archivo JSON."""

    def __init__(self, file_path: Path) -> None:
        self._file_path = file_path

    def guardar_reporte(self, reporte: dict[str, Any]) -> None:
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        with self._file_path.open("w", encoding="utf-8") as f:
            json.dump(reporte, f, indent=2, ensure_ascii=False)
