"""Script to call local API and generate pred_retrieve.json."""
from __future__ import annotations
import json
import time
import requests
from pathlib import Path

QUESTIONS_PATH = Path("data/questions.json")
OUTPUT_PATH = Path("data/pred_retrieve.json")
API_URL = "http://127.0.0.1:8000/api/chat"  # uvicorn default port

def main():
    questions = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))['questions']
    out = {'answers': []}
    start = time.time()
    for q in questions:
        resp = requests.post(API_URL, json=q, timeout=30)
        resp.raise_for_status()
        res = resp.json()
        out['answers'].append({'qid': res['qid'], 'retrieve': res['retrieve']})
        print(f"QID={res['qid']} => {res['retrieve']}")
    OUTPUT_PATH.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Done in {time.time()-start:.1f}s, saved -> {OUTPUT_PATH}")
if __name__ == "__main__":
    main()
