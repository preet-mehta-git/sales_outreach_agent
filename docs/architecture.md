# High-Level Architecture & System Blueprint

## 1. System Vision & Scope
The **AI Restaurant & Cafe Prospecting Engine** is an enterprise-ready, modular system designed to discover, evaluate, score, audit, demo, and prepare personalized outreach for web development prospects in Ahmedabad, India.

---

## 2. Core Architectural Layers

```
                     +---------------------------------------+
                     |         Presentation Layer            |
                     |  (Internal Sales & Campaign Dashboard)|
                     +---------------------------------------+
                                         |
                                         v
                     +---------------------------------------+
                     |       REST API / FastAPI Layer        |
                     +---------------------------------------+
                                         |
                                         v
                     +---------------------------------------+
                     |       Deterministic Orchestrator      |
                     |   (State Machine & Workflow Engine)   |
                     +---------------------------------------+
                                         |
        +--------------------------------+--------------------------------+
        |                                |                                |
        v                                v                                v
+-------------------+        +-----------------------+        +-----------------------+
|  Agent Layer      |        |  Provider Adapters    |        |  Service Layer        |
|  - Discovery      |        |  - Google Places API  |        |  - HTTP / DOM Fetcher |
|  - Verification   |        |  - Search APIs        |        |  - Audit Calculator   |
|  - Website Detect |        |  - PageSpeed API      |        |  - Template Renderer  |
|  - Website Audit  |        |  - LLM Adapters       |        |  - Compliance Check   |
|  - Opp Scoring    |        |  - Email/WhatsApp     |        |  - Suppression Engine |
|  - Decision Maker |        +-----------------------+        +-----------------------+
|  - Business Audit |                                                     |
|  - Demo Generator |                                                     v
|  - Outreach Agent |                                        +----------------------------+
|  - Response Class |                                        |  PostgreSQL / SQLite Database|
+-------------------+                                        |  & Immutable Audit Log     |
                                                             +----------------------------+
```

---

## 3. Workflow State Machine

Every lead transitions through an explicit state machine managed solely by the **Deterministic Orchestrator**. Agents **never** modify workflow state independently.

```
DISCOVERED
    │
    ▼
VERIFIED ──────► REJECTED (e.g. permanently closed / wrong category)
    │
    ▼
WEBSITE_ANALYZED (Classified: NO_WEBSITE | WEBSITE_FOUND | WEBSITE_UNREACHABLE)
    │
    ▼
SCORED ─────────► REJECTED (Opportunity Score < 70)
    │
    ▼
DECISION_MAKER_RESEARCHED
    │
    ▼
BUSINESS_AUDITED
    │
    ▼
DEMO_GENERATED
    │
    ▼
OUTREACH_DRAFTED
    │
    ▼
AWAITING_APPROVAL (Human Review via Dashboard)
    ├──► APPROVED (Email Dispatched via dry-run/provider API)
    └──► REJECTED / EDITED
```

---

## 4. Agent Architecture Principles

### 4.1 Strict Schema Boundaries
All agent inputs and outputs must be strongly typed using `pydantic` schemas.
- `input_schema`: Context payload passed from Orchestrator.
- `output_schema`: Structured result with `confidence` score (0.0 to 1.0) and `provenance` metadata.

### 4.2 Prompt Injection Defense (External Data Isolation)
Because the system fetches external website text, meta tags, and public profiles, external content must be treated as **UNTRUSTED USER INPUT**.
- All external HTML/text passed into LLM prompts is sanitized and wrapped inside strict XML data blocks (`<untrusted_external_content>...</untrusted_external_content>`).
- Prompts explicitly instruct LLMs to treat contents inside these blocks purely as data and ignore any embedded instructions.

### 4.3 Evidence-Based Reasoning
AI agents cannot generate free-form qualitative claims without referencing specific data fields (e.g., "Review count: 1,200", "Meta viewport tag missing", "Last Google post: 2 weeks ago").

---

## 5. Security & Compliance Safeguards
1. **DRY_RUN Default**: Environment setting `OUTREACH_MODE=DRY_RUN` enforces that outreach generation outputs drafts for human review. Real email dispatching requires explicit admin approval.
2. **WhatsApp Restrictions**: No automated WhatsApp dispatch in V1. WhatsApp messages are generated as copyable drafts.
3. **Suppression List**: Any contact marked `DO_NOT_CONTACT` halts all pipeline execution for that business.
