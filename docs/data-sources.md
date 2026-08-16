# Data Sources & Provider Evaluation

## 1. Overview
This document evaluates potential external data providers for the AI Prospecting Engine targeting restaurants and cafes in Ahmedabad, Gujarat, India. Per rule **1.3 (Do not build a scraper-dependent architecture)** and rule **1.2 (Research before integrating external services)**, all data sources must be accessed legally via official APIs/data feeds with terms compatible with B2B lead generation and analytical processing.

---

## 2. Discovery & Places Data Providers

| Provider | India / Ahmedabad Coverage | Data Quality & Depth | Commercial / Lead Gen Terms | Storage Rights & Cache Limits | Recommendation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Google Places API (New)** | **Exceptional** (Primary source for local SMBs in India) | High (Name, Address, Phone, Website, Rating, Review Count, Opening Hours) | Commercial use permitted. Scraping Google Maps UI directly is strictly prohibited by ToS Section 3.2.3. Official Places API must be used. | **Strict Caching Rule**: Place IDs can be cached indefinitely. Place Details (e.g. name, rating, website) **cannot be cached for more than 30 days**. Must be refreshed or purged. | **APPROVED (Primary Places Provider)** |
| **OpenStreetMap (Overpass API / Nominatim)** | Moderate (Good for road network & major landmarks, spotty for small local cafes) | Basic (Name, Lat/Lng, Category, rare website tags) | Open Data Commons Open Database License (ODbL). Commercial use permitted with proper attribution. | Full storage permitted. | **APPROVED (Secondary / Validation Provider)** |
| **SerpAPI / Google Search API** | High | High (Organic web search results, official domain discovery) | Commercial API service. Search results processed via API endpoint. | Result caching permitted for operational workflows. | **APPROVED (Discovery Search Provider)** |
| **Bing Web Search API** | High | High (Alternative web search endpoint) | Microsoft Azure Cognitive Services terms. Commercial use permitted. | Caching permitted according to Azure Cognitive Services policies. | **APPROVED (Fallback Search Provider)** |
| **Third-Party Directory Scraping (Zomato/Swiggy)** | High | High | **PROHIBITED**. Scraping without explicit platform permission violates Zomato/Swiggy Terms of Service and anti-scraping protections. | No storage allowed. | **REJECTED / PROHIBITED** |

---

## 3. Web Performance & Audit Providers

| Tool / API | Capability | Pricing & Limits | Terms & Compliance | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Google PageSpeed Insights API** | Returns Core Web Vitals, performance score, accessibility score, SEO score, mobile responsiveness. | Free tier (up to 25,000 queries/day). | Official Google API, fully compliant. | **APPROVED (Primary Performance Auditor)** |
| **Python `httpx` / `BeautifulSoup4` HTTP Inspection** | Fetches target site HTML header, SSL certificate validity, meta viewport, title tags, DOM node count. | Self-hosted / local execution. | Standard HTTP client requests respecting `robots.txt` and polite user-agent headers. | **APPROVED (Primary DOM Inspector)** |
| **Headless Browser / Playwright** | Full DOM screenshot & layout evaluation for AI visual analysis. | Self-hosted compute cost. | Strictly restricted to inspecting target website public URL. No circumventing anti-bot mechanisms. | **APPROVED (Visual Screenshot Auditor)** |

---

## 4. LLM & AI Reasoning Providers

| Provider | Primary Models | Usage in Engine | Cost & Rate Limits | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Google Gemini API** | Gemini 1.5 Flash / Gemini 2.0 Flash / Pro | Fast, structured audit evaluation, visual template customization. | Pay-per-token API; compliant with Google AI Terms. | **APPROVED (Primary Structured Reasoning)** |
| **OpenAI API** | GPT-4o / GPT-4o-mini | Personalization, sales audit synthesis, outreach draft creation. | Standard commercial API terms. No training on API data. | **APPROVED (Secondary Personalization Engine)** |
| **Anthropic Claude API** | Claude 3.5 Sonnet / Haiku | Complex evidence-backed analysis & compliance checking. | Standard commercial API terms. | **APPROVED (Compliance & Audit Evaluator)** |

---

## 5. Summary of Compliance Requirements
1. **Google Places Data Retention**: Place details stored in database must include `retrieved_at` timestamp and undergo automatic purge/refresh after 30 days.
2. **Robots.txt & HTTP Headers**: All direct website reachability checks must set a identifying User-Agent (`WebDevProspectingBot/1.0 (+https://agency.domain.com/bot-info)`) and respect `robots.txt` crawl delays.
3. **No Scraping Bypass**: No proxy rotation or anti-bot bypassing will be used.
