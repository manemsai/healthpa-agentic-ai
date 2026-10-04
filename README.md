# HealthPA Agentic AI

Healthcare policy retrieval and agentic AI proof of concept for **grounded coverage and prior-authorization support**.

The repository explores how policy documents can be ingested, indexed, retrieved, and presented as evidence to an AI workflow while keeping final member-specific coverage or authorization decisions outside the model.

> **Project status:** End-to-end local/demo MVP implemented. Policy ingestion, FAISS retrieval, deterministic agent routing/review, FastAPI, policy MCP exposure, Docker packaging, aggregate observability, safety evaluation, integration tests, and CI are implemented. AWS Bedrock/CMS experiments remain available as optional research paths; production payer/member integrations and cloud infrastructure are intentionally out of scope until real authorized services and a deployment target are selected.

## What This Project Demonstrates

- Policy ingestion from public Anthem policy/catalog pages
- Normalization of policy documents into structured records
- Local vector indexing and retrieval with FAISS
- Evidence-oriented policy search through a FastAPI service
- Retrieval filters for payer market and line of business
- Agentic orchestration for policy, member-coverage, provider-cost, reviewer, and human-escalation paths
- Experimental AWS Bedrock generation using Amazon Nova Lite
- Unit, integration, and safety-evaluation tests plus GitHub Actions CI
- MCP exposure for policy retrieval so external agent clients can call the grounded search capability
- Privacy-safe process-local metrics for aggregate route and decision-status monitoring
- Safety-oriented responses that avoid treating public policy evidence as a final member-specific coverage decision

## Architecture

The repository has one primary local/demo architecture under `src/elevance_ai/` plus a retained legacy/experimental CMS RAG track.

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

### 2. Legacy/experimental CMS RAG + Bedrock track

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
tests/integration/          API integration tests
tests/evaluation/           Safety evaluation tests
docker/                     Container packaging
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
- `GET /metrics` — non-sensitive aggregate route/status counters
- `POST /query` — route a policy, coverage, or cost question through the HealthPA agent flow

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

Run the CI test scope locally with:

```bash
PYTHONPATH=. pytest tests/unit tests/evaluation
ruff check src apps scripts tests
```

The suite covers ingestion, retrieval, agent routing/review, API contracts, safety behavior, and observability. GitHub Actions runs the same test/lint quality gate on pushes and pull requests.

## Safety and Scope

This repository is an engineering proof of concept, **not a medical device and not an authorization decision system**.

The implemented workflows intentionally distinguish public policy evidence from member-specific benefits and authorization decisions. Human or authorized plan verification should remain part of any real operational workflow.

## Current Limitations

- This is a local/demo MVP, not a production healthcare authorization system.
- Member eligibility, claims, benefits, provider contracts, and negotiated-rate systems are not connected to real authorized payer services.
- Provider-cost routing therefore escalates rather than inventing a price.
- CMS/Bedrock code under the legacy experimental track is not required by the primary local flow.
- Terraform remains a deployment-target placeholder; no cloud environment is claimed as deployed.
- Metrics are process-local aggregate counters, not a production telemetry backend.
- Production identity/access management, audit retention, PHI controls, secret management, distributed tracing, SLOs, and operational hardening remain deployment work.

## Roadmap

- Add larger retrieval/grounding evaluation datasets using synthetic or public non-PHI fixtures
- Add authenticated payer/member adapters only when authorized services are available
- Add normalized machine-readable pricing ingestion for provider-cost questions
- Add production telemetry/tracing and audit controls for a selected deployment environment
- Finalize Terraform only after choosing the actual AWS runtime and security boundary
- Add a recorded/demo walkthrough using non-sensitive sample data

## Author

**Mohana Sai Manem**

Focused on Generative AI, Agentic AI, RAG, machine learning, and cloud AI engineering.
