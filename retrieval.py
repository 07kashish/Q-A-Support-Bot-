from typing import List, Dict, Any
from collections import OrderedDict
from dotenv import load_dotenv

load_dotenv()

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from memory import ConversationMemory
from langchain_openai import ChatOpenAI



def load_vectordb(
    persist_dir: str = "chroma_db",
    collection_name: str = "rag_chunks",
):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    vectordb = Chroma(
        persist_directory=persist_dir,
        collection_name=collection_name,
        embedding_function=embeddings,
    )
    return vectordb


def retrieve_chunks(
    vectordb,
    query: str,
    k: int = 5,
) -> Dict[str, Any]:
    """
    Retrieval function:
    - embeds query (via vector DB embedding function)
    - fetches top relevant chunks
    - returns chunks + metadata
    """
    results = vectordb.similarity_search_with_score(query, k=k)

    chunks = []
    for doc, score in results:
        md = doc.metadata or {}
        chunks.append({
            "score": score,
            "chunk_text": doc.page_content,
            "chunk_id": md.get("chunk_id"),
            "parent_url": md.get("parent_url") or md.get("source"),
            "page_title": md.get("page_title") or md.get("title", ""),
        })

    return {"query": query, "top_k": k, "chunks": chunks}


def generate_answer(
    retrieved: Dict[str, Any],
    model: str = "gpt-4o-mini",
) -> Dict[str, Any]:
    """
    Answer generation function:
    - prepares prompt with retrieved context
    - calls the LLM
    - forces answer only from context
    - returns answer + sources
    """
    query = retrieved["query"]
    chunks = retrieved["chunks"]

    
    context_blocks = []
    for i, c in enumerate(chunks, 1):
        title = c.get("page_title", "")
        url = c.get("parent_url", "")
        text = c.get("chunk_text", "")
        context_blocks.append(
            f"[{i}] Title: {title}\nURL: {url}\nContent:\n{text}"
        )
    context = "\n\n---\n\n".join(context_blocks)

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a helpful support bot. You MUST answer ONLY using the provided context. "
         "If the answer is not in the context, say: \"I don't know based on the provided content.\" "
         "Do not use outside knowledge. Be concise and clear."),
        ("user",
         "Question:\n{question}\n\n"
         "Context:\n{context}\n\n"
         "Instructions:\n"
         "- Use only the context above.\n"
         "- If unsure or missing info, say you don't know based on the provided content.\n"
         "- Cite sources by listing their URLs at the end.\n")
    ])

    llm = ChatOpenAI(model=model, temperature=0)
    chain = prompt | llm

    response = chain.invoke({"question": query, "context": context})
    answer_text = response.content

    
    urls = []
    for c in chunks:
        u = c.get("parent_url")
        if u:
            urls.append(u)

    unique_urls = list(OrderedDict.fromkeys(urls))

    return {
        "question": query,
        "answer": answer_text,
        "sources": unique_urls,
        "retrieved_chunks": chunks, 
    }


if __name__ == "__main__":
    
    db = load_vectordb(persist_dir="chroma_db", collection_name="rag_chunks")

  
    question1 = "What are symptoms of type 2 diabetes?"
    retrieved1 = retrieve_chunks(db, question1, k=5)
    result1 = generate_answer(retrieved1)

    print("\n--- TEST 1 ---")
    print("QUESTION:", result1["question"])
    print("ANSWER:\n", result1["answer"])
    print("SOURCES:", result1["sources"])

   
    question2 = "what is diabetes?"
    retrieved2 = retrieve_chunks(db, question2, k=5)
    result2 = generate_answer(retrieved2)

    print("\n--- TEST 2 ---")
    print("QUESTION:", result2["question"])
    print("ANSWER:\n", result2["answer"])
    print("SOURCES:", result2["sources"])
