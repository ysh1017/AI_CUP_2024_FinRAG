"""FastAPI service exposing retrieval endpoint."""
from fastapi import FastAPI
from pydantic import BaseModel, Field

from .retriever import Retriever
from .settings import cfg, logger

app = FastAPI(title="FinRAG Retrieval API", version="0.1.0")

retriever = Retriever()

class Question(BaseModel):
    """Single question schema."""
    qid: int = Field(..., example=1)
    source: list[int] = Field(..., example=[442,115,440])
    query: str = Field(..., example="匯款銀行及中間行所收取之相關費用由誰負擔?")
    category: str = Field(..., example="insurance")

class Answer(BaseModel):
    qid: int
    retrieve: int

@app.post("/api/chat", response_model=Answer)
def chat(req: Question):
    try:
        pid = retriever.top1(req.query, pids=req.source, category=req.category)
    except Exception:
        logger.exception("retrieval failed – fallback to last source pid")
        pid = req.source[-1]
    return Answer(qid=req.qid, retrieve=pid)
