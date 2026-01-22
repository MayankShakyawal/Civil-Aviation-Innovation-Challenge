"""
Configuration for AirSathi POC.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration."""
    
    # Twilio
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
    
    # Application
    APP_NAME = os.getenv("APP_NAME", "AirSathi")
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
    DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"
    
    # Webhook
    WEBHOOK_BASE_URL = os.getenv("WEBHOOK_BASE_URL", "https://your-domain.com")
    
    # Mock Data
    MOCK_DATA_PATH = os.getenv("MOCK_DATA_PATH", "mock_data.json")
    
    # Notification Settings
    REMINDER_HOURS_BEFORE_FLIGHT = int(os.getenv("REMINDER_HOURS_BEFORE_FLIGHT", "24"))
    GATE_CHANGE_IMMEDIATE = os.getenv("GATE_CHANGE_IMMEDIATE", "True").lower() == "true"
    DELAY_THRESHOLD_MINUTES = int(os.getenv("DELAY_THRESHOLD_MINUTES", "15"))
    
    # Test Passenger
    PASSENGER_PHONE = os.getenv("PASSENGER_PHONE", "+919876543210")
    PASSENGER_NAME = os.getenv("PASSENGER_NAME", "Rajesh Kumar")


# Airline web check-in URLs
AIRLINE_CHECKIN_URLS = {
    "6E": "https://www.goindigo.in/web-check-in.html",
    "AI": "https://www.airindia.com/in/en/manage/web-check-in.html",
    "SG": "https://www.spicejet.com/check-in.aspx",
    "UK": "https://www.airvistara.com/in/en/travel-information/web-check-in",
}

# Airport names
AIRPORT_NAMES = {
    "DEL": "Indira Gandhi International Airport, Delhi",
    "BOM": "Chhatrapati Shivaji Maharaj International Airport, Mumbai",
    "BLR": "Kempegowda International Airport, Bangalore",
    "MAA": "Chennai International Airport",
    "HYD": "Rajiv Gandhi International Airport, Hyderabad",
}