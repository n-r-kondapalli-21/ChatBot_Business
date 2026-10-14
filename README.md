# FAQ Chatbot API

A **standalone, production-oriented FAQ chatbot module** built with Python and FastAPI.
It uses semantic search (sentence-transformers) to match user questions against a predefined FAQ dataset — no LLM, no vector database, no external paid API required.

---

## Table of Contents

1. [Project Structure](#project-structure)
2. [Requirements](#requirements)
3. [Installation](#installation)
4. [Running the Application](#running-the-application)
5. [Web UI](#web-ui)
6. [API Reference](#api-reference)
7. [Configuration](#configuration)
8. [Running Tests](#running-tests)
9. [Adding New FAQs](#adding-new-faqs)
10. [Architecture Notes](#architecture-notes)

---

## Project Structure

```
faq_chatbot/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app + lifespan (startup/shutdown)
│   ├── config.py            # Centralised settings (env-var overridable)
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py       # Pydantic request/response models
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── health.py        # GET /health, GET /
│   │   ├── faqs.py          # GET /faqs
│   │   └── chat.py          # POST /chat
│   └── services/
│       ├── __init__.py
│       ├── faq_loader.py    # Data loading (JSON today, DB tomorrow)
│       └── matcher.py       # Semantic similarity engine
├── data/
│   └── faqs.json            # FAQ data store (12 sample entries)
├── embedded_model/          # Local cache for sentence-transformer model (all-MiniLM-L6-v2)
├── web_ui/                  # Web interface (separate module)
│   ├── index.html           # HTML structure
│   ├── styles.css           # Styling
│   ├── app.js               # JavaScript logic
│   ├── serve.py             # Simple HTTP server
│   └── README.md            # Web UI documentation
├── tests/
│   ├── __init__.py
│   └── test_chatbot.py      # pytest test suite (30+ tests)
├── download_model.py        # Script to download model locally
├── requirements.txt
└── README.md
```

---

## Requirements

- **Python 3.11+** (tested on 3.12)
- pip / venv

No external service dependencies — everything runs locally.

---

## Installation

```powershell
# 1. Navigate into the project folder
cd faq_chatbot

# 2. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows PowerShell
# or .venv\Scripts\activate.bat   # Windows CMD

# 3. Install all dependencies
pip install -r requirements.txt

# 4. (Optional) Download the model locally to avoid downloading on startup
python download_model.py
```

> **First run note:** The `all-MiniLM-L6-v2` sentence-transformer model (~90 MB)
> is downloaded automatically from Hugging Face on the first startup and cached
> in the `embedded_model/` folder. You can run `python download_model.py` to download
> it beforehand. Subsequent starts are instant.

---

## Running the Application

```powershell
# From inside faq_chatbot/ with .venv activated:
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

| URL | Purpose |
|-----|---------|
| `http://localhost:8000/` | Redirects to API documentation |
| `http://localhost:8000/docs` | Interactive Swagger UI |
| `http://localhost:8000/redoc` | ReDoc documentation |

---

## Web UI

A simple, beautiful web interface is available in the `web_ui/` folder.

### Starting the Web UI

```powershell
# Terminal 1: Start the API server
cd faq_chatbot
.venv/Scripts/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2: Start the web UI
cd faq_chatbot/web_ui
python serve.py
```

Then open http://localhost:3000 in your browser.

### Web UI Features

- Clean chat interface
- Real-time connection status
- Clickable FAQ list
- Similarity score display
- Responsive design

For more details, see [web_ui/README.md](web_ui/README.md).

---

## API Reference

### `GET /`

Redirects to the API documentation at `/docs`.

### `GET /health`

**Response:**
```json
{
  "status": "ok",
  "service": "FAQ Chatbot API",
  "version": "1.0.0",
  "model_loaded": true,
  "faq_count": 12
}
```

### `GET /faqs`

**Response:**
```json
{
  "success": true,
  "data": [ { "id": "faq_001", "question": "...", "answer": "...", "category": "general" } ],
  "message": "12 FAQ entries available."
}
```

### `POST /chat`

**Request:** `{ "question": "When do you open?" }`

**Matched response:**
```json
{
  "question": "When do you open?",
  "answer": "We are open Monday through Friday, 9 AM to 6 PM (IST)...",
  "matched_faq_id": "faq_001",
  "similarity_score": 0.7821,
  "matched": true
}
```

**Fallback response:**
```json
{
  "question": "What is the speed of light?",
  "answer": "I'm sorry, I don't have an answer to that...",
  "matched_faq_id": null,
  "similarity_score": 0.1532,
  "matched": false
}
```

### cURL Examples

```bash
# Health check
curl http://localhost:8000/health

# List FAQs
curl http://localhost:8000/faqs

# Ask a question
curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d "{\"question\": \"How do I reset my password?\"}"

# Paraphrase
curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d "{\"question\": \"I forgot my password, how do I get a new one?\"}"

# Trigger fallback
curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d "{\"question\": \"What is the capital of France?\"}"
```

---

## Configuration

All settings are in `app/config.py` and overridable via environment variables or a `.env` file.

| Variable | Default | Description |
|----------|---------|-------------|
| `EMBEDDING_MODEL_NAME` | `all-MiniLM-L6-v2` | Sentence-transformer model |
| `CACHE_FOLDER_PATH` | `embedded_model/` | Local cache directory for the model |
| `SIMILARITY_THRESHOLD` | `0.38` | Min cosine similarity to accept a match (0.0-1.0) |
| `FAQ_FILE_PATH` | `data/faqs.json` | Path to the FAQ JSON file |
| `FALLBACK_MESSAGE` | *(see config.py)* | Response when no match found |
| `DEBUG` | `false` | Enable DEBUG logging |

**Example `.env`:**
```env
CACHE_FOLDER_PATH=embedded_model/
SIMILARITY_THRESHOLD=0.50
DEBUG=true
```

---

## Running Tests

```powershell
# From inside faq_chatbot/ with .venv activated:
pytest tests/ -v
```

| Test Class | Coverage |
|------------|----------|
| `TestHealthEndpoint` | /health status, shape, version |
| `TestFAQsEndpoint` | /faqs list and fields |
| `TestExactMatching` | Exact questions -> correct faq_id |
| `TestParaphrasedMatching` | Paraphrases resolve correctly |
| `TestInputValidation` | Empty/whitespace/missing/too-long -> 422 |
| `TestNoMatchFallback` | Irrelevant questions -> fallback |
| `TestFAQMatcherUnit` | FAQMatcher internals |

---

## Adding New FAQs

Append to `data/faqs.json`:

```json
{
  "id": "faq_013",
  "question": "Do you offer bulk discounts?",
  "answer": "Yes, we offer tiered discounts. Contact sales@example.com for a quote.",
  "category": "billing"
}
```

**Rules:** `id` must be unique. Restart the server after editing.

To switch to a database: override only `FAQLoader._load_raw()`.

---

## Architecture Notes

```
HTTP Request --> FastAPI App --> FAQMatcher (cosine sim)
                                    |              |
                         SentenceTransformer   FAQLoader
                         (loaded at startup)   (JSON file)
```

- Model load: ~2-5 s (once at startup)
- Per-request: one encode + O(N) dot products
- Memory: ~60 MB model + tiny numpy array
