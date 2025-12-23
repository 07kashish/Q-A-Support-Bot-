from typing import List, Dict
from langchain_core.documents import Document
from langchain_community.document_transformers import BeautifulSoupTransformer


def pages_to_documents(pages: List[Dict]) -> List[Document]:
    return [
        Document(
            page_content=p["raw_html"],
            metadata={"source": p["url"], "title": p.get("title", "")},
        )
        for p in pages
    ]


def clean_html_docs(docs: List[Document]) -> List[Document]:
    transformer = BeautifulSoupTransformer()

    cleaned_docs = transformer.transform_documents(
        docs,
       
        tags_to_extract=["article", "main", "p", "li", "h1", "h2", "h3", "h4"],
        remove_lines=True,
    )

   
    NOISE_PHRASES = [
        "An official website of the United States government",
        "Here’s how you know",
        "Secure .gov websites use HTTPS",
        "Official websites use .gov",
        "A .gov website belongs to an official government organization in the United States.",
        "A lock ( ) or https:// means you’ve safely connected to the .gov website.",
        "Share sensitive information only on official, secure websites."
    ]

    import re

    for d in cleaned_docs:
        
        text = d.page_content
        
        
        noise_patterns = [
            r"An official website of the United States government",
            r"Here’s how you know",
            r"Official websites use \.gov",
            r"Secure \.gov websites use HTTPS",
            r"A \.gov website belongs to an official government organization in the United States",
            r"A lock \(.*\) or https:// means you’ve safely connected to the \.gov website",
            r"Share sensitive information only on official, secure websites",
            r"Lock Locked padlock icon",
            r"Medical Encyclopedia", 
        ]
        
        for pattern in noise_patterns:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE)
            
     
        text = re.sub(r'[ \t]+', ' ', text)
        
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        d.page_content = text.strip()

    return cleaned_docs


def clean_pages(pages: List[Dict]) -> List[Dict]:
    docs = pages_to_documents(pages)
    cleaned_docs = clean_html_docs(docs)

    cleaned_pages = []
    for d in cleaned_docs:
        cleaned_text = d.page_content.strip()

        
        if len(cleaned_text) < 400:
            continue

        cleaned_pages.append({
            "url": d.metadata.get("source", ""),
            "title": d.metadata.get("title", ""),
            "cleaned_text": cleaned_text,
        })

    return cleaned_pages


if __name__ == "__main__":
    from crawling import crawl_website

   
    BASE_URL = "https://medlineplus.gov/diabetes.html"

    pages = crawl_website(
        base_url=BASE_URL,
        max_depth=2,
        max_pages=15,
        allowed_path_prefixes=["/diabetes", "/ency/article/"],
    )

    cleaned = clean_pages(pages)

    print("✅ Cleaned pages:", len(cleaned))

    for i, p in enumerate(cleaned[:3], start=1):
        print(f"\n--- CLEANED PAGE {i} ---")
        print("URL:", p["url"])
        print("TITLE:", p["title"])
        print("TEXT (first 1800 chars):")
        print(p["cleaned_text"][:1800])
