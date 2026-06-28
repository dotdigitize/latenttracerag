# LatentTraceRAG

LatentTraceRAG is a local RAG evaluation and diagnostics framework for tracing how retrieval augmented generation systems move from query to evidence to answer. It compares naive retrieval, explicit agentic retrieval, and compact latent trace retrieval, while recording retrieval steps, grounding quality, citation behavior, latency by stage, and failure cases.

## Overview

LatentTraceRAG runs locally with SQLite telemetry and optional Ollama models. If Ollama is unavailable, it falls back to deterministic extractive answers and lexical embeddings so evaluations still run.

## Why LatentTraceRAG Exists

RAG systems often look correct in simple demos but fail under multi step questions, weak citations, redundant retrieval, or latency pressure. This project makes those behaviors observable.

## The Bottleneck in Explicit Agentic RAG

Explicit agentic RAG often spends most of its time generating long thoughts and subqueries. Those tokens are generated sequentially and increase latency. LatentTraceRAG measures that overhead by tracking thought generation, subquery generation, retrieval, answer generation, and total latency.

## Latent Trace Retrieval

Latent Trace Retrieval reduces that overhead by using compact structured retrieval actions in latent trace mode. These actions preserve the retrieval decision path while avoiding unnecessary verbose reasoning text. The system still logs enough information for auditability, but it does not force every retrieval step to be preceded by long natural language reasoning.

  

## What It Measures

- Retrieval hit rate and retrieval success rate
- Source coverage
- Answer overlap score and grounding score
- Citation recall and citation precision
- Missing source count and empty retrieval count
- Unsupported answer flags
- Redundant retrieval rate
- Agentic overhead ratio
- Efficiency adjusted score
- Latency and token estimates by stage

## Architecture

The backend is FastAPI with SQLite tables for documents, chunks, queries, retrieval traces, retrieval steps, answers, evaluation runs, failure cases, latency traces, trajectory metrics, embedding diagnostics, and model run configs. The frontend is React, TypeScript, Vite, and Tailwind CSS 3.

## Modes

Naive RAG retrieves top-k chunks once, generates or extracts a grounded answer, stores a trace, and scores the result.

Explicit Agentic RAG performs iterative retrieval with natural language thoughts and subqueries before answering or reaching the retrieval step limit.

Latent Trace Retrieval performs iterative retrieval through compact JSON-like retrieval actions, converts actions into compact subqueries, retrieves evidence, and logs an optional decoded trace.

## Features

- Local corpus seeding
- Local Ollama integration with safe fallback
- SQLite telemetry
- Stage wise latency profiling
- Evaluation runner and reports
- Failure case categories
- Embedding diagnostics with lexical fallback
- Browser UI for queries, traces, evaluations, and reports

## Data Model

Tables include `documents`, `chunks`, `queries`, `retrieval_traces`, `retrieval_steps`, `answers`, `evaluation_cases`, `evaluation_runs`, `failure_cases`, `latency_traces`, `trajectory_metrics`, `embedding_diagnostics`, and `model_run_configs`.

## Local Models

Default Ollama model names:

```bash
ollama pull gemma4:e4b
ollama pull gemma4:e2b
ollama pull embeddinggemma:latest
```

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
npm install
```

## Linux Setup

```bash
cd ~/ai-portfolio
git clone https://github.com/dotdigitize/latenttracerag.git
cd latenttracerag
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m backend.seed_data
python -m pytest
uvicorn backend.server:app --host 127.0.0.1 --port 8010
npm install
npm run dev
```

## Windows Setup

```powershell
git clone https://github.com/dotdigitize/latenttracerag.git
cd latenttracerag
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m backend.seed_data
python -m pytest
uvicorn backend.server:app --host 127.0.0.1 --port 8010
npm install
npm run dev
```

## Seeding the Corpus

```bash
python -m backend.seed_data
```

## Running the Backend

```bash
uvicorn backend.server:app --host 127.0.0.1 --port 8010
```

## Running the Frontend

```bash
npm run dev
```

## Running Evaluations

Use the UI evaluation runner or call:

```bash
curl -X POST "http://127.0.0.1:8010/api/evals/run?mode=latent_trace"
```

## Understanding Results

Generated results are written to `results/`, including evaluation summaries, failure cases, retrieval trace samples, stage latency reports, agentic overhead reports, trajectory quality reports, and embedding diagnostics.

## Security and Privacy

The project is local first, does not require cloud APIs, and does not expose raw SQL endpoints. Do not expose the backend publicly without authentication and deployment hardening.

## Limitations

## License

Apache License 2.0.

## Attribution

Project: LatentTraceRAG  
Author: Jose Perez  
Repository: https://github.com/dotdigitize/latenttracerag
