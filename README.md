# HealthPA Agentic AI

Healthcare policy retrieval and agentic AI proof of concept for **grounded coverage and prior-authorization support**.

The repository explores how policy documents can be ingested, indexed, retrieved, and presented as evidence to an AI workflow while keeping final member-specific coverage or authorization decisions outside the model.

> **Project status:** Active proof of concept. Policy ingestion, local FAISS retrieval, API contracts, and unit tests are implemented. Agentic orchestration, evaluation, infrastructure, and deployment areas are still experimental or scaffolded.

## What This Project Demonstrates

- Policy ingestion from public Anthem policy/catalog pages
- Normalization of policy documents into structured records
- Local vector indexing and retrieval with FAISS
- Evidence-oriented policy search through a FastAPI service
- Retrieval filters for payer market and line of business
- Experimental LangGraph workflow for routing, retrieval, grounding, confidence checks, and human-review escalation
- Experimental AWS Bedrock generation using Amazon Nova Lite
- Unit tests for ingestion, policy retrieval, RAG behavior, and API response contracts
- Safety-oriented responses that avoid treating public policy evidence as a final member-specific coverage decision

## Architecture

The repository currently contains two related implementation tracks.

### 1. Policy Search API — primary implementation

```text
Public policy pages
      |
      v
Policy ingestion
      |
      v
Normalized JSONL
      |
      v
Chunking + local embeddings
      |
      v
FAISS policy index
      |
      v
PolicySearchTool
      |
      v
FastAPI /query endpoint
      |
      v
Evidence + verification guidance
```

The primary package lives under `src/elevance_ai/`, with the API entrypoint in `apps/api/main.py`.

### 2. Agentic CMS RAG prototype — experimental

```text
User question
    |
    v
Intent router
    |
    v
Policy retrieval + reranking
    |
    v
Evidence sufficiency check
    |
    +---- insufficient ----> Human review
    |
    v
Bedrock generation
    |
    v
Grounding check
    |
    +---- low confidence ---> Human review
    |
    v
Final response
```

The experimental graph/RAG implementation is under `src/graph/`, `src/rag/`, and `src/llm/`.

## Technology Stack

- **Language:** Python 3.12+
- **API:** FastAPI, Pydantic
- **Agent orchestration:** LangGraph
- **LLM integration:** AWS Bedrock / Amazon Nova Lite
- **Retrieval:** FAISS
- **Data:** Pandas, PyArrow, DuckDB
- **Web ingestion:** HTTPX, BeautifulSoup, lxml
- **Testing:** pytest, pytest-asyncio
- **Quality tooling:** Ruff, mypy
- **Package management/build:** uv / pyproject.toml

## Repository Structure

```text
apps/api/                  FastAPI service
src/elevance_ai/           Primary policy-search package
src/graph/                 Experimental LangGraph workflow
src/rag/                   Experimental CMS RAG components
src/llm/                   Experimental Bedrock client
scripts/                    Ingestion, indexing, and evaluation entrypoints
tests/unit/                 Unit tests
tests/integration/          Integration-test scaffold
tests/evaluation/           Evaluation scaffold
docker/                     Deployment scaffold
infra/terraform/            Infrastructure scaffold
data/                       Local/generated data locations
```

## Getting Started

### Prerequisites

- Python 3.12+
- A virtual environment or `uv`
- AWS credentials only if you run the Bedrock-based experimental workflow

### Install

Using `uv`:

```bash
uv sync
```

Or install the package with your preferred Python environment from `pyproject.toml`.

### Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

All application environment variables use the `ELEVANCE_` prefix.

### Ingest Policy Documents

```bash
python scripts/ingest_policies.py --limit 25
```

The ingestion script reads configured public policy/catalog pages and writes normalized policy documents to the configured JSONL path.

### Build the Local FAISS Index

```bash
python scripts/build_index.py
```

### Run the API

```bash
uvicorn apps.api.main:app --reload
```

Available endpoints include:

- `GET /health` — service/configuration health information
- `POST /query` — retrieve policy evidence for a question

Example request:

```json
{
  "question": "Is prior authorization required for this procedure?",
  "market": "IN",
  "line_of_business": "COMMERCIAL",
  "top_k": 5
}
```

The API returns retrieved evidence plus guidance that plan/member-specific verification is required rather than claiming an authorization approval or denial.

## Testing

Run the unit tests with:

```bash
pytest tests/unit
```

The current test suite includes coverage for policy ingestion, retrieval tooling, RAG behavior, and API response contracts.

## Safety and Scope

This repository is an engineering proof of concept, **not a medical device and not an authorization decision system**.

The implemented workflows intentionally distinguish public policy evidence from member-specific benefits and authorization decisions. Human or authorized plan verification should remain part of any real operational workflow.

## Current Limitations

- Docker configuration is currently scaffolded rather than deployment-ready.
- Terraform infrastructure is currently scaffolded.
- Evaluation tooling is not yet complete.
- Integration/evaluation test suites require further implementation.
- The experimental CMS RAG/LangGraph code and the newer policy-search package have not yet been consolidated into one architecture.
- Production authentication, authorization, audit controls, observability, and deployment hardening are outside the current proof-of-concept scope.

## Roadmap

- Consolidate the policy API and agentic workflow into one package structure
- Expand automated evaluation and integration testing
- Add measurable retrieval and grounding evaluation
- Add Docker packaging and deployment configuration
- Add infrastructure-as-code when the deployment target is finalized
- Add observability and audit-friendly tracing
- Document an end-to-end demo with sample, non-sensitive data

## Author

**Mohana Sai Manem**

Focused on Generative AI, Agentic AI, RAG, machine learning, and cloud AI engineering.
