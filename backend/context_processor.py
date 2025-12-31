"""
Context processor using Google Gemini to synthesize current reality.
Generates calm, simple explanations of the current state.
"""

import os
import json
from datetime import datetime

class ContextProcessor:
    def __init__(self):
        """Initialize Gemini context processor."""
        self.model_name = "gemini-1.5-flash"
        
        # Try to import Vertex AI (will fail gracefully if not configured)
        try:
            import vertexai
            from vertexai.generative_models import GenerativeModel
            
            project_id = os.getenv('GOOGLE_PROJECT_ID')
            region = os.getenv('GOOGLE_REGION', 'us-central1')
            
            if project_id:
                vertexai.init(project=project_id, location=region)
                self.model = GenerativeModel(self.model_name)
                self.ready = True
            else:
                self.ready = False
                print("[Context] Gemini not configured (missing GOOGLE_PROJECT_ID)")
        except ImportError:
            self.ready = False
            print("[Context] Vertex AI SDK not installed")
    
    def synthesize_reality(self, state):
        """
        Synthesize current reality from state.
        
        Args:
            state: CurrentRealityState object
        
        Returns:
            str: Calm, simple explanation (2-3 sentences)
        """
        if not self.ready:
            return self._fallback_synthesis(state)
        
        try:
            prompt = self._build_prompt(state)
            response = self.model.generate_content(prompt)
            explanation = response.text.strip()
            return explanation
        except Exception as e:
            print(f"[Context Error] {e}")
            return self._fallback_synthesis(state)
    
    def _build_prompt(self, state):
        """Build prompt for Gemini."""
        state_dict = state.to_dict()
        
        prompt = f"""You are a calm, reassuring voice for someone with dementia who is feeling confused.
Based on their current situation, provide a brief, simple explanation (2-3 sentences max) of what is happening right now.

Current situation:
- Location: {state_dict.get('location', 'unknown')}
- Time: {state_dict.get('time_of_day', 'unknown')}
- People present: {', '.join(state_dict.get('people_present', [])) or 'no one'}
- On a call with: {state_dict.get('call_active_with', 'no one')}
- Recent activity: {state_dict.get('recent_activity', 'none')}

Provide a warm, grounding explanation. Use simple words. Be reassuring. Do not ask questions.
Example: "You are at home. It is Tuesday morning. Your daughter Anna is with you."

Explanation:"""
        
        return prompt
    
    def _fallback_synthesis(self, state):
        """Fallback synthesis when Gemini is not available."""
        state_dict = state.to_dict()
        
        location = state_dict.get('location', 'home')
        time_of_day = state_dict.get('time_of_day', 'now')
        people = state_dict.get('people_present', [])
        call_with = state_dict.get('call_active_with')
        
        # Build simple explanation
        parts = [f"You are at {location}."]
        
        if time_of_day:
            parts.append(f"It is {time_of_day}.")
        
        if call_with:
            parts.append(f"You are on a call with {call_with}.")
        elif people:
            people_str = ' and '.join(people)
            parts.append(f"{people_str} {'is' if len(people) == 1 else 'are'} with you.")
        
        return ' '.join(parts)
