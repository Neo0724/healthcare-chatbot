# Ontology-Grounded Healthcare Chatbot & Diagnostic System

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Neo4j](https://img.shields.io/badge/Neo4j-Graph_Database-008CC1?style=flat&logo=neo4j&logoColor=white)](https://neo4j.com)
[![Flutter](https://img.shields.io/badge/Flutter-Cross--Platform-02569B?style=flat&logo=flutter&logoColor=white)](https://flutter.dev)
[![SNOMED CT](https://img.shields.io/badge/Ontology-SNOMED--CT-blue?style=flat)](https://www.snomed.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An intelligent clinical inquiry and preliminary diagnosis assistant designed to eliminate large language model (LLM) hallucinations through ontology-anchored knowledge grounding. By implementing **Graph-Augmented Retrieval (GraphRAG)** with a structured **SNOMED-CT** graph and chunked medical truths, the system provides traceable, factually grounded health guidance through a cross-platform mobile chatbot interface.

---

## 🌟 Key Features

### 1. GraphRAG Retrieval Architecture

- **Ontology Anchoring:** Implemented a Neo4j knowledge graph grounded in SNOMED-CT ontologies to link formal clinical entities with lay terminology, enforcing semantic consistency and preventing inaccurate relationship formation across chunked medical documents.
- **Literature Grounding:** Ingests external, verified medical documents preprocessed and chunked into contextual units, linked directly to relevant SNOMED-CT concept nodes.
- **Hallucination Mitigation:** Ensures generation is strictly bounded to verified medical information, enabling verifiable references.

### 2. Conversational Mobile Application

- **Cross-Platform Client:** Developed with **Flutter** for seamless execution across iOS and Android.
- **Authentication & Security:** Secure token-based session handling via **JWT (JSON Web Tokens)**.
- **Conversation Lifecycle:** Complete state persistence allowing users to create new conversation, review past conversation histories, and delete past conversations.
- **Responsive RESTful Backend:** Powered by **Flask** server routing queries between graph traversal pipelines and LLM inference endpoints.
- **Real-Time Token Streaming:** Delivers live, progressive response rendering via WebSocket streaming

---

## 🏗️ System Architecture

```text
  +-------------------------------------------------------------+
  |                   Flutter Mobile Client                     |
  |  - JWT Authentication    - History Management               |
  +------------------------------+------------------------------+
                                 | REST API / JSON / WebSocket
                                 v
  +----------------------------------------------------------------------+
  |                     Flask Backend API                                |
  |  - Auth & Query Router   - RAG Orchestrator  - LLM Message Streaming |
  +------------------------------+---------------------------------------+
                                 |
         +-----------------------+-----------------------+
         |                                               |
         v                                               v
+-------------------------------+               +-------------------------------+
|     Neo4j Knowledge Graph     |               |         Medical Document      |
| - SNOMED-CT Concept Hierarchy | <--- Linked - | - Preprocessed & Chunked      |
|                               |               |   Literature                  |
+-------------------------------+               +-------------------------------+
                                 \             /
                                  \           /
                                   v         v
                      +----------------------------------------+
                      |       LLM Generation                   |
                      |   Grounding & PreliminaryDiagnostics   |
                      +----------------------------------------+
```

---

## 🛠️ Tech Stack

- **Frontend:** Flutter
- **Backend:** Flask
- **Knowledge Graph:** Neo4j
- **Database:** MongoDB
- **Medical Terminology:** SNOMED-CT
- **Information Retrieval:** GraphRAG and Cosine Similarity
- **Evaluation Frameworks:** DeepEval

---

## 📊 Evaluation & Benchmarks

The diagnostic and retrieval pipeline was evaluated using **DeepEval** against clinical test cases to measure faithfulness, retrieval accuracy, and disease retrieval given symptoms rankings.

| Metric                |   Score    | Description                                                                                               |
| :-------------------- | :--------: | :-------------------------------------------------------------------------------------------------------- |
| **Contextual Recall** | **93.00%** | Completeness of retrieving the required medical contexts to answer user's query                           |
| **Faithfulness**      | **78.00%** | Factual consistency of generated responses grounded against retrieved context.                            |
| **Answer Relevancy**  | **78.00%** | Direct alignment between the diagnostic inquiry and the synthesized clinical guidance.                    |
| **Disease Hit@5**     | **73.33%** | Probability that the correct target condition appears within the top 5 suggested differential diagnoses.  |
| **Disease Hit@10**    | **70.00%** | Probability that the correct target condition appears within the top 10 suggested differential diagnoses. |
