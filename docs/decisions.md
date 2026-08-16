# Architectural Decision Log (ADR)

## ADR 001: Technology Stack Selection
- **Date**: 2026-08-16
- **Status**: Approved
- **Context**: Need a robust, typed, scalable, and maintainable framework for B2B lead discovery, AI agent execution, and audit trail management.
- **Decision**: Python 3.14+ with FastAPI, Pydantic v2, SQLAlchemy (PostgreSQL in production, SQLite for local dev/testing), and standard HTML/CSS + Vanilla JS dashboard for V1.
- **Rationale**:
  - Python provides best-in-class libraries for AI orchestration, HTTP inspection (`httpx`), and schema validation (`pydantic`).
  - FastAPI provides fast, asynchronous API routing with automatic OpenAPI docs.
  - Keeps deployment simple and maintainable without bloated web framework overhead.

---

## ADR 002: Deterministic State Machine Orchestration
- **Date**: 2026-08-16
- **Status**: Approved
- **Context**: Per Master Prompt Rule 1.4, AI agents must not decide system workflow or state transitions.
- **Decision**: Implement a standalone Python Orchestrator using a deterministic finite state machine pattern.
- **Rationale**: Ensures full auditability, reproducibility, and prevents hallucinated state changes or unauthorized automated outreach.

---

## ADR 003: Human-in-the-Loop (HITL) for V1 Outreach
- **Date**: 2026-08-16
- **Status**: Approved
- **Context**: Master Prompt Rule 1.9 prohibits fully automated outbound communication in V1.
- **Decision**: Outreach drafts (Email & WhatsApp) are generated and saved with state `AWAITING_APPROVAL`. Email sending is gated by a manual dashboard trigger. WhatsApp is restricted to manual copy-paste by sales representatives.
- **Rationale**: Protects brand reputation, ensures 100% messaging quality control, and complies with anti-spam / marketing restrictions.

---

## ADR 004: Provider Abstraction & Offline Mocking
- **Date**: 2026-08-16
- **Status**: Approved
- **Context**: System must run tests and execute offline without relying on expensive or brittle external API calls.
- **Decision**: Build abstract base classes (`BasePlacesProvider`, `BaseSearchProvider`, `BaseLLMProvider`, `BaseAuditProvider`) with deterministic mock implementations.
- **Rationale**: Allows instant unit testing, offline development, and provider swapping (e.g. Google Places -> OpenStreetMap or OpenAI -> Gemini) without changing core agent logic.
