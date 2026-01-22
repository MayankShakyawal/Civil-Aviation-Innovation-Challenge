# AirSathi - WhatsApp AI Travel Concierge 🛫

**AirSathi** is a WhatsApp-based AI travel concierge designed specifically for Indian airports. It provides automated flight notifications, real-time updates, and interactive FAQ support to enhance the passenger experience.

## 🏗️ Project Structure

```
airsathi/
│
├── main.py                          # FastAPI entry point and webhook handler
├── config.py                        # Configuration and environment management
├── requirements.txt                 # Python dependencies
├── mock_data.json                   # Sample flight data (AODB/FIDS simulation)
├── .env.example                     # Environment variables template
├── .env                            # Environment variables (create from .env.example)
│
├── models/
│   └── __init__.py                 # Data models (User, Flight, Notification)
│
├── services/
│   ├── twilio_service.py           # Twilio WhatsApp API integration
│   ├── flight_service.py           # Flight data management and PNR operations
│   └── notification_service.py     # Notification creation and delivery
│
└── utils/
    └── template_manager.py         # Message templates (multilingual ready)
```

## ✨ Core Features (Phase 1)

### 1. **Automated Initial Outreach**
- Immediate WhatsApp message upon booking confirmation
- Includes passenger name, PNR, flight details, gate, terminal
- Airline-specific web check-in links
- Travel tips and helpful reminders

### 2. **Real-time Notification System**
- **Gate Changes**: Instant alerts with new gate information
- **Flight Delays**: Updates with revised departure/arrival times
- **Flight Reminders**: Scheduled alerts 24 hours before departure
- **Boarding Alerts**: Notifications when boarding commences

### 3. **Interactive FAQ System**
- WhatsApp list picker menu (7 categories)
- Baggage rules and regulations
- Wheelchair assistance requests
- Terminal information
- Flight status queries
- Check-in help
- Lounge access information
- Contact support

### 4. **PNR-based Flight Status**
- Quick status lookup by sending PNR
- Real-time flight information
- Gate and terminal details
- Delay notifications

## 🚀 Getting Started

### Prerequisites
- Python 3.10 or higher
- Twilio account with WhatsApp API access
- Valid Twilio phone number enabled for WhatsApp

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/airsathi.git
cd airsathi
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your Twilio credentials
```

5. **Set up Twilio WhatsApp Sandbox** (for testing)
- Go to Twilio Console → Messaging → Try it out → Send a WhatsApp message
- Follow instructions to connect your WhatsApp number to the sandbox
- Note your sandbox number (e.g., +14155238886)

### Configuration

Edit `.env` file with your credentials:

```bash
# Twilio Configuration
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_NUMBER=+14155238886  # Your Twilio WhatsApp number

# Application Configuration
DEBUG_MODE=True  # Set to False in production
WEBHOOK_BASE_URL=https://your-ngrok-url.ngrok.io  # For local testing
```

### Running the Application

1. **Start the FastAPI server**
```bash
python main.py
```

The server will start at `http://localhost:8000`

2. **Expose webhook with ngrok** (for local testing)
```bash
ngrok http 8000
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

3. **Configure Twilio webhook**
- Go to Twilio Console → Messaging → Settings → WhatsApp Sandbox Settings
- Set "When a message comes in" to: `https://your-ngrok-url.ngrok.io/webhook/whatsapp`
- Method: POST
- Save

## 📱 Usage Examples

### Testing Initial Booking Notification

**API Request:**
```bash
curl -X POST "http://localhost:8000/api/trigger-booking-notification" \
  -H "Content-Type: application/json" \
  -d '{
    "pnr": "ABC123",
    "phone_number": "+919876543210",
    "passenger_name": "Rajesh Kumar",
    "language": "en"
  }'
```

### Testing Gate Change Notification

**API Request:**
```bash
curl -X POST "http://localhost:8000/api/simulate-gate-change" \
  -H "Content-Type: application/json" \
  -d '{
    "pnr": "ABC123",
    "new_gate": "45C",
    "phone_number": "+919876543210",
    "passenger_name": "Rajesh Kumar"
  }'
```

### Testing Flight Delay Notification

**API Request:**
```bash
curl -X POST "http://localhost:8000/api/simulate-delay" \
  -H "Content-Type: application/json" \
  -d '{
    "pnr": "ABC123",
    "delay_minutes": 45,
    "phone_number": "+919876543210",
    "passenger_name": "Rajesh Kumar"
  }'
```

### WhatsApp User Interactions

**Check Flight Status:**
- Send PNR: `ABC123`
- Receive: Detailed flight status

**Access FAQ:**
- Send: `HELP` or `MENU` or `FAQ`
- Receive: Interactive menu with 7 options
- Reply with number (1-7) to get specific information

**Quick Commands:**
- `HELP` - Show FAQ menu
- `STATUS` - Flight status reminder
- `[PNR]` - Check specific flight (e.g., ABC123)

## 🧪 Testing with Mock Data

The application includes `mock_data.json` with 5 sample flights for testing:

| PNR    | Flight   | Route       | Status    | Passenger     |
|--------|----------|-------------|-----------|---------------|
| ABC123 | 6E-2345  | DEL → BLR   | Scheduled | Rajesh Kumar  |
| DEF456 | AI-860   | BOM → MAA   | Delayed   | Priya Sharma  |
| GHI789 | UK-852   | HYD → DEL   | Scheduled | Amit Patel    |
| JKL012 | SG-134   | CCU → AMD   | Scheduled | Sneha Reddy   |
| MNO345 | 6E-5421  | BLR → COK   | Arrived   | Vikram Singh  |

You can modify `mock_data.json` to add more test flights.

## 🏛️ Architecture & Design Principles

### SOLID Principles Implementation

1. **Single Responsibility Principle**
   - Each service handles one specific domain (Twilio, Flights, Notifications)
   - Template management separated from business logic

2. **Open/Closed Principle**
   - Notification types are extensible via enum
   - Template manager supports new languages without modifying core code

3. **Liskov Substitution Principle**
   - Models use Pydantic for type safety
   - Services can be mocked for testing

4. **Interface Segregation Principle**
   - Services expose minimal, focused interfaces
   - No unnecessary dependencies between modules

5. **Dependency Inversion Principle**
   - Services depend on abstractions (Pydantic models)
   - Configuration injected via settings

### Key Design Decisions

**Multilingual Support**
- `template_manager.py` designed with language parameter
- Currently supports English, structured for Hindi/Telugu expansion
- Simple addition of new language dictionaries

**Extensibility**
- New notification types: Add to `NotificationType` enum + template
- New services: Follow existing service pattern
- New data sources: Replace `FlightService._load_mock_data()`

**Error Handling**
- All Twilio operations wrapped in try-catch
- Failed notifications logged with error messages
- Graceful degradation for missing data

## 📊 API Endpoints

### Health Check
```
GET /
```

### WhatsApp Webhook
```
POST /webhook/whatsapp
```
Receives incoming messages from Twilio

### Trigger Booking Notification
```
POST /api/trigger-booking-notification
Body: {pnr, phone_number, passenger_name, language}
```

### Simulate Gate Change
```
POST /api/simulate-gate-change
Body: {pnr, new_gate, phone_number, passenger_name}
```

### Simulate Flight Delay
```
POST /api/simulate-delay
Body: {pnr, delay_minutes, phone_number, passenger_name}
```

## 🔮 Future Enhancements (Planned)

### Phase 2 Features
- [ ] Real-time AODB/FIDS integration
- [ ] Hindi and Telugu language support
- [ ] Real-time congestion forecasting
- [ ] Personalized recommendations (dining, shopping)
- [ ] Multi-user support with database
- [ ] Scheduled reminder system with APScheduler
- [ ] Analytics dashboard

### Advanced Features
- [ ] Natural Language Understanding (NLU) for free-text queries
- [ ] Integration with airport Wi-Fi systems
- [ ] Baggage tracking
- [ ] Lounge booking
- [ ] Taxi/ride-sharing integration

## 🤝 Contributing

This is a feasibility prototype. For production deployment:

1. Replace mock data with real AODB/FIDS API
2. Add database for user and notification persistence
3. Implement proper authentication
4. Add monitoring and logging (Sentry, CloudWatch)
5. Deploy with production WSGI server (Gunicorn)
6. Set up CI/CD pipeline

## 📄 License

This project is developed as a proof-of-concept for Indian airport passenger experience enhancement.

## 👥 Support

For questions or issues:
- Create an issue in the repository
- Contact the development team

## 🎯 Key Metrics (Target - Phase 1)

- **Helpdesk Load Reduction**: 30-50% for routine queries
- **Response Time**: < 2 seconds for notifications
- **User Satisfaction**: Measured via post-flight surveys
- **FAQ Resolution Rate**: 70%+ without human intervention

---

**Built with ❤️ for Indian Aviation** ✈️🇮🇳