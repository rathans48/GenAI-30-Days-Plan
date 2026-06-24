# 🚀 Day 07 Mini-Project: Advanced PDF & Text Q&A RAG Dashboard

An interactive, web-based Retrieval-Augmented Generation (RAG) dashboard that allows users to seamlessly ingest custom text files or multi-page PDF documents, automatically slice text layers into semantic embeddings, index coordinates using local ChromaDB storage, and stream fact-grounded responses back to the UI interface.

---

## 📸 System Interface Walkthrough

### 1. Unified Streamlit Navigation Hub
The main application control panel features a sidebar interface allowing users to dynamically select their text ingestion methodology.

![Streamlit Dashboard Navigation Layout](Doc%QA%Dashboard.png)

### 2. Scenario A: Custom Text Ingestion Matrix
Users can choose between processing default sample policies, copy-pasting raw text data fields directly into an expandable canvas workspace, or uploading standalone plain text files (`.txt`).

![Text Ingestion Interface UI](Doc%QA%Custom%Ingestion.png)

### 3. Scenario B: High-Fidelity PDF Coordinate Indexing
The system reads character layer strings directly from arbitrary multi-page documents, generates 384-dimensional dense vectors using a local ONNX runtime engine, and runs spatial Euclidean calculations to return context-constrained answers.

![PDF Analysis Execution View](PDF%QA%Query%1.2.png)

### Additional Images
Following are some additional images of the same.

![Custom Query 1.1](Doc%20QA%20Custom%20Query%201.1.png)

![Custom Query 1.2](Doc%20QA%20Custom%20Query%201.2.png)

![QA Query 1](Doc%20QA%20Query%201.png)

![QA Query 2](Doc%20QA%20Query%202.png)

![Dashboard View](PDF%20QA%20Dashboard.png)

![PDF Query 1.1](PDF%20QA%20Query%201.1.png)
