"""
User and caregiver management system.
Handles relationships between dementia users and their caregivers.
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional

class UserManager:
    def __init__(self, db_path='anchor_users.db'):
        """Initialize user manager."""
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                location TEXT,
                latitude REAL,
                longitude REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Caregiver relationships
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS caregiver_relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dementia_user_id TEXT NOT NULL,
                caregiver_id TEXT NOT NULL,
                relationship TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(dementia_user_id) REFERENCES users(user_id),
                FOREIGN KEY(caregiver_id) REFERENCES users(user_id)
            )
        ''')
        
        # Memories
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        ''')
        
        # People registry (for proximity detection)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS people_registry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                relationship TEXT,
                phone TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("[UserManager] Database initialized")
    
    def create_user(self, user_id: str, name: str, role: str) -> bool:
        """Create a new user (dementia user or caregiver)."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO users (user_id, name, role)
                VALUES (?, ?, ?)
            ''', (user_id, name, role))
            
            conn.commit()
            conn.close()
            print(f"[UserManager] Created user: {user_id} ({role})")
            return True
        except Exception as e:
            print(f"[UserManager] Error creating user: {e}")
            return False
    
    def add_caregiver(self, dementia_user_id: str, caregiver_id: str, relationship: str) -> bool:
        """Link a caregiver to a dementia user."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO caregiver_relationships (dementia_user_id, caregiver_id, relationship)
                VALUES (?, ?, ?)
            ''', (dementia_user_id, caregiver_id, relationship))
            
            conn.commit()
            conn.close()
            print(f"[UserManager] Added caregiver {caregiver_id} for {dementia_user_id}")
            return True
        except Exception as e:
            print(f"[UserManager] Error adding caregiver: {e}")
            return False
    
    def get_caregivers(self, dementia_user_id: str) -> List[Dict]:
        """Get all caregivers for a dementia user."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT u.user_id, u.name, cr.relationship
                FROM caregiver_relationships cr
                JOIN users u ON cr.caregiver_id = u.user_id
                WHERE cr.dementia_user_id = ?
            ''', (dementia_user_id,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"[UserManager] Error getting caregivers: {e}")
            return []
    
    def add_memory(self, user_id: str, title: str, content: str, category: str = 'general') -> bool:
        """Add a memory for a user."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO memories (user_id, title, content, category)
                VALUES (?, ?, ?, ?)
            ''', (user_id, title, content, category))
            
            conn.commit()
            conn.close()
            print(f"[UserManager] Added memory for {user_id}: {title}")
            return True
        except Exception as e:
            print(f"[UserManager] Error adding memory: {e}")
            return False
    
    def get_memories(self, user_id: str) -> List[Dict]:
        """Get all memories for a user."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, title, content, category, created_at
                FROM memories
                WHERE user_id = ?
                ORDER BY created_at DESC
            ''', (user_id,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"[UserManager] Error getting memories: {e}")
            return []
    
    def add_person(self, user_id: str, name: str, relationship: str, phone: str = None) -> bool:
        """Add a person to the registry."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO people_registry (user_id, name, relationship, phone)
                VALUES (?, ?, ?, ?)
            ''', (user_id, name, relationship, phone))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"[UserManager] Error adding person: {e}")
            return False
    
    def get_people(self, user_id: str) -> List[Dict]:
        """Get all people in registry for a user."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, name, relationship, phone
                FROM people_registry
                WHERE user_id = ?
                ORDER BY name
            ''', (user_id,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"[UserManager] Error getting people: {e}")
            return []
    
    def update_location(self, user_id: str, location: str, latitude: float = None, longitude: float = None) -> bool:
        """Update user location."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE users
                SET location = ?, latitude = ?, longitude = ?
                WHERE user_id = ?
            ''', (location, latitude, longitude, user_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"[UserManager] Error updating location: {e}")
            return False
    
    def get_nearby_people(self, user_id: str, radius_km: float = 0.1) -> List[Dict]:
        """Get people within radius (100m = 0.1km)."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get user's location
            cursor.execute('''
                SELECT latitude, longitude FROM users WHERE user_id = ?
            ''', (user_id,))
            
            user_loc = cursor.fetchone()
            if not user_loc or not user_loc['latitude']:
                return []
            
            user_lat, user_lon = user_loc['latitude'], user_loc['longitude']
            
            # Simple distance calculation (Haversine)
            cursor.execute('''
                SELECT id, name, relationship, 
                       (3959 * acos(cos(radians(?)) * cos(radians(latitude)) * 
                        cos(radians(longitude) - radians(?)) + 
                        sin(radians(?)) * sin(radians(latitude)))) AS distance
                FROM people_registry
                WHERE user_id = ?
                HAVING distance < ?
                ORDER BY distance
            ''', (user_lat, user_lon, user_lat, user_id, radius_km))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"[UserManager] Error getting nearby people: {e}")
            return []
