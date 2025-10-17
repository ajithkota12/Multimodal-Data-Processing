import os
from typing import List

try:
    import google.generativeai as genai
except Exception:  # optional dependency at runtime
    genai = None  # type: ignore


SYSTEM_PROMPT = (
    "You are a concise assistant. Answer the user's question using the provided context. "
    "If the answer isn't in the context, say you don't know."
)


class GeminiLLM:
    def __init__(self) -> None:
        self.api_key = os.getenv("GEMINI_API_KEY")
        if genai and self.api_key:
            genai.configure(api_key=self.api_key)
            # Prefer explicit env override if user provided one
            env_model = os.getenv("GEMINI_MODEL")
            if env_model:
                try:
                    self.model = genai.GenerativeModel(env_model)
                except Exception:
                    self.model = None
            # If not set or failed, auto-discover a compatible model available to this account
            if self.model is None:
                try:
                    models = list(genai.list_models())
                    # Prefer stable 2.x flash/pro models which support generateContent
                    supports = [
                        m for m in models
                        if hasattr(m, "supported_generation_methods")
                        and "generateContent" in getattr(m, "supported_generation_methods", [])
                        and ("gemini-2" in m.name or "gemini-2.5" in m.name)
                    ]
                    if supports:
                        # Choose flash first then pro
                        flash = [m for m in supports if "flash" in m.name]
                        chosen = (flash or supports)[0]
                        self.model = genai.GenerativeModel(chosen.name)
                    else:
                        # Fallback to any model with generateContent
                        any_gen = [m for m in models if "generateContent" in getattr(m, "supported_generation_methods", [])]
                        self.model = genai.GenerativeModel(any_gen[0].name) if any_gen else None
                except Exception:
                    self.model = None
        else:
            self.model = None

    def _fallback_answer(self, query: str, contexts: List[str]) -> str:
        joined = "\n\n".join(contexts[:5])
        if not joined:
            return "I don't have any data yet. Please ingest files first."
        return f"[Local Answer]\nQuestion: {query}\nContext:\n{joined[:1500]}"

    def answer(self, query: str, contexts: List[str]) -> str:
        if self.model is None:
            return self._fallback_answer(query, contexts)
        joined_context = "\n\n".join(contexts[:10])
        prompt = f"{SYSTEM_PROMPT}\n\nContext:\n{joined_context}\n\nQuestion: {query}"
        try:
            resp = self.model.generate_content(prompt)
            return resp.text or ""
        except Exception as exc:
            return f"[Gemini error] {exc}"


