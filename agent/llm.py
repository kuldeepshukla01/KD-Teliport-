import requests
import json
import logging

logger = logging.getLogger(__name__)

class LLM:
    def __init__(self, config):
        self.config = config
        self.api_base = config.get('api', {}).get('api_base', "http://localhost:8080/v1")
        self.model = config.get('api', {}).get('model', "gpt-3.5-turbo")
        self.timeout = config.get('api', {}).get('timeout', 60)
        self.system_prompt = config.get('agent', {}).get('system_prompt', "You are a helpful assistant.")

    def generate(self, context, user_query):
        """
        Generates a response from the LLM based on context and user query.
        """
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": self._format_prompt(context, user_query)}
        ]

        try:
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers={"Content-Type": "application/json"},
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.7,
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            return data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        except requests.exceptions.RequestException as e:
            logger.error(f"LLM API Error: {e}")
            return f"Error communicating with LLM: {str(e)}"

    def _format_prompt(self, context, query):
        """
        Formats the full prompt with context.
        """
        # Context is a dictionary containing history, cwd, etc.
        prompt = f"""
Current Directory: {context.get('cwd', 'Unknown')}
Shell: {context.get('shell', 'Unknown')}

User Query: {query}
"""
        if context.get('history'):
            prompt = f"Recent History:\n{context.get('history')}\n\n{prompt}"
            
        return prompt
