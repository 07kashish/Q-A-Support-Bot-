# 🤖 Q&A Support Bot

A powerful **Retrieval-Augmented Generation (RAG)** application built with **FastAPI** and **LangChain**. This bot crawls websites, processes content, and answers user questions using accurate, source-backed context.

## 🚀 Features

- **🕷️ Smart Crawling**: recursively crawls websites to gather knowledge (configured for depth and page limits).
- **🧹 Intelligent Extraction**: cleans generic HTML boilerplate (navbars, footers) to extract only meaningful text.
- **📦 Efficient Chunking**: splits text into optimal chunks for embedding using overlapping windows.
- **🧠 Vector Search**: uses **ChromaDB** and **OpenAI Embeddings** to store and retrieve semantic context.
- **💡 Contextual Answers**: Generates precise answers using **GPT-4o-mini**, strictly based on the retrieved documentation.
- **🔌 REST API**: Fully functional endpoints for managing the knowledge base and querying.

## 🛠️ Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **LLM Orchestration**: [LangChain](https://python.langchain.com/)
- **Vector Database**: [ChromaDB](https://www.trychroma.com/)
- **AI Models**: OpenAI (Embeddings & GPT-4)
- **Utilities**: BeautifulSoup4, Tiktoken

---

## 📂 Project Structure

```bash
.
├── API.py                 # 🚀 Main FastAPI entry point
├── crawling.py            # 🕸️ Web crawler logic (RecursiveUrlLoader)
├── text_extraction.py     # 🧹 HTML cleaning and text extraction
├── chunking.py            # 🧩 Text splitting/chunking logic
├── embeddings.py          # 🗄️ Vector store indexing (ChromaDB)
├── retrieval.py           # 🔍 Search, retrieval, and answer generation
├── memory.py              # 🧠 Conversation history management
├── requirements.txt       # 📦 Project dependencies
└── README.md              # 📄 This documentation
```

---

## ⚡ Getting Started

### 1. Prerequisites

- Python 3.9+
- An OpenAI API Key

### 2. Installation

Clone the repository and install dependencies:

```bash
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Setup

Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=sk-your-api-key-here
```

---

## 🏃 Usage

Start the FastAPI server:

```bash
uvicorn API:app --reload
```

The server will start at `http://127.0.0.1:8000`.

### 📖 API Endpoints

#### 1. Populate Knowledge Base (`/crawl`)

Crawls a website and builds the vector index.

**POST** `/crawl`
```json
{
  "baseUrl": "https://example.com/docs",
  "maxDepth": 2,
  "maxPages": 10
}
```

#### 2. Ask a Question (`/ask`)

Queries the bot.

**POST** `/ask`
```json
{
  "question": "How do I install the SDK?",
  "k": 5
}
```

### 📄 API Documentation

Visit `http://127.0.0.1:8000/docs` for the interactive Swagger UI to test endpoints directly in your browser.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
