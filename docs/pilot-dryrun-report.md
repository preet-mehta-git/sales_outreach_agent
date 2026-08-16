# Ahmedabad Pilot Dry-Run Audit Report

## Executive Summary
This document records the results of the **Controlled Real-Data Dry Run** for 10 Ahmedabad-based businesses. The pipeline executed with `OUTREACH_MODE=DRY_RUN`, ensuring **zero** live outreach messages were dispatched. All outreach copies were safely generated and routed to `AWAITING_APPROVAL`.

---

## 1. Processed Pilot Batch Summary & V1 Classification

| Business Name | Category | City | Website Status | Quality Score | Opportunity Score | Qualification Classification | Workflow State | Outreach Draft Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Manek Chowk Night Food Market** | Street Food | Ahmedabad | NO_WEBSITE | N/A | **81.0** | **PRIORITY** | `AWAITING_APPROVAL` | `AWAITING_APPROVAL` |
| **Agashiye - House of MG** | Fine Dining | Ahmedabad | WEBSITE_FOUND | 76.8 | **51.1** | **REJECTED** | `REJECTED` | N/A (Score < 70) |
| **Gordhan Thal** | Gujarati Thali | Ahmedabad | WEBSITE_FOUND | 76.8 | **50.8** | **REJECTED** | `REJECTED` | N/A (Score < 70) |
| **Zen Cafe** | Cafe | Ahmedabad | NO_WEBSITE | N/A | **75.1** | **QUALIFIED** | `AWAITING_APPROVAL` | `AWAITING_APPROVAL` |
| **Lucky Tea Stall** | Cafe & Tea | Ahmedabad | NO_WEBSITE | N/A | **76.1** | **QUALIFIED** | `AWAITING_APPROVAL` | `AWAITING_APPROVAL` |
| **Karnavati Dabeli & Vadapav** | Fast Food | Ahmedabad | NO_WEBSITE | N/A | **74.1** | **QUALIFIED** | `AWAITING_APPROVAL` | `AWAITING_APPROVAL` |
| **Havmor Restaurant** | Family Dining | Ahmedabad | WEBSITE_FOUND | 76.8 | **50.8** | **REJECTED** | `REJECTED` | N/A (Score < 70) |
| **Upper Crust Bakery & Cafe** | Bakery & Cafe | Ahmedabad | WEAK_WEBSITE | 76.8 | **50.3** | **REJECTED** | `REJECTED` | N/A (Score < 70) |
| **Swati Snacks** | Traditional Snacks| Ahmedabad | NO_WEBSITE | N/A | **77.7** | **QUALIFIED** | `AWAITING_APPROVAL` | `AWAITING_APPROVAL` |
| **Vishalla Village Restaurant** | Heritage Dining | Ahmedabad | WEAK_WEBSITE | 76.8 | **51.1** | **REJECTED** | `REJECTED` | N/A (Score < 70) |

---

## 2. Key Observations & Threshold Precision

1. **V1 Qualification Classification Rules**:
   - **PRIORITY (Score ≥ 80.0)**: Manek Chowk (81.0). High priority lead advanced to demo generation & outreach drafting.
   - **QUALIFIED (70.0 - 79.9)**: Zen Cafe (75.1), Lucky Tea Stall (76.1), Karnavati Dabeli (74.1), Swati Snacks (77.7). Standard qualified leads.
   - **POTENTIAL / REVIEW (60.0 - 69.9)**: Borderline leads reserved for manual review (none in this sample batch).
   - **REJECTED (< 60.0)**: Agashiye, Gordhan Thal, Havmor, Upper Crust, Vishalla. Disqualified from outreach pipeline.

2. **Agent Correctness**:
   - Zero generic owner names fabricated (`DM = None`, `Confidence = NOT_FOUND`).
   - Outreach draft greetings defaulted safely to `Hello {Business Name} Team,`.
   - Zero invented revenue loss claims.

3. **Safety & Compliance Verification**:
   - SSRF protection active on all website fetches.
   - External website content isolated using XML tags (`<untrusted_external_content>`).
   - All 5 generated drafts placed into `AWAITING_APPROVAL` state for human review.
   - Google Places 30-day storage compliance purge verified (Place IDs retained, raw Places attributes purged after 30 days).
