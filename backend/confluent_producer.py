"""
Confluent Kafka producer for Anchor events.
Produces events to Confluent Cloud topics.
"""

import json
import os
from confluent_kafka import Producer, KafkaError

class ConfluentProducer:
    def __init__(self):
        """Initialize Confluent producer."""
        self.config = {
            'bootstrap.servers': os.getenv('CONFLUENT_BOOTSTRAP_SERVERS'),
            'sasl.username': os.getenv('CONFLUENT_API_KEY'),
            'sasl.password': os.getenv('CONFLUENT_API_SECRET'),
            'security.protocol': os.getenv('CONFLUENT_SECURITY_PROTOCOL', 'SASL_SSL'),
            'sasl.mechanism': os.getenv('CONFLUENT_SASL_MECHANISM', 'PLAIN'),
        }
        
        try:
            self.producer = Producer(self.config)
            self.ready = True
            print("[Producer] Initialized and ready")
        except Exception as e:
            self.ready = False
            print(f"[Producer] Failed to initialize: {e}")
    
    def produce_event(self, topic, payload):
        """
        Produce an event to Confluent.
        
        Args:
            topic: Kafka topic name
            payload: Event payload (dict)
        """
        if not self.ready:
            print("[Producer] Producer not ready")
            return False
        
        try:
            message = json.dumps(payload).encode('utf-8')
            
            self.producer.produce(
                topic,
                value=message,
                callback=self._delivery_report
            )
            
            # Flush to ensure message is sent
            self.producer.flush(timeout=5)
            
            print(f"[Producer] ✓ Event produced to {topic}")
            return True
        
        except Exception as e:
            print(f"[Producer] Error producing event: {e}")
            return False
    
    def _delivery_report(self, err, msg):
        """Delivery callback."""
        if err is not None:
            print(f"[Producer] Message delivery failed: {err}")
        else:
            print(f"[Producer] Message delivered to {msg.topic()}")
