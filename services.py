

from twilio.rest import Client
from datetime import datetime, timedelta
from typing import Optional
import logging

from models import Flight, NotificationType, NotificationLog
from config import Config, AIRLINE_CHECKIN_URLS, AIRPORT_NAMES

logger = logging.getLogger(__name__)


class TwilioService:
    
    def __init__(self):
        self.client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
        self.whatsapp_number = Config.TWILIO_WHATSAPP_NUMBER
    
    
    def send_message(self, to: str, body: str, media_url: str = None, media_urls: list = None) -> Optional[str]:
        try:
            message_params = {
                "from_": f"whatsapp:{self.whatsapp_number}",
                "to": f"whatsapp:{to}",
                "body": body
            }
        
        # Handle multiple media URLs (carousel)
            if media_urls:
                message_params["media_url"] = media_urls
            # Handle single media URL
            elif media_url:
                message_params["media_url"] = [media_url]
            
            message = self.client.messages.create(**message_params)
            logger.info(f"Message sent successfully. SID: {message.sid}")
            return message.sid
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return None


class NotificationService:
    
    def __init__(self, twilio_service: TwilioService):
        self.twilio = twilio_service
        self.notification_history = []

    def handle_incoming_message(
        self,
        flight: Flight,
        from_number: str,
        user_message: str,
    ) -> NotificationLog:
        text = (user_message or "").strip().lower()

        if not text:
            reply = (
                "Namaste from AirSathi! I couldn't read your message.\n\n"
                "You can ask things like:\n"
                "- 'status' – to get your flight status\n"
                "- 'gate' – to know your gate and terminal\n"
                "- 'help' – to see all options again"
            )
        elif "gate" in text:
            reply = (
                f"*AirSathi – Gate & Terminal Info*\n\n"
                f"Flight {flight.flight_number} (PNR {flight.pnr}) is scheduled to depart from "
                f"Gate *{flight.gate or 'TBA'}*, Terminal *{flight.terminal}*.\n\n"
                "Follow airport signages to the gate and keep an eye on display boards for any changes."
            )
        elif "status" in text or "delay" in text or "time" in text:
            reply = (
                f"*AirSathi – Flight Status (POC)*\n\n"
                f"Your flight {flight.flight_number} (PNR {flight.pnr}) is scheduled to depart at "
                f"{self._format_datetime(flight.scheduled_departure)}.\n\n"
                "This POC uses static mock data – in a production version this would be connected "
                "to live airline / airport APIs for real-time status and delays."
            )
        elif "check in" in text or "check-in" in text or "web checkin" in text:
            from config import AIRLINE_CHECKIN_URLS  # local import to avoid cycles at module load

            checkin_url = AIRLINE_CHECKIN_URLS.get(flight.airline_code, "")
            if checkin_url:
                reply = (
                    f"*AirSathi – Web Check‑in Link*\n\n"
                    f"For flight {flight.flight_number} (PNR {flight.pnr}), you can use the "
                    f"following link for web check‑in:\n{checkin_url}"
                )
            else:
                reply = (
                    "*AirSathi – Web Check‑in*\n\n"
                    "I don't yet have a saved web check‑in link for this airline in the POC setup."
                )
        elif "help" in text or "menu" in text or "options" in text:
            reply = (
                "*AirSathi – What I Can Help With (POC)*\n\n"
                "You can try sending:\n"
                "- 'status' – get basic flight status from mock data\n"
                "- 'gate' – see your gate and terminal\n"
                "- 'check in' – get an airline web check‑in link (if available)\n"
                "- 'help' – show this menu again"
            )
        elif "items" in text:
            
            if flight:
                # Send pre-flight checklist with image
                self.send_pre_flight_checklist(
                    flight=flight,
                    phone=from_number,
                    hours_until=24
                )
                reply = "I've sent you a detailed pre-flight checklist with baggage allowance information. Please review it carefully!!"
            else:
                reply = "I couldn't find your flight details. Please share your PNR to get the pre-flight checklist."
        elif "airport" in text:
            
            if flight:
                # Send pre-flight checklist with image
                self.send_smart_arrival_assistance(
                    flight=flight,
                    phone=from_number,
                    buffer_hours=24,
                    link_map="https://maps.app.goo.gl/Fpk1LuQzKJ5Gqu379"
                )
                reply = "I've sent you arrival assistance to help you navigate the airport smoothly."
            else:
                reply = "I couldn't find your flight details. Please share your PNR to get the pre-flight checklist."
        else:
            reply = (
                "*AirSathi – I Didn't Understand That*\n\n"
                "This is an early POC, so I currently understand only a few keywords.\n\n"
                "Try sending one of these:\n"
                "- 'status'\n"
                "- 'gate'\n"
                "- 'check in'\n"
                "- 'help'"
            )

        message_sid = self.twilio.send_message(from_number, reply)

        log = NotificationLog(
            notification_type=NotificationType.USER_MESSAGE,
            message_sid=message_sid or "failed",
            sent_at=datetime.now(),
            metadata={"from": from_number, "user_message": user_message},
        )
        self.notification_history.append(log)
        return log
    
    def send_booking_confirmation(self, flight: Flight, phone: str) -> NotificationLog:
        checkin_url = AIRLINE_CHECKIN_URLS.get(flight.airline_code, "")
        dep_airport = AIRPORT_NAMES.get(flight.departure_airport, flight.departure_airport)
        arr_airport = AIRPORT_NAMES.get(flight.arrival_airport, flight.arrival_airport)
        
        message = f"""*AirSathi – Booking Confirmation*

Dear *{flight.passenger_name}*,

Your flight booking has been confirmed. Please find the details below:

*PNR:* {flight.pnr}
*Flight:* {flight.flight_number}
*From:* {flight.departure_airport} - {dep_airport}
*To:* {flight.arrival_airport} - {arr_airport}
*Scheduled Departure:* {self._format_datetime(flight.scheduled_departure)}
*Scheduled Arrival:* {self._format_datetime(flight.scheduled_arrival)}
*Gate:* {flight.gate or 'TBA'}
*Terminal:* {flight.terminal}

*Web check-in:* {checkin_url}

You can type “help” or “menu” for seeing more options in this chat to prepare for your journey. I will inform if there are any further updates to your flight."""

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
        message = f"""*AirSathi – Gate Change Notification*

Dear *{flight.passenger_name}*,

The departure gate for your flight has changed. Please review the updated details:

*Flight:* {flight.flight_number}
*PNR:* {flight.pnr}
*Previous Gate:* {old_gate}
*New Gate:* {new_gate}
*Terminal:* {flight.terminal}
*Scheduled Departure:* {self._format_datetime(flight.scheduled_departure + timedelta(minutes=45))}

Please proceed to the new gate at the earliest. If you require directions within the terminal, reply to this message."""

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
        new_departure = flight.scheduled_departure + timedelta(minutes=delay_minutes)
        new_arrival = flight.scheduled_arrival + timedelta(minutes=delay_minutes)
        
        delay_text = (
            f"{delay_minutes} minutes" if delay_minutes < 60 
            else f"{delay_minutes // 60} hour(s) {delay_minutes % 60} minutes"
        )
        
        message = f"""*AirSathi – Flight Delay Notification*

Dear *{flight.passenger_name}*,

We would like to inform you that your flight has been delayed. The updated details are as follows:

*Flight:* {flight.flight_number}
*PNR:* {flight.pnr}
*Original Departure Time:* {self._format_datetime(flight.scheduled_departure)}
*Revised Departure Time:* {self._format_datetime(new_departure)}
*Delay Duration:* {delay_text}
*Gate:* {flight.gate or 'TBA'}
*Terminal:* {flight.terminal}

I will notify you notified if there are any additional changes to your flight schedule. Regretting the inconvenience caused to you."""

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
        message = f"""*AirSathi – Flight Reminder*

Dear *{flight.passenger_name}*,

This is a reminder that your *flight {flight.flight_number}* with *PNR {flight.pnr}* is scheduled to depart in approximately {hours_until} hours.

Before leaving for the airport, please ensure that you have a valid identification document, your boarding pass, and that your baggage complies with airline regulations.
For any assistance related to your flight, reply to this message."""

        message_sid = self.twilio.send_message(phone, message)
        
        log = NotificationLog(
            notification_type=NotificationType.REMINDER,
            message_sid=message_sid or "failed",
            sent_at=datetime.now(),
            metadata={"hours_until": hours_until, "pnr": flight.pnr}
        )
        self.notification_history.append(log)
        return log
    
    def send_pre_flight_checklist(
        self,
        flight: Flight,
        phone: str,
        hours_until: int = 24
    ) -> NotificationLog:
        message = f"""*AirSathi – Pre-Flight Checklist*

Dear *{flight.passenger_name}*,

To help you prepare for your upcoming journey in advance, I have prepared an item checklist for your assistance, please review the checklist:

*1. Travel documents* - Valid government-issued photo identification and boarding pass with Visa (if applicable)

*2. Baggage and security* - For item allowance, please check the image attached

*3. Recommended Reporting time* - at least 2 hours before scheduled departure for domestic flights

Review this checklist beforehand to avoid last-minute issues at the airport."""

        # Multiple images for carousel
        image_urls = [
            "https://i.ibb.co/BVVC7Lv6/Gemini-Generated-Image-ku1g97ku1g97ku1g.png",
        ]
        
        message_sid = self.twilio.send_message(phone, message, media_urls=image_urls)

        log = NotificationLog(
            notification_type=NotificationType.PRE_FLIGHT_CHECKLIST,
            message_sid=message_sid or "failed",
            sent_at=datetime.now(),
            metadata={"hours_until": hours_until, "pnr": flight.pnr}
        )
        self.notification_history.append(log)
        return log
    
    def send_smart_arrival_assistance(
        self,
        flight: Flight,
        phone: str,
        buffer_hours: int = 2,
        link_map: str = "https://maps.app.goo.gl/Fpk1LuQzKJ5Gqu379"
    ) -> NotificationLog:
        message = f"""*AirSathi – Airport Arrival Guidance*

Dear *{flight.passenger_name}*,

To help you plan your journey to the airport with confidence, you can take help from here:

*1. Recommended arrival window* - approximately {buffer_hours} hours before the scheduled departure time

*2. Airport Directions* -  {link_map}

*3. From airport entry to check-in* - Proceed to the check-in counters for your airline and complete baggage drop, if required

*4. Security screening*
- Proceed to the security check area after check-in with printed or digital boarding pass and ID card
- Ensure that you comply with cabin baggage rules and remove items as instructed by security staff

*5. Before boarding* - Monitor airport displays for any gate or timing changes and keep your boarding pass accessible

By following this sequence, you can reduce last-minute delays and move smoothly from the airport entrance to your departure gate."""

        message_sid = self.twilio.send_message(phone, message)

        log = NotificationLog(
            notification_type=NotificationType.SMART_ARRIVAL_ASSISTANCE,
            message_sid=message_sid or "failed",
            sent_at=datetime.now(),
            metadata={"buffer_hours": buffer_hours, "pnr": flight.pnr}
        )
        self.notification_history.append(log)
        return log
    
    def send_boarding_call(
        self,
        flight: Flight,
        phone: str,
        boarding_in_minutes: int = 30
    ) -> NotificationLog:
        message = f"""*AirSathi – Boarding Update*

Dear *{flight.passenger_name}*,

Boarding for your flight is scheduled to begin shortly. Please review the details below:

*Flight:* {flight.flight_number}
*PNR:* {flight.pnr}
*Gate:* {flight.gate or 'TBA'}
*Terminal:* {flight.terminal}
*Scheduled Departure:* {self._format_datetime(flight.scheduled_departure + timedelta(minutes=45))}
*Estimated time until boarding starts:* approximately {boarding_in_minutes} minutes

Please proceed to the departure gate in good time and listen for any further instructions from airport or airline staff."""

        message_sid = self.twilio.send_message(phone, message)

        log = NotificationLog(
            notification_type=NotificationType.BOARDING_CALL,
            message_sid=message_sid or "failed",
            sent_at=datetime.now(),
            metadata={"boarding_in_minutes": boarding_in_minutes, "pnr": flight.pnr}
        )
        self.notification_history.append(log)
        return log
    
    def send_baggage_belt_update(
        self,
        flight: Flight,
        phone: str,
        belt_number: str
    ) -> NotificationLog:
        message = f"""*AirSathi – Baggage Claim Information*

Dear *{flight.passenger_name}*,

Baggage for your arriving flight is expected on the following belt:

*Flight:* {flight.flight_number}
*PNR:* {flight.pnr}
*Arrival Airport:* {flight.arrival_airport}
*Baggage Belt:* {belt_number}

Please follow the terminal signage to the indicated belt and keep your baggage tag available for verification if requested by airport staff."""

        message_sid = self.twilio.send_message(phone, message)

        log = NotificationLog(
            notification_type=NotificationType.BAGGAGE_BELT,
            message_sid=message_sid or "failed",
            sent_at=datetime.now(),
            metadata={"belt_number": belt_number, "pnr": flight.pnr}
        )
        self.notification_history.append(log)
        return log
    
    @staticmethod
    def _format_datetime(dt: datetime) -> str:
        return dt.strftime("%d %b %Y, %I:%M %p")
    
    def get_history(self):
        return self.notification_history