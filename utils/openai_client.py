import os
import openai

class OpenAIClient:
    def __init__(self, api_key=None, model=None):
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY')
        self.model = model or os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo')
        openai.api_key = self.api_key

    def generate(self, prompt, system_prompt=None, max_tokens=512, temperature=0.7):
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message["content"].strip()
