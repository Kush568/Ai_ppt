# ai_tools.py
# This version requires the API token to be passed directly during initialization.
# (Code is identical to the previous "no-secrets" version. No changes needed if you already have it.)

import requests
from urllib.parse import quote as url_encode
from typing import List, Dict, Any, Optional

class PollinationsAI:
    IMAGE_API_BASE = "https://image.pollinations.ai/prompt/"
    TEXT_API_BASE = "https://text.pollinations.ai/openai/chat/completions"

    def __init__(self, api_token: str):
        if not api_token or not isinstance(api_token, str):
            raise ValueError("A valid API token must be provided as a string.")
        self.api_token = api_token
        self.headers = {"Authorization": f"Bearer {self.api_token}", "Content-Type": "application/json"}

    def generate_image(self, prompt: str, output_path: str, model: str = 'flux', width: int = 1024, height: int = 1024, seed: Optional[int] = None, nologo: bool = True, enhance: bool = True, private: bool = True) -> str:
        print(f"  - Generating image for prompt: '{prompt[:50]}...'")
        encoded_prompt = url_encode(prompt)
        url = f"{self.IMAGE_API_BASE}{encoded_prompt}"
        params = {'model': model, 'width': width, 'height': height, 'nologo': str(nologo).lower(), 'enhance': str(enhance).lower(), 'private': str(private).lower()}
        if seed is not None: params['seed'] = seed
        response = requests.get(url, params=params, headers={"Authorization": f"Bearer {self.api_token}"})
        if response.status_code != 200: raise requests.HTTPError(f"API Error [{response.status_code}]: {response.text}")
        with open(output_path, 'wb') as f: f.write(response.content)
        print(f"  - Image successfully saved to '{output_path}'")
        return output_path

    def generate_text(self, prompt: str, model: str = 'gpt-4', system_prompt: Optional[str] = None, temperature: float = 0.7, max_tokens: Optional[int] = 2048) -> str:
        print(f"Generating text for prompt: '{prompt[:50]}...'")
        messages = []
        if system_prompt: messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        payload = {"model": model, "messages": messages, "temperature": temperature}
        if max_tokens: payload['max_tokens'] = max_tokens
        response = requests.post(self.TEXT_API_BASE, headers=self.headers, json=payload)
        if response.status_code != 200: raise requests.HTTPError(f"API Error [{response.status_code}]: {response.text}")
        try:
            content = response.json()['choices'][0]['message']['content']
            return content.strip()
        except (KeyError, IndexError) as e:
            raise KeyError(f"Could not parse the API response. Error: {e}. Response received: {response.json()}")