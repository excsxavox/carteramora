from datetime import datetime
from typing import List, Optional

from sqlalchemy import select

from sqlalchemy.orm import Session, sessionmaker

from cobranzas.domain.models.credito import Credito
from cobranzas.domain.ports.cobranza_db_repository import CobranzaDbRepositoryPort
from cobranzas.infrastructure.persistence.mappers.cobranza_credito_mapper import (
    CLAVE_CLASIFICACION_MORA,
    catalogo_descripcion_clasificacion,
    cedula_asesor,
    clasificacion_mora_valor,
    codigo_asesor,
    estado_operacion_valor,
    montos_desde_credito,
    nombre_asesor,
)
from cobranzas.infrastructure.persistence.mappers.deuda_deudor_mapper import (
    mapear_deuda,
    mapear_deudor,
)
from cobranzas.infrastructure.persistence.models import (
    Asesor,
    AsesorDeuda,
    Catalogo,
    Clave,
    Deuda,
    Deudor,
)


def _parse_fecha_tab(valor: str):
    if not valor:
        return None
    texto = valor.strip()[:10]
    for fmt in ("%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(texto, fmt).date()
        except ValueError:
            continue
    return None


class SqlAlchemyCobranzaRepository(CobranzaDbRepositoryPort):
    """Persiste deudores, deudas, asesores y asignaciones desde cartera en mora."""

    def __init__(
        self,
        session_factory: sessionmaker,
        dias_mora_minimo: int = 30,
    ) -> None:
        self._session_factory = session_factory
        self._dias_mora_minimo = dias_mora_minimo

    def guardar_creditos_mora(self, creditos: List[Credito]) -> int:
        with self._session_factory() as session:
            procesados = 0
            for credito in creditos:
                self._upsert_credito(session, credito)
                procesados += 1
            session.commit()
        return procesados

    def _upsert_credito(self, session: Session, credito: Credito) -> None:
        datos_deudor = mapear_deudor(credito)
        datos_deuda = mapear_deuda(credito)
        deudor = self._obtener_o_crear_deudor(session, datos_deudor)
        deuda = self._obtener_o_crear_deuda(session, datos_deuda, deudor.id_deudor)
        self._actualizar_deuda(deuda, datos_deuda)

        id_catalogo = self._resolver_id_catalogo_mora(session, credito)
        id_asesor = self._obtener_o_crear_asesor(session, credito)
        self._upsert_asesor_deuda(
            session, credito, deuda.id_deuda, id_asesor, id_catalogo
        )

    def _obtener_o_crear_deudor(self, session: Session, datos) -> Deudor:
        deudor = session.scalar(
            select(Deudor).where(Deudor.documento == datos.documento).limit(1)
        )
        if deudor is None:
            deudor = Deudor(
                nombre=datos.nombre,
                documento=datos.documento,
                socio=datos.socio or None,
                creado_en=datetime.utcnow(),
            )
            session.add(deudor)
            session.flush()
            return deudor
        if datos.nombre:
            deudor.nombre = datos.nombre
        if datos.socio:
            deudor.socio = datos.socio
        return deudor

    def _obtener_o_crear_deuda(
        self, session: Session, datos, id_deudor: int
    ) -> Deuda:
        deuda = session.scalar(
            select(Deuda)
            .where(Deuda.numero_operacion == datos.numero_operacion)
            .limit(1)
        )
        if deuda is None:
            deuda = Deuda(
                id_deudor=id_deudor,
                numero_operacion=datos.numero_operacion,
                creado_en=datetime.utcnow(),
            )
            session.add(deuda)
            session.flush()
        elif deuda.id_deudor != id_deudor:
            deuda.id_deudor = id_deudor
        return deuda

    def _actualizar_deuda(self, deuda: Deuda, datos) -> None:
        deuda.oficina = datos.oficina or None
        deuda.descripcion_oficina = datos.descripcion_oficina or None
        deuda.sector = datos.sector or None
        deuda.tipo_operacion = datos.tipo_operacion or None
        deuda.tipo_destino = datos.tipo_destino or None
        deuda.fecha_concesion = _parse_fecha_tab(datos.fecha_concesion)
        deuda.fecha_vencimiento = _parse_fecha_tab(datos.fecha_vencimiento)
        deuda.fecha_ultimo_pago = _parse_fecha_tab(datos.fecha_ultimo_pago)
        deuda.valor_original_prestamo = datos.valor_original_prestamo
        deuda.saldo_capital_prestamo = datos.saldo_capital_prestamo
        deuda.calificacion = datos.calificacion or None
        deuda.total_provision = datos.total_provision
        deuda.saldo = datos.saldo

    def _obtener_o_crear_asesor(
        self, session: Session, credito: Credito
    ) -> Optional[int]:
        codigo = codigo_asesor(credito)
        if not codigo:
            return None

        documento_asesor = cedula_asesor(codigo)
        asesor = session.scalar(
            select(Asesor).where(Asesor.cedula == documento_asesor).limit(1)
        )
        nombre = nombre_asesor(credito) or f"Oficial {codigo}"
        if asesor is None:
            asesor = Asesor(
                nombre=nombre,
                cedula=documento_asesor,
                activo=True,
                creado_en=datetime.utcnow(),
            )
            session.add(asesor)
            session.flush()
            return asesor.id_asesor

        if nombre and asesor.nombre != nombre:
            asesor.nombre = nombre
        return asesor.id_asesor

    def _obtener_o_crear_clave(self, session: Session, codigo_clave: str) -> int:
        clave = session.scalar(
            select(Clave).where(Clave.clave == codigo_clave).limit(1)
        )
        if clave is None:
            clave = Clave(
                clave=codigo_clave,
                descripcion=f"Catálogo {codigo_clave}",
                vigente=True,
                fecha_creacion=datetime.utcnow(),
            )
            session.add(clave)
            session.flush()
        return clave.id_clave

    def _obtener_o_crear_catalogo(
        self,
        session: Session,
        id_clave: int,
        valor: str,
        descripcion: str,
    ) -> int:
        if not valor:
            valor = "sin_valor"
        catalogo = session.scalar(
            select(Catalogo)
            .where(Catalogo.id_clave == id_clave, Catalogo.valor == valor)
            .limit(1)
        )
        if catalogo is None:
            catalogo = Catalogo(
                id_clave=id_clave,
                valor=valor,
                descripcion=descripcion,
                vigencia=True,
                fecha_creacion=datetime.utcnow(),
            )
            session.add(catalogo)
            session.flush()
        return catalogo.id_catalogo

    def _resolver_id_catalogo_mora(
        self, session: Session, credito: Credito
    ) -> int:
        estado = credito.clasificar_mora(self._dias_mora_minimo)
        id_clave = self._obtener_o_crear_clave(session, CLAVE_CLASIFICACION_MORA)
        return self._obtener_o_crear_catalogo(
            session,
            id_clave,
            clasificacion_mora_valor(credito, self._dias_mora_minimo),
            catalogo_descripcion_clasificacion(estado),
        )

    def _upsert_asesor_deuda(
        self,
        session: Session,
        credito: Credito,
        id_deuda: int,
        id_asesor: Optional[int],
        id_catalogo: int,
    ) -> None:
        if id_asesor is None:
            return

        monto, monto_inicial, monto_mora = montos_desde_credito(credito)
        estado = estado_operacion_valor(credito)
        ahora = datetime.utcnow()

        asignacion = session.scalar(
            select(AsesorDeuda).where(AsesorDeuda.id_deuda == id_deuda).limit(1)
        )
        if asignacion is None:
            session.add(
                AsesorDeuda(
                    id_catalogo=id_catalogo,
                    id_asesor=id_asesor,
                    id_deuda=id_deuda,
                    estado=estado,
                    monto=monto,
                    monto_inicial=monto_inicial,
                    monto_mora=monto_mora,
                    fecha_asignacion=credito.fecha_corte,
                    fecha_modificacion=ahora,
                )
            )
            return

        asignacion.id_catalogo = id_catalogo
        asignacion.id_asesor = id_asesor
        asignacion.estado = estado
        asignacion.monto = monto
        asignacion.monto_inicial = monto_inicial
        asignacion.monto_mora = monto_mora
        asignacion.fecha_asignacion = credito.fecha_corte
        asignacion.fecha_modificacion = ahora
