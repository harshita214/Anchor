"""
Anchor Backend - Flask API
Real-time context continuity engine for dementia care.
"""

import os
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime

from state_manager import CurrentRealityState
from confluent_consumer import ConfluentConsumer
from confluent_producer import ConfluentProducer
from context_processor import ContextProcessor
from voice_service import VoiceService
from event_store import EventStore

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize services
state = CurrentRealityState()
event_store = EventStore()
context_processor = ContextProcessor()
voice_service = VoiceService()
confluent_consumer = ConfluentConsumer(state, event_store)
confluent_producer = ConfluentProducer()

# Start Confluent consumer on app startup
@app.before_request
def startup():
    """Start consumer on first request."""
    if not hasattr(app, 'consumer_started'):
        # Disable consumer for now due to threading issues on macOS
        # In production, use a separate consumer process
        print("[Confluent] Consumer disabled (use separate process in production)")
        app.consumer_started = True

# ============================================================================
# API Endpoints
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'timestamp': state.last_updated
    })

@app.route('/api/state', methods=['GET'])
def get_state():
    """Get current reality state."""
    return jsonify(state.to_dict())

@app.route('/api/explain', methods=['POST'])
def explain():
    """
    Generate and synthesize current reality explanation.
    
    POST /api/explain
    Returns: {
        'success': bool,
        'explanation': str,
        'audio_base64': str (optional),
        'state': dict
    }
    """
    try:
        # Synthesize explanation from current state
        explanation = context_processor.synthesize_reality(state)
        
        # Synthesize voice
        voice_result = voice_service.synthesize(explanation)
        
        response = {
            'success': True,
            'explanation': explanation,
            'state': state.to_dict()
        }
        
        if voice_result.get('success'):
            response['audio_base64'] = voice_result['audio_base64']
        else:
            response['voice_error'] = voice_result.get('error')
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/events/presence', methods=['POST'])
def event_presence():
    """
    Manually trigger a presence event (for testing).
    
    POST /api/events/presence
    Body: {
        'action': 'enter' | 'leave',
        'person': 'name'
    }
    """
    try:
        data = request.json
        action = data.get('action')
        person = data.get('person')
        
        if action == 'enter':
            state.add_person(person)
        elif action == 'leave':
            state.remove_person(person)
        
        return jsonify({
            'success': True,
            'state': state.to_dict()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/events/call', methods=['POST'])
def event_call():
    """
    Manually trigger a call event (for testing).
    
    POST /api/events/call
    Body: {
        'action': 'started' | 'ended',
        'caller': 'name' (required if action is 'started')
    }
    """
    try:
        data = request.json
        action = data.get('action')
        
        if action == 'started':
            caller = data.get('caller')
            state.set_call_active(caller)
        elif action == 'ended':
            state.set_call_inactive()
        
        return jsonify({
            'success': True,
            'state': state.to_dict()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/events/location', methods=['POST'])
def event_location():
    """
    Manually trigger a location event (for testing).
    
    POST /api/events/location
    Body: {
        'location': 'home' | 'hospital' | 'park' | etc
    }
    """
    try:
        data = request.json
        location = data.get('location')
        state.set_location(location)
        
        return jsonify({
            'success': True,
            'state': state.to_dict()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/events/time', methods=['POST'])
def event_time():
    """
    Manually trigger a time event (for testing).
    
    POST /api/events/time
    Body: {
        'time_of_day': 'morning' | 'afternoon' | 'evening' | 'night'
    }
    """
    try:
        data = request.json
        time_of_day = data.get('time_of_day')
        state.set_time_of_day(time_of_day)
        
        return jsonify({
            'success': True,
            'state': state.to_dict()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/reset', methods=['POST'])
def reset_state():
    """Reset state to defaults (for testing)."""
    state.reset()
    return jsonify({
        'success': True,
        'state': state.to_dict()
    })

@app.route('/api/history', methods=['GET'])
def get_history():
    """
    Get event history from Confluent.
    
    Query params:
    - topic: Filter by topic (optional)
    - limit: Max events to return (default 100)
    """
    try:
        topic = request.args.get('topic')
        limit = int(request.args.get('limit', 100))
        
        events = event_store.get_events(topic=topic, limit=limit)
        
        return jsonify({
            'success': True,
            'events': events,
            'count': len(events)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get event statistics."""
    try:
        stats = event_store.get_event_stats()
        
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/events/create', methods=['POST'])
def create_event():
    """
    Manually create an event (for dashboard).
    This simulates Confluent events for demo purposes.
    
    POST /api/events/create
    Body: {
        'topic': 'anchor-presence-events',
        'payload': { ... }
    }
    """
    try:
        data = request.json
        topic = data.get('topic')
        payload = data.get('payload')
        
        if not topic or not payload:
            return jsonify({
                'success': False,
                'error': 'Missing topic or payload'
            }), 400
        
        # Produce to Confluent Cloud
        confluent_producer.produce_event(topic, payload)
        
        # Store the event locally
        event_store.store_event(topic, payload)
        
        # Also update state if it's a state-changing event
        if topic == 'anchor-presence-events':
            action = payload.get('action')
            person = payload.get('person')
            if action == 'enter':
                state.add_person(person)
            elif action == 'leave':
                state.remove_person(person)
        elif topic == 'anchor-call-events':
            action = payload.get('action')
            if action == 'started':
                state.set_call_active(payload.get('caller'))
            elif action == 'ended':
                state.set_call_inactive()
        elif topic == 'anchor-location-events':
            state.set_location(payload.get('location'))
        elif topic == 'anchor-time-events':
            state.set_time_of_day(payload.get('time_of_day'))
        
        return jsonify({
            'success': True,
            'state': state.to_dict()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/memories/add', methods=['POST'])
def add_memory():
    """
    Add a memory (stored in Confluent and SQLite).
    
    POST /api/memories/add
    Body: {
        'user_id': 'dementia-user-1',
        'title': 'Our Wedding Day',
        'content': 'We got married on June 15th, 1985...',
        'category': 'family'
    }
    """
    try:
        data = request.json
        user_id = data.get('user_id')
        title = data.get('title')
        content = data.get('content')
        category = data.get('category', 'general')
        
        print(f"[Memory] Received: user_id={user_id}, title={title}, category={category}")
        
        if not user_id or not title or not content:
            print(f"[Memory] Missing fields: user_id={user_id}, title={title}, content={content}")
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400
        
        # Create memory event
        memory_event = {
            'user_id': user_id,
            'title': title,
            'content': content,
            'category': category,
            'timestamp': datetime.now().isoformat()
        }
        
        # Produce to Confluent (permanent storage)
        print(f"[Memory] Producing to Confluent...")
        confluent_producer.produce_event('anchor-memories', memory_event)
        
        # Also store locally
        print(f"[Memory] Storing locally...")
        event_store.store_event('anchor-memories', memory_event)
        
        print(f"[Memory] ✓ Memory saved successfully")
        
        return jsonify({
            'success': True,
            'memory': memory_event
        })
    
    except Exception as e:
        print(f"[Memory] Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/memories/get', methods=['GET'])
def get_memories():
    """
    Get all memories for a user.
    
    GET /api/memories/get?user_id=dementia-user-1
    """
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'Missing user_id'
            }), 400
        
        # Get memories from event store
        memories = event_store.get_events(topic='anchor-memories', limit=100)
        
        # Filter by user_id
        user_memories = [
            m for m in memories 
            if m.get('payload', {}).get('user_id') == user_id
        ]
        
        return jsonify({
            'success': True,
            'memories': user_memories
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Server error'}), 500

# ============================================================================
# Shutdown
# ============================================================================

@app.teardown_appcontext
def shutdown(exception=None):
    """Clean up on shutdown."""
    # Consumer disabled for now
    pass

if __name__ == '__main__':
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║  Anchor: Context Continuity Engine for Dementia Care      ║
    ║  Backend running on http://localhost:5000                 ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    app.run(debug=True, port=5000, host='0.0.0.0')
