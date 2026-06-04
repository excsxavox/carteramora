from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cobranzas.infrastructure.persistence.base import Base

if TYPE_CHECKING:
    from cobranzas.infrastructure.persistence.models.catalogo import Catalogo


class Clave(Base):
    __tablename__ = "claves"

    id_clave: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    clave: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    descripcion: Mapped[Optional[str]] = mapped_column(String(250), nullable=True)
    fecha_creacion: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=False), nullable=True
    )
    vigente: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    fecha_modificacion: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=False), nullable=True
    )

    catalogos: Mapped[List["Catalogo"]] = relationship(back_populates="clave")
