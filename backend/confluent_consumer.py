"""
Confluent Kafka consumer for Anchor events.
Consumes real-time events and updates the current reality state.
"""

import json
import os
from confluent_kafka import Consumer, KafkaError
from datetime import datetime
import threading

class ConfluentConsumer:
    def __init__(self, state_manager, event_store=None):
        """
        Initialize Confluent consumer.
        
        Args:
            state_manager: Reference to CurrentRealityState to update
            event_store: Optional event store for persistence
        """
        self.state_manager = state_manager
        self.event_store = event_store
        self.running = False
        self.consumer = None
        self.thread = None
        
        # Confluent configuration
        self.config = {
            'bootstrap.servers': os.getenv('CONFLUENT_BOOTSTRAP_SERVERS'),
            'sasl.username': os.getenv('CONFLUENT_API_KEY'),
            'sasl.password': os.getenv('CONFLUENT_API_SECRET'),
            'security.protocol': os.getenv('CONFLUENT_SECURITY_PROTOCOL', 'SASL_SSL'),
            'sasl.mechanism': os.getenv('CONFLUENT_SASL_MECHANISM', 'PLAIN'),
            'group.id': 'anchor-consumer-group',
            'auto.offset.reset': 'latest',
            'enable.auto.commit': True,
        }
    
    def start(self):
        """Start consuming events in background thread."""
        if self.running:
            return
        
        self.running = True
        self.consumer = Consumer(self.config)
        
        # Subscribe to all event topics
        topics = [
            'anchor-presence-events',
            'anchor-call-events',
            'anchor-time-events',
            'anchor-location-events'
        ]
        self.consumer.subscribe(topics)
        
        self.thread = threading.Thread(target=self._consume_loop, daemon=True)
        self.thread.start()
        print(f"[Confluent] Consumer started, listening to {topics}")
    
    def stop(self):
        """Stop consuming events."""
        self.running = False
        if self.consumer:
            self.consumer.close()
        if self.thread:
            self.thread.join(timeout=5)
        print("[Confluent] Consumer stopped")
    
    def _consume_loop(self):
        """Main consumption loop."""
        while self.running:
            try:
                msg = self.consumer.poll(timeout=1.0)
                
                if msg is None:
                    continue
                
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        print(f"[Confluent Error] {msg.error()}")
                        break
                
                # Process the message
                self._process_event(msg)
                
            except Exception as e:
                print(f"[Confluent Error] {e}")
    
    def _process_event(self, msg):
        """
        Process a single event and update state.
        
        Args:
            msg: Confluent message object
        """
        try:
            topic = msg.topic()
            payload = json.loads(msg.value().decode('utf-8'))
            timestamp = datetime.now().isoformat()
            
            # Store event if event store is available
            if self.event_store:
                self.event_store.store_event(topic, payload)
            
            print(f"[Event] {topic}: {payload}")
            
            if topic == 'anchor-presence-events':
                self._handle_presence(payload, timestamp)
            elif topic == 'anchor-call-events':
                self._handle_call(payload, timestamp)
            elif topic == 'anchor-time-events':
                self._handle_time(payload, timestamp)
            elif topic == 'anchor-location-events':
                self._handle_location(payload, timestamp)
        
        except json.JSONDecodeError:
            print(f"[Error] Failed to decode message: {msg.value()}")
        except Exception as e:
            print(f"[Error] Processing event: {e}")
    
    def _handle_presence(self, payload, timestamp):
        """Handle presence events (person enters/leaves)."""
        action = payload.get('action')  # 'enter' or 'leave'
        person = payload.get('person')
        
        if action == 'enter':
            self.state_manager.add_person(person, timestamp)
        elif action == 'leave':
            self.state_manager.remove_person(person, timestamp)
    
    def _handle_call(self, payload, timestamp):
        """Handle call events."""
        action = payload.get('action')  # 'started' or 'ended'
        caller = payload.get('caller')
        
        if action == 'started':
            self.state_manager.set_call_active(caller, timestamp)
        elif action == 'ended':
            self.state_manager.set_call_inactive(timestamp)
    
    def _handle_time(self, payload, timestamp):
        """Handle time-of-day events."""
        time_of_day = payload.get('time_of_day')  # 'morning', 'afternoon', 'evening', 'night'
        self.state_manager.set_time_of_day(time_of_day, timestamp)
    
    def _handle_location(self, payload, timestamp):
        """Handle location events."""
        location = payload.get('location')
        self.state_manager.set_location(location, timestamp)
