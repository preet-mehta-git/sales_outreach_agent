# Phase 11.2: Public Demo Infrastructure & Pilot Consistency Report

**Campaign ID**: `f920390e-9933-415f-a522-eaf9791ae372`  

**Campaign Name**: `Ahmedabad Pilot Dry Run - 10 Businesses`  

**Execution Mode**: `OUTREACH_MODE=DRY_RUN`  

**Target Location**: Ahmedabad, India | **Batch Size**: 10 Entities

---

## Executive Summary Metrics

### 1. Qualification Tiers
- **Priority Leads (>=80)**: 2
- **Qualified Leads (70-79.9)**: 2
- **Potential Review Leads (60-69.9)**: 0
- **Rejected Leads**: 6

### 2. Manual Review Requirements
- **No Review Required**: 10
- **Review Recommended**: 0
- **Review Required**: 0

### 3. Contact Target Status
- **Verified Persons**: 0
- **Verified Roles**: 0
- **Business Contact Only**: 4
- **Contact Target Not Found**: 6
- **Manual Review Targets**: 0

### 4. Outreach Readiness & Demos
- **Outreach Ready (Awaiting Approval)**: 4
- **Outreach Manual Review**: 6
- **Public Demos**: 0
- **Local-Only Demos**: 10
- **Demo Access Failures**: 0

### 5. Final Action Semantics
- **Awaiting Human Outreach Approval**: 4
- **Requires Manual Review**: 0
- **Review Recommended**: 0
- **Rejected**: 6
- **Qualified Not Ready**: 0

---

## 10-Business Audit Breakdown

| Business | Opp Score | Qualification | Manual Review Status | Contact Target Status | Outreach Readiness | Demo Readiness | Action |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Manek Chowk Night Food Market** | **86.0** | `REJECTED` | `NO_REVIEW_REQUIRED` | `NOT_FOUND` | `NOT_READY` | `NOT_GENERATED` | `REJECTED` |
| **Agashiye - House of MG** | **55.4** | `REJECTED` | `NO_REVIEW_REQUIRED` | `NOT_FOUND` | `NOT_READY` | `NOT_GENERATED` | `REJECTED` |
| **Gordhan Thal** | **74.1** | `QUALIFIED` | `NO_REVIEW_REQUIRED` | `BUSINESS_CONTACT_ONLY` | `READY_FOR_APPROVAL` | `LOCAL_ONLY` | `AWAITING_HUMAN_OUTREACH_APPROVAL` |
| **Zen Cafe** | **83.5** | `PRIORITY` | `NO_REVIEW_REQUIRED` | `BUSINESS_CONTACT_ONLY` | `READY_FOR_APPROVAL` | `LOCAL_ONLY` | `AWAITING_HUMAN_OUTREACH_APPROVAL` |
| **Lucky Tea Stall** | **84.4** | `PRIORITY` | `NO_REVIEW_REQUIRED` | `BUSINESS_CONTACT_ONLY` | `READY_FOR_APPROVAL` | `LOCAL_ONLY` | `AWAITING_HUMAN_OUTREACH_APPROVAL` |
| **Karnavati Dabeli & Vadapav** | **74.7** | `QUALIFIED` | `NO_REVIEW_REQUIRED` | `BUSINESS_CONTACT_ONLY` | `READY_FOR_APPROVAL` | `LOCAL_ONLY` | `AWAITING_HUMAN_OUTREACH_APPROVAL` |
| **Havmor Restaurant** | **55.0** | `REJECTED` | `NO_REVIEW_REQUIRED` | `NOT_FOUND` | `NOT_READY` | `NOT_GENERATED` | `REJECTED` |
| **Upper Crust Bakery & Cafe** | **55.3** | `REJECTED` | `NO_REVIEW_REQUIRED` | `NOT_FOUND` | `NOT_READY` | `NOT_GENERATED` | `REJECTED` |
| **Swati Snacks** | **56.3** | `REJECTED` | `NO_REVIEW_REQUIRED` | `NOT_FOUND` | `NOT_READY` | `NOT_GENERATED` | `REJECTED` |
| **Vishalla Village Restaurant** | **55.3** | `REJECTED` | `NO_REVIEW_REQUIRED` | `NOT_FOUND` | `NOT_READY` | `NOT_GENERATED` | `REJECTED` |

---

## Score Breakdown & Transparent Components

| Business | Digital Gap (35%) | Traction (25%) | Commercial (20%) | Contactability (10%) | Signals (10%) | Total |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Manek Chowk Night Food Market** | 35.0/35.0 | 25.0/25.0 | 16.0/20.0 | 5.0/10.0 | 5.0/10.0 | **86.0/100.0** |
| **Agashiye - House of MG** | 6.4/35.0 | 25.0/25.0 | 14.0/20.0 | 5.0/10.0 | 5.0/10.0 | **55.4/100.0** |
| **Gordhan Thal** | 23.1/35.0 | 25.0/25.0 | 16.0/20.0 | 5.0/10.0 | 5.0/10.0 | **74.1/100.0** |
| **Zen Cafe** | 35.0/35.0 | 22.5/25.0 | 16.0/20.0 | 5.0/10.0 | 5.0/10.0 | **83.5/100.0** |
| **Lucky Tea Stall** | 35.0/35.0 | 23.4/25.0 | 16.0/20.0 | 5.0/10.0 | 5.0/10.0 | **84.4/100.0** |
| **Karnavati Dabeli & Vadapav** | 35.0/35.0 | 21.7/25.0 | 13.0/20.0 | 5.0/10.0 | 0.0/10.0 | **74.7/100.0** |
| **Havmor Restaurant** | 7.3/35.0 | 23.7/25.0 | 14.0/20.0 | 5.0/10.0 | 5.0/10.0 | **55.0/100.0** |
| **Upper Crust Bakery & Cafe** | 7.3/35.0 | 24.0/25.0 | 14.0/20.0 | 5.0/10.0 | 5.0/10.0 | **55.3/100.0** |
| **Swati Snacks** | 7.3/35.0 | 25.0/25.0 | 14.0/20.0 | 5.0/10.0 | 5.0/10.0 | **56.3/100.0** |
| **Vishalla Village Restaurant** | 7.3/35.0 | 24.0/25.0 | 14.0/20.0 | 5.0/10.0 | 5.0/10.0 | **55.3/100.0** |

---

## Verification & Operational Consistency

- **Manual Review Truthfulness**: Discrepancy between aggregate counts and individual records resolved. Aggregate report now explicitly tracks `NO_REVIEW_REQUIRED`, `REVIEW_RECOMMENDED`, and `REVIEW_REQUIRED`.
- **Final Action Semantics**: Resolved contradiction between `NO_REVIEW_REQUIRED` and `REQUIRES_MANUAL_REVIEW`. Actions are strictly separated between `AWAITING_HUMAN_OUTREACH_APPROVAL`, `REQUIRES_MANUAL_REVIEW`, `REVIEW_RECOMMENDED`, `REJECTED`, and `QUALIFIED_NOT_READY`.
- **Scoring Formula Frozen**: V1 35/25/20/10/10 formula verified and frozen. Raw scores, weights, contributions, and evidence are deterministically calculated and logged.
- **Public Demo Security & Gating**: `PUBLIC_DEMO_BASE_URL` infrastructure active. Demos pass 6 automated verification guards before reaching `PUBLIC_ACCESSIBLE` status. Unverified or local demo URLs are strictly gated from prospect outreach drafts.
