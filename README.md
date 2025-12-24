Here’s a **clean, submission-ready `README.md`** you can directly paste into your project.
It matches your **RAG support bot** exactly and aligns with the assignment rubric.

---

# 🧠 Q&A Support Bot using Retrieval Augmented Generation (RAG)

## 📌 Project Overview

This project implements a **Q&A Support Bot** using **Retrieval Augmented Generation (RAG)**.
The bot crawls a website, extracts and cleans content, chunks the text, generates embeddings, stores them in a vector database, and answers user questions **only from the crawled content**.

The system is built using:

* **FastAPI** for REST APIs
* **LangChain** for RAG pipeline
* **OpenAI Embeddings**
* **ChromaDB** for vector storage

---

## 🏗️ Architecture Overview

1. **Crawling** – Crawl internal pages of a given website
2. **Text Extraction** – Clean HTML to visible text
3. **Chunking** – Split text into overlapping chunks
4. **Embeddings** – Convert chunks into vectors
5. **Vector Storage** – Store vectors in ChromaDB
6. **Retrieval + Generation** – Retrieve relevant chunks and generate answers

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the repository

```bash
git clone <repo-url>
cd Q&A-support-Bot
```

### 2️⃣ Create and activate virtual environment

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # Windows
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Set environment variables

Create a `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

---

## 🚀 Running the Application

### Start FastAPI server

```bash
uvicorn api:app --reload
```

Server runs at:

```
http://127.0.0.1:8000
```

Swagger UI:

```
http://127.0.0.1:8000/docs
```

---

## 🔎 Crawling the Website

### Endpoint

**POST /crawl**

### Description

* Crawls internal pages of a website
* Extracts and cleans text
* Chunks content
* Generates embeddings
* Indexes everything into the vector database

### Example Request (Swagger / Postman)

```json
{
  "baseUrl": "https://medlineplus.gov/diabetes.html",
  "maxDepth": 1,
  "maxPages": 15,
  "allowedPathPrefixes": ["/diabetes", "/ency/article/"],
  "rebuildIndex": true
}
```

### Example Response

```json
{
  "status": "Crawl and indexing completed successfully"
}
```

---

## ❓ Asking Questions

### Endpoint

**POST /ask**

### Description

* Embeds the user question
* Retrieves top relevant chunks
* Generates an answer using only retrieved context
* Returns answer + source URLs

### Example Request

```json
{
  "question": "What is diabetes?",
  "k": 5
}
```

### Example Response

```json
{
  "question": "What is diabetes?",
  "answer": "Diabetes is a condition in which blood glucose levels are too high...",
  "sources": [
    "https://medlineplus.gov/diabetes.html",
    "https://medlineplus.gov/diabetestype2.html"
  ]
}
```

---

## 🧪 Example Questions to Try

* What is diabetes?
* What are symptoms of type 2 diabetes?
* What complications can diabetes cause?
* How is diabetes treated?
* Difference between type 1 and type 2 diabetes?

---

## 🔮 Future Improvements

* Support for PDFs and dynamic websites
* Improve answer grounding and citation formatting


---
