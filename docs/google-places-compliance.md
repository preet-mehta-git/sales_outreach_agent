# Google Places API Storage Compliance Audit & Retention Policy

## Executive Summary
This document defines the strict field-by-field compliance rules for storing Google Places API Content in accordance with Section 3.2.3 of the **Google Maps Platform Terms of Service**.

---

## 1. Field-by-Field Compliance Matrix

| Field Name | Source | Storage Permission | Max Retention Period | Compliance Requirement / Action on Expiry |
| :--- | :--- | :--- | :--- | :--- |
| `place_id` | Google Places API | **PERMANENT** | Indefinite | **Allowed**. Retained indefinitely to reference Google Places API endpoints. |
| `name` | Google Places API | Temporary Cache | 30 Calendar Days | Must be purged or refreshed via Places API after 30 days. |
| `address` | Google Places API | Temporary Cache | 30 Calendar Days | Must be purged or refreshed via Places API after 30 days. |
| `phone` | Google Places API | Temporary Cache | 30 Calendar Days | Must be purged or refreshed via Places API after 30 days. |
| `rating` | Google Places API | Temporary Cache | 30 Calendar Days | Must be purged or refreshed via Places API after 30 days. |
| `review_count` | Google Places API | Temporary Cache | 30 Calendar Days | Must be purged or refreshed via Places API after 30 days. |
| `website_url` | Google Places API / Scraper | Temporary Cache | 30 Calendar Days | Raw Google URL purged or refreshed after 30 days. |
| `opportunity_score`| System Derived | **PERMANENT** | Indefinite | **Allowed**. Proprietary calculated metric; not raw Google content. |
| `website_audit` | System Derived | **PERMANENT** | Indefinite | **Allowed**. Proprietary technical evaluation. |
| `workflow_state` | System Derived | **PERMANENT** | Indefinite | **Allowed**. Internal workflow state machine tracker. |
| `outreach_draft` | System Derived | **PERMANENT** | Indefinite | **Allowed**. Generated outreach message copy. |

---

## 2. Automated Purge Enforcement Architecture

When `CachePurgerService.run_compliance_purge(db, max_age_days=30)` executes on records older than 30 days:
1. `place_id` is **retained** as authorized by Google TOS.
2. Raw Google-supplied cached attributes (`rating`, `review_count`, `phone`, `address`, `website_url`) are **cleared** (set to `None`) or flagged for refresh.
3. System-derived opportunity scores, audit metrics, and workflow state remain untouched.
4. An immutable audit log entry (`GOOGLE_PLACES_30DAY_COMPLIANCE_PURGE`) is recorded for compliance tracking.
