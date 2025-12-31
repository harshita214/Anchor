"""
Test event producer for Anchor.
Sends simulated real-world events to Confluent topics.
"""

import json
import os
import time
import sys
from confluent_kafka import Producer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TestEventProducer:
    def __init__(self):
        """Initialize Confluent producer."""
        self.config = {
            'bootstrap.servers': os.getenv('CONFLUENT_BOOTSTRAP_SERVERS'),
            'sasl.username': os.getenv('CONFLUENT_API_KEY'),
            'sasl.password': os.getenv('CONFLUENT_API_SECRET'),
            'security.protocol': os.getenv('CONFLUENT_SECURITY_PROTOCOL', 'SASL_SSL'),
            'sasl.mechanism': os.getenv('CONFLUENT_SASL_MECHANISM', 'PLAIN'),
        }
        
        self.producer = Producer(self.config)
        print("[Producer] Initialized")
    
    def delivery_report(self, err, msg):
        """Delivery callback."""
        if err is not None:
            print(f"[Error] Message delivery failed: {err}")
        else:
            print(f"[Sent] {msg.topic()}: {msg.value().decode('utf-8')}")
    
    def send_event(self, topic, event):
        """Send an event to a topic."""
        try:
            self.producer.produce(
                topic,
                value=json.dumps(event).encode('utf-8'),
                callback=self.delivery_report
            )
            self.producer.flush()
        except Exception as e:
            print(f"[Error] {e}")
    
    def run_scenario(self):
        """Run a realistic scenario."""
        print("\n" + "="*60)
        print("Anchor Test Scenario: Morning at Home")
        print("="*60 + "\n")
        
        # Scenario: Tuesday morning, person wakes up at home
        
        print("1. Setting time to morning...")
        self.send_event('anchor-time-events', {
            'time_of_day': 'morning',
            'timestamp': int(time.time())
        })
        time.sleep(1)
        
        print("\n2. Setting location to home...")
        self.send_event('anchor-location-events', {
            'location': 'home',
            'timestamp': int(time.time())
        })
        time.sleep(1)
        
        print("\n3. Daughter Anna enters the room...")
        self.send_event('anchor-presence-events', {
            'action': 'enter',
            'person': 'Anna (daughter)',
            'timestamp': int(time.time())
        })
        time.sleep(2)
        
        print("\n4. Phone call from son Michael...")
        self.send_event('anchor-call-events', {
            'action': 'started',
            'caller': 'Michael (son)',
            'timestamp': int(time.time())
        })
        time.sleep(3)
        
        print("\n5. Call ends...")
        self.send_event('anchor-call-events', {
            'action': 'ended',
            'timestamp': int(time.time())
        })
        time.sleep(1)
        
        print("\n6. Anna leaves the room...")
        self.send_event('anchor-presence-events', {
            'action': 'leave',
            'person': 'Anna (daughter)',
            'timestamp': int(time.time())
        })
        time.sleep(1)
        
        print("\n" + "="*60)
        print("Scenario complete!")
        print("="*60)
        print("\nNow visit http://localhost:8000 and click 'I'm confused'")
        print("You should hear the current reality explained.\n")

if __name__ == '__main__':
    try:
        producer = TestEventProducer()
        producer.run_scenario()
    except KeyboardInterrupt:
        print("\n[Producer] Stopped")
        sys.exit(0)
    except Exception as e:
        print(f"[Error] {e}")
        sys.exit(1)
