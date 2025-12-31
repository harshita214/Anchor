"""
Event store for persisting Confluent events.
Demonstrates how Confluent retains data and enables replay.
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict

class EventStore:
    def __init__(self, db_path='anchor_events.db'):
        """Initialize event store."""
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                event_type TEXT,
                payload TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                received_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_topic ON events(topic)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp ON events(timestamp)
        ''')
        
        conn.commit()
        conn.close()
        print("[EventStore] Database initialized")
    
    def store_event(self, topic: str, payload: Dict):
        """
        Store an event from Confluent.
        
        Args:
            topic: Kafka topic name
            payload: Event payload (dict)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            event_type = payload.get('action') or payload.get('time_of_day') or payload.get('location')
            payload_json = json.dumps(payload)
            
            cursor.execute('''
                INSERT INTO events (topic, event_type, payload)
                VALUES (?, ?, ?)
            ''', (topic, event_type, payload_json))
            
            conn.commit()
            conn.close()
            
            print(f"[EventStore] Stored event: {topic} - {event_type}")
        except Exception as e:
            print(f"[EventStore] Error storing event: {e}")
    
    def get_events(self, topic: str = None, limit: int = 100) -> List[Dict]:
        """
        Retrieve stored events.
        
        Args:
            topic: Filter by topic (optional)
            limit: Max number of events to return
        
        Returns:
            List of events
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if topic:
                cursor.execute('''
                    SELECT id, topic, event_type, payload, timestamp
                    FROM events
                    WHERE topic = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (topic, limit))
            else:
                cursor.execute('''
                    SELECT id, topic, event_type, payload, timestamp
                    FROM events
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            events = []
            for row in rows:
                events.append({
                    'id': row['id'],
                    'topic': row['topic'],
                    'event_type': row['event_type'],
                    'payload': json.loads(row['payload']),
                    'timestamp': row['timestamp']
                })
            
            return events
        except Exception as e:
            print(f"[EventStore] Error retrieving events: {e}")
            return []
    
    def get_event_stats(self) -> Dict:
        """Get statistics about stored events."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total events
            cursor.execute('SELECT COUNT(*) FROM events')
            total = cursor.fetchone()[0]
            
            # Events by topic
            cursor.execute('''
                SELECT topic, COUNT(*) as count
                FROM events
                GROUP BY topic
            ''')
            by_topic = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Latest event
            cursor.execute('''
                SELECT timestamp FROM events
                ORDER BY timestamp DESC
                LIMIT 1
            ''')
            latest = cursor.fetchone()
            latest_time = latest[0] if latest else None
            
            conn.close()
            
            return {
                'total_events': total,
                'by_topic': by_topic,
                'latest_event': latest_time
            }
        except Exception as e:
            print(f"[EventStore] Error getting stats: {e}")
            return {}
    
    def clear_events(self):
        """Clear all stored events (for testing)."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM events')
            conn.commit()
            conn.close()
            print("[EventStore] Cleared all events")
        except Exception as e:
            print(f"[EventStore] Error clearing events: {e}")
