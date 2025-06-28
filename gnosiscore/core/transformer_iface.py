import os
import openai

MODEL = os.getenv("GNOSIS_MODEL", "gpt-4o-mini")
SNAPSHOT = os.getenv("GNOSIS_SNAPSHOT", MODEL)

class LLMTransformer:
    def __init__(self, model: str = None):
        self.model = model or SNAPSHOT

    def __call__(self, prompt: str, **kwargs) -> dict:
        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=kwargs.get("max_tokens", 256),
                stream=False,
            )
            content = response.choices[0].message.content
            return {
                "response": content,
                "model": self.model,
                "prompt": prompt,
            }
        except Exception as e:
            return {
                "response": f"LLM ERROR: {e}",
                "model": self.model,
                "prompt": prompt,
            }
