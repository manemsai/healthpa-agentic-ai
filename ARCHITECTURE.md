# HealthPA Agentic AI — Architecture

## Status

This repository is an active proof of concept. It currently contains a primary policy-search implementation and an experimental agentic CMS RAG workflow. They should not yet be treated as one production architecture.

## Primary Policy Search Flow

1. **Ingestion** — public Anthem policy/catalog pages are collected and normalized into structured policy documents.
2. **Chunking and indexing** — normalized documents are chunked, embedded locally, and stored in a FAISS index.
3. **Retrieval** — `PolicySearchTool` searches the local index and can filter evidence by market and line of business.
4. **API** — FastAPI exposes health and policy-query endpoints.
5. **Decision boundary** — retrieved public evidence is returned with explicit warnings that member-specific coverage and prior authorization require plan or authorized verification.

## Experimental Agentic RAG Flow

The prototype under `src/graph/` uses LangGraph nodes for:

- intent routing
- retrieval
- evidence-sufficiency checks
- answer generation
- grounding checks
- review decisions
- human-review escalation
- final response handling

The associated experimental RAG implementation uses a local FAISS store and an AWS Bedrock client configured for Amazon Nova Lite.

## Safety Design

The prototype is intentionally conservative. Low retrieval confidence, low grounding scores, payer-specific authorization questions, or insufficient evidence can route to human review instead of producing a definitive coverage determination.

## Known Architecture Work

- Consolidate duplicate/legacy package paths.
- Connect the primary policy-search package to the agentic orchestration path.
- Complete evaluation and integration suites.
- Implement deployment packaging and infrastructure only after the runtime target is selected.
- Add production authentication, authorization, audit logging, observability, and secret-management patterns.
