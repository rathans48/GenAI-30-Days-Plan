# ◈ 30-Day Generative AI Mastery Curriculum

A structured, production-focused roadmap tracking development patterns from theoretical LLM architecture up to advanced multi-agent orchestration frameworks. This repository acts as a single, consolidated portfolio tracking daily implementation checkpoints, type-safe data pipelines, vector space operations, and system metrics.

---

## Progress Tracker (Foundations Phase)

| Milestone / Day | Focus Domain | Primary Engineering Objective | Status |
| :--- | :--- | :--- | :--- |
| **Day 01** | Theory & Intuition | Core LLM Mechanics, Tokenization, & Context Architectures | ⚡ Completed |
| **Day 02** | Craft & Technique | Advanced Prompt Design, Structural Logic Patterns, & CoT | ⚡ Completed |
| **Day 03** | Hands-on Python | Asynchronous API Streaming & Multi-Model Network Tunnels | ✅ Active |
| **Day 04** | Production Patterns | Deterministic Ingestion via Pydantic & Strict JSON Schemas | ✅ Active |
| **Day 05** | Vector Fundamentals | High-Dimensional Matrix Math & Local Cosine Search Spaces | ✅ Active |
| **Day 06** | Production Storage | Vector Databases & Low-Latency HNSW Index Ingestion | ✅ Active |
| **Day 07** | Week 1 Review | Full-Stack Text & PDF Q&A RAG Dashboard (Streamlit) | ✅ Active |
| **Day 08** | RAG Deep Dive | Advanced Chunking Strategies & Metadata Filtering Layers | ✅ Active |
| **Day 09** | Validation Layer | Context Grounding, Hallucination Guards, & Guardrails | ⏳ Scheduled |

---

## Active Implementation Repositories (Days 1–5)

### 📂 Day 03: Multi-Model Streaming CLI Chatbot
* **Objective:** Establish low-latency asynchronous server connections to pull streaming real-time tokens without blocking client backend application threads.
* **Architecture:** Utilizes an OpenAI-compatible client wrapper targeting a unified proxy engine to abstract endpoint logic. It features a custom multi-key parsing structure that dynamically extracts real-time typewriter-style textual data from varied upstream payloads.
* **Core Tools:** Python, Server-Sent Events (SSE), OpenRouter Meta-Gateways.

### 📂 Day 04: Type-Safe Ingestion via Strict JSON Schemas
* **Objective:** Build an automated metadata extraction engine that transforms unorganized, conversational user text blocks into type-safe JSON payloads.
* **Architecture:** Leverages Pydantic validation classes translated natively into standard JSON schemas via `.model_json_schema()`. Network calls use strict formatting constraints (`"strict": true`), freezing token selection boundaries to mathematically guarantee perfect database mapping compliance without formatting errors.
* **Core Tools:** Python, Pydantic v2, Strict JSON Schema Constraints.

### 📂 Day 05: High-Dimensional Semantic Search & PCA Vector Mapping
* **Objective:** Move beyond restrictive character keyword matching by executing spatial semantic search over unindexed data fragments using directional matrix math.
* **Architecture:** Generates data vectors across local text pools, using a synonym mapping layer to inject contextual weights. Angular distance intersections are processed via custom Cosine Similarity loops ($$\frac{\vec{A} \cdot \vec{B}}{\|\vec{A}\| \|\vec{B}\|}$$). Includes an isolated visualization module executing Principal Component Analysis (PCA) to squash 45-dimensional tokens down into a 2D coordinate plot.
* **Core Tools:** Python, NumPy, Scikit-Learn (PCA Matrix Processing), Matplotlib.

### 📂 Day 06: Local Vector Database Ingestion
* **Objective:** Index documents into a dedicated vector database to run high-speed conceptual queries without linear search bottlenecks.
* **Architecture:** Uses ChromaDB to build a local, persistent database index. It converts text strings into 384-dimensional vectors completely offline using an embedded model and runs Approximate Nearest Neighbor (ANN) searches using an HNSW graph index.
* **Core Tools:** Python, ChromaDB, ONNX Runtime.

### 📂 Day 07: Week 1 Review & Mini-Project — Full-Stack Interactive RAG Dashboard
* **Objective:** Consolidate foundational GenAI concepts into a single interactive web interface that enables context-grounded document analysis on demand.
* **Architecture:** Combines an upstream LLM inference gateway with a persistent local vector storage engine. The application handles dynamic text processing across multi-page PDF layers (`pypdf`) and flexible plaintext data blocks. Relevant context segments are retrieved by mapping user query vectors against local indices via Euclidean distance algorithms, with the resulting completion payloads routed directly into a responsive Streamlit UI layout.
* **Core Tools:** Python, Streamlit, ChromaDB, PyPDF, OpenRouter APIs.

### 📂 Day 08: RAG Deep Dive — Advanced Chunking Strategies & Ingestion Analysis
* **Objective:** Move beyond naive data splitting to evaluate how mathematical chunk structural patterns affect downstream vector precision and semantic text recall.
* **Architecture:** Implemented distinct advanced data engineering scripts. Engineered a script running a head-to-head architectural comparison between Fixed-Size, Recursive Character, and Semantic chunking methodologies inside isolated ChromaDB collections, documenting critical trade-offs regarding token fragmentation, boundary mutilation, and document noise filtering.
* **Core Tools:** Python, ChromaDB, Advanced Regex Parsing.

---

## Security & Local Execution Safety

This repository contains a unified root-level `.gitignore` layout that systematically prevents leaking keys or developer environments. To test any individual subfolder application locally, move into the day's directory, initialize an isolated virtual environment (`venv`), verify your local `.env` values are set up, and execute the runtime file:

```bash
cd "Day 05 - Semantic Search"
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
python semantic_search.py
```

---
