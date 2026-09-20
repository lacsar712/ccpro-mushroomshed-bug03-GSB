from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ClimateLog(Base):
    __tablename__ = "climate_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), nullable=False, index=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    temp_c: Mapped[float] = mapped_column(Float, nullable=False)
    # Decimal with fractional scale so boundary-adjacent values (e.g. 0.5/1.5) survive a round-trip.
    humidity_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    co2_ppm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    room: Mapped["Room"] = relationship("Room", back_populates="climate_logs")
