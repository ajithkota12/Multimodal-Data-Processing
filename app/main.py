from pathlib import Path
from typing import List, Optional

from .processors.router import process_inputs
from .kb.store import KnowledgeBase
from .retrieval.pipeline import RetrievalPipeline
from .llm.gemini import GeminiLLM


def ingest(paths_or_urls: List[str], kb_path: str = "data/kb.jsonl") -> KnowledgeBase:
    kb = KnowledgeBase(kb_path)
    docs = process_inputs(paths_or_urls)
    kb.add_documents(docs)
    kb.persist()
    return kb


def answer(query: str, kb_path: str = "data/kb.jsonl", use_semantic: bool = True) -> str:
    kb = KnowledgeBase(kb_path)
    kb.load()
    retriever = RetrievalPipeline(kb, use_semantic=use_semantic)
    contexts = retriever.retrieve(query, top_k=5)
    llm = GeminiLLM()
    return llm.answer(query, contexts)


def ensure_data_dir() -> None:
    Path("data").mkdir(parents=True, exist_ok=True)


__all__ = ["ingest", "answer", "ensure_data_dir"]


