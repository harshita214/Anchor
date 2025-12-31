# Anchor: Context Continuity Engine for Dementia Care

Grounding people with dementia in the present moment through real-time context synthesis and calm voice explanations.

## The Problem
People with early-to-mid stage dementia experience sudden context collapse — losing track of where they are, who's with them, and what's happening. This triggers anxiety, repeated questioning, and exhaustion for caregivers.

## The Solution
Anchor is a real-time system that:
- **Captures** events from the environment (who's present, location, time, calls)
- **Synthesizes** context using AI (Google Gemini)
- **Communicates** calmly through voice (ElevenLabs) and text
- **Stores** memories permanently (Confluent Cloud + SQLite)

When someone feels confused, they click "Get Grounding" and hear a clear, compassionate explanation of their current reality.

## Features
- **User Dashboard**: One-page interface with "What's Happening?" grounding, location tracking, people registry, and memory recall
- **Caregiver Dashboard**: Add memories, manage people, update location, view recent memories
- **Event History**: Real-time event log from Confluent Cloud
- **Accessibility First**: Large text, high contrast, keyboard navigation, screen reader support
- **Permanent Memory**: All memories stored in Confluent with infinite retention

## Quick Start

### Prerequisites
- Python 3.9+
- Confluent Cloud account (see `CONFLUENT_SETUP.md`)
- Google Vertex AI credentials (optional, has fallback)
- ElevenLabs API key (optional, has fallback)

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Confluent credentials and API keys

# Start backend (port 5001)
python -c "import sys; sys.path.insert(0, 'backend'); from app import app; app.run(debug=True, port=5001, host='0.0.0.0')"

# Start frontend (port 8001, in another terminal)
cd frontend
python -m http.server 8001
```

Visit `http://localhost:8001` to access the system.

## Architecture

```
Real-World Events (IoT, sensors, manual input)
    ↓
Confluent Cloud (Kafka topics)
    ↓
Backend Consumer (Flask)
    ↓
State Manager (current reality)
    ↓
Context Processor (Gemini AI)
    ↓
Voice Synthesis (ElevenLabs)
    ↓
Web UI (User & Caregiver Dashboards)
```

## Project Structure
```
/Anchor
  /backend
    app.py                    # Flask API
    state_manager.py          # Current reality state
    confluent_producer.py     # Produces events to Kafka
    confluent_consumer.py     # Consumes events from Kafka
    context_processor.py      # Gemini integration
    voice_service.py          # ElevenLabs integration
    event_store.py            # SQLite event storage
  /frontend
    index.html                # Main dashboard
    user-dashboard.html       # User interface
    caregiver-dashboard.html  # Caregiver interface
    history.html              # Event history viewer
    styles.css                # Shared styles
  .env                        # Configuration (Confluent, API keys)
  requirements.txt            # Python dependencies
  QUICKSTART.md               # Getting started guide
  CONFLUENT_SETUP.md          # Confluent Cloud setup
```

## How It Works

### For Users
1. Open the User Dashboard
2. Click "Get Grounding" to hear what's happening
3. Update your location or confirm who's with you
4. Browse your memories for comfort

### For Caregivers
1. Open the Caregiver Dashboard
2. Add memories (family stories, important dates)
3. Add people (family members, friends)
4. Update location when the person moves
5. View recent memories and event history

### Behind the Scenes
- Events flow to Confluent Cloud (presence, calls, location, time)
- Backend synthesizes context: "You're at home with Anna. It's afternoon."
- Voice is generated and played
- All data is stored permanently for replay and continuity

## Event Types
- **Presence Events**: Who enters/leaves
- **Call Events**: Incoming/outgoing calls
- **Location Events**: Where the person is
- **Time Events**: Time of day (morning, afternoon, evening, night)
- **Memory Events**: Stored memories for recall

## Accessibility
- Large, readable text (2.5rem headings, 1.1-1.3rem body)
- High contrast (21:1 WCAG AAA compliant)
- Full keyboard navigation
- Screen reader support (ARIA labels, live regions)
- Reduced motion support
- Calm, non-overwhelming design

## Next Steps
- Integrate real IoT sensors (location tracking, presence detection)
- Mobile app for on-the-go access
- Multi-language support
- Deploy to Google Cloud Run
- Caregiver notifications and alerts

## Documentation
- `QUICKSTART.md` — How to run the system
- `CONFLUENT_SETUP.md` — Setting up Confluent Cloud
