# Multimodal-Data-Processing

Quickstart (Windows PowerShell)
1) Create and activate a virtual environment
```powershell
python -m venv .venv
 .\.venv\Scripts\Activate.ps1
python --version
```

2) Install dependencies
```powershell
pip install -r requirements.txt
```

3) Configure Gemini (LLM)
- Temporary for this session:
```powershell
$env:GEMINI_API_KEY="YOUR_KEY"
$env:GEMINI_MODEL="models/gemini-2.5-flash"   # good default
```
- Persist for future sessions (optional):
```powershell
setx GEMINI_API_KEY "YOUR_KEY"
setx GEMINI_MODEL "models/gemini-2.5-flash"
```

4) (Optional) OCR setup
- Install Tesseract for Windows and ensure `tesseract.exe` is on PATH, or set:
```powershell
$env:TESSERACT_CMD="C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
```

5) (Optional) Offline embeddings
- Pre-cache the MiniLM model so retrieval works with limited internet:
```powershell
mkdir models 2>$null
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2', cache_folder='models/all-MiniLM-L6-v2')"
# To force offline later:
$env:EMBEDDING_MODEL_DIR="models\all-MiniLM-L6-v2"
$env:TRANSFORMERS_OFFLINE="1"; $env:HF_HUB_OFFLINE="1"
```

6) Ingest content into the knowledge base
- Local files (PDF/DOCX/PPTX/MD/TXT/PNG/JPG/MP3/MP4):
```powershell
python -m app.cli ingest "C:\\path\\to\\file.pdf"
```
- YouTube URL (playlists/extra params handled):
```powershell
python -m app.cli ingest "https://www.youtube.com/watch?v=VIDEO_ID&list=..."
```
- Custom KB path (defaults to `data/kb.jsonl`):
```powershell
python -m app.cli ingest "C:\\path\\to\\file.pdf" --kb data\mykb.jsonl
```

7) Ask questions
```powershell
python -m app.cli ask "Summarize the content in 5 bullet points." --kb data\kb.jsonl
```

Project Structure
- app/
  - processors/: handlers for each modality
  - kb/: lightweight knowledge base and vector store
  - retrieval/: keyword and semantic search
  - llm/: Gemini wrapper and fallbacks
  - ui_streamlit.py: simple UI
  - cli.py: command-line interface
  - main.py: library entrypoints

Notes
- Tesseract OCR must be installed for OCR to work. On Windows, install from https://github.com/UB-Mannheim/tesseract/wiki and ensure tesseract is on PATH or set TESSERACT_CMD.
- Whisper (faster-whisper) is used for speech-to-text; it downloads a small model on first run.
- For PDFs we use pypdf; for Office files python-docx and python-pptx.

Troubleshooting
- If `ModuleNotFoundError` appears, ensure you are using the venv Python: ` .\.venv\Scripts\python -m pip install -r requirements.txt`.
- If YouTube transcript fetch fails (HTTP 400), the app automatically cleans the URL and falls back to audio download + Whisper transcription.
- If console shows Unicode errors on Windows, the CLI forces UTF‑8 output; you can also run `chcp 65001`.


