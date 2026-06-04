from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cobranzas.infrastructure.persistence.base import Base

if TYPE_CHECKING:
    from cobranzas.infrastructure.persistence.models.deuda import Deuda


class Deudor(Base):
    __tablename__ = "deudores"

    id_deudor: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    documento: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    socio: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    creado_en: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=False), nullable=True
    )

    deudas: Mapped[List["Deuda"]] = relationship(back_populates="deudor")
