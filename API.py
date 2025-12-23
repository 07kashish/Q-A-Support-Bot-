from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
import json
import os
import shutil


from crawling import crawl_website
from text_extraction import clean_pages
from chunking import chunk_pages
from embeddings import build_chroma_openai
from retrieval import load_vectordb, retrieve_chunks, generate_answer

app = FastAPI(title="Q&A Support Bot")

PERSIST_DIR = "chroma_db"
COLLECTION_NAME = "rag_chunks"
CHUNKS_PATH = "chunks.json"


class CrawlRequest(BaseModel):
    baseUrl: HttpUrl
    maxDepth: int = 2
    maxPages: int = 15
    allowedPathPrefixes: Optional[List[str]] = None
    rebuildIndex: bool = True  


class AskRequest(BaseModel):
    question: str
    k: int = 5


@app.post("/crawl")
def crawl_endpoint(req: CrawlRequest) -> Dict[str, Any]:
    """
    POST /crawl
    Input: baseUrl
    Actions: crawl -> extract -> chunk -> embeddings -> index to vector store
    Output: success message + counts
    """
    base_url = str(req.baseUrl)

    
    if req.rebuildIndex and os.path.exists(PERSIST_DIR):
        shutil.rmtree(PERSIST_DIR)

    # 1) crawl
    pages = crawl_website(
        base_url=base_url,
        max_depth=req.maxDepth,
        max_pages=req.maxPages,
        allowed_path_prefixes=req.allowedPathPrefixes,
    )
    if not pages:
        raise HTTPException(status_code=400, detail="No pages crawled. Check baseUrl / depth / filters.")

    # 2) extract/clean
    cleaned_pages = clean_pages(pages)
    if not cleaned_pages:
        raise HTTPException(status_code=400, detail="No cleaned pages produced. Check extraction filters.")

    # 3) chunk
    chunks = chunk_pages(cleaned_pages, chunk_size=1000, chunk_overlap=200)
    if not chunks:
        raise HTTPException(status_code=400, detail="No chunks created. Check cleaned_text content.")

   
    with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    # 4) embeddings + index into vector store
    build_chroma_openai(
        chunks_path=CHUNKS_PATH,
        persist_dir=PERSIST_DIR,
        collection_name=COLLECTION_NAME,
    )

    return {
        "message": "✅ Crawl + extract + chunk + embed + index completed",
        "baseUrl": base_url,
        "pages_crawled": len(pages),
        "pages_cleaned": len(cleaned_pages),
        "chunks_created": len(chunks),
        "vector_store": {
            "persist_dir": PERSIST_DIR,
            "collection_name": COLLECTION_NAME,
        }
    }


@app.post("/ask")
def ask_endpoint(req: AskRequest) -> Dict[str, Any]:
    """
    POST /ask
    Input: question
    Actions: retrieve -> generate answer
    Output: answer + source URLs
    """
    if not os.path.exists(PERSIST_DIR):
        raise HTTPException(status_code=400, detail="Vector store not found. Call POST /crawl first.")

    db = load_vectordb(persist_dir=PERSIST_DIR, collection_name=COLLECTION_NAME)
    retrieved = retrieve_chunks(db, req.question, k=req.k)
    result = generate_answer(retrieved)

    return {
        "question": result["question"],
        "answer": result["answer"],
        "sources": result["sources"],
    }
