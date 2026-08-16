# Master Development Roadmap

| Phase | Title | Focus & Core Deliverables | Status |
| :--- | :--- | :--- | :--- |
| **Phase 0** | **Project Inspection & Architecture Blueprint** | Repository inspection, provider ToS evaluation, `docs/` architecture documents, Git init baseline. | **IN PROGRESS** |
| **Phase 1** | **Project Foundation** | Project structure (`app/`), Pydantic models, config manager, database setup, abstract agent framework, test suite. | Pending |
| **Phase 2** | **Data Model & Lead Management** | Database migrations/schemas (`Lead`, `Campaign`, `AuditLog`, `OutreachDraft`), deduplication logic, CRUD APIs. | Pending |
| **Phase 3** | **Discovery Pipeline** | `PlacesProvider`, `SearchProvider`, Discovery Agent, Verification Agent, Ahmedabad restaurant discovery query generator. | Pending |
| **Phase 4** | **Website Detection** | Reachability checker, URL canonicalization, website classification (`NO_WEBSITE`, `WEBSITE_FOUND`, `UNREACHABLE`). | Pending |
| **Phase 5** | **Website Audit Engine** | DOM/Performance auditor, PageSpeed integration, Website Quality Score formula (0-100 breakdown). | Pending |
| **Phase 6** | **Opportunity Scoring** | Opportunity Score engine (Digital Gap, Customer Traction, Commercial Potential, Contactability, Purchase Signals), hard disqualifiers. | Pending |
| **Phase 7** | **Decision Maker Research** | Decision Maker Agent, owner/manager detection, confidence scoring, evidence linkage. | Pending |
| **Phase 8** | **Business Audit Engine** | Business Audit Agent, digital opportunity report, website value proposition synthesis, sales talking points. | Pending |
| **Phase 9** | **Demo Website Generator** | Restaurant/Cafe demo templates (Cafe, Fine Dining, Bakery, Family Dining), static generator, customization engine. | Pending |
| **Phase 10** | **Outreach Drafting & Compliance** | Personalization engine for Email & WhatsApp drafts, compliance checks, dry-run safety lock. | Pending |
| **Phase 11** | **Internal Sales Dashboard** | FastAPI presentation layer, lead management UI, score breakdown visualizer, demo viewer, outreach approval queue. | Pending |
| **Phase 12** | **End-to-End Orchestrated Pipeline** | Deterministic orchestrator linking all agents, state persistence, failure recovery, idempotency verification. | Pending |
| **Phase 13** | **Response Classification** | Response classification agent, reply handling, opt-out suppression updater. | Pending |
| **Phase 14** | **Security, Compliance & Pilot Run** | Security audit, prompt injection verification, pilot testing on 20-50 Ahmedabad businesses, final docs. | Pending |
