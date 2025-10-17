from typing import List, Tuple
import numpy as np
from rank_bm25 import BM25Okapi
import os
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from ..kb.store import KnowledgeBase


class RetrievalPipeline:
    def __init__(self, kb: KnowledgeBase, use_semantic: bool = True):
        self.kb = kb
        self.use_semantic = use_semantic
        self._bm25 = None
        self._embedder = None
        self._doc_embeddings = None

    def _ensure_bm25(self) -> None:
        if self._bm25 is None:
            tokenized = [d.content.split() for d in self.kb.documents]
            self._bm25 = BM25Okapi(tokenized) if tokenized else None

    def _ensure_embeddings(self) -> None:
        if not self.use_semantic:
            return
        if self._embedder is None:
            # Allow fully offline use by loading model from a local directory if provided.
            # Use env EMBEDDING_MODEL_DIR or default to ./models/all-MiniLM-L6-v2 if present.
            preferred_local = os.getenv("EMBEDDING_MODEL_DIR") or os.path.join("models", "all-MiniLM-L6-v2")
            offline = os.getenv("TRANSFORMERS_OFFLINE") == "1" or os.getenv("HF_HUB_OFFLINE") == "1"
            model_id = "all-MiniLM-L6-v2"
            try:
                if os.path.isdir(preferred_local):
                    # Load strictly from local files
                    self._embedder = SentenceTransformer(preferred_local, device="cpu")
                else:
                    # If offline, force local-only to avoid DNS/HTTP errors.
                    self._embedder = SentenceTransformer(
                        model_id,
                        device="cpu",
                        cache_folder=os.path.join("models", model_id),
                        local_files_only=offline,
                    )
            except Exception:
                # If loading the embedding model fails (e.g., no internet and no local cache),
                # disable semantic search gracefully and continue with keyword search only.
                self.use_semantic = False
                self._embedder = None
                self._doc_embeddings = None
                return
        if self._doc_embeddings is None and self.kb.documents and self._embedder is not None:
            self._doc_embeddings = self._embedder.encode([d.content for d in self.kb.documents])

    def retrieve(self, query: str, top_k: int = 5) -> List[str]:
        if not self.kb.documents:
            return []

        self._ensure_bm25()
        bm25_scores = []
        if self._bm25 is not None:
            bm25_scores = self._bm25.get_scores(query.split())
        else:
            bm25_scores = np.zeros(len(self.kb.documents))

        self._ensure_embeddings()
        semantic_scores = np.zeros(len(self.kb.documents))
        if self.use_semantic and self._doc_embeddings is not None:
            q_emb = self._embedder.encode([query])
            sims = cosine_similarity(q_emb, self._doc_embeddings)[0]
            semantic_scores = sims

        # Simple score fusion
        scores = 0.5 * np.array(bm25_scores) + 0.5 * np.array(semantic_scores)
        top_idx = np.argsort(scores)[::-1][:top_k]
        return [self.kb.documents[i].content for i in top_idx]


