import json
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma


def load_chunks(path: str) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def chunks_to_documents(chunks: List[Dict]) -> List[Document]:
    docs = []
    for c in chunks:
        text = (c.get("chunk_text") or "").strip()
        if not text:
            continue

        parent_url = c.get("parent_url")

        docs.append(
            Document(
                page_content=text,
                metadata={
                    "chunk_id": c.get("chunk_id"),
                    "parent_url": parent_url,
                    "source": parent_url,              
                    "page_title": c.get("page_title", ""),
                },
            )
        )
    return docs


def build_chroma_openai(
    chunks_path: str = "chunks.json",
    persist_dir: str = "chroma_db",
    collection_name: str = "rag_chunks",
):
    chunks = load_chunks(chunks_path)
    docs = chunks_to_documents(chunks)

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    vectordb = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=persist_dir,
        collection_name=collection_name,
    )

   
    vectordb.persist()

    print(f"✅ Inserted {len(docs)} chunks into Chroma: {persist_dir} ({collection_name})")
    return vectordb


def test_similarity(vectordb, query: str, k: int = 5):
    results = vectordb.similarity_search_with_score(query, k=k)

    print("\n🔎 Top matches:")
    for i, (doc, score) in enumerate(results, 1):
        md = doc.metadata
        print(f"\n{i}) score: {score}")
        print(f"   title: {md.get('page_title')}")
        print(f"   url:   {md.get('parent_url')}")
        print(f"   chunk_id: {md.get('chunk_id')}")
        print(f"   text:  {doc.page_content[:250]}...")


if __name__ == "__main__":
    db = build_chroma_openai("chunks.json", "chroma_db", "rag_chunks")
    test_similarity(db, "What are symptoms of type 2 diabetes?", k=5)
