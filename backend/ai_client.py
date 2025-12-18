import requests
import json

class OllamaClient:
    def __init__(self, model="gemma3:270m", url="http://localhost:11434/api/generate"):
        self.model = model
        self.url = url

    def generate_text(self, prompt):
        """
        Sends a prompt to Ollama and returns the generated text.
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }

        try:
            response = requests.post(self.url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            return data.get("response", "")
            
        except requests.exceptions.RequestException as e:
            return f"Error connecting to Ollama: {e}"
        except json.JSONDecodeError:
            return "Error decoding response from Ollama."
