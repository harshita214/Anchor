# Anchor: Context Continuity Engine for Dementia Care

A real-time system that reconstructs and communicates a person's current reality through calm, repeatable voice explanations.

## Problem
People with early-to-mid stage dementia experience context collapse — sudden loss of understanding of where they are, who they're with, and what's happening. This causes anxiety, repeated questioning, and increased caregiver burden.

## Solution
Anchor consumes real-time events (Confluent), synthesizes context (Gemini), and delivers calm voice explanations (ElevenLabs).

## Quick Start

### Prerequisites
- Python 3.9+
- Confluent Cloud account (see `CONFLUENT_SETUP.md`)
- ElevenLabs API key
- Google Vertex AI credentials

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys and Confluent credentials

# Start backend
python app.py

# Start frontend (in another terminal)
cd frontend
python -m http.server 8000
```

Visit `http://localhost:8000` and click "I'm confused" to hear your current reality.

## Architecture

```
Event Sources (Confluent)
    ↓
Context Processor (Gemini)
    ↓
Current Reality State
    ↓
Voice Synthesis (ElevenLabs)
    ↓
Web UI
```

## Project Structure
```
/dec31
  /backend
    app.py                 # Flask backend
    confluent_consumer.py  # Kafka consumer
    context_processor.py   # Gemini integration
    voice_service.py       # ElevenLabs integration
  /frontend
    index.html
    styles.css
    app.js
  /scripts
    produce_test_events.py # Send test events to Confluent
  requirements.txt
  .env.example
```

## Demo Flow
1. Test events are produced to Confluent topics
2. Backend consumes events and updates context state
3. User clicks "I'm confused"
4. Gemini synthesizes current reality
5. ElevenLabs speaks the explanation
6. UI displays the text

## Next Steps
- Integrate real IoT event sources
- Add caregiver dashboard
- Deploy to Google Cloud Run
- Multilingual support
