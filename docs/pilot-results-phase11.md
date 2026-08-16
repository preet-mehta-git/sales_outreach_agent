# Phase 11: Lead Verification & Prospect Intelligence Pilot Report

**Campaign ID**: `b87e03e1-95cb-4f28-bee0-9b83eb9c437e`  

**Campaign Name**: `Ahmedabad Pilot Dry Run - 10 Businesses`  

**Execution Mode**: `OUTREACH_MODE=DRY_RUN`  

**Target Location**: Ahmedabad, India | **Batch Size**: 10 Entities

---

## Executive Summary & Phase 11 Metrics

- **Total Entities Processed**: 10
- **Non-Business Entities Filtered & Rejected**: 1
- **Verified Business Prospects**: 9
- **Official Websites Verified**: 6 (Source B Discovered: 1)
- **Confirmed NO_WEBSITE**: 3
- **Verified Decision Makers**: 0 (Zero Fabrication Enforcement: 10 marked NOT_FOUND)
- **Opportunity Scoring**: PRIORITY (2), QUALIFIED (2), POTENTIAL_REVIEW (0), REJECTED (6)
- **Outreach Readiness**: READY_FOR_APPROVAL (4), MANUAL_REVIEW (6)

---

## Phase 11 Prospect Intelligence Summary Table

| Business | Entity Type | Website Discovery Source | Website Classification | Opportunity Score | Decision Maker | Outreach Readiness |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Manek Chowk Night Food Market** | `NON_BUSINESS` | `SOURCE_A` | `NO_WEBSITE` | **86.0** | `NOT_FOUND (NOT_FOUND)` | `NOT_READY` |
| **Agashiye - House of MG** | `BUSINESS` | `GOOGLE_PLACES_SOURCE_A` | `GOOD_WEBSITE` | **55.4** | `NOT_FOUND (NOT_FOUND)` | `NOT_READY` |
| **Gordhan Thal** | `BUSINESS` | `GOOGLE_PLACES_SOURCE_A` | `OUTDATED_WEBSITE` | **74.1** | `NOT_FOUND (NOT_FOUND)` | `READY_FOR_APPROVAL` |
| **Zen Cafe** | `BUSINESS` | `SOURCE_A_AND_B_SEARCH` | `NO_WEBSITE` | **83.5** | `NOT_FOUND (NOT_FOUND)` | `READY_FOR_APPROVAL` |
| **Lucky Tea Stall** | `BUSINESS` | `SOURCE_A_AND_B_SEARCH` | `NO_WEBSITE` | **84.4** | `NOT_FOUND (NOT_FOUND)` | `READY_FOR_APPROVAL` |
| **Karnavati Dabeli & Vadapav** | `BUSINESS` | `SOURCE_A_AND_B_SEARCH` | `NO_WEBSITE` | **74.7** | `NOT_FOUND (NOT_FOUND)` | `READY_FOR_APPROVAL` |
| **Havmor Restaurant** | `BUSINESS` | `GOOGLE_PLACES_SOURCE_A` | `GOOD_WEBSITE` | **55.0** | `NOT_FOUND (NOT_FOUND)` | `NOT_READY` |
| **Upper Crust Bakery & Cafe** | `BUSINESS` | `GOOGLE_PLACES_SOURCE_A` | `GOOD_WEBSITE` | **55.3** | `NOT_FOUND (NOT_FOUND)` | `NOT_READY` |
| **Swati Snacks** | `BUSINESS` | `WEB_SEARCH_SOURCE_B` | `GOOD_WEBSITE` | **56.3** | `NOT_FOUND (NOT_FOUND)` | `NOT_READY` |
| **Vishalla Village Restaurant** | `BUSINESS` | `GOOGLE_PLACES_SOURCE_A` | `GOOD_WEBSITE` | **55.3** | `NOT_FOUND (NOT_FOUND)` | `NOT_READY` |

---

## Detailed 10-Entity Audit Records

### 1. Manek Chowk Night Food Market

1. **Business Name**: Manek Chowk Night Food Market
2. **Category**: street food
3. **Location**: Manek Chowk, Danaplee, Khadia, Ahmedabad
4. **Entity Verification**: `{"entity_type": "NON_BUSINESS", "verification_status": "REJECTED"}`
5. **Website Discovery & Classification**: `{"source_a_places_url": "NONE", "source_b_search_url": "NONE", "final_website_url": "NONE", "website_source": "SOURCE_A", "verification_status": "WEBSITE_FOUND_UNVERIFIED", "classification": "NO_WEBSITE"}`
6. **Website Quality Score**: NOT_AVAILABLE
7. **Opportunity Score Breakdown**: `{"total_score": 86.0, "digital_opportunity_gap": 35.0, "customer_traction": 25.0, "commercial_potential": 16.0, "contactability": 5.0, "purchase_signals": 5.0}`
8. **Qualification Classification**: `REJECTED`
9. **Classification Reason**: `NON_BUSINESS_ENTITY (Entity rejected as market/landmark)`
10. **Decision Maker Discovery**: `{"name": "NOT_FOUND", "title": "NOT_FOUND", "confidence": "NOT_FOUND", "evidence": "No public verifiable evidence"}`
11. **Facts vs Inference Business Audit**:
```json
{
  "known_facts": {
    "business_name": "Manek Chowk Night Food Market",
    "category": "street food",
    "city": "Ahmedabad",
    "rating": 4.6,
    "review_count": 2850,
    "website_status": "NO_WEBSITE"
  },
  "inferred_insights": [
    "Significant customer search demand indicated by 2850+ public reviews."
  ],
  "potential_opportunities": [
    "Service catalog and pricing package overview",
    "Direct appointment scheduling & lead capture form",
    "Customer testimonial & portfolio section"
  ],
  "unknown_variables": [
    "Exact monthly direct customer website traffic (requires web analytics)",
    "Financial commission split paid to third-party platforms (requires internal finance records)",
    "Exact conversion rate of phone inquiries into bookings"
  ]
}
```
12. **Public Demo URL**: NOT_AVAILABLE
13. **Outreach Readiness**: `{"status": "NOT_READY", "reasons": []}`
14. **Email Draft**:
```json
"NOT_AVAILABLE"
```
15. **WhatsApp Draft**:
```json
"NOT_AVAILABLE"
```
16. **Suppression Status**: `False`

---

### 2. Agashiye - House of MG

1. **Business Name**: Agashiye - House of MG
2. **Category**: fine dining restaurant
3. **Location**: Opp. Sidi Saiyyed Mosque, Lal Darwaja, Ahmedabad
4. **Entity Verification**: `{"entity_type": "BUSINESS", "verification_status": "VERIFIED"}`
5. **Website Discovery & Classification**: `{"source_a_places_url": "https://houseofmg.com", "source_b_search_url": "NONE", "final_website_url": "https://houseofmg.com", "website_source": "GOOGLE_PLACES_SOURCE_A", "verification_status": "OFFICIAL_WEBSITE_VERIFIED", "classification": "GOOD_WEBSITE"}`
6. **Website Quality Score**: 81.75
7. **Opportunity Score Breakdown**: `{"total_score": 55.4, "digital_opportunity_gap": 6.4, "customer_traction": 25.0, "commercial_potential": 14.0, "contactability": 5.0, "purchase_signals": 5.0}`
8. **Qualification Classification**: `REJECTED`
9. **Classification Reason**: `SCORE_BELOW_THRESHOLD (Opportunity Score < 70.0)`
10. **Decision Maker Discovery**: `{"name": "NOT_FOUND", "title": "NOT_FOUND", "confidence": "NOT_FOUND", "evidence": "No public verifiable evidence"}`
11. **Facts vs Inference Business Audit**:
```json
{
  "known_facts": {
    "business_name": "Agashiye - House of MG",
    "category": "fine dining restaurant",
    "city": "Ahmedabad",
    "rating": 4.7,
    "review_count": 1420,
    "website_status": "WEBSITE_FOUND"
  },
  "inferred_insights": [
    "Significant customer search demand indicated by 1420+ public reviews."
  ],
  "potential_opportunities": [
    "Owned mobile digital menu with instant QR accessibility",
    "Direct table enquiry & reservation booking form",
    "Instant WhatsApp click-to-order CTA"
  ],
  "unknown_variables": [
    "Exact monthly direct customer website traffic (requires web analytics)",
    "Financial commission split paid to third-party platforms (requires internal finance records)",
    "Exact conversion rate of phone inquiries into bookings"
  ]
}
```
12. **Public Demo URL**: NOT_AVAILABLE
13. **Outreach Readiness**: `{"status": "NOT_READY", "reasons": []}`
14. **Email Draft**:
```json
"NOT_AVAILABLE"
```
15. **WhatsApp Draft**:
```json
"NOT_AVAILABLE"
```
16. **Suppression Status**: `False`

---

### 3. Gordhan Thal

1. **Business Name**: Gordhan Thal
2. **Category**: gujarati thali restaurant
3. **Location**: SG Highway, Bodakdev, Ahmedabad
4. **Entity Verification**: `{"entity_type": "BUSINESS", "verification_status": "VERIFIED"}`
5. **Website Discovery & Classification**: `{"source_a_places_url": "http://gordhanthal.com", "source_b_search_url": "NONE", "final_website_url": "http://gordhanthal.com", "website_source": "GOOGLE_PLACES_SOURCE_A", "verification_status": "OFFICIAL_WEBSITE_VERIFIED", "classification": "OUTDATED_WEBSITE"}`
6. **Website Quality Score**: 34.0
7. **Opportunity Score Breakdown**: `{"total_score": 74.1, "digital_opportunity_gap": 23.1, "customer_traction": 25.0, "commercial_potential": 16.0, "contactability": 5.0, "purchase_signals": 5.0}`
8. **Qualification Classification**: `QUALIFIED`
9. **Classification Reason**: `QUALIFIED_THRESHOLD_MET (Opportunity Score >= 70.0)`
10. **Decision Maker Discovery**: `{"name": "NOT_FOUND", "title": "NOT_FOUND", "confidence": "NOT_FOUND", "evidence": {"source": "Public Web & Registry Discovery", "status": "NOT_FOUND", "searched_sources": ["official_website_about", "contact_page", "public_business_directory"], "reason": "No explicit individual owner or executive name could be verified from public sources without guessing."}}`
11. **Facts vs Inference Business Audit**:
```json
{
  "known_facts": {
    "business_name": "Gordhan Thal",
    "category": "gujarati thali restaurant",
    "city": "Ahmedabad",
    "rating": 4.5,
    "review_count": 980,
    "website_status": "WEAK_WEBSITE"
  },
  "inferred_insights": [
    "Significant customer search demand indicated by 980+ public reviews.",
    "Existing digital channel presents user-experience or mobile conversion limitations."
  ],
  "potential_opportunities": [
    "Owned mobile digital menu with instant QR accessibility",
    "Direct table enquiry & reservation booking form",
    "Instant WhatsApp click-to-order CTA"
  ],
  "unknown_variables": [
    "Exact monthly direct customer website traffic (requires web analytics)",
    "Financial commission split paid to third-party platforms (requires internal finance records)",
    "Exact conversion rate of phone inquiries into bookings"
  ]
}
```
12. **Public Demo URL**: http://localhost:8000/static/demos/daa23f80-ac64-4d5f-92c7-e5aabcf957d1/index.html
13. **Outreach Readiness**: `{"status": "READY_FOR_APPROVAL", "reasons": ["All 8 Phase 11 outreach readiness criteria passed."]}`
14. **Email Draft**:
```json
{
  "subject": "Digital opportunity assessment for Gordhan Thal",
  "body": "Hello Gordhan Thal Team,\n\nI came across Gordhan Thal while reviewing commercial businesses in Ahmedabad. Your 4.5\u2b50 public rating across 980 Google reviews reflects strong customer interest.\n\nBased on our digital audit, we identified a key growth opportunity: online searchers looking for Gordhan Thal currently lack an direct mobile menu and WhatsApp instant ordering route.\n\nTo demonstrate how this can be resolved, we assembled a live mobile prototype for Gordhan Thal:\nhttp://localhost:8000/static/demos/daa23f80-ac64-4d5f-92c7-e5aabcf957d1/index.html\n\nPrototype features included:\n- Instant WhatsApp Click-to-Order CTA\n- Mobile-responsive menu display\n- One-tap location & enquiry form\n\nWould you be open to a 5-minute call this week to review how this can be enabled for Gordhan Thal?\n\nBest regards,\nOutreach Team | Antigravity AI Systems\n\n---\nTo update outreach preferences or opt out, please reply with \"REMOVE\".\n"
}
```
15. **WhatsApp Draft**:
```json
{
  "body": "Hello Gordhan Thal Team, We put together a live mobile web prototype for Gordhan Thal featuring instant WhatsApp ordering and mobile menu. View it here: http://localhost:8000/static/demos/daa23f80-ac64-4d5f-92c7-e5aabcf957d1/index.html - Let us know your thoughts!"
}
```
16. **Suppression Status**: `False`

---

### 4. Zen Cafe

1. **Business Name**: Zen Cafe
2. **Category**: cafe
3. **Location**: University Road, Navrangpura, Ahmedabad
4. **Entity Verification**: `{"entity_type": "BUSINESS", "verification_status": "VERIFIED"}`
5. **Website Discovery & Classification**: `{"source_a_places_url": "NONE", "source_b_search_url": "NONE", "final_website_url": "NONE", "website_source": "SOURCE_A_AND_B_SEARCH", "verification_status": "NO_WEBSITE_CONFIRMED", "classification": "NO_WEBSITE"}`
6. **Website Quality Score**: 0.0
7. **Opportunity Score Breakdown**: `{"total_score": 83.5, "digital_opportunity_gap": 35.0, "customer_traction": 22.5, "commercial_potential": 16.0, "contactability": 5.0, "purchase_signals": 5.0}`
8. **Qualification Classification**: `PRIORITY`
9. **Classification Reason**: `PRIORITY_SCORE_MET (Opportunity Score >= 80.0)`
10. **Decision Maker Discovery**: `{"name": "NOT_FOUND", "title": "NOT_FOUND", "confidence": "NOT_FOUND", "evidence": {"source": "Public Web & Registry Discovery", "status": "NOT_FOUND", "searched_sources": ["official_website_about", "contact_page", "public_business_directory"], "reason": "No explicit individual owner or executive name could be verified from public sources without guessing."}}`
11. **Facts vs Inference Business Audit**:
```json
{
  "known_facts": {
    "business_name": "Zen Cafe",
    "category": "cafe",
    "city": "Ahmedabad",
    "rating": 4.4,
    "review_count": 510,
    "website_status": "NO_WEBSITE"
  },
  "inferred_insights": [
    "Significant customer search demand indicated by 510+ public reviews.",
    "Online searchers rely on Google Maps listing and third-party pages due to lack of an official website."
  ],
  "potential_opportunities": [
    "Mobile menu showcase with beverage & snack items",
    "Direct WhatsApp click-to-order CTA",
    "Table reservation & event enquiry form"
  ],
  "unknown_variables": [
    "Exact monthly direct customer website traffic (requires web analytics)",
    "Financial commission split paid to third-party platforms (requires internal finance records)",
    "Exact conversion rate of phone inquiries into bookings"
  ]
}
```
12. **Public Demo URL**: http://localhost:8000/static/demos/dff86629-e143-4802-84ae-06ed9326be31/index.html
13. **Outreach Readiness**: `{"status": "READY_FOR_APPROVAL", "reasons": ["All 8 Phase 11 outreach readiness criteria passed."]}`
14. **Email Draft**:
```json
{
  "subject": "Digital opportunity assessment for Zen Cafe",
  "body": "Hello Zen Cafe Team,\n\nI came across Zen Cafe while reviewing commercial businesses in Ahmedabad. Your 4.4\u2b50 public rating across 510 Google reviews reflects strong customer interest.\n\nBased on our digital audit, we identified a key growth opportunity: online searchers looking for Zen Cafe currently lack an direct mobile menu and WhatsApp instant ordering route.\n\nTo demonstrate how this can be resolved, we assembled a live mobile prototype for Zen Cafe:\nhttp://localhost:8000/static/demos/dff86629-e143-4802-84ae-06ed9326be31/index.html\n\nPrototype features included:\n- Instant WhatsApp Click-to-Order CTA\n- Mobile-responsive menu display\n- One-tap location & enquiry form\n\nWould you be open to a 5-minute call this week to review how this can be enabled for Zen Cafe?\n\nBest regards,\nOutreach Team | Antigravity AI Systems\n\n---\nTo update outreach preferences or opt out, please reply with \"REMOVE\".\n"
}
```
15. **WhatsApp Draft**:
```json
{
  "body": "Hello Zen Cafe Team, We put together a live mobile web prototype for Zen Cafe featuring instant WhatsApp ordering and mobile menu. View it here: http://localhost:8000/static/demos/dff86629-e143-4802-84ae-06ed9326be31/index.html - Let us know your thoughts!"
}
```
16. **Suppression Status**: `False`

---

### 5. Lucky Tea Stall

1. **Business Name**: Lucky Tea Stall
2. **Category**: cafe & tea
3. **Location**: Opp. Dinbai Tower, Mirzapur, Ahmedabad
4. **Entity Verification**: `{"entity_type": "BUSINESS", "verification_status": "VERIFIED"}`
5. **Website Discovery & Classification**: `{"source_a_places_url": "NONE", "source_b_search_url": "NONE", "final_website_url": "NONE", "website_source": "SOURCE_A_AND_B_SEARCH", "verification_status": "NO_WEBSITE_CONFIRMED", "classification": "NO_WEBSITE"}`
6. **Website Quality Score**: 0.0
7. **Opportunity Score Breakdown**: `{"total_score": 84.4, "digital_opportunity_gap": 35.0, "customer_traction": 23.4, "commercial_potential": 16.0, "contactability": 5.0, "purchase_signals": 5.0}`
8. **Qualification Classification**: `PRIORITY`
9. **Classification Reason**: `PRIORITY_SCORE_MET (Opportunity Score >= 80.0)`
10. **Decision Maker Discovery**: `{"name": "NOT_FOUND", "title": "NOT_FOUND", "confidence": "NOT_FOUND", "evidence": {"source": "Public Web & Registry Discovery", "status": "NOT_FOUND", "searched_sources": ["official_website_about", "contact_page", "public_business_directory"], "reason": "No explicit individual owner or executive name could be verified from public sources without guessing."}}`
11. **Facts vs Inference Business Audit**:
```json
{
  "known_facts": {
    "business_name": "Lucky Tea Stall",
    "category": "cafe & tea",
    "city": "Ahmedabad",
    "rating": 4.3,
    "review_count": 760,
    "website_status": "NO_WEBSITE"
  },
  "inferred_insights": [
    "Significant customer search demand indicated by 760+ public reviews.",
    "Online searchers rely on Google Maps listing and third-party pages due to lack of an official website."
  ],
  "potential_opportunities": [
    "Mobile menu showcase with beverage & snack items",
    "Direct WhatsApp click-to-order CTA",
    "Table reservation & event enquiry form"
  ],
  "unknown_variables": [
    "Exact monthly direct customer website traffic (requires web analytics)",
    "Financial commission split paid to third-party platforms (requires internal finance records)",
    "Exact conversion rate of phone inquiries into bookings"
  ]
}
```
12. **Public Demo URL**: http://localhost:8000/static/demos/c48bf134-a091-4956-a35f-fd460db4ef71/index.html
13. **Outreach Readiness**: `{"status": "READY_FOR_APPROVAL", "reasons": ["All 8 Phase 11 outreach readiness criteria passed."]}`
14. **Email Draft**:
```json
{
  "subject": "Digital opportunity assessment for Lucky Tea Stall",
  "body": "Hello Lucky Tea Stall Team,\n\nI came across Lucky Tea Stall while reviewing commercial businesses in Ahmedabad. Your 4.3\u2b50 public rating across 760 Google reviews reflects strong customer interest.\n\nBased on our digital audit, we identified a key growth opportunity: online searchers looking for Lucky Tea Stall currently lack an direct mobile menu and WhatsApp instant ordering route.\n\nTo demonstrate how this can be resolved, we assembled a live mobile prototype for Lucky Tea Stall:\nhttp://localhost:8000/static/demos/c48bf134-a091-4956-a35f-fd460db4ef71/index.html\n\nPrototype features included:\n- Instant WhatsApp Click-to-Order CTA\n- Mobile-responsive menu display\n- One-tap location & enquiry form\n\nWould you be open to a 5-minute call this week to review how this can be enabled for Lucky Tea Stall?\n\nBest regards,\nOutreach Team | Antigravity AI Systems\n\n---\nTo update outreach preferences or opt out, please reply with \"REMOVE\".\n"
}
```
15. **WhatsApp Draft**:
```json
{
  "body": "Hello Lucky Tea Stall Team, We put together a live mobile web prototype for Lucky Tea Stall featuring instant WhatsApp ordering and mobile menu. View it here: http://localhost:8000/static/demos/c48bf134-a091-4956-a35f-fd460db4ef71/index.html - Let us know your thoughts!"
}
```
16. **Suppression Status**: `False`

---

### 6. Karnavati Dabeli & Vadapav

1. **Business Name**: Karnavati Dabeli & Vadapav
2. **Category**: fast food
3. **Location**: C G Road, Navrangpura, Ahmedabad
4. **Entity Verification**: `{"entity_type": "BUSINESS", "verification_status": "VERIFIED"}`
5. **Website Discovery & Classification**: `{"source_a_places_url": "NONE", "source_b_search_url": "NONE", "final_website_url": "NONE", "website_source": "SOURCE_A_AND_B_SEARCH", "verification_status": "NO_WEBSITE_CONFIRMED", "classification": "NO_WEBSITE"}`
6. **Website Quality Score**: 0.0
7. **Opportunity Score Breakdown**: `{"total_score": 74.7, "digital_opportunity_gap": 35.0, "customer_traction": 21.7, "commercial_potential": 13.0, "contactability": 5.0, "purchase_signals": 0.0}`
8. **Qualification Classification**: `QUALIFIED`
9. **Classification Reason**: `QUALIFIED_THRESHOLD_MET (Opportunity Score >= 70.0)`
10. **Decision Maker Discovery**: `{"name": "NOT_FOUND", "title": "NOT_FOUND", "confidence": "NOT_FOUND", "evidence": {"source": "Public Web & Registry Discovery", "status": "NOT_FOUND", "searched_sources": ["official_website_about", "contact_page", "public_business_directory"], "reason": "No explicit individual owner or executive name could be verified from public sources without guessing."}}`
11. **Facts vs Inference Business Audit**:
```json
{
  "known_facts": {
    "business_name": "Karnavati Dabeli & Vadapav",
    "category": "fast food",
    "city": "Ahmedabad",
    "rating": 4.2,
    "review_count": 340,
    "website_status": "NO_WEBSITE"
  },
  "inferred_insights": [
    "Significant customer search demand indicated by 340+ public reviews.",
    "Online searchers rely on Google Maps listing and third-party pages due to lack of an official website."
  ],
  "potential_opportunities": [
    "Owned mobile digital menu with instant QR accessibility",
    "Direct table enquiry & reservation booking form",
    "Instant WhatsApp click-to-order CTA"
  ],
  "unknown_variables": [
    "Exact monthly direct customer website traffic (requires web analytics)",
    "Financial commission split paid to third-party platforms (requires internal finance records)",
    "Exact conversion rate of phone inquiries into bookings"
  ]
}
```
12. **Public Demo URL**: http://localhost:8000/static/demos/3a2145c2-7859-4af4-af50-5376a5677265/index.html
13. **Outreach Readiness**: `{"status": "READY_FOR_APPROVAL", "reasons": ["All 8 Phase 11 outreach readiness criteria passed."]}`
14. **Email Draft**:
```json
{
  "subject": "Digital opportunity assessment for Karnavati Dabeli & Vadapav",
  "body": "Hello Karnavati Dabeli & Vadapav Team,\n\nI came across Karnavati Dabeli & Vadapav while reviewing commercial businesses in Ahmedabad. Your 4.2\u2b50 public rating across 340 Google reviews reflects strong customer interest.\n\nBased on our digital audit, we identified a key growth opportunity: online searchers looking for Karnavati Dabeli & Vadapav currently lack an direct mobile menu and WhatsApp instant ordering route.\n\nTo demonstrate how this can be resolved, we assembled a live mobile prototype for Karnavati Dabeli & Vadapav:\nhttp://localhost:8000/static/demos/3a2145c2-7859-4af4-af50-5376a5677265/index.html\n\nPrototype features included:\n- Instant WhatsApp Click-to-Order CTA\n- Mobile-responsive menu display\n- One-tap location & enquiry form\n\nWould you be open to a 5-minute call this week to review how this can be enabled for Karnavati Dabeli & Vadapav?\n\nBest regards,\nOutreach Team | Antigravity AI Systems\n\n---\nTo update outreach preferences or opt out, please reply with \"REMOVE\".\n"
}
```
15. **WhatsApp Draft**:
```json
{
  "body": "Hello Karnavati Dabeli & Vadapav Team, We put together a live mobile web prototype for Karnavati Dabeli & Vadapav featuring instant WhatsApp ordering and mobile menu. View it here: http://localhost:8000/static/demos/3a2145c2-7859-4af4-af50-5376a5677265/index.html - Let us know your thoughts!"
}
```
16. **Suppression Status**: `False`

---

### 7. Havmor Restaurant

1. **Business Name**: Havmor Restaurant
2. **Category**: family restaurant
3. **Location**: Navrangpura Bus Stop, Ahmedabad
4. **Entity Verification**: `{"entity_type": "BUSINESS", "verification_status": "VERIFIED"}`
5. **Website Discovery & Classification**: `{"source_a_places_url": "https://havmor.com", "source_b_search_url": "NONE", "final_website_url": "https://havmor.com", "website_source": "GOOGLE_PLACES_SOURCE_A", "verification_status": "OFFICIAL_WEBSITE_VERIFIED", "classification": "GOOD_WEBSITE"}`
6. **Website Quality Score**: 79.25
7. **Opportunity Score Breakdown**: `{"total_score": 55.0, "digital_opportunity_gap": 7.3, "customer_traction": 23.7, "commercial_potential": 14.0, "contactability": 5.0, "purchase_signals": 5.0}`
8. **Qualification Classification**: `REJECTED`
9. **Classification Reason**: `SCORE_BELOW_THRESHOLD (Opportunity Score < 70.0)`
10. **Decision Maker Discovery**: `{"name": "NOT_FOUND", "title": "NOT_FOUND", "confidence": "NOT_FOUND", "evidence": "No public verifiable evidence"}`
11. **Facts vs Inference Business Audit**:
```json
{
  "known_facts": {
    "business_name": "Havmor Restaurant",
    "category": "family restaurant",
    "city": "Ahmedabad",
    "rating": 4.4,
    "review_count": 890,
    "website_status": "WEBSITE_FOUND"
  },
  "inferred_insights": [
    "Significant customer search demand indicated by 890+ public reviews."
  ],
  "potential_opportunities": [
    "Owned mobile digital menu with instant QR accessibility",
    "Direct table enquiry & reservation booking form",
    "Instant WhatsApp click-to-order CTA"
  ],
  "unknown_variables": [
    "Exact monthly direct customer website traffic (requires web analytics)",
    "Financial commission split paid to third-party platforms (requires internal finance records)",
    "Exact conversion rate of phone inquiries into bookings"
  ]
}
```
12. **Public Demo URL**: NOT_AVAILABLE
13. **Outreach Readiness**: `{"status": "NOT_READY", "reasons": []}`
14. **Email Draft**:
```json
"NOT_AVAILABLE"
```
15. **WhatsApp Draft**:
```json
"NOT_AVAILABLE"
```
16. **Suppression Status**: `False`

---

### 8. Upper Crust Bakery & Cafe

1. **Business Name**: Upper Crust Bakery & Cafe
2. **Category**: bakery & cafe
3. **Location**: Vijay Cross Road, Navrangpura, Ahmedabad
4. **Entity Verification**: `{"entity_type": "BUSINESS", "verification_status": "VERIFIED"}`
5. **Website Discovery & Classification**: `{"source_a_places_url": "http://uppercrustindia.com", "source_b_search_url": "NONE", "final_website_url": "http://uppercrustindia.com", "website_source": "GOOGLE_PLACES_SOURCE_A", "verification_status": "OFFICIAL_WEBSITE_VERIFIED", "classification": "GOOD_WEBSITE"}`
6. **Website Quality Score**: 79.25
7. **Opportunity Score Breakdown**: `{"total_score": 55.3, "digital_opportunity_gap": 7.3, "customer_traction": 24.0, "commercial_potential": 14.0, "contactability": 5.0, "purchase_signals": 5.0}`
8. **Qualification Classification**: `REJECTED`
9. **Classification Reason**: `SCORE_BELOW_THRESHOLD (Opportunity Score < 70.0)`
10. **Decision Maker Discovery**: `{"name": "NOT_FOUND", "title": "NOT_FOUND", "confidence": "NOT_FOUND", "evidence": "No public verifiable evidence"}`
11. **Facts vs Inference Business Audit**:
```json
{
  "known_facts": {
    "business_name": "Upper Crust Bakery & Cafe",
    "category": "bakery & cafe",
    "city": "Ahmedabad",
    "rating": 4.5,
    "review_count": 620,
    "website_status": "WEBSITE_FOUND"
  },
  "inferred_insights": [
    "Significant customer search demand indicated by 620+ public reviews."
  ],
  "potential_opportunities": [
    "Mobile menu showcase with beverage & snack items",
    "Direct WhatsApp click-to-order CTA",
    "Table reservation & event enquiry form"
  ],
  "unknown_variables": [
    "Exact monthly direct customer website traffic (requires web analytics)",
    "Financial commission split paid to third-party platforms (requires internal finance records)",
    "Exact conversion rate of phone inquiries into bookings"
  ]
}
```
12. **Public Demo URL**: NOT_AVAILABLE
13. **Outreach Readiness**: `{"status": "NOT_READY", "reasons": []}`
14. **Email Draft**:
```json
"NOT_AVAILABLE"
```
15. **WhatsApp Draft**:
```json
"NOT_AVAILABLE"
```
16. **Suppression Status**: `False`

---

### 9. Swati Snacks

1. **Business Name**: Swati Snacks
2. **Category**: traditional snacks
3. **Location**: Law Garden, Ellisbridge, Ahmedabad
4. **Entity Verification**: `{"entity_type": "BUSINESS", "verification_status": "VERIFIED"}`
5. **Website Discovery & Classification**: `{"source_a_places_url": "https://swatisnacks.com", "source_b_search_url": "https://swatisnacks.com", "final_website_url": "https://swatisnacks.com", "website_source": "WEB_SEARCH_SOURCE_B", "verification_status": "OFFICIAL_WEBSITE_VERIFIED", "classification": "GOOD_WEBSITE"}`
6. **Website Quality Score**: 79.25
7. **Opportunity Score Breakdown**: `{"total_score": 56.3, "digital_opportunity_gap": 7.3, "customer_traction": 25.0, "commercial_potential": 14.0, "contactability": 5.0, "purchase_signals": 5.0}`
8. **Qualification Classification**: `REJECTED`
9. **Classification Reason**: `SCORE_BELOW_THRESHOLD (Opportunity Score < 70.0)`
10. **Decision Maker Discovery**: `{"name": "NOT_FOUND", "title": "NOT_FOUND", "confidence": "NOT_FOUND", "evidence": "No public verifiable evidence"}`
11. **Facts vs Inference Business Audit**:
```json
{
  "known_facts": {
    "business_name": "Swati Snacks",
    "category": "traditional snacks",
    "city": "Ahmedabad",
    "rating": 4.6,
    "review_count": 1150,
    "website_status": "WEBSITE_FOUND"
  },
  "inferred_insights": [
    "Significant customer search demand indicated by 1150+ public reviews."
  ],
  "potential_opportunities": [
    "Service catalog and pricing package overview",
    "Direct appointment scheduling & lead capture form",
    "Customer testimonial & portfolio section"
  ],
  "unknown_variables": [
    "Exact monthly direct customer website traffic (requires web analytics)",
    "Financial commission split paid to third-party platforms (requires internal finance records)",
    "Exact conversion rate of phone inquiries into bookings"
  ]
}
```
12. **Public Demo URL**: NOT_AVAILABLE
13. **Outreach Readiness**: `{"status": "NOT_READY", "reasons": []}`
14. **Email Draft**:
```json
"NOT_AVAILABLE"
```
15. **WhatsApp Draft**:
```json
"NOT_AVAILABLE"
```
16. **Suppression Status**: `False`

---

### 10. Vishalla Village Restaurant

1. **Business Name**: Vishalla Village Restaurant
2. **Category**: heritage dining
3. **Location**: Vasna Road, Opposite APMC Market, Ahmedabad
4. **Entity Verification**: `{"entity_type": "BUSINESS", "verification_status": "VERIFIED"}`
5. **Website Discovery & Classification**: `{"source_a_places_url": "http://vishalla.com", "source_b_search_url": "NONE", "final_website_url": "http://vishalla.com", "website_source": "GOOGLE_PLACES_SOURCE_A", "verification_status": "OFFICIAL_WEBSITE_VERIFIED", "classification": "GOOD_WEBSITE"}`
6. **Website Quality Score**: 79.25
7. **Opportunity Score Breakdown**: `{"total_score": 55.3, "digital_opportunity_gap": 7.3, "customer_traction": 24.0, "commercial_potential": 14.0, "contactability": 5.0, "purchase_signals": 5.0}`
8. **Qualification Classification**: `REJECTED`
9. **Classification Reason**: `SCORE_BELOW_THRESHOLD (Opportunity Score < 70.0)`
10. **Decision Maker Discovery**: `{"name": "NOT_FOUND", "title": "NOT_FOUND", "confidence": "NOT_FOUND", "evidence": "No public verifiable evidence"}`
11. **Facts vs Inference Business Audit**:
```json
{
  "known_facts": {
    "business_name": "Vishalla Village Restaurant",
    "category": "heritage dining",
    "city": "Ahmedabad",
    "rating": 4.3,
    "review_count": 1680,
    "website_status": "WEBSITE_FOUND"
  },
  "inferred_insights": [
    "Significant customer search demand indicated by 1680+ public reviews."
  ],
  "potential_opportunities": [
    "Owned mobile digital menu with instant QR accessibility",
    "Direct table enquiry & reservation booking form",
    "Instant WhatsApp click-to-order CTA"
  ],
  "unknown_variables": [
    "Exact monthly direct customer website traffic (requires web analytics)",
    "Financial commission split paid to third-party platforms (requires internal finance records)",
    "Exact conversion rate of phone inquiries into bookings"
  ]
}
```
12. **Public Demo URL**: NOT_AVAILABLE
13. **Outreach Readiness**: `{"status": "NOT_READY", "reasons": []}`
14. **Email Draft**:
```json
"NOT_AVAILABLE"
```
15. **WhatsApp Draft**:
```json
"NOT_AVAILABLE"
```
16. **Suppression Status**: `False`

---

## Compliance & Phase 11 Assurance Statement

All output generated during this dry-run (`OUTREACH_MODE=DRY_RUN`) strictly enforces Phase 11 verification, zero fabrication decision-maker rules, multi-source website verification, facts vs. inference separation, public demo URL generation, and Outreach Readiness checklist decoupling.
