"""
Current Reality State Manager.
Maintains the minimal state needed to ground a person with dementia.
"""

from datetime import datetime
from typing import List, Dict, Optional

class CurrentRealityState:
    def __init__(self):
        """Initialize empty state."""
        self.location: str = "home"
        self.time_of_day: str = "morning"
        self.people_present: List[str] = []
        self.call_active_with: Optional[str] = None
        self.recent_activity: str = "none"
        self.last_updated: str = datetime.now().isoformat()
    
    def add_person(self, person: str, timestamp: str = None):
        """Add a person to the current location."""
        if person not in self.people_present:
            self.people_present.append(person)
            self.last_updated = timestamp or datetime.now().isoformat()
            print(f"[State] Added {person}. Present: {self.people_present}")
    
    def remove_person(self, person: str, timestamp: str = None):
        """Remove a person from the current location."""
        if person in self.people_present:
            self.people_present.remove(person)
            self.last_updated = timestamp or datetime.now().isoformat()
            print(f"[State] Removed {person}. Present: {self.people_present}")
    
    def set_call_active(self, caller: str, timestamp: str = None):
        """Set an active call."""
        self.call_active_with = caller
        self.last_updated = timestamp or datetime.now().isoformat()
        print(f"[State] Call started with {caller}")
    
    def set_call_inactive(self, timestamp: str = None):
        """End the active call."""
        if self.call_active_with:
            print(f"[State] Call ended with {self.call_active_with}")
            self.call_active_with = None
            self.last_updated = timestamp or datetime.now().isoformat()
    
    def set_location(self, location: str, timestamp: str = None):
        """Update location."""
        self.location = location
        self.last_updated = timestamp or datetime.now().isoformat()
        print(f"[State] Location: {location}")
    
    def set_time_of_day(self, time_of_day: str, timestamp: str = None):
        """Update time of day."""
        self.time_of_day = time_of_day
        self.last_updated = timestamp or datetime.now().isoformat()
        print(f"[State] Time: {time_of_day}")
    
    def set_recent_activity(self, activity: str, timestamp: str = None):
        """Update recent activity."""
        self.recent_activity = activity
        self.last_updated = timestamp or datetime.now().isoformat()
        print(f"[State] Activity: {activity}")
    
    def to_dict(self) -> Dict:
        """Convert state to dictionary."""
        return {
            'location': self.location,
            'time_of_day': self.time_of_day,
            'people_present': self.people_present,
            'call_active_with': self.call_active_with,
            'recent_activity': self.recent_activity,
            'last_updated': self.last_updated
        }
    
    def reset(self):
        """Reset state to defaults."""
        self.location = "home"
        self.time_of_day = "morning"
        self.people_present = []
        self.call_active_with = None
        self.recent_activity = "none"
        self.last_updated = datetime.now().isoformat()
        print("[State] Reset to defaults")
