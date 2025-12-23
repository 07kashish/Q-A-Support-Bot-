import json
from typing import List, Dict
from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_pages(
    cleaned_pages: List[Dict],
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> List[Dict]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks: List[Dict] = []
    chunk_id = 0

    for page in cleaned_pages:
        url = page["url"]
        title = page.get("title", "")
        text = page.get("cleaned_text", "") or ""

        split_texts = splitter.split_text(text)

        for t in split_texts:
            chunks.append({
                "chunk_id": chunk_id,
                "parent_url": url,
                "page_title": title,
                "chunk_text": t,
            })
            chunk_id += 1

    return chunks


if __name__ == "__main__":
    
    from crawling import crawl_website
    from text_extraction import clean_pages  

    BASE_URL = "https://medlineplus.gov/diabetes.html"

    pages = crawl_website(
        base_url=BASE_URL,
        max_depth=1,
        max_pages=15,
        allowed_path_prefixes=["/diabetes", "/ency/article/"],
    )

    cleaned = clean_pages(pages)

  
    chunks = chunk_pages(cleaned, chunk_size=1000, chunk_overlap=200)
    
    counts = {}
    for c in chunks:
        counts[c["parent_url"]] = counts.get(c["parent_url"], 0) + 1

    print("\nChunks per page:")
    for url, cnt in counts.items():
        print("-", cnt, "chunks:", url)

    print("\nTotal chunks:", len(chunks))

   
    if chunks:
        print("\nSample chunk:")
        print("chunk_id:", chunks[0]["chunk_id"])
        print("parent_url:", chunks[0]["parent_url"])
        print("page_title:", chunks[0]["page_title"])
        print("chunk_text (first 300 chars):", chunks[0]["chunk_text"][:300])

    with open("chunks.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
    print("\n✅ Saved chunks to chunks.json")
