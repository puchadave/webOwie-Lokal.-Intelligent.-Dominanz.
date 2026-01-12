import os
import requests

class GeminiClient:
    def __init__(self, api_key=None, model=None):
        self.api_key = api_key or os.environ.get('GEMINI_API_KEY')
        self.model = model or os.environ.get('GEMINI_MODEL', 'gemini-pro')
        self.base_url = os.environ.get('GEMINI_BASE_URL', 'https://generativelanguage.googleapis.com/v1beta/models')

    def generate(self, prompt, system_prompt=None, max_tokens=512, temperature=0.7):
        url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": temperature
            }
        }
        if system_prompt:
            data["systemInstruction"] = {"parts": [{"text": system_prompt}]}
        response = requests.post(url, json=data, timeout=60)
        response.raise_for_status()
        result = response.json()
        # Gemini returns candidates list
        return result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
