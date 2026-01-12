import os
import requests

class OllamaClient:
    def __init__(self, base_url=None, model=None):
        self.base_url = base_url or os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.model = model or os.environ.get('OLLAMA_MODEL', 'llama2')

    def generate(self, prompt, system_prompt=None, max_tokens=512, temperature=0.7):
        payload = {
            "model": self.model,
            "prompt": prompt,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature
            }
        }
        if system_prompt:
            payload["system"] = system_prompt
        response = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "").strip()
