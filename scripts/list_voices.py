"""
List available ElevenLabs voices.
Run this to see all available voice IDs and pick one you like.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('ELEVENLABS_API_KEY')

if not api_key:
    print("Error: ELEVENLABS_API_KEY not set in .env")
    exit(1)

url = "https://api.elevenlabs.io/v1/voices"
headers = {'xi-api-key': api_key}

try:
    response = requests.get(url, headers=headers, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        voices = data.get('voices', [])
        
        print("\n" + "="*70)
        print("Available ElevenLabs Voices")
        print("="*70 + "\n")
        
        for voice in voices:
            voice_id = voice.get('voice_id')
            name = voice.get('name')
            category = voice.get('category', 'unknown')
            
            print(f"Name: {name}")
            print(f"ID: {voice_id}")
            print(f"Category: {category}")
            print()
        
        print("="*70)
        print(f"Total voices: {len(voices)}")
        print("="*70)
        print("\nTo use a voice, set ELEVENLABS_VOICE_ID in .env to the ID above.")
        print("Current setting: 21m00Tcm4TlvDq8ikWAM (calm, professional)")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

except Exception as e:
    print(f"Error: {e}")
