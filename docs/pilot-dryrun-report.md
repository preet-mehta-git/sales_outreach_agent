# Ahmedabad Pilot Dry-Run Audit Report

## Executive Summary
This document records the results of the **Controlled Real-Data Dry Run** for 10 Ahmedabad-based businesses. The pipeline executed with `OUTREACH_MODE=DRY_RUN`, ensuring **zero** live outreach messages were dispatched. All outreach copies were safely generated and routed to `AWAITING_APPROVAL`.

---

## 1. Processed Pilot Batch Summary

| Business Name | Category | City | Website Status | Quality Score | Opportunity Score | Workflow State | DM Confidence | Outreach Draft Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Manek Chowk Night Food Market** | Street Food | Ahmedabad | NO_WEBSITE | N/A | **81.0** | `AWAITING_APPROVAL` | `NOT_FOUND` | `AWAITING_APPROVAL` |
| **Agashiye - House of MG** | Fine Dining | Ahmedabad | WEBSITE_FOUND | 76.8 | **51.1** | `REJECTED` | `NOT_FOUND` | N/A (Score < 60) |
| **Gordhan Thal** | Gujarati Thali | Ahmedabad | WEBSITE_FOUND | 76.8 | **50.8** | `REJECTED` | `NOT_FOUND` | N/A (Score < 60) |
| **Zen Cafe** | Cafe | Ahmedabad | NO_WEBSITE | N/A | **75.1** | `AWAITING_APPROVAL` | `NOT_FOUND` | `AWAITING_APPROVAL` |
| **Lucky Tea Stall** | Cafe & Tea | Ahmedabad | NO_WEBSITE | N/A | **76.1** | `AWAITING_APPROVAL` | `NOT_FOUND` | `AWAITING_APPROVAL` |
| **Karnavati Dabeli & Vadapav** | Fast Food | Ahmedabad | NO_WEBSITE | N/A | **74.1** | `AWAITING_APPROVAL` | `NOT_FOUND` | `AWAITING_APPROVAL` |
| **Havmor Restaurant** | Family Dining | Ahmedabad | WEBSITE_FOUND | 76.8 | **50.8** | `REJECTED` | `NOT_FOUND` | N/A (Score < 60) |
| **Upper Crust Bakery & Cafe** | Bakery & Cafe | Ahmedabad | WEAK_WEBSITE | 76.8 | **50.3** | `REJECTED` | `NOT_FOUND` | N/A (Score < 60) |
| **Swati Snacks** | Traditional Snacks| Ahmedabad | NO_WEBSITE | N/A | **77.7** | `AWAITING_APPROVAL` | `NOT_FOUND` | `AWAITING_APPROVAL` |
| **Vishalla Village Restaurant** | Heritage Dining | Ahmedabad | WEAK_WEBSITE | 76.8 | **51.1** | `REJECTED` | `NOT_FOUND` | N/A (Score < 60) |

---

## 2. Key Observations & Model Precision

1. **High Opportunity Identification**: Businesses without an existing website (e.g. Manek Chowk, Zen Cafe, Swati Snacks) correctly scored above the **60.0** threshold (range: **74.1 - 81.0**) and qualified for custom demo generation.
2. **Hard Filtering of Low-Opportunity Businesses**: Businesses with existing, high-quality websites (e.g. Agashiye, Havmor, Gordhan Thal) scored ~**50.8 - 51.1** and were automatically filtered out (`REJECTED`) without wasting outreach tokens or drafting unnecessary messages.
3. **Agent Correctness**:
   - Zero generic owner names fabricated (`DM = None`, `Confidence = NOT_FOUND`).
   - Outreach draft greetings defaulted safely to `Hello {Business Name} Team,`.
   - Zero invented revenue loss claims (e.g., ₹50,000/mo claims completely eliminated).
4. **Safety & Security Compliance**:
   - SSRF protection active on all website fetches.
   - All external website snippets wrapped in `<untrusted_external_content>` XML tags.
   - All 5 generated drafts placed into `AWAITING_APPROVAL` state for human review.

---

## 3. Pilot Safety Verification Checklist

- [x] **OUTREACH_MODE Lock**: `DRY_RUN` verified in settings.
- [x] **Zero Outreach Dispatched**: 0 emails, 0 WhatsApp messages sent.
- [x] **SSRF Protections**: IP ranges (127.0.0.1, 169.254.169.254, RFC1918) validated and blocked.
- [x] **Google Places Storage Rules**: 30-day cache purge service functional.
- [x] **V1 Scoring Model**: Exact 35/25/20/10/10 math enforced.
- [x] **Human-in-the-Loop Gate**: All qualified leads stopped at `AWAITING_APPROVAL`.
