

from fastapi import FastAPI, Query, Request
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
    return {
        "status": "operational",
        "app": Config.APP_NAME,
        "version": Config.APP_VERSION
    }


@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    form = await request.form()

    # Twilio sends numbers in the format 'whatsapp:+91XXXXXXXXXX'
    from_number = form.get("From", "")
    body = form.get("Body", "") or ""

    # For this POC we assume a single mock flight and treat any inbound
    # WhatsApp message as coming from our test passenger.
    log = notification_service.handle_incoming_message(
        mock_flight,
        from_number.replace("whatsapp:", ""),  # normalise in case the prefix is present
        body,
    )

    return {
        "status": "received",
        "type": log.notification_type,
        "message_id": log.message_sid,
    }


@app.post("/api/send-booking-confirmation")
def send_booking():
    log = notification_service.send_booking_confirmation(mock_flight, Config.PASSENGER_PHONE)
    return {
        "status": "sent",
        "type": log.notification_type,
        "message_id": log.message_sid,
        "pnr": mock_flight.pnr
    }


@app.post("/api/send-gate-change")
def send_gate(new_gate: str = Query("45C")):
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
    log = notification_service.send_flight_reminder(
        mock_flight, Config.PASSENGER_PHONE, hours
    )
    return {
        "status": "sent",
        "type": log.notification_type,
        "message_id": log.message_sid,
        "hours_until": hours
    }


@app.post("/api/send-pre-flight-checklist")
def send_pre_flight_checklist(hours: int = Query(24)):
    log = notification_service.send_pre_flight_checklist(
        mock_flight, Config.PASSENGER_PHONE, hours
    )
    return {
        "status": "sent",
        "type": log.notification_type,
        "message_id": log.message_sid,
        "hours_until": hours
    }


@app.post("/api/send-smart-arrival-assistance")
def send_smart_arrival_assistance(buffer_hours: int = Query(2)):
    log = notification_service.send_smart_arrival_assistance(
        mock_flight, Config.PASSENGER_PHONE, buffer_hours
    )
    return {
        "status": "sent",
        "type": log.notification_type,
        "message_id": log.message_sid,
        "buffer_hours": buffer_hours
    }


@app.post("/api/send-boarding-call")
def send_boarding_call(boarding_in_minutes: int = Query(30)):
    log = notification_service.send_boarding_call(
        mock_flight, Config.PASSENGER_PHONE, boarding_in_minutes
    )
    return {
        "status": "sent",
        "type": log.notification_type,
        "message_id": log.message_sid,
        "boarding_in_minutes": boarding_in_minutes
    }


@app.post("/api/send-baggage-belt-update")
def send_baggage_belt_update(belt_number: str = Query("5")):
    log = notification_service.send_baggage_belt_update(
        mock_flight, Config.PASSENGER_PHONE, belt_number
    )
    return {
        "status": "sent",
        "type": log.notification_type,
        "message_id": log.message_sid,
        "belt_number": belt_number
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