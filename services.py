"""
Services for Twilio messaging and notifications.
"""

from twilio.rest import Client
from datetime import datetime, timedelta
from typing import Optional
import logging

from models import Flight, NotificationType, NotificationLog
from config import Config, AIRLINE_CHECKIN_URLS, AIRPORT_NAMES

logger = logging.getLogger(__name__)


class TwilioService:
    """Handles WhatsApp messaging via Twilio."""
    
    def __init__(self):
        self.client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
        self.whatsapp_number = Config.TWILIO_WHATSAPP_NUMBER
    
    def send_message(self, to: str, body: str) -> Optional[str]:
        """
        Send WhatsApp message.
        
        Args:
            to: Recipient phone number
            body: Message content
            
        Returns:
            Message SID if successful, None otherwise
        """
        try:
            message = self.client.messages.create(
                from_=f"whatsapp:{self.whatsapp_number}",
                to=f"whatsapp:{to}",
                body=body
            )
            logger.info(f"Message sent successfully. SID: {message.sid}")
            return message.sid
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return None


class NotificationService:
    """Handles notification creation and sending."""
    
    def __init__(self, twilio_service: TwilioService):
        self.twilio = twilio_service
        self.notification_history = []
    
    def send_booking_confirmation(self, flight: Flight, phone: str) -> NotificationLog:
        """Send initial booking confirmation."""
        checkin_url = AIRLINE_CHECKIN_URLS.get(flight.airline_code, "")
        dep_airport = AIRPORT_NAMES.get(flight.departure_airport, flight.departure_airport)
        arr_airport = AIRPORT_NAMES.get(flight.arrival_airport, flight.arrival_airport)
        
        message = f"""✈️ *Welcome to AirSathi!* ✈️

Dear *{flight.passenger_name}*,

Your flight is confirmed! Here are your details:

📋 *PNR:* {flight.pnr}
✈️ *Flight:* {flight.flight_number}
🛫 *From:* {flight.departure_airport} - {dep_airport}
🛬 *To:* {flight.arrival_airport} - {arr_airport}
📅 *Departure:* {self._format_datetime(flight.scheduled_departure)}
📅 *Arrival:* {self._format_datetime(flight.scheduled_arrival)}
🚪 *Gate:* {flight.gate or 'TBA'}
🏢 *Terminal:* {flight.terminal}

🌐 *Web Check-in:* {checkin_url}

💡 *AirSathi Tips:*
• Arrive 2 hours before domestic flights
• Complete web check-in for faster boarding
• Keep your ID and boarding pass ready

I'll keep you updated on any changes! 🛫"""

        message_sid = self.twilio.send_message(phone, message)
        
        log = NotificationLog(
            notification_type=NotificationType.BOOKING,
            message_sid=message_sid or "failed",
            sent_at=datetime.now(),
            metadata={"pnr": flight.pnr}
        )
        self.notification_history.append(log)
        return log
    
    def send_gate_change(
        self, 
        flight: Flight, 
        phone: str, 
        old_gate: str, 
        new_gate: str
    ) -> NotificationLog:
        """Send gate change alert."""
        message = f"""🚨 *GATE CHANGE ALERT* 🚨

Dear *{flight.passenger_name}*,

Your departure gate has changed:

✈️ *Flight:* {flight.flight_number}
📋 *PNR:* {flight.pnr}

🚪 *Old Gate:* {old_gate}
🚪 *NEW GATE:* *{new_gate}*
🏢 *Terminal:* {flight.terminal}
📅 *Departure:* {self._format_datetime(flight.scheduled_departure)}

⏰ Please proceed to the new gate immediately.

Need directions? Reply for assistance."""

        message_sid = self.twilio.send_message(phone, message)
        
        log = NotificationLog(
            notification_type=NotificationType.GATE_CHANGE,
            message_sid=message_sid or "failed",
            sent_at=datetime.now(),
            metadata={"old_gate": old_gate, "new_gate": new_gate, "pnr": flight.pnr}
        )
        self.notification_history.append(log)
        return log
    
    def send_delay_notification(
        self, 
        flight: Flight, 
        phone: str, 
        delay_minutes: int
    ) -> NotificationLog:
        """Send flight delay notification."""
        new_departure = flight.scheduled_departure + timedelta(minutes=delay_minutes)
        new_arrival = flight.scheduled_arrival + timedelta(minutes=delay_minutes)
        
        delay_text = (
            f"{delay_minutes} minutes" if delay_minutes < 60 
            else f"{delay_minutes // 60} hour(s) {delay_minutes % 60} minutes"
        )
        
        message = f"""⏰ *FLIGHT DELAY NOTIFICATION* ⏰

Dear *{flight.passenger_name}*,

Your flight has been delayed:

✈️ *Flight:* {flight.flight_number}
📋 *PNR:* {flight.pnr}

🕐 *Original Departure:* {self._format_datetime(flight.scheduled_departure)}
🕐 *NEW Departure:* {self._format_datetime(new_departure)}
⏱️ *Delay:* {delay_text}

🚪 *Gate:* {flight.gate or 'TBA'}
🏢 *Terminal:* {flight.terminal}

We apologize for the inconvenience. I'll notify you of any further changes.

Reply 'LOUNGE' for lounge access info or 'FOOD' for dining options."""

        message_sid = self.twilio.send_message(phone, message)
        
        log = NotificationLog(
            notification_type=NotificationType.DELAY,
            message_sid=message_sid or "failed",
            sent_at=datetime.now(),
            metadata={
                "delay_minutes": delay_minutes,
                "new_departure": new_departure.isoformat(),
                "pnr": flight.pnr
            }
        )
        self.notification_history.append(log)
        return log
    
    def send_flight_reminder(
        self, 
        flight: Flight, 
        phone: str, 
        hours_until: int = 24
    ) -> NotificationLog:
        """Send flight reminder."""
        message = f"""✈️ *FLIGHT REMINDER* ✈️

Dear *{flight.passenger_name}*,

Your flight departs in *{hours_until} hours*!

📋 *PNR:* {flight.pnr}
✈️ *Flight:* {flight.flight_number}
🛫 *From:* {flight.departure_airport}
🛬 *To:* {flight.arrival_airport}
📅 *Departure:* {self._format_datetime(flight.scheduled_departure)}

🚪 *Gate:* {flight.gate or 'TBA'}
🏢 *Terminal:* {flight.terminal}

✅ *Pre-Flight Checklist:*
• Valid ID and boarding pass
• Baggage within limits
• Arrive 2 hours early
• Web check-in completed

Reply 'STATUS' for current flight status or 'HELP' for assistance.

Safe travels! 🌟"""

        message_sid = self.twilio.send_message(phone, message)
        
        log = NotificationLog(
            notification_type=NotificationType.REMINDER,
            message_sid=message_sid or "failed",
            sent_at=datetime.now(),
            metadata={"hours_until": hours_until, "pnr": flight.pnr}
        )
        self.notification_history.append(log)
        return log
    
    @staticmethod
    def _format_datetime(dt: datetime) -> str:
        """Format datetime for display."""
        return dt.strftime("%d %b %Y, %I:%M %p")
    
    def get_history(self):
        """Get notification history."""
        return self.notification_history