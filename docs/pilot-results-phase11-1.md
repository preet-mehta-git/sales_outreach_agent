# Phase 11.1: Pilot Blocking Fixes & Comparison Report

**Campaign ID**: `7f0319ad-60c6-4bae-a5ea-7b17567a77a3`  

**Campaign Name**: `Ahmedabad Pilot Dry Run - 10 Businesses`  

**Execution Mode**: `OUTREACH_MODE=DRY_RUN`  

**Target Location**: Ahmedabad, India | **Batch Size**: 10 Entities

---

## Executive Summary Metrics

- **Priority Leads (>=80)**: 2
- **Qualified Leads (70-79.9)**: 2
- **Potential Review Leads (60-69.9)**: 0
- **Rejected Leads**: 6
- **Verified Persons**: 0
- **Verified Roles**: 0
- **Business Contact Only**: 4
- **Contact Target Not Found**: 6
- **Manual Review Targets**: 0
- **Outreach Ready**: 4
- **Public Demos**: 0
- **Local-Only Demos**: 10
- **Demo Access Failures**: 0

---

## 10-Business Audit Breakdown

| Business | Entity Status | Website Classification | Opp Score | Qualification | Decision Maker | Contact Target Status | Outreach Readiness | Demo Access Status | Action |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Manek Chowk Night Food Market** | `REJECTED` | `NO_WEBSITE` | **86.0** | `REJECTED` | `NOT_FOUND (NOT_FOUND)` | `NOT_FOUND` | `NOT_READY` | `NOT_GENERATED` | `REQUIRES_MANUAL_REVIEW` |
| **Agashiye - House of MG** | `VERIFIED` | `GOOD_WEBSITE` | **55.4** | `REJECTED` | `NOT_FOUND (NOT_FOUND)` | `NOT_FOUND` | `NOT_READY` | `NOT_GENERATED` | `REQUIRES_MANUAL_REVIEW` |
| **Gordhan Thal** | `VERIFIED` | `OUTDATED_WEBSITE` | **74.1** | `QUALIFIED` | `NOT_FOUND (NOT_FOUND)` | `BUSINESS_CONTACT_ONLY` | `READY_FOR_APPROVAL` | `LOCAL_ONLY` | `AWAITING_HUMAN_APPROVAL` |
| **Zen Cafe** | `VERIFIED` | `NO_WEBSITE` | **83.5** | `PRIORITY` | `NOT_FOUND (NOT_FOUND)` | `BUSINESS_CONTACT_ONLY` | `READY_FOR_APPROVAL` | `LOCAL_ONLY` | `AWAITING_HUMAN_APPROVAL` |
| **Lucky Tea Stall** | `VERIFIED` | `NO_WEBSITE` | **84.4** | `PRIORITY` | `NOT_FOUND (NOT_FOUND)` | `BUSINESS_CONTACT_ONLY` | `READY_FOR_APPROVAL` | `LOCAL_ONLY` | `AWAITING_HUMAN_APPROVAL` |
| **Karnavati Dabeli & Vadapav** | `VERIFIED` | `NO_WEBSITE` | **74.7** | `QUALIFIED` | `NOT_FOUND (NOT_FOUND)` | `BUSINESS_CONTACT_ONLY` | `READY_FOR_APPROVAL` | `LOCAL_ONLY` | `AWAITING_HUMAN_APPROVAL` |
| **Havmor Restaurant** | `VERIFIED` | `GOOD_WEBSITE` | **55.0** | `REJECTED` | `NOT_FOUND (NOT_FOUND)` | `NOT_FOUND` | `NOT_READY` | `NOT_GENERATED` | `REQUIRES_MANUAL_REVIEW` |
| **Upper Crust Bakery & Cafe** | `VERIFIED` | `GOOD_WEBSITE` | **55.3** | `REJECTED` | `NOT_FOUND (NOT_FOUND)` | `NOT_FOUND` | `NOT_READY` | `NOT_GENERATED` | `REQUIRES_MANUAL_REVIEW` |
| **Swati Snacks** | `VERIFIED` | `GOOD_WEBSITE` | **56.3** | `REJECTED` | `NOT_FOUND (NOT_FOUND)` | `NOT_FOUND` | `NOT_READY` | `NOT_GENERATED` | `REQUIRES_MANUAL_REVIEW` |
| **Vishalla Village Restaurant** | `VERIFIED` | `GOOD_WEBSITE` | **55.3** | `REJECTED` | `NOT_FOUND (NOT_FOUND)` | `NOT_FOUND` | `NOT_READY` | `NOT_GENERATED` | `REQUIRES_MANUAL_REVIEW` |

---

## Comparative Delta: Phase 11 vs Phase 11.1

| Business | Phase 11 Demo Status | Phase 11.1 Demo Status | Phase 11 Contact Target | Phase 11.1 Contact Target | Phase 11 Outreach Demo Link | Phase 11.1 Outreach Demo Link |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Manek Chowk Night Food Market** | `Public Accessible HTTP` | `NOT_GENERATED` | `NOT_FOUND` | `NOT_FOUND` | `http://localhost:8000/...` | `INCLUDED` |
| **Agashiye - House of MG** | `Public Accessible HTTP` | `NOT_GENERATED` | `NOT_FOUND` | `NOT_FOUND` | `http://localhost:8000/...` | `INCLUDED` |
| **Gordhan Thal** | `Public Accessible HTTP` | `LOCAL_ONLY` | `NOT_FOUND` | `BUSINESS_CONTACT_ONLY` | `http://localhost:8000/...` | `EXCLUDED` |
| **Zen Cafe** | `Public Accessible HTTP` | `LOCAL_ONLY` | `NOT_FOUND` | `BUSINESS_CONTACT_ONLY` | `http://localhost:8000/...` | `EXCLUDED` |
| **Lucky Tea Stall** | `Public Accessible HTTP` | `LOCAL_ONLY` | `NOT_FOUND` | `BUSINESS_CONTACT_ONLY` | `http://localhost:8000/...` | `EXCLUDED` |
| **Karnavati Dabeli & Vadapav** | `Public Accessible HTTP` | `LOCAL_ONLY` | `NOT_FOUND` | `BUSINESS_CONTACT_ONLY` | `http://localhost:8000/...` | `EXCLUDED` |
| **Havmor Restaurant** | `Public Accessible HTTP` | `NOT_GENERATED` | `NOT_FOUND` | `NOT_FOUND` | `http://localhost:8000/...` | `INCLUDED` |
| **Upper Crust Bakery & Cafe** | `Public Accessible HTTP` | `NOT_GENERATED` | `NOT_FOUND` | `NOT_FOUND` | `http://localhost:8000/...` | `INCLUDED` |
| **Swati Snacks** | `Public Accessible HTTP` | `NOT_GENERATED` | `NOT_FOUND` | `NOT_FOUND` | `http://localhost:8000/...` | `INCLUDED` |
| **Vishalla Village Restaurant** | `Public Accessible HTTP` | `NOT_GENERATED` | `NOT_FOUND` | `NOT_FOUND` | `http://localhost:8000/...` | `INCLUDED` |

---

## Corrections

- **Localhost Classification**: Fixed Phase 11 bug where local dev URLs (`http://localhost:8000/...`) were misclassified as `Public Accessible HTTP Server Endpoint`. Local URLs are now strictly classified as `LOCAL_ONLY`.
- **Outreach Link Exclusion**: Prevented local/unverified demo links from leaking into outreach copy sent to prospects.
- **Target Status Separation**: Separated prospect contact channel representation into explicit states (`BUSINESS_CONTACT_ONLY` vs `VERIFIED_PERSON`), preventing false negative outreach blocks when a phone contact route exists.

## Improvements

- **6-Priority Discovery Hierarchy**: Added structured search query generation spanning official site, social, LinkedIn, professional profiles, news, and registries.
- **Automated Verification Guard**: Added HTTP reachability & demo content validation before marking any URL `PUBLIC_ACCESSIBLE`.
- **Dynamic Personalization Rules**: Adjusted outreach template copy to automatically format greetings based on `ContactTargetStatus` (`Hi [First Name]` vs `Hello [Business Name] Team`).

## Remaining Limitations

- **Zero-Fabrication DM Limit**: Traditional local businesses (e.g. street food markets, small dabeli stalls) rarely publish decision-maker executive names on public web directories. Under strict anti-fabrication rules, these correctly resolve to `NOT_FOUND` or `BUSINESS_CONTACT_ONLY`.
- **Public Hosting Dependency**: Without a configured `PUBLIC_DEMO_BASE_URL` pointing to an active cloud edge server (e.g. S3 / Vercel), generated prototype demos remain `LOCAL_ONLY`.
