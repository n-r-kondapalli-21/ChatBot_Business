# FAQ Chatbot - Project Overview

## What is this project?

A simple AI-powered FAQ chatbot that answers user questions by matching them against a predefined FAQ database. It uses **semantic search** (understanding meaning, not just keywords) to find the most relevant answer.

**Key Features:**
- No external AI APIs required (runs locally)
- Fast and lightweight
- Uses semantic similarity to understand paraphrased questions
- Easy to add new FAQs

---

## How it Works (The Pipeline)

```
User Question
    ↓
FastAPI Receives Request
    ↓
Convert Question to Embeddings (Vector Representation)
    ↓
Compare with Pre-computed FAQ Embeddings
    ↓
Find Best Match (Cosine Similarity)
    ↓
If Score > Threshold → Return Matched FAQ Answer
If Score < Threshold → Return Fallback Message
```

### Step-by-Step Explanation:

1. **User asks a question** (e.g., "I forgot my password")
2. **Server receives the request** via FastAPI
3. **Question is converted to numbers** (embeddings) using a pre-trained sentence-transformer model
4. **Compare with all FAQs** - The system compares the question embedding with pre-computed embeddings of all FAQ questions
5. **Calculate similarity score** - Uses cosine similarity to find the closest match (0.0 = no match, 1.0 = perfect match)
6. **Decision making**:
   - If similarity > threshold (0.38): Return the matched FAQ answer
   - If similarity < threshold: Return a fallback message (e.g., "I don't have an answer for that")

---

## Project Structure & File Functionality

```
faq_chatbot/
├── app/                          # Main application code
│   ├── main.py                   # FastAPI application entry point
│   │                             # - Initializes the app
│   │                             # - Loads the model on startup
│   │                             # - Pre-computes FAQ embeddings
│   │                             # - Registers API routes
│   │
│   ├── config.py                 # Configuration settings
│   │                             # - Model name, file paths, thresholds
│   │                             # - Can be overridden via environment variables
│   │
│   ├── models/                   # Data models (Pydantic schemas)
│   │   └── schemas.py            # - Request/response structure definitions
│   │                             # - Ensures data validation
│   │
│   ├── routes/                   # API endpoints
│   │   ├── health.py             # - GET / (redirects to docs)
│   │                             # - GET /health (health check)
│   │   ├── faqs.py               # - GET /faqs (list all FAQs)
│   │   └── chat.py               # - POST /chat (ask a question)
│   │
│   └── services/                 # Business logic
│       ├── faq_loader.py         # - Loads FAQ data from JSON file
│       └── matcher.py            # - Semantic matching engine
│                                 # - Converts text to embeddings
│                                 # - Calculates similarity scores
│
├── data/
│   └── faqs.json                 # FAQ database (questions & answers)
│
├── embedded_model/               # Local cache for AI model
│   └── models--sentence-transformers--all-MiniLM-L6-v2/
│                                 # - Pre-trained model files
│                                 # - Downloaded once, reused on startup
│
├── tests/
│   └── test_chatbot.py           # Test suite (30+ tests)
│                                 # - Tests all endpoints
│                                 # - Tests matching accuracy
│
├── download_model.py             # Script to download model locally
│                                 # - Run once to cache the model
│
├── requirements.txt              # Python dependencies
├── .gitignore                    # Files to exclude from git
└── README.md                     # Main documentation
```

---

## File-by-File Deep Dive

### Core Application Files

#### `app/main.py` - The Brain
**Purpose:** FastAPI application factory and startup manager

**What it does:**
- Creates the FastAPI application
- Manages startup/shutdown lifecycle
- Loads the embedding model (once at startup)
- Pre-computes FAQ embeddings for fast responses
- Registers all API routes (health, faqs, chat)
- Configures CORS (Cross-Origin Resource Sharing)

**Key Functions:**
- `lifespan()` - Runs at startup to load model and compute embeddings
- `create_app()` - Creates and configures the FastAPI app

---

#### `app/config.py` - The Settings
**Purpose:** Centralized configuration management

**What it does:**
- Defines all configurable settings
- Allows overrides via environment variables or `.env` file
- Provides defaults for everything

**Key Settings:**
- `embedding_model_name` - Which AI model to use (all-MiniLM-L6-v2)
- `cache_folder_path` - Where to store the model (embedded_model/)
- `similarity_threshold` - Minimum score to accept a match (0.38)
- `faq_file_path` - Path to FAQ JSON file
- `fallback_message` - What to say when no match found

---

#### `app/models/schemas.py` - The Data Structures
**Purpose:** Pydantic models for request/response validation

**What it does:**
- Defines the structure of API requests
- Defines the structure of API responses
- Automatically validates incoming data
- Provides type hints for better code

**Key Models:**
- `ChatRequest` - User question input
- `ChatResponse` - Answer with similarity score
- `FAQsResponse` - List of all FAQs
- `HealthResponse` - Service status

---

### API Routes

#### `app/routes/health.py` - Health Check
**Purpose:** Service health monitoring

**Endpoints:**
- `GET /` - Redirects to API documentation
- `GET /health` - Returns service status, model loaded flag, FAQ count

**Use Case:** Monitoring if the service is running correctly

---

#### `app/routes/faqs.py` - FAQ Listing
**Purpose:** List all available FAQs

**Endpoints:**
- `GET /faqs` - Returns all FAQ entries

**Use Case:** Admins can view all FAQs, debugging

---

#### `app/routes/chat.py` - Question Answering
**Purpose:** The main chat endpoint

**Endpoints:**
- `POST /chat` - Accepts a question, returns an answer

**How it works:**
1. Receives user question
2. Calls FAQMatcher to find best match
3. Returns answer with similarity score

**Use Case:** Users asking questions

---

### Business Logic Services

#### `app/services/faq_loader.py` - Data Loading
**Purpose:** Load FAQ data from storage

**What it does:**
- Reads FAQ data from JSON file
- Validates the data structure
- Provides methods to access FAQs
- Can be extended to load from databases

**Key Methods:**
- `load()` - Loads data from file
- `get_all()` - Returns all FAQs
- `count()` - Returns number of FAQs

---

#### `app/services/matcher.py` - Semantic Matching Engine
**Purpose:** Core AI logic for matching questions

**What it does:**
- Converts text to embeddings (vector representations)
- Pre-computes FAQ embeddings at startup
- Calculates cosine similarity between questions
- Finds the best matching FAQ
- Handles fallback when no good match found

**Key Methods:**
- `__init__()` - Pre-computes FAQ embeddings
- `find_best_match()` - Finds best FAQ for a user question
- `_encode()` - Converts text to embeddings
- `_compute_similarity()` - Calculates similarity score

**How similarity works:**
- Uses cosine similarity (dot product of normalized vectors)
- Score ranges from 0.0 (completely different) to 1.0 (identical)
- Threshold of 0.38 means need at least 38% similarity to accept a match

---

### Data Files

#### `data/faqs.json` - FAQ Database
**Purpose:** Stores all question-answer pairs

**Structure:**
```json
[
  {
    "id": "faq_001",
    "question": "What are your business hours?",
    "answer": "We are open Monday-Friday, 9 AM to 6 PM",
    "category": "general"
  }
]
```

**Adding new FAQs:**
- Add a new entry to the array
- Ensure unique `id`
- Restart the server to load new FAQs

---

### Utility Files

#### `download_model.py` - Model Downloader
**Purpose:** Download the AI model locally before starting the server

**Why use it:**
- Avoids downloading on every startup
- Faster server startup
- Can run offline after download

**Usage:**
```bash
python download_model.py
```

---

#### `requirements.txt` - Dependencies
**Purpose:** Lists all Python packages needed

**Key Dependencies:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `sentence-transformers` - AI model library
- `pydantic` - Data validation
- `pydantic-settings` - Configuration management

---

#### `tests/test_chatbot.py` - Test Suite
**Purpose:** Automated testing

**What it tests:**
- Health endpoint
- FAQ listing
- Exact question matching
- Paraphrased question matching
- Input validation
- Fallback behavior
- Matcher internals

**Running tests:**
```bash
pytest tests/ -v
```

---

## Technology Stack

- **Language:** Python 3.11+
- **Web Framework:** FastAPI
- **Server:** Uvicorn
- **AI Model:** sentence-transformers (all-MiniLM-L6-v2)
- **Data Format:** JSON
- **Testing:** pytest

---

## Why This Architecture?

### Advantages:
1. **Simple** - No complex setup, just Python
2. **Fast** - Pre-computed embeddings, instant responses
3. **Offline** - No external API calls needed
4. **Scalable** - Easy to add more FAQs
5. **Testable** - Comprehensive test suite
6. **Configurable** - All settings in one place

### Design Decisions:
- **JSON for FAQs** - Easy to edit, can migrate to database later
- **Pre-computed embeddings** - Faster than computing on every request
- **Cosine similarity** - Standard, effective semantic similarity metric
- **Threshold-based matching** - Flexible control over sensitivity
- **Local model caching** - Faster startup, offline capability

---

## How to Extend This Project

### Switch to Database:
Modify `app/services/faq_loader.py` to load from database instead of JSON

### Add New AI Model:
Change `embedding_model_name` in config.py

### Add Multiple Languages:
Use a multilingual model in config.py

### Add Analytics:
Log all questions and matches to a database

### Add Rate Limiting:
Add middleware in `app/main.py`

---

## Common Questions

**Q: Why not use ChatGPT or other LLMs?**
A: This is faster, cheaper, runs locally, and gives consistent answers from your FAQ database.

**Q: Can it handle typos?**
A: Yes, the semantic model understands misspelled words reasonably well.

**Q: How accurate is it?**
A: Depends on your FAQ quality and threshold. With good FAQs, 85-95% accuracy is typical.

**Q: Can I add more FAQs?**
A: Yes, just add to `data/faqs.json` and restart the server.

**Q: Does it need internet?**
A: Only for the first model download. After that, it works offline.

---

## Quick Start for New Developers

1. Read this document to understand the architecture
2. Look at `data/faqs.json` to understand the data format
3. Run `python download_model.py` to cache the model
4. Start the server: `uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload`
5. Open http://127.0.0.1:8000/docs to test the API
6. Read the code in `app/services/matcher.py` to understand the core logic
7. Run tests: `pytest tests/ -v`

---

## Summary

This project is a **semantic FAQ matcher** that:
- Loads FAQs from a JSON file
- Uses a pre-trained AI model to understand question meaning
- Matches user questions to FAQs using semantic similarity
- Returns the best matching answer or a fallback message

The architecture is clean, modular, and easy to extend. Each file has a single responsibility, making it easy to understand and maintain.
