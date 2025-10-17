import argparse
import sys
from .main import ingest, answer, ensure_data_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Multimodal Data Processing CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_ingest = sub.add_parser("ingest", help="Ingest files/URLs into the knowledge base")
    p_ingest.add_argument("items", nargs="+", help="Paths or URLs to ingest")
    p_ingest.add_argument("--kb", default="data/kb.jsonl")

    p_ask = sub.add_parser("ask", help="Ask a question against the knowledge base")
    p_ask.add_argument("query", help="User query")
    p_ask.add_argument("--kb", default="data/kb.jsonl")
    p_ask.add_argument("--no-semantic", action="store_true", help="Disable semantic search")

    args = parser.parse_args()
    # Ensure UTF-8 output on Windows consoles to avoid UnicodeEncodeError
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass
    ensure_data_dir()

    if args.cmd == "ingest":
        kb = ingest(args.items, kb_path=args.kb)
        print(f"Ingested {len(kb.documents)} documents into {args.kb}")
    elif args.cmd == "ask":
        print(answer(args.query, kb_path=args.kb, use_semantic=not args.no_semantic))


if __name__ == "__main__":
    main()


