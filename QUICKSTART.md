# Anchor Quick Start Guide

## 1. Prerequisites

- Python 3.9+
- Confluent Cloud account (free tier works)
- ElevenLabs API key (free tier available)
- Google Cloud project with Vertex AI enabled (optional, fallback works)

## 2. Confluent Cloud Setup (5 minutes)

### Create Cluster
1. Go to https://confluent.cloud
2. Sign up or log in
3. Create a new cluster (Basic tier, any region)
4. Wait for cluster to be ready

### Create API Keys
1. In your cluster, go to **API Keys** (left sidebar)
2. Click **Create key**
3. Choose **Granular access** → **Service account**
4. Create a new service account (e.g., "anchor-app")
5. Grant permissions:
   - Topic management
   - Produce
   - Consume
6. Copy the **Key** and **Secret** (save these!)

### Create Topics
1. Go to **Topics** in your cluster
2. Click **Create topic** and create these 4 topics:
   - `anchor-presence-events`
   - `anchor-call-events`
   - `anchor-time-events`
   - `anchor-location-events`

Each topic: 1 partition, 1 day retention (default is fine)

## 3. Local Setup (5 minutes)

### Clone and Install
```bash
cd dec31

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configure Environment
```bash
# Copy example env file
cp .env.example .env

# Edit .env with your credentials
nano .env
```

Fill in:
```
CONFLUENT_BOOTSTRAP_SERVERS=pkc-xxx.region.provider.confluent.cloud:9092
CONFLUENT_API_KEY=your_key_here
CONFLUENT_API_SECRET=your_secret_here
ELEVENLABS_API_KEY=your_elevenlabs_key_here
GOOGLE_PROJECT_ID=your_project_id  # Optional
```

## 4. Run Anchor (3 terminals)

### Terminal 1: Backend
```bash
cd dec31/backend
python app.py
```
You should see:
```
╔════════════════════════════════════════════════════════════╗
║  Anchor: Context Continuity Engine for Dementia Care      ║
║  Backend running on http://localhost:5000                 ║
╚════════════════════════════════════════════════════════════╝
```

### Terminal 2: Frontend
```bash
cd dec31/frontend
python -m http.server 8000
```
Visit: http://localhost:8000

### Terminal 3: Send Test Events
```bash
cd dec31/scripts
python produce_test_events.py
```

This sends a realistic scenario:
- Morning time
- Home location
- Daughter Anna enters
- Son Michael calls
- Call ends
- Anna leaves

## 5. Test the Flow

1. **Open frontend**: http://localhost:8000
2. **Watch state update** as events arrive (you'll see Anna, Michael, etc.)
3. **Click "I'm Confused"** button
4. **Hear explanation** via ElevenLabs voice
5. **See text** of what's happening

## 6. Manual Testing (Optional)

In browser console, you can manually trigger events:

```javascript
// Add a person
testAnchor.sendPresenceEvent('enter', 'John (brother)');

// Start a call
testAnchor.sendCallEvent('started', 'Doctor');

// Change location
testAnchor.sendLocationEvent('hospital');

// Change time
testAnchor.sendTimeEvent('afternoon');

// End call
testAnchor.sendCallEvent('ended');

// Reset everything
testAnchor.resetState();
```

## 7. Troubleshooting

### Backend won't connect to Confluent
- Check `.env` file has correct credentials
- Verify Confluent cluster is running
- Check firewall/VPN isn't blocking connection

### No audio playing
- Check ElevenLabs API key is valid
- Check browser allows audio playback
- Check browser console for errors

### State not updating
- Verify test events are being sent
- Check Confluent topics exist
- Check backend logs for errors

### Gemini not working
- Optional - fallback text synthesis works fine
- If you want it: set `GOOGLE_PROJECT_ID` and authenticate with `gcloud auth application-default login`

## 8. Next Steps

### For Demo
- Run the test scenario
- Record a 3-minute video showing:
  1. Events being sent
  2. State updating in UI
  3. Clicking "I'm confused"
  4. Hearing explanation

### For Production
- Deploy backend to Google Cloud Run
- Deploy frontend to Cloud Storage + CDN
- Set up real event sources (IoT, calendar, etc.)
- Add caregiver dashboard
- Implement user authentication

## 9. Architecture Reminder

```
Real-world Events
    ↓
Confluent Cloud (Kafka)
    ↓
Backend Consumer (Python)
    ↓
Current Reality State
    ↓
Gemini (Context Synthesis)
    ↓
ElevenLabs (Voice)
    ↓
Web UI (User hears explanation)
```

## 10. Key Files

- `backend/app.py` - Flask API
- `backend/confluent_consumer.py` - Kafka consumer
- `backend/context_processor.py` - Gemini integration
- `backend/voice_service.py` - ElevenLabs integration
- `frontend/index.html` - UI
- `frontend/app.js` - Frontend logic
- `scripts/produce_test_events.py` - Test event producer

---

**Questions?** Check the main README.md or CONFLUENT_SETUP.md for more details.
