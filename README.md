# ◈ 30-Day Generative AI Mastery Curriculum

A structured, production-focused roadmap tracking development patterns from theoretical LLM architecture up to advanced multi-agent orchestration frameworks. This repository acts as a single, consolidated portfolio tracking daily implementation checkpoints, type-safe data pipelines, vector space operations, and system metrics.

---

## Progress Tracker (Foundations Phase)

| Milestone / Day | Focus Domain | Primary Engineering Objective | Status |
| :--- | :--- | :--- | :--- |
| **Day 01** | Theory & Intuition | Core LLM Mechanics, Tokenization, & Context Architectures | ⚡ Completed |
| **Day 02** | Craft & Technique | Advanced Prompt Design, Structural Logic Patterns, & CoT | ⚡ Completed |
| **Day 03** | Hands-on Python | Asynchronous API Streaming & Multi-Model Network Tunnels | ⚡ Completed |
| **Day 04** | Production Patterns | Deterministic Ingestion via Pydantic & Strict JSON Schemas | ⚡ Completed |
| **Day 05** | Vector Fundamentals | High-Dimensional Matrix Math & Local Cosine Search Spaces | ⚡ Completed |
| **Day 06** | Production Storage | Vector Databases & Low-Latency HNSW Index Ingestion | ⚡ Completed |
| **Day 07** | Week 1 Review | Full-Stack Text & PDF Q&A RAG Dashboard (Streamlit) | ⚡ Completed |
| **Day 08** | RAG Deep Dive | Advanced Chunking Strategies & Metadata Filtering Layers | ⚡ Completed |
| **Day 09** | LangChain Core Concepts | LangChain chains, LCEL, LangChain-powered RAG Pipeline| ⚡ Completed |
| **Day 10** | Validation & Evals | Production Observability via LangSmith & RAGAs Metrics | ⚡ Completed |
| **Day 11** | Multi-Modal Engines | Vision Capabilities & Browser Voice Command Integration | ⚡ Completed |
| **Day 12** | Autonomous Agents | Custom ReAct Loop Engine From Scratch (No Frameworks) | ⚡ Completed |
| **Day 13** | Agent Orchestration | Building Stateful Graph Machines with LangGraph & HITL | ⚡ Completed |
| **Day 14** | Multi-Agent Coordination | Hierarchical Agent Teams & Cross-Node Communication | ⚡ Completed |
| **Day 15** | Tool Integration | Hybrid Core Gateways, Tool Schemas, and Mock API Sync | ⚡ Completed |
| **Day 16** | Week 2 Review | Advanced Retrieval | Production Hybrid RAG System with Lexical Re-ranking | ⚡ Completed |
| **Day 17** | Custom Models | Fine-Tuning Pipelines & Local Sovereign Inference | ⚡ Completed |
| **Day 18** | AI Governance | Guardrails, Input Firewalls, & Hallucination Audits | ⚡ Completed |
| **Day 19** | Full-Stack App | FastAPI Async Streaming Engine & React SSE UI Client | ⚡ Completed |
| **Day 20** | Database Layers | Hybrid Postgres Storage (pgvector) & Serverless Redis Caching | ⚡ Completed |
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

### 📂 Day 09: Framework Orchestration — LangChain-Powered RAG Pipelines
* **Objective:** Transition from raw procedural data manipulation loops to declarative, component-driven AI orchestration architectures.
* **Architecture:** Engineered a standalone pipeline script and a full-stack Streamlit dashboard utilizing LangChain Expression Language (LCEL). Replaced manual file-reading routines with standardized `TextLoader` and `PyPDFLoader` modules, managed in-memory Chroma vectors implicitly, and constructed an immutable, component-swappable streaming retrieval graph (`retriever | prompt | llm | parser`).
* **Core Tools:** LangChain, Python, Streamlit, ChromaDB, OpenAI/OpenRouter APIs.

### 📂 Day 10: Validation & Evals — Production Observability, Tracing, & RAGAs
* **Objective:** Establish measurable, non-blind metric architectures to scientifically score RAG generation outputs instead of manual spot-checking.
* **Architecture:** Implemented a standardized testing suite utilizing a 10-pair "Golden Dataset." Wired up runtime telemetry hooks to LangSmith to isolate pipeline execution graphs, breakdown execution latency bottlenecks, and capture system Input/Output parameters. Configured an automated algorithmic grading harness using the RAGAs framework to compute precise vectors for Faithfulness, Answer Relevancy, and Answer Correctness. Integrated a fault-tolerant exponential back-off wrapper loop to handle concurrency throttling and API rate limits.
* **Core Tools:** LangSmith Tracing, RAGAs Evaluation Framework, Pydantic, Python, ChromaDB.

### 📂 Day 11: Multi-Modal Vision & Voice Interfaces
* **Objective:** Expand classical text-only LLM pipelines into multi-modal systems capable of processing real-time visual assets and client-side vocal inputs.
* **Architecture:** Developed an interactive multi-modal processing workspace built on Streamlit. Integrated a client-side, browser-native Web Speech STT (Speech-to-Text) module to intercept microphone audio streams and transcribe operator queries completely free of cloud compute overhead. Configured an automated base64 file serializer to pack localized pixel arrays into standard OpenAI payload specs. Wired the backend into OpenRouter’s dynamic multi-modal abstraction gateway to balance and route incoming joint visual-textual tokens without experiencing downstream model deprecations or 429 rate limit errors.
* **Core Tools:** Streamlit, OpenRouter Gateway API, Web Speech API Architecture, Python, Base64 Stream Encoding.

### 📂 Day 12: Introduction to Autonomous AI Agents & The ReAct Loop
* **Objective:** Understand and engineer the foundational runtime loops that allow LLMs to act as autonomous problem-solving engines using tools, without relying on third-party orchestration frameworks.
* **Architecture:** Developed a native Reason-and-Act (ReAct) execution loop from scratch using pure Python. Implemented a custom text parser to intercept structured LLM syntax patterns (`Action: tool_name[param]`), route variables dynamically to local tools (a math calculator and the Tavily live web-search API), and pipe the real-world output back into the conversation's short-term history memory state. Built robust error guardrails to gracefully handle API rate limits, quote stripping, and formatting failures.
* **Core Tools:** Python, OpenRouter Meta-Gateway, Tavily Search API, Regular Expressions (Regex).

### 📂 Day 13: LangGraph for Agentic Workflows & Human-in-the-Loop Orchestration
* **Objective:** Transition from unconstrained, text-parsed single-agent loops into structured, deterministic, stateful graph machines capable of complex routing and human verification gates.
* **Architecture:** Engineered a stateful research agent architecture utilizing LangGraph to handle cyclic workflows via defined Nodes, Edges, and State parameters. Configured an append-only state reducer pattern using an Annotated list of base messages to preserve an unalterable multi-turn conversation history thread. Implemented short-term in-memory state persistence utilizing a `MemorySaver` checkpointer. Embedded a synchronized breakpoint boundary (`interrupt_before`) directly ahead of the external web search tool node, creating a reliable Human-in-the-Loop (HITL) manual verification gate that freezes execution mid-stream and safely rehydrates the active thread context upon approval. Integrated native ASCII graph tree compilation for direct terminal visualization.
* **Core Tools:** LangGraph, LangChain Core Primitives, Tavily Search API Engine, Grandalf Graph Layout, Python.

### 📂 Day 14: Multi-Agent Systems & Role-Driven Assembly Coordination
* **Objective:** Transition from strict, state-centric mathematical graphs into object-oriented, high-autonomy, role-driven multi-agent clusters using collaborative framework primitives.
* **Architecture:** Engineered a 3-agent cooperative execution crew (Technical Researcher, Senior Writer, Chief Editor) operating along a linear sequential task dependency chain to analyze and synthesize complex technical paradigms. Configured distinct, decoupled persona models by defining strict Role, Goal, and Backstory criteria to isolate cognitive scopes and eliminate context-drifting. Implemented automated context hand-offs between separate processing threads, pushing outputs from upstream tasks directly into the context frames of downstream actors. Managed third-party model meta-gateways natively using an explicit abstract LLM connection layer. Integrated programmatic markdown file export to disk boundaries for raw data validation.
* **Core Tools:** CrewAI Core Framework, OpenRouter Meta-Gateway Engine, Dotenv System Environment Isolator, Python.

### 📂 Day 15: Tool Integration & Resilient Hybrid Routing Gateways
* **Objective:** Architect highly stable, framework-free tool integration pipelines capable of processing raw contextual data pools and sync records to external infrastructure safely.
* **Architecture:** Designed and implemented a Hybrid Tool Pipeline that isolates semantic extraction from infrastructure execution boundaries. Engineered native Python tools for inbox ingestion and GitHub issue creation using clean parameter type mapping. Configured a text-based semantic compiler prompt that forces the model to emit predictable plain-text tokens (`TITLE:` / `BODY:`), bypassing fragile multi-turn JSON generation failures. Created a line-by-line string-slicing extraction matrix to catch, sanitize, and unpack parameter inputs cleanly, routing the data safely to local execution gates without parsing crashes.
* **Core Tools:** LangChain Message Primitives, OpenRouter Inference Gateway, Regular Expressions (`re`), Python.

### 📂 Day 16: Advanced Retrieval, Hybrid RAG, & Lexical Re-ranking Engines
* **Objective:** Mitigate the structural limitations of standard vector-similarity retrieval models by engineering a multi-layered, hybrid semantic-lexical search engine for code repositories and dense system documentation.
* **Architecture:** Engineered a stateful multi-stage RAG validation pipeline inside an interactive user runtime interface. Implemented dual-engine tool retrieval consisting of an email parsing node and an automated GitHub tracker integration. Designed a strict regex-driven parameter extraction boundary to safely isolate raw text outputs from underlying model context spaces. Built an explicit search optimization layer using tokenized text normalization rules to prevent literal line-break string parsing failures during JSON de-serialization. Structured conditional routing logic that isolates critical system bugs while filtering out secondary pricing inquiries.
* **Core Tools:** LangChain Core Expression Language (LCEL), OpenRouter API Portals, Python Regular Expression Parsers, Streamlit / Interactive Console UI.

### 📂 Day 17: Fine-Tuning Customization & Sovereign Local Inference
* **Objective:** Establish a robust model selection decision framework and evaluate cloud-based parameter tuning against sovereign, local offline inference models for private deployment.
* **Architecture:** Formulated an architectural evaluation matrix contrasting Prompt Engineering, RAG structures, and Fine-Tuning scopes. Structured a custom training dataset in JSON Lines (`.jsonl`) schema designed to compress style instruction prompt overhead into structural internal weights. Configured an asynchronous OpenAI remote customization pipeline to register file entities and handle automated training triggers. Provisioned an offline enterprise-tier local model inference sandbox via Ollama, mapping out persistent model assets to storage configurations on the `D:` drive array. Programmatically routed native Python orchestration flows to interface directly with local multi-gigabyte models using standard base URL port interception.
* **Core Tools:** OpenAI Fine-Tuning API, Ollama Local Server, LangChain OpenRouter/OpenAI Adapters, Python.

### 📂 Day 18: Guardrails, Input Safety Envelopes, & Hallucination Audits
* **Objective:** Safeguard internal application contexts by engineering proactive input injection interceptors and automated post-generation output grounding verification gates.
* **Architecture:** Formulated an integrated input/output security pipeline acting as an application firewall layer. Designed regex-driven input filtering arrays to block malicious jailbreak and prompt instruction overrides before OpenRouter API submission loops. Implemented an automated text-intersection grounding validator to measure token metrics against source documentation arrays, removing grammar noise via stop-word tokenization filters. Established an automated governance boundary floor that automatically flags and drops any generated responses containing unverified factual hallucinations before delivery to the client.
* **Core Tools:** Python Regular Expression Tooling, Grounding Intersection Verification Matrices, LangChain Message Primitives, OpenRouter Inference Gateway.

### 📂 Day 19: Full-Stack AI Integration, Async Streaming, & JWT Security
* **Objective:** Architect a high-throughput, secure backend server engine paired with a modern reactive frontend interface capable of rendering authenticated token streams over unidirectional text/event-stream communication channels.
* **Architecture:** Formulated an asynchronous ASGI service topology via FastAPI backed by Uvicorn event loops. Engineered an in-memory sliding window queue map to enforce a rolling-window rate-limiting guard (max 5 requests per minute), preventing downstream API key abuse. Integrated a custom JWT user session validation interceptor module compatible with standard query parameter extraction for browser-tab testing fallback streams. Developed a real-time Server-Sent Events (SSE) packet delivery engine using LangChain's non-blocking asynchronous primitives (`astream`), yielding incremental tokens immediately upon generation. Configured a high-fidelity transaction metrics tracker to compute total execution token costs relative to baseline parameter pricing weights. Built an optimized React user interface via Vite, using browser `EventSource` listening streams to handle continuous network packet parsing and seamless string character-by-character appending on a customized dark-mode terminal canvas.
* **Core Tools:** FastAPI, Uvicorn ASGI Server, PyJWT, Vite, React Engine, LangChain Async Streams, OpenRouter Portal Matrix, HTML5 EventSource Browser APIs.

### 📂 Day 20: Persistent Hybrid Storage & In-Memory Cost Caching
* **Objective:** Transition the application from a stateless execution loop into an enterprise-grade persistent engine utilizing unified vector/relational storage and high-speed serverless memory buffers.
* **Architecture:** Integrated Supabase (PostgreSQL) to serve as a unified hybrid database infrastructure. Prepared the schema for upcoming Capstone embedding arrays by configuring the `pgvector` extension alongside a relational logging architecture (`chat_messages`) to permanently track user session histories under explicit user identity parameters. Implemented an exact-match caching pipeline using Redis (via Upstash serverless infrastructure) over a native secure protocol (`rediss://`) to intercept incoming requests before hitting downstream LLM pathways. Engineered a SHA-256 cryptographic hashing module to map raw user string prompts to lightweight cache keys. The asynchronous generator stream now resolves identical questions with sub-millisecond cached responses, reducing public cloud token expenditures to zero. On cache misses, the pipeline streams live data chunks while asynchronously executing dual-write synchronization blocks to update both the Redis time-to-live (TTL) buffer and the remote cloud Postgres relational tables seamlessly upon stream completion. Resolved critical system environmental traps involving PostgREST schema reloads, Windows file-lock cache updates, and path concatenation anomalies.
* **Core Tools:** Supabase, PostgreSQL Client SDK, pgvector Extension, Upstash Serverless Redis, PyJWT Session Interceptors, Cryptographic Hashing (SHA-256), Python Asyncio.

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
