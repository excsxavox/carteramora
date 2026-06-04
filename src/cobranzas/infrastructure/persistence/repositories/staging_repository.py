from datetime import datetime
from pathlib import Path
from typing import List, Optional

from sqlalchemy.orm import Session, sessionmaker

from cobranzas.domain.models.lote_carga import LoteCargaResult
from cobranzas.domain.ports.staging_repository import StagingRepositoryPort
from cobranzas.infrastructure.adapters.tab_lis_staging_reader import (
    TabArchivoParseado,
    extraer_numero_operacion,
    fila_a_json,
    parsear_archivo_tab,
    registrar_columnas,
)
from cobranzas.infrastructure.logging.archivo_lis_logger import ArchivoLisLogger
from cobranzas.infrastructure.persistence.models.staging import (
    ESTADO_LOTE_CARGADO,
    TIPO_ARCHIVO_MORA,
    TIPO_ARCHIVO_MOROSIDAD,
    TmpColumnaArchivo,
    TmpLoteCarga,
    TmpStgMora,
    TmpStgMorosidad,
)

TAMANO_LOTE_INSERCION = 500


class SqlAlchemyStagingRepository(StagingRepositoryPort):
    def __init__(
        self,
        session_factory: sessionmaker,
        archivo_logger: Optional[ArchivoLisLogger] = None,
    ) -> None:
        self._session_factory = session_factory
        self._archivo_log = archivo_logger or ArchivoLisLogger(0)

    def cargar_archivos_limpios(
        self,
        archivo_morosidad: Path,
        archivo_mora: Path,
    ) -> LoteCargaResult:
        if not archivo_morosidad.is_file():
            raise FileNotFoundError(f"No existe archivo morosidad: {archivo_morosidad}")
        if not archivo_mora.is_file():
            raise FileNotFoundError(f"No existe archivo mora: {archivo_mora}")

        parse_morosidad = parsear_archivo_tab(archivo_morosidad)
        parse_mora = parsear_archivo_tab(archivo_mora)

        self._archivo_log.log_inicio(archivo_morosidad, archivo_mora)
        self._archivo_log.log_archivo(archivo_morosidad, parse_morosidad)
        self._archivo_log.log_archivo(archivo_mora, parse_mora)

        with self._session_factory() as session:
            lote = TmpLoteCarga(
                fecha_carga=datetime.utcnow(),
                ruta_archivo_morosidad=archivo_morosidad.as_posix(),
                ruta_archivo_mora=archivo_mora.as_posix(),
                estado=ESTADO_LOTE_CARGADO,
            )
            session.add(lote)
            session.flush()

            self._registrar_columnas(
                session,
                lote.id_lote,
                TIPO_ARCHIVO_MOROSIDAD,
                parse_morosidad,
            )
            self._registrar_columnas(
                session,
                lote.id_lote,
                TIPO_ARCHIVO_MORA,
                parse_mora,
            )

            filas_morosidad = self._insertar_morosidad(
                session, lote.id_lote, parse_morosidad
            )
            filas_mora = self._insertar_mora(session, lote.id_lote, parse_mora)

            lote.filas_morosidad = filas_morosidad
            lote.filas_mora = filas_mora
            session.commit()

            self._archivo_log.log_resumen_carga(
                lote.id_lote, filas_morosidad, filas_mora
            )

            return LoteCargaResult(
                id_lote=lote.id_lote,
                filas_morosidad=filas_morosidad,
                filas_mora=filas_mora,
                columnas_morosidad=len(parse_morosidad.columnas),
                columnas_mora=len(parse_mora.columnas),
                archivo_morosidad=archivo_morosidad,
                archivo_mora=archivo_mora,
            )

    def _registrar_columnas(
        self,
        session: Session,
        id_lote: int,
        tipo_archivo: str,
        parseado: TabArchivoParseado,
    ) -> None:
        for orden, nombre_columna, nombre_original in registrar_columnas(
            parseado.encabezados_originales, parseado.columnas
        ):
            session.add(
                TmpColumnaArchivo(
                    id_lote=id_lote,
                    tipo_archivo=tipo_archivo,
                    orden=orden,
                    nombre_columna=nombre_columna,
                    nombre_original=nombre_original,
                )
            )

    def _insertar_morosidad(
        self,
        session: Session,
        id_lote: int,
        parseado: TabArchivoParseado,
    ) -> int:
        buffer: List[TmpStgMorosidad] = []
        total = 0
        for numero_fila, campos in enumerate(parseado.filas, start=2):
            buffer.append(
                TmpStgMorosidad(
                    id_lote=id_lote,
                    numero_fila=numero_fila,
                    no_operacion=extraer_numero_operacion(campos) or None,
                    campos_json=fila_a_json(campos),
                )
            )
            if len(buffer) >= TAMANO_LOTE_INSERCION:
                session.add_all(buffer)
                session.flush()
                total += len(buffer)
                buffer.clear()
        if buffer:
            session.add_all(buffer)
            session.flush()
            total += len(buffer)
        return total

    def _insertar_mora(
        self,
        session: Session,
        id_lote: int,
        parseado: TabArchivoParseado,
    ) -> int:
        buffer: List[TmpStgMora] = []
        total = 0
        for numero_fila, campos in enumerate(parseado.filas, start=2):
            buffer.append(
                TmpStgMora(
                    id_lote=id_lote,
                    numero_fila=numero_fila,
                    no_operacion=extraer_numero_operacion(campos) or None,
                    campos_json=fila_a_json(campos),
                )
            )
            if len(buffer) >= TAMANO_LOTE_INSERCION:
                session.add_all(buffer)
                session.flush()
                total += len(buffer)
                buffer.clear()
        if buffer:
            session.add_all(buffer)
            session.flush()
            total += len(buffer)
        return total
