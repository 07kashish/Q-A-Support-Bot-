import re
from typing import List, Dict, Optional
from urllib.parse import urlparse              
from langchain_community.document_loaders import RecursiveUrlLoader


SKIP_PATTERNS = [
    r"/login", r"/signin", r"/sign-in",
    r"/signup", r"/sign-up", r"/register",
    r"/cart", r"/checkout", r"/payment",
]


SKIP_EXTENSIONS = (
    ".css", ".js", ".png", ".jpg", ".jpeg", ".gif", ".svg",
    ".ico", ".pdf", ".zip", ".xml", ".json", ".woff", ".woff2", ".ttf"
)

def crawl_website(
    base_url: str,
    max_depth: int = 2,
    max_pages: int = 15,
    allowed_path_prefixes: Optional[List[str]] = None,
) -> List[Dict]:
    """
    Returns a list of dicts with:
      - url
      - title
      - raw_html
    """

    base_netloc = urlparse(base_url).netloc.lower()  

    loader = RecursiveUrlLoader(
        base_url,
        max_depth=max_depth,
        prevent_outside=True,
        extractor=None,
        check_response_status=True,
        continue_on_failure=True,
    )

    docs = loader.load()

    pages: List[Dict] = []
    seen_urls = set()                               

    for d in docs:
        url = (d.metadata.get("source") or "").strip()
        if not url:
            continue

        parsed = urlparse(url)                        
        if parsed.netloc.lower() != base_netloc:  
            continue

        
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        u = normalized.lower()

       
        if any(u.endswith(ext) for ext in SKIP_EXTENSIONS):
            continue

      
        if any(re.search(pat, u) for pat in SKIP_PATTERNS):
            continue


        if allowed_path_prefixes:
            path = parsed.path.lower()
            if not any(pref.lower() in path for pref in allowed_path_prefixes):
                continue

       
        if normalized in seen_urls:
            continue
        seen_urls.add(normalized)

        pages.append({
            "url": normalized,                       
            "title": (d.metadata.get("title") or "").strip(),
            "raw_html": d.page_content,
        })

        if len(pages) >= max_pages:
            break

    return pages


if __name__ == "__main__":
    
    BASE_URL = "https://medlineplus.gov/diabetes.html"

    pages = crawl_website(
        base_url=BASE_URL,
        max_depth=2,
        max_pages=15,
        allowed_path_prefixes=["/diabetes", "/ency/article/"], 
    )

    print("\nCrawled URLs:")
    for p in pages:
        print("-", p["url"])

    print("\nTotal pages stored:", len(pages))

