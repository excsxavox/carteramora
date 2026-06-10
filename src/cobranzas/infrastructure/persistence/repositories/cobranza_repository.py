import logging
from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import delete, select

from sqlalchemy.orm import Session, sessionmaker

from cobranzas.domain.models.credito import Credito
from cobranzas.domain.ports.cobranza_db_repository import CobranzaDbRepositoryPort
from cobranzas.domain.ports.recblue_port import RecbluePort
from cobranzas.infrastructure.persistence.mappers.cobranza_credito_mapper import (
    CLAVE_CLASIFICACION_MORA,
    cedula_asesor,
    clasificacion_para_asignacion,
    codigo_asesor,
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


logger = logging.getLogger("cobranzas.persistencia")


class SqlAlchemyCobranzaRepository(CobranzaDbRepositoryPort):
    """Persiste deudores, deudas, asesores y asignaciones desde cartera en mora."""

    def __init__(
        self,
        session_factory: sessionmaker,
        dias_mora_minimo: int = 30,
        recblue: Optional[RecbluePort] = None,
        usar_mora_temprana: bool = False,
        mora_temprana_dias_min: int = 1,
        mora_temprana_dias_max: int = 0,
    ) -> None:
        self._session_factory = session_factory
        self._dias_mora_minimo = dias_mora_minimo
        self._recblue = recblue
        self._usar_mora_temprana = usar_mora_temprana
        self._mora_temprana_dias_min = mora_temprana_dias_min
        self._mora_temprana_dias_max = mora_temprana_dias_max
        self._cache_recblue: Optional[dict] = None

    def guardar_creditos_mora(self, creditos: List[Credito]) -> int:
        if not creditos:
            return 0

        fechas = {c.fecha_corte for c in creditos}
        if len(fechas) != 1:
            raise ValueError(
                "Todos los créditos del lote deben compartir la misma fecha_corte"
            )
        fecha_corte = next(iter(fechas))

        with self._session_factory() as session:
            try:
                borrados = self._eliminar_lote_fecha_corte(session, fecha_corte)
                if borrados:
                    logger.info(
                        "Lote %s: eliminados %s registro(s) previos "
                        "(deuda + asesores_deuda)",
                        fecha_corte.isoformat(),
                        borrados,
                    )

                for credito in creditos:
                    self._upsert_credito(session, credito)

                session.commit()
                logger.info(
                    "Lote %s persistido | operaciones=%s",
                    fecha_corte.isoformat(),
                    len(creditos),
                )
                return len(creditos)
            except Exception:
                session.rollback()
                logger.exception(
                    "Error persistiendo lote %s; se revirtió la transacción",
                    fecha_corte.isoformat(),
                )
                raise

    def _eliminar_lote_fecha_corte(self, session: Session, fecha_corte: date) -> int:
        """Borra asignaciones y deudas del corte antes de recargar el mismo día."""
        ids_deuda = list(
            session.scalars(
                select(Deuda.id_deuda).where(Deuda.fecha_corte == fecha_corte)
            ).all()
        )
        if not ids_deuda:
            return 0

        session.execute(
            delete(AsesorDeuda).where(AsesorDeuda.id_deuda.in_(ids_deuda))
        )
        session.execute(delete(Deuda).where(Deuda.fecha_corte == fecha_corte))
        return len(ids_deuda)

    def _upsert_credito(self, session: Session, credito: Credito) -> None:
        datos_deudor = mapear_deudor(credito)
        datos_deuda = mapear_deuda(credito)
        deudor = self._obtener_o_crear_deudor(session, datos_deudor)
        deuda = self._obtener_o_crear_deuda(session, datos_deuda, deudor.id_deudor)
        self._actualizar_deuda(deuda, datos_deuda)

        cat_valor, cat_desc, estado_asignacion = clasificacion_para_asignacion(
            credito,
            self._dias_mora_minimo,
            usar_mora_temprana=self._usar_mora_temprana,
            mora_temprana_dias_min=self._mora_temprana_dias_min,
            mora_temprana_dias_max=self._mora_temprana_dias_max,
        )
        id_clave = self._obtener_o_crear_clave(session, CLAVE_CLASIFICACION_MORA)
        id_catalogo = self._obtener_o_crear_catalogo(
            session, id_clave, cat_valor, cat_desc
        )
        id_asesor = self._obtener_o_crear_asesor(session, credito)
        self._upsert_asesor_deuda(
            session,
            credito,
            deuda.id_deuda,
            id_asesor,
            id_catalogo,
            estado_asignacion,
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
        ahora = datetime.utcnow()
        deuda.fecha_carga = ahora
        deuda.fecha_corte = datos.fecha_corte
        deuda.archivo_origen = datos.archivo_origen or None
        deuda.oficina = datos.oficina or None
        deuda.desc_oficina = datos.desc_oficina or None
        deuda.socio = datos.socio or None
        deuda.nombre = datos.nombre or None
        deuda.cedula = datos.cedula or None
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
        deuda.saldo_140x = datos.saldo_140x
        deuda.saldo_141x = datos.saldo_141x
        deuda.saldo_142x = datos.saldo_142x
        deuda.interes_normal = datos.interes_normal
        deuda.interes_devengado = datos.interes_devengado
        deuda.interes_vencido = datos.interes_vencido
        deuda.interes_resolucion = datos.interes_resolucion
        deuda.interes_castigado = datos.interes_castigado
        deuda.interes_mora = datos.interes_mora
        deuda.otros_rubros_deuda = datos.otros_rubros_deuda
        deuda.total_operacion = datos.total_operacion
        deuda.estado = datos.estado or None
        deuda.oficial = datos.oficial or None
        deuda.dias_mora = datos.dias_mora
        deuda.dias_atraso_camorosico = datos.dias_atraso_camorosico
        deuda.fecha_ingreso = _parse_fecha_tab(datos.fecha_ingreso)
        deuda.tipo = datos.tipo or None
        deuda.dia_pago = datos.dia_pago
        deuda.valor_cuota = datos.valor_cuota
        deuda.cuota_actual = datos.cuota_actual
        deuda.dividendos = datos.dividendos
        deuda.cod_oficial_asignado = datos.cod_oficial_asignado or None
        deuda.oficial_asignado = datos.oficial_asignado or None
        deuda.cod_oficial_adm = datos.cod_oficial_adm or None
        deuda.oficial_adm = datos.oficial_adm or None
        deuda.operacion_homologada = datos.operacion_homologada or None
        deuda.decision = datos.decision or None
        deuda.segmentacion = datos.segmentacion or None
        deuda.score = datos.score or None
        deuda.fuente_repago = datos.fuente_repago or None
        deuda.identificacion_ifi = datos.identificacion_ifi or None
        deuda.actividad_economica = datos.actividad_economica or None
        deuda.fecha_archivo = _parse_fecha_tab(datos.fecha_archivo)
        deuda.tipo_mes = datos.tipo_mes or None
        deuda.tipo_fideicomiso = datos.tipo_fideicomiso or None
        deuda.proceso_cod = datos.proceso_cod

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

    def _upsert_asesor_deuda(
        self,
        session: Session,
        credito: Credito,
        id_deuda: int,
        id_asesor: Optional[int],
        id_catalogo: int,
        estado_asignacion: str,
    ) -> None:
        if id_asesor is None:
            return

        monto, monto_inicial, monto_mora = montos_desde_credito(credito)
        id_credito_recblue = self._resolver_id_credito_recblue(credito)
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
                    estado=estado_asignacion,
                    monto=monto,
                    monto_inicial=monto_inicial,
                    monto_mora=monto_mora,
                    id_credito_recblue=id_credito_recblue,
                    fecha_asignacion=credito.fecha_corte,
                    fecha_modificacion=ahora,
                )
            )
            return

        asignacion.id_catalogo = id_catalogo
        asignacion.id_asesor = id_asesor
        asignacion.estado = estado_asignacion
        asignacion.monto = monto
        asignacion.monto_inicial = monto_inicial
        asignacion.monto_mora = monto_mora
        asignacion.id_credito_recblue = id_credito_recblue
        asignacion.fecha_asignacion = credito.fecha_corte
        asignacion.fecha_modificacion = ahora

    def _resolver_id_credito_recblue(self, credito: Credito) -> Optional[str]:
        id_rb = (credito.id_credito_recblue or "").strip()
        if id_rb:
            return id_rb
        if self._recblue is None:
            return None
        if self._cache_recblue is None:
            self._cache_recblue = self._recblue.id_credito_por_operacion()
        id_rb = (self._cache_recblue.get(credito.id_credito) or "").strip()
        return id_rb or None
