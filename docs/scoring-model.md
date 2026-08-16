# V1 Opportunity Scoring Model Specification

## Overview
The V1 Opportunity Scoring Model evaluates local business prospects on a **0.0 to 100.0** composite scale. It determines sales priority based on digital opportunity gap, customer traction, commercial potential, contactability, and verifiable purchase signals.

---

## Formula & Weight Distribution

$$\text{Total Score} = S_{\text{DigitalGap}} + S_{\text{Traction}} + S_{\text{Commercial}} + S_{\text{Contactability}} + S_{\text{Signals}}$$

| Category | Max Score | Description / Formula |
| :--- | :--- | :--- |
| **Digital Opportunity Gap** | **35.0** | $35 \times (1 - \frac{\text{QualityScore}}{100})$ if site exists; $35.0$ if no site / unreachable. |
| **Customer Traction** | **25.0** | $\min(15, \log_{10}(\text{Reviews}) \times 5) + \text{RatingScore} (0\text{--}5) + \text{RecentActivity} (0\text{--}5)$. |
| **Commercial Potential** | **20.0** | Pricing positioning (5) + Scale (5) + Digital Revenue Opp (5) + Brand Sophistication (5). |
| **Contactability** | **10.0** | Decision Maker Confidence (5 if HIGH/MED) + Contact availability (5 for phone/address). |
| **Purchase Signals** | **10.0** | Verifiable expansion, hiring, or menu update signals ($\min(10.0, N_{\text{signals}} \times 3.5)$). |

---

## Hard Rejection Filters

A business lead is immediately disqualified (`QUALIFIED = False`) if any of the following apply:
1. Business is permanently closed or unverified.
2. Composite Opportunity Score < campaign threshold (default: 60.0).
3. Business marked `DO_NOT_CONTACT` or suppressed.
4. Business has an excellent website ($\text{QualityScore} \ge 85.0$) with zero digital opportunity.
5. Critical contact information (phone and address) is missing.
