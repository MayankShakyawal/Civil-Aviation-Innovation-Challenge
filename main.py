"""
AirSathi POC - Main Application
WhatsApp-based Travel Notifications for Indian Airports
"""

from fastapi import FastAPI, Query
from datetime import datetime
import logging

from models import Flight
from services import TwilioService, NotificationService
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="AirSathi POC",
    description="WhatsApp Travel Notifications",
    version="1.0.0"
)

# Initialize services
twilio_service = TwilioService()
notification_service = NotificationService(twilio_service)

# Mock flight data
mock_flight = Flight(
    pnr="ABC123",
    flight_number="6E-2345",
    airline_code="6E",
    passenger_name=Config.PASSENGER_NAME,
    departure_airport="DEL",
    arrival_airport="BLR",
    scheduled_departure=datetime(2026, 1, 25, 10, 30),
    scheduled_arrival=datetime(2026, 1, 25, 13, 0),
    gate="23A",
    terminal="3"
)


@app.get("/")
def health_check():
    """Health check endpoint."""
    return {
        "status": "operational",
        "app": Config.APP_NAME,
        "version": Config.APP_VERSION
    }


@app.post("/api/send-booking-confirmation")
def send_booking():
    """Send booking confirmation."""
    log = notification_service.send_booking_confirmation(mock_flight, Config.PASSENGER_PHONE)
    return {
        "status": "sent",
        "type": log.notification_type,
        "message_id": log.message_sid,
        "pnr": mock_flight.pnr
    }


@app.post("/api/send-gate-change")
def send_gate(new_gate: str = Query("45C")):
    """Send gate change notification."""
    old_gate = mock_flight.gate or "N/A"
    mock_flight.gate = new_gate
    
    log = notification_service.send_gate_change(
        mock_flight, Config.PASSENGER_PHONE, old_gate, new_gate
    )
    return {
        "status": "sent",
        "type": log.notification_type,
        "message_id": log.message_sid,
        "old_gate": old_gate,
        "new_gate": new_gate
    }


@app.post("/api/send-delay")
def send_delay(delay_minutes: int = Query(30)):
    """Send delay notification."""
    log = notification_service.send_delay_notification(
        mock_flight, Config.PASSENGER_PHONE, delay_minutes
    )
    return {
        "status": "sent",
        "type": log.notification_type,
        "message_id": log.message_sid,
        "delay": delay_minutes
    }


@app.post("/api/send-reminder")
def send_reminder(hours: int = Query(24)):
    """Send flight reminder."""
    log = notification_service.send_flight_reminder(
        mock_flight, Config.PASSENGER_PHONE, hours
    )
    return {
        "status": "sent",
        "type": log.notification_type,
        "message_id": log.message_sid,
        "hours_until": hours
    }


@app.get("/api/flight-info")
def get_flight():
    """Get current flight info."""
    return {
        "pnr": mock_flight.pnr,
        "flight": mock_flight.flight_number,
        "route": f"{mock_flight.departure_airport} → {mock_flight.arrival_airport}",
        "departure": mock_flight.scheduled_departure.isoformat(),
        "gate": mock_flight.gate,
        "terminal": mock_flight.terminal
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)