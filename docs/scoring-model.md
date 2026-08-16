# V1 Opportunity Scoring Model & Qualification Threshold Specification

## Overview
The V1 Opportunity Scoring Model evaluates local business prospects on a **0.0 to 100.0** composite scale. It determines sales priority based on five normalized signals:
- **Digital Opportunity Gap**: 35% weight (0 to 35.0 pts)
- **Local Customer Traction**: 25% weight (0 to 25.0 pts)
- **Commercial Potential**: 20% weight (0 to 20.0 pts)
- **Contactability**: 10% weight (0 to 10.0 pts)
- **Purchase Signals**: 10% weight (0 to 10.0 pts)

Total composite score = sum of component contributions, capped at **100.0 pts**.

---

## Formula & Weight Distribution

$$\text{Total Score} = S_{\text{DigitalGap}} + S_{\text{Traction}} + S_{\text{Commercial}} + S_{\text{Contactability}} + S_{\text{Signals}}$$

| Category | Weight / Max Score | Normalized Formula | Calculation Method |
| :--- | :--- | :--- | :--- |
| **Digital Opportunity Gap** | **35.0 pts (35%)** | $\text{Raw} = 100 \times (1 - \frac{\text{QualityScore}}{100})$ | 35.0 pts if no site / unreachable / unverified; $35 \times (1 - \frac{\text{QualityScore}}{100})$ if site audited. |
| **Customer Traction** | **25.0 pts (25%)** | $\text{Raw} = \frac{\text{TractionScore}}{25} \times 100$ | $\min(15, \log_{10}(\text{Reviews}) \times 5) + \text{RatingScore} (0\text{--}5) + \text{RecentActivity} (0\text{--}5)$. |
| **Commercial Potential** | **20.0 pts (20%)** | $\text{Raw} = \frac{\text{CommScore}}{20} \times 100$ | Pricing positioning (5) + Scale (5) + Digital Revenue Opp (5) + Brand Sophistication (5). |
| **Contactability** | **10.0 pts (10%)** | $\text{Raw} = \frac{\text{ContactScore}}{10} \times 100$ | Decision Maker Confidence (5 if HIGH/MED) + Contact availability (3 for phone, 2 for address). |
| **Purchase Signals** | **10.0 pts (10%)** | $\text{Raw} = \frac{\text{SignalScore}}{10} \times 100$ | Verifiable expansion, hiring, or review scale signals ($\min(10.0, N_{\text{signals}} \times 5.0)$). |

---

## Score Transparency Schema

Every score calculated by `ScoringEngine` outputs transparent breakdown metadata:

```json
{
  "total_score": 83.5,
  "score_version": "V1_AGREED_35_25_20_10_10",
  "components": {
    "digital_opportunity_gap": {
      "raw_score": 100.0,
      "weight_pct": 35.0,
      "contribution": 35.0,
      "reason": "Digital Gap Score 35.0/35.0 (Website verification status: NO_WEBSITE)",
      "evidence": {"website_status": "NO_WEBSITE", "quality_score": null}
    },
    "customer_traction": {
      "raw_score": 80.0,
      "weight_pct": 25.0,
      "contribution": 20.0,
      "reason": "Customer Traction Score 20.0/25.0 based on 510 reviews & 4.4 rating",
      "evidence": {"reviews": 510, "rating": 4.4}
    }
  }
}
```

---

## Qualification & Classification Tiers

| Score Range | Classification | Workflow Action | Automated Outreach Eligible |
| :--- | :--- | :--- | :--- |
| **≥ 80.0** | **PRIORITY** | Advance to Contact Research & Demo Generation | **Yes** (High Priority) |
| **70.0 - 79.9** | **QUALIFIED** | Advance to Contact Research & Demo Generation | **Yes** |
| **60.0 - 69.9** | **POTENTIAL / REVIEW** | Held for Manual Review / Nurture Batch | **No** (Requires Human Approval) |
| **< 60.0** | **REJECTED** | Disqualified; Lead Workflow Terminated | **No** |

---

## Hard Rejection Filters

A business lead is immediately disqualified (`QUALIFIED = False`) if any of the following apply:
1. Business is permanently closed or unverified non-business location (`NON_BUSINESS`).
2. Composite Opportunity Score < 70.0 (or below campaign threshold).
3. Business marked `DO_NOT_CONTACT` or suppressed.
4. Business has an excellent website ($\text{QualityScore} \ge 85.0$) with zero digital opportunity gap.
5. Critical contact information (phone and address) is missing.
