from pathlib import Path

from cartera_mora.domain.ports.manifiesto_repository import ManifiestoRepositoryPort


class LisManifiestoRepository(ManifiestoRepositoryPort):
    """Adaptador: escribe el manifiesto en archivo .lis."""

    def __init__(self, file_path: Path) -> None:
        self._file_path = file_path

    def guardar_manifiesto(self, contenido: str) -> None:
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        self._file_path.write_text(contenido, encoding="utf-8")
