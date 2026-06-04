from datetime import datetime
from typing import List

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from cobranzas.domain.models.asesor_registro import AsesorRegistro
from cobranzas.domain.models.sincronizacion_asesores_result import (
    SincronizacionAsesoresResult,
)
from cobranzas.domain.ports.asesor_sync_repository import AsesorSyncRepositoryPort
from cobranzas.domain.services.validar_asesores_service import registro_igual_a_bd
from cobranzas.infrastructure.persistence.models import Asesor


class SqlAlchemyAsesorSyncRepository(AsesorSyncRepositoryPort):
    def __init__(self, session_factory: sessionmaker) -> None:
        self._session_factory = session_factory

    def sincronizar(self, registros: List[AsesorRegistro]) -> SincronizacionAsesoresResult:
        resultado = SincronizacionAsesoresResult(total_leidos=len(registros))
        ahora = datetime.utcnow()

        with self._session_factory() as session:
            for registro in registros:
                try:
                    asesor = session.scalar(
                        select(Asesor).where(Asesor.cedula == registro.cedula).limit(1)
                    )
                    if asesor is None:
                        session.add(
                            Asesor(
                                cedula=registro.cedula,
                                nombre=registro.nombre,
                                numero_telefono=registro.numero_telefono or None,
                                email=registro.email or None,
                                activo=registro.activo,
                                creado_en=ahora,
                            )
                        )
                        resultado.creados += 1
                    elif registro_igual_a_bd(registro, asesor):
                        resultado.sin_cambios += 1
                    else:
                        asesor.nombre = registro.nombre
                        asesor.numero_telefono = registro.numero_telefono or None
                        asesor.email = registro.email or None
                        asesor.activo = registro.activo
                        resultado.actualizados += 1
                except Exception as exc:
                    resultado.errores.append(f"{registro.cedula}: {exc}")

            session.commit()

        return resultado
