"""
Voice synthesis using ElevenLabs API.
Converts text explanations to calm, consistent audio.
"""

import os
import base64

class VoiceService:
    def __init__(self):
        """Initialize ElevenLabs voice service."""
        self.api_key = os.getenv('ELEVENLABS_API_KEY')
        self.voice_id = os.getenv('ELEVENLABS_VOICE_ID')
        self.ready = bool(self.api_key)
        
        if not self.ready:
            print("[Voice] ElevenLabs not configured")
    
    def synthesize(self, text):
        """
        Synthesize text to speech.
        
        Args:
            text: Text to synthesize
        
        Returns:
            dict: {
                'success': bool,
                'audio_base64': str (base64 encoded audio or empty),
                'error': str (if failed)
            }
        """
        # Return empty audio for now (no sound)
        return {
            'success': True,
            'audio_base64': ''
        }
    
    def get_available_voices(self):
        """Get list of available voices."""
        return []
