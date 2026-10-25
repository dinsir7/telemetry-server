import os
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker

# База данных: берется из переменной окружения облака
DATABASE_URL = os.getenv("DATABASE_URL")

# Небольшое исправление для облачных адресов PostgreSQL
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class SystemTelemetry(Base):
    __tablename__ = "telemetry"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    device_name = Column(String)
    cpu_percent = Column(Float)
    ram_percent = Column(Float)
    disk_usage_percent = Column(Float)
    disk_free_gb = Column(Float)
    disk_read_mbs = Column(Float, nullable=True)
    disk_write_mbs = Column(Float, nullable=True)
    disk_name = Column(String)
    disk_type = Column(String)
    disk_temperature = Column(Float, nullable=True)
    power_on_hours = Column(Integer, nullable=True)
    critical_warning = Column(Integer, nullable=True)
    wear_percentage = Column(Float, nullable=True)
    available_spare = Column(Float, nullable=True)
    data_units_written_gb = Column(Float, nullable=True)
    data_units_read_gb = Column(Float, nullable=True)
    unsafe_shutdowns = Column(Integer, nullable=True)
    media_errors = Column(Integer, nullable=True)
    reallocated_sectors = Column(Integer, nullable=True)
    pending_sectors = Column(Integer, nullable=True)
    uncorrectable_errors = Column(Integer, nullable=True)
    offline_uncorrectable = Column(Integer, nullable=True)
    command_timeouts = Column(Integer, nullable=True)
    crc_errors = Column(Integer, nullable=True)


app = FastAPI(title="Cloud Telemetry Server")


class TelemetryItem(BaseModel):
    timestamp: datetime
    device_name: str
    cpu_percent: float
    ram_percent: float
    disk_usage_percent: float
    disk_free_gb: float
    disk_read_mbs: Optional[float] = 0.0
    disk_write_mbs: Optional[float] = 0.0
    disk_name: str
    disk_type: str
    disk_temperature: Optional[float] = None
    power_on_hours: Optional[int] = None
    critical_warning: Optional[int] = 0
    wear_percentage: Optional[float] = None
    available_spare: Optional[float] = None
    data_units_written_gb: Optional[float] = None
    data_units_read_gb: Optional[float] = None
    unsafe_shutdowns: Optional[int] = None
    media_errors: Optional[int] = None
    reallocated_sectors: Optional[int] = None
    pending_sectors: Optional[int] = None
    uncorrectable_errors: Optional[int] = None
    offline_uncorrectable: Optional[int] = None
    command_timeouts: Optional[int] = None
    crc_errors: Optional[int] = None


@app.get("/")
def home():
    return {"status": "Telemetry Server is running 24/7!"}


@app.post("/api/telemetry")
def receive_telemetry(items: List[TelemetryItem]):
    session = SessionLocal()
    try:
        for item in items:
            entry = SystemTelemetry(**item.dict())
            session.add(entry)
        session.commit()
        return {"status": "success", "saved": len(items)}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
