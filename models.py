"""
Data models for AirSathi POC.
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum


class NotificationType(str, Enum):
    """Types of notifications."""
    BOOKING = "booking"
    GATE_CHANGE = "gate_change"
    DELAY = "delay"
    REMINDER = "reminder"


class Flight(BaseModel):
    """Flight information model."""
    pnr: str
    flight_number: str
    airline_code: str
    passenger_name: str
    departure_airport: str
    arrival_airport: str
    scheduled_departure: datetime
    scheduled_arrival: datetime
    gate: Optional[str] = None
    terminal: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "pnr": "ABC123",
                "flight_number": "6E-2345",
                "airline_code": "6E",
                "passenger_name": "Rajesh Kumar",
                "departure_airport": "DEL",
                "arrival_airport": "BLR",
                "scheduled_departure": "2026-01-25T10:30:00",
                "scheduled_arrival": "2026-01-25T13:00:00",
                "gate": "23A",
                "terminal": "3"
            }
        }


class NotificationLog(BaseModel):
    """Log entry for sent notifications."""
    notification_type: NotificationType
    message_sid: str
    sent_at: datetime
    metadata: dict = {}
    
    class Config:
        json_schema_extra = {
            "example": {
                "notification_type": "gate_change",
                "message_sid": "SM1234567890",
                "sent_at": "2026-01-25T09:00:00",
                "metadata": {"old_gate": "23A", "new_gate": "45C"}
            }
        }