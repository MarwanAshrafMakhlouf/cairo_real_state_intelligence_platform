# Cairo Real Estate Intelligence Platform — Data Cleaning Knowledge Base

**Dataset:** ~70,000 property listings scraped from a major Egyptian real estate platform  
**Data range:** 2024-04-29 to 2026-05-04  
**Note:** Data collected during this period may not reflect current market conditions

---

## Dropped Columns & Why

- **compound:** Only 3 non-null values. Redundant with the neighborhood column — a few sellers highlighted their neighborhood name in the title and it got extracted into a separate column by mistake.
- **area (m²) [malformed]:** Naming/encoding error column, not the real area column.
- **monthly installments & payment period (years):** Not relevant to the current analysis scope.
- **price type:** Redundant after cleaning the sale_or_rent column.
- **delivery term (duplicate with trailing space):** Encoding artifact, dropped after cleaning.
- **level & imputed_level:** Intermediate columns, replaced by `level_clean`.

---

## Data Type Fixes

- All additional feature columns (balcony, private garden, pool, etc.) converted to boolean.
- `listing_date` converted to datetime.
- `price` and `area (m²)` converted to numeric — commas and currency symbols stripped first.

---

## Rows Dropped

- All listings with null price were dropped. Investigation showed they had no meaningful data across any column — no district, no property type, nothing recoverable.

---

## Column: level → level_clean

**Starting state:** ~6k filled values out of 70k  
**Final state:** ~50k+ after imputation  

**Imputation was done in three layers:**

**Layer 1 — Property subtype logic:**
- Penthouse → `top floor`
- Roof subtype → `roof`
- Villas → `Independent Unit`

**Layer 2 — Regex on English titles:**
- Patterns captured: "ground floor", "3rd floor", "first floor", "roof floor", "typical floor", multi-floor phrases
- One manual fix: index 32481 had "level" in title referring to ground floor — all other "level" mentions were about quality (e.g. "level of finishing"), not floor number
- "With garden" in title → set `private garden = True` then re-applied subtype logic

**Layer 3 — Regex on Arabic titles:**
- Detected Arabic listings containing دور
- Extracted and standardized: دور أول → 1, دور تاني → 2, دور تالت → 3, متكرر → recurring, ارضي → ground, etc.

**Standardization categories:**
- `ground`, `top`, `recurring`, `basement`, numeric floor number (1–50), anything >50 mapped to `top`
- Edge case: values containing 'hdf' were set to None (referred to apartment square footage, not floor)

**Key insight:** The `private garden` flag in the data is building-level information, not unit-level. Advertisers apply it to any apartment that has access to a shared garden or even a small landscape in front of the building — it does not mean the unit has its own private garden.

---

## Column: delivery term (finishing level)

**Starting state:** ~6,840 filled values out of ~70k  
**Final state:** ~19,791 after imputation  
**Model decision:** DROPPED from feature matrix — 71%+ missing, insufficient signal for modeling  
**Retained for:** EDA and the RAG chatbot knowledge base  

**Imputation approach:**

**Step 1 — English titles:**
- "core & shell" → `core & shell`
- "semi-finished" / "semi finished" → `semi_finished`
- "not finished" → `not_finished`
- "finished" (without the above) → `finished`

**Step 2 — Arabic titles:**
- Regex classifier built on تشطيب keyword and its qualifiers
- Quality ladder found in the data (low to high): بدون تشطيب → نص تشطيب → تشطيب → لوكس → سوبر لوكس → هاي سوبر لوكس → الترا سوبر لوكس → فندقي/VIP
- Classifier outputs: `not_finished`, `semi_finished`, `finished`
- Finishing tier (ultra_super_lux, hotel, etc.) was explored but not kept — too granular for the current scope

---

## Column: rental frequency

**Context:** 14k total rental properties, ~12k had frequency, ~2,430 missing  
**Decision:** Impute all unknowns as `monthly`  

**Evidence used:**

1. **Overall KDE:** Price distribution of no-frequency listings (n=2,385) was nearly identical to monthly (n=11,690). Daily listings (n=283) had a completely different distribution — peaked sharply at 2k–5k EGP vs ~50k median for monthly.

2. **District breakdown:** 72% of unknown-frequency listings (1,759 out of 2,430) were in New Cairo — a market dominated by compound apartments where daily rentals are extremely rare.

3. **Property type check:** Villa-specific KDE confirmed the same pattern. Daily villas peaked at 5k–50k EGP (sensible daily rate). Monthly and no-frequency villas both clustered around 100k–115k EGP median. Note: daily villa sample was only n=11, too small for strong conclusions but directionally consistent.

**Conclusion:** Unknown frequency listings price like monthly rentals across both overall and property-type-specific distributions. Imputation as monthly is justified and well-evidenced.

---

## Column: deposit & insurance

**Coverage:** ~3k listings out of 14k rental properties (~21%)  
**Model decision:** DROPPED — too sparse to generalize  
**Retained for:** EDA and RAG chatbot  

**Key insight:** Deposit and insurance are a compound rental culture norm, not a city-wide standard. New Cairo (948) and Madinaty (938) together account for 63% of all deposit/insurance listings. These are professionally managed compound rentals where brokers follow a standardized process. Informal or older areas (Shubra, Helwan, Basateen) have almost none.

**RAG chatbot use case:** Can advise landlords listing in New Cairo or Madinaty to include deposit and insurance terms, as tenants in those areas expect it and its absence may make the listing look less professional.

---
## Column: delivery date

**Coverage:** ~1k non-null values out of 70k (~1.4%)
**Decision:** Raw column dropped, derived `is_off_plan` boolean created

**Why not just drop it:**
Non-null values are meaningful — a listing with a future delivery date (2027, 2028, etc.)
is an off-plan property, which is fundamentally different from a ready-to-move-in listing
and affects price significantly. Dropping the column entirely would lose that signal.

**Approach:**
Created a binary `is_off_plan` feature instead:
- True → delivery year is 2026 or later (confirmed future delivery)
- False → no delivery date or garbage values (soon, within 6 months, 7, 13, etc.)

**Garbage values found:** soon, within 6 months, 7, 7.0, 13, 14 — ignored in derivation.
**Raw column dropped** after `is_off_plan` was created.
---
## General Patterns & Market Observations

- Listings are bilingual (Arabic and English), sometimes mixed within the same title. All regex-based extraction had to handle both languages separately.
- Egyptian real estate uses informal Arabic spellings heavily (دور تالت instead of الدور الثالث, نص instead of نصف). Standardization had to account for colloquial variants, not just formal Arabic.
- New Cairo dominates the dataset across almost every segment — rental frequency unknowns, deposit/insurance, level data. Models should be evaluated separately per district if possible.
- Daily rental listings are a very small segment (283 out of 14k rental properties) and mostly non-compound properties.