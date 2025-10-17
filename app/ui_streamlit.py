import os
import streamlit as st
from typing import List

from .main import ingest, answer, ensure_data_dir


st.set_page_config(page_title="Multimodal QA", page_icon="🤖", layout="wide")
ensure_data_dir()

st.title("Multimodal Data Processing System")

with st.sidebar:
    st.header("Ingest Files/URLs")
    uploaded = st.file_uploader("Upload files", type=["pdf","docx","pptx","md","txt","png","jpg","jpeg","mp3","mp4"], accept_multiple_files=True)
    url = st.text_input("YouTube URL or file URL (optional)")
    kb_path = st.text_input("KB path", value="data/kb.jsonl")
    if st.button("Ingest"):
        paths: List[str] = []
        if uploaded:
            for f in uploaded:
                tmp_path = os.path.join("data", f.name)
                with open(tmp_path, "wb") as w:
                    w.write(f.getbuffer())
                paths.append(tmp_path)
        if url:
            paths.append(url)
        if not paths:
            st.warning("No files or URLs provided")
        else:
            kb = ingest(paths, kb_path=kb_path)
            st.success(f"Ingested {len(kb.documents)} documents")

st.header("Ask a question")
q = st.text_input("Your question")
use_sem = st.checkbox("Use semantic search", value=True)
if st.button("Ask") and q:
    st.write(answer(q, kb_path=kb_path, use_semantic=use_sem))


