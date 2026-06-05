import logging
from datetime import date, datetime
from typing import Dict

from sqlalchemy import select

from cobranzas.domain.ports.feriado_catalogo_repository import (
    FeriadoCatalogoRepositoryPort,
    FeriadoSincronizadoDetalle,
)
from cobranzas.domain.services.feriado_fechas import (
    fecha_a_valor_catalogo,
    parsear_fecha_catalogo,
    rango_dias,
)
from cobranzas.infrastructure.persistence.models import Catalogo, Clave

log = logging.getLogger("cobranzas.sync.feriados.bd")


class SqlAlchemyFeriadoCatalogoRepository(FeriadoCatalogoRepositoryPort):
    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def obtener_o_crear_clave(self, clave: str) -> int:
        with self._session_factory() as session:
            registro = session.scalar(
                select(Clave).where(Clave.clave == clave).limit(1)
            )
            ahora = datetime.utcnow()
            if registro is None:
                registro = Clave(
                    clave=clave,
                    descripcion="Catálogo de feriados",
                    fecha_creacion=ahora,
                    vigente=True,
                    fecha_modificacion=ahora,
                )
                session.add(registro)
                session.flush()
                log.info("Clave '%s' creada | id_clave=%s", clave, registro.id_clave)
            elif not registro.vigente:
                registro.vigente = True
                registro.fecha_modificacion = ahora
                log.info("Clave '%s' reactivada | id_clave=%s", clave, registro.id_clave)
            else:
                log.info("Clave '%s' vigente | id_clave=%s", clave, registro.id_clave)

            id_clave = int(registro.id_clave)
            session.commit()
            return id_clave

    def sincronizar_rango(
        self,
        id_clave: int,
        descripcion: str,
        fecha_inicio: date,
        fecha_fin: date,
    ) -> FeriadoSincronizadoDetalle:
        detalle = FeriadoSincronizadoDetalle()
        dias_excel = set(rango_dias(fecha_inicio, fecha_fin))

        with self._session_factory() as session:
            like_descripcion = f"%{descripcion}%"
            filas = session.scalars(
                select(Catalogo).where(
                    Catalogo.id_clave == id_clave,
                    Catalogo.descripcion.like(like_descripcion),
                )
            ).all()

            dias_bd: Dict[date, dict] = {}
            for registro in filas:
                fecha_valor = parsear_fecha_catalogo(registro.valor)
                if fecha_valor is None:
                    log.warning(
                        "Catálogo ignorado (valor no fecha): id=%s valor=%s",
                        registro.id_catalogo,
                        registro.valor,
                    )
                    continue
                dias_bd[fecha_valor] = {
                    "id_catalogo": int(registro.id_catalogo),
                    "vigencia": bool(registro.vigencia),
                }

            ahora = datetime.utcnow()

            if not dias_bd:
                for dia in sorted(dias_excel):
                    session.add(
                        Catalogo(
                            id_clave=id_clave,
                            valor=fecha_a_valor_catalogo(dia),
                            descripcion=descripcion,
                            fecha_creacion=ahora,
                            vigencia=True,
                            fecha_modificacion=ahora,
                        )
                    )
                    detalle.insertados += 1
                session.commit()
                return detalle

            for dia in sorted(dias_excel):
                if dia in dias_bd:
                    if not dias_bd[dia]["vigencia"]:
                        reg = session.get(Catalogo, dias_bd[dia]["id_catalogo"])
                        if reg is not None:
                            reg.vigencia = True
                            reg.fecha_modificacion = ahora
                            detalle.activados += 1
                else:
                    session.add(
                        Catalogo(
                            id_clave=id_clave,
                            valor=fecha_a_valor_catalogo(dia),
                            descripcion=descripcion,
                            fecha_creacion=ahora,
                            vigencia=True,
                            fecha_modificacion=ahora,
                        )
                    )
                    detalle.insertados += 1

            for dia_bd, data in sorted(dias_bd.items()):
                if dia_bd not in dias_excel and data["vigencia"]:
                    reg = session.get(Catalogo, data["id_catalogo"])
                    if reg is not None:
                        reg.vigencia = False
                        reg.fecha_modificacion = ahora
                        detalle.desactivados += 1

            session.commit()

        return detalle
