
# AirSathi - WhatsApp Travel Concierge

## How to Run (Windows)

1. **Install Python 3.11**
2. Open PowerShell in the project folder.
3. Create and activate a virtual environment:
  ```powershell
  py -3.11 -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
4. Install dependencies:
  ```powershell
  py -3.11 -m pip install --upgrade pip
  py -3.11 -m pip install -r requirements.txt
  ```
5. Create a `.env` file with your Twilio and app config (see below).
6. Start the server:
  ```powershell
  py -3.11 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
  ```
7. (Optional) Expose with ngrok for Twilio:
  ```bash
  ngrok http 8000
  ```

## .env Example

```
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_NUMBER=+14155238886
APP_NAME=AirSaathi
APP_VERSION=1.0.0
DEBUG_MODE=True
PASSENGER_PHONE=+91XXXXXXXXXX
PASSENGER_NAME=Your Name
```

## WhatsApp Commands

- `status` — Get flight status
- `gate` — Get gate and terminal info
- `check in` — Get airline web check-in link
- `help` — List available commands

Send these from your WhatsApp (set in `PASSENGER_PHONE`) to your Twilio WhatsApp number.

## API Endpoints

- `GET /` — Health check
- `POST /webhook/whatsapp` — WhatsApp webhook
- `GET /api/flight-info` — Get mock flight info
- `POST /api/send-booking-confirmation`
- `POST /api/send-gate-change?new_gate=45C`
- `POST /api/send-delay?delay_minutes=30`
- `POST /api/send-reminder?hours=24`
- `POST /api/send-pre-flight-checklist?hours=24`
- `POST /api/send-smart-arrival-assistance?buffer_hours=2`
- `POST /api/send-boarding-call?boarding_in_minutes=30`
- `POST /api/send-baggage-belt-update?belt_number=5`

## HTTP Testing (PowerShell)

Example:
```powershell
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/flight-info" -UseBasicParsing
```

## Notes

- Requires Twilio WhatsApp API access and ngrok for webhook testing.
- Uses mock data in `flights.json`.
- For production, replace mock data and add a database.

### Prerequisites

- Python 3.11 (recommended)
- Twilio account with WhatsApp API access (sandbox or a WhatsApp‑enabled number)
- `ngrok` (or similar) to expose your local server to Twilio

### 1. Install dependencies (Windows, Python 3.11)

> **Important (Windows + this POC)**  
> Use `py -3.11` explicitly. Newer Python versions (for example 3.14) may try to compile `pydantic-core` from source and require a full Rust toolchain.

From the project folder in **PowerShell**:

```powershell
cd "c:\path\to\project"

# Create and activate a virtual environment with Python 3.11
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1

# Upgrade pip and install dependencies
py -3.11 -m pip install --upgrade pip
py -3.11 -m pip install -r requirements.txt
```

### 2. Configure environment variables

Create a `.env` file (if not already present) with at least:

```bash
# Twilio configuration
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_NUMBER=+14155238886  # Your Twilio WhatsApp sandbox/number

# Application configuration
APP_NAME=AirSaathi
APP_VERSION=1.0.0
DEBUG_MODE=True

# Test passenger
PASSENGER_PHONE=+91XXXXXXXXXX        # Your personal WhatsApp number
PASSENGER_NAME=Your Name
```

### 3. Run the FastAPI application

In **PowerShell**, from the project folder with the virtual environment activated:

```powershell
py -3.11 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

You should now be able to open:

- `http://127.0.0.1:8000/` → health check JSON

### 4. Expose the webhook with ngrok

In a **second** terminal:

```bash
ngrok http 8000
```

Copy the HTTPS URL from the **Forwarding** line, for example:

```text
https://your-subdomain.ngrok-free.dev -> http://localhost:8000
```

### 5. Configure Twilio WhatsApp webhook

In the Twilio Console (WhatsApp sandbox or WhatsApp‑enabled number), set **Incoming Messages**:

- **URL**: `https://your-subdomain.ngrok-free.dev/webhook/whatsapp`
- **Method**: `POST`

Save the settings.

## 📱 Usage – What to Test

With `uvicorn` and `ngrok` running and Twilio pointed at `/webhook/whatsapp`, send WhatsApp messages **from the number in `PASSENGER_PHONE`** to your Twilio WhatsApp number.

The POC currently understands a small set of keyword‑based intents:

- **Flight status**
  - Send: `status`
  - Reply: basic status of the mock flight (number, PNR, scheduled departure).

- **Gate & terminal**
  - Send: `gate`
  - Reply: gate and terminal for the mock flight.

- **Web check‑in link**
  - Send: `check in`
  - Reply: airline web check‑in URL (based on `airline_code` and `AIRLINE_CHECKIN_URLS`).

- **Help/menu**
  - Send: `help`
  - Reply: list of available commands and what they do.

- **Unknown message**
  - Send any other free‑text query.
  - Reply: fallback message explaining supported commands.

### Windows HTTP testing (PowerShell)

On Windows, use `Invoke-WebRequest` instead of `curl -X ...` when calling the HTTP APIs locally.

Examples (with the app running on `http://127.0.0.1:8000`):

```powershell
# Health check
Invoke-WebRequest -Uri "http://127.0.0.1:8000/" -UseBasicParsing

# Current mock flight info
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/flight-info" -UseBasicParsing

# Booking confirmation
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/send-booking-confirmation" -Method POST -UseBasicParsing

# Gate change
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/send-gate-change?new_gate=45C" -Method POST -UseBasicParsing

# Delay notification
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/send-delay?delay_minutes=45" -Method POST -UseBasicParsing

# Pre-flight checklist
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/send-pre-flight-checklist?hours=24" -Method POST -UseBasicParsing

# Smart arrival assistance
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/send-smart-arrival-assistance?buffer_hours=2" -Method POST -UseBasicParsing

# Boarding call
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/send-boarding-call?boarding_in_minutes=30" -Method POST -UseBasicParsing

# Baggage belt update
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/send-baggage-belt-update?belt_number=5" -Method POST -UseBasicParsing
```

These examples reflect the main deviations from typical Unix-style docs: explicit `py -3.11` usage, PowerShell commands, and `Invoke-WebRequest` instead of `curl`.

## 📊 API Endpoints (Current POC)

### Health Check

```text
GET /
```

Returns basic app metadata.

### WhatsApp Webhook

```text
POST /webhook/whatsapp
```

Called by Twilio for every inbound WhatsApp message. Parses the text and sends an appropriate WhatsApp reply.

### Notification Triggers (using mock flight data)

These endpoints send WhatsApp messages to `PASSENGER_PHONE` using the single mock flight defined in `main.py`:

```text
POST /api/send-booking-confirmation
POST /api/send-gate-change?new_gate=45C
POST /api/send-delay?delay_minutes=30
POST /api/send-reminder?hours=24
POST /api/send-pre-flight-checklist?hours=24
POST /api/send-smart-arrival-assistance?buffer_hours=2
POST /api/send-boarding-call?boarding_in_minutes=30
POST /api/send-baggage-belt-update?belt_number=5
```

### Flight Information

```text
GET /api/flight-info
```

Returns the current mock flight’s basic details (PNR, flight number, route, departure, gate, terminal).

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
