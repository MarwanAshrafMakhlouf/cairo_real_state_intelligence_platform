#  Cairo Real Estate Data Cleaning Pipeline

**Author:** Marwan Ashraf  
**Last updated:** May 2026  
**Project:** Cairo Real Estate Intelligence Platform  
**Dataset:** ~76,000 property listings scraped from a major Egyptian real estate platform (2024-04-29 to 2026-05-04)

---

## Overview

`cleaning.py` is the production data cleaning pipeline for the Cairo Real Estate dataset. It transforms the raw scraped CSV into a clean, properly typed Parquet file ready for EDA and modeling.

The pipeline is fully sequential — each function takes a DataFrame, applies a single transformation, and returns it. Every step is wrapped in `try/except` and logs via `src.utils.get_logger` instead of printing.

---

## Dependencies

```python
import re
import yaml
import numpy as np
import pandas as pd
from src.utils import get_logger
```

`config.yaml` must be one directory above the script (`../config.yaml`) and must expose:

```yaml
data_source:
  file_paths:
    raw_file: "..."
    cleaned_dataset: "..."
  realstate_website:
    features_list: [...]
```

---

## Entry Point

```python
if __name__ == "__main__":
    main()
```

Run directly:

```bash
python cleaning.py
```

---

## Function Reference

### `main()`

Orchestrates the full pipeline. Loads `config.yaml`, then calls every cleaning function in order, passing the DataFrame through sequentially.

---

### Stage 0 — Load

#### `load_data(config: dict) → pd.DataFrame`

Reads the raw CSV from the path specified in `config["data_source"]["file_paths"]["raw_file"]`.

---

### Stage 1 — Drop Irrelevant Columns

#### `drop_irrelevant_columns(df) → pd.DataFrame`

Drops the following columns unconditionally:

| Column | Reason |
|---|---|
| `compound` | 3 non-null values, redundant with neighbourhood |
| `area (mÂ²)` | Encoding artifact of `area (m²)` — duplicate |
| `monthly installments` | Out of modeling scope |
| `payment period (years)` | Out of modeling scope |
| `price type` | Redundant with `sale_or_rent` |

---

### Stage 2 — Fix Data Types

#### `fix_boolean_features(df, config) → pd.DataFrame`

Casts all columns listed under `config["data_source"]["realstate_website"]["features_list"]` to `bool`. These are binary amenity flags scraped from the listing page (e.g. `private garden`, `pool`, `security`).

#### `fix_listing_date(df) → pd.DataFrame`

Parses `listing_date` to `datetime64` using `pd.to_datetime(..., errors="coerce")`. Unparseable values become `NaT`.

#### `fix_price(df) → pd.DataFrame`

Cleans the raw price string:
- Strips comma thousand-separators
- Strips the `EGP` currency prefix
- Replaces the string `"nan"` with `pd.NA`
- Casts to nullable `Int64`

#### `fix_delivery_date(df) → pd.DataFrame`

Casts `delivery date` to `str` as-is. The column has highly inconsistent values; it is kept in string form here and consumed downstream by `derive_off_plan()`.

#### `fix_area(df) → pd.DataFrame`

Cleans `area (m²)`:
- Removes comma thousand-separators
- Replaces `"nan"` strings with `pd.NA`
- Coerces to numeric via `pd.to_numeric(..., errors="coerce")`

Legitimate decimals (e.g. `163.5`) are preserved.

#### `fix_object_dtypes(df) → pd.DataFrame`

Runs `convert_dtypes()` on every remaining `object` column. This lets pandas infer the most appropriate nullable extension type (e.g. `StringDtype`, `Int64`) automatically.

#### `fix_deposit_insurance(df) → pd.DataFrame`

Cleans `deposit` and `insurance` by stripping commas, replacing `"nan"` with `pd.NA`, and casting to `Int64`. Called after rental frequency imputation because both columns are rental-context fields.

---

### Stage 3 — Handle Missing Prices

#### `drop_missing_prices(df) → pd.DataFrame`

Drops all rows where `price` is null. Investigation confirmed these rows had no meaningful data across any other column — no district, no property type, nothing recoverable.

---

### Stage 4 — Level Imputation → `level_clean`

The raw `level` column started at ~6k filled values out of 76k. The pipeline imputes it in three layers and normalizes the result into `level_clean`, reaching 50k+ filled values.

#### Helper functions

##### `extract_floor_info(text: str) → str | None`

Applies a cascade of 9 English regex patterns to extract floor references from listing titles. Handles ordinal numbers (`2nd floor`), written numbers (`second floor`), directional hints (`ground floor`, `roof floor`), and compound forms (`two-floor`).

##### `extract_arabic_floor_info(title: str) → str | None`

Arabic equivalent. Searches for patterns anchored to `دور` (floor), `الدور`, and `بالدور`.

##### `impute_level(row: pd.Series) → str | None`

Rule-based imputation from `property_type` and `property_subtype`:

| property_type | property_subtype | Imputed value |
|---|---|---|
| `apartments` | `Penthouse` | `"top floor"` |
| `apartments` | `Roof` | `"roof"` |
| `villas` | any | `"Independent Unit"` |

##### `standardize_level(val) → int | str | None`

Maps raw imputed strings to a clean controlled vocabulary:

| Input keywords | Output |
|---|---|
| `ground`, `garden floor` | `"ground"` |
| `roof`, `top`, `last`, `high` | `"top"` |
| `recurring`, `repeated`, `typical` | `"recurring"` |
| `basement` | `"basement"` |
| `hdf` | `None` (referred to apartment square footage, not floor number) |
| Ordinal words (`first`, `second`, …) | Integer (`1`, `2`, …) |
| Numeric string | Integer, or `"top"` if > 50 |

##### `standardize_arabic_level(match: str) → int | str | None`

Arabic counterpart to `standardize_level`. Handles `متكرر` (recurring), ground floor variants (`الأرضي`, `ارضي`), and a hardcoded lookup of common Arabic ordinal floor phrases (دور أول → 1, دور تاني → 2, دور تالت → 3, etc.).

#### `build_level_clean(df) → pd.DataFrame`

Orchestrates the full imputation:

1. **Subtype logic** — calls `impute_level()` on every null row
2. **English title regex** — calls `extract_floor_info()` on titles containing `"floor"`
3. **Edge case** — hardcodes index `32481` as `"ground"` (only listing where `"level"` in title refers to floor number, not finishing quality)
4. **Garden-in-title** — marks `private garden = True` and re-applies subtype logic for listings mentioning `"with garden"`
5. **Standardization** — applies `standardize_level()` to produce `level_clean`
6. **Arabic imputation** — extracts Arabic floor phrases and maps them via `standardize_arabic_level()`

Drops the original `level` and intermediate `imputed_level` columns at the end.

---

### Stage 5 — Delivery Term Imputation

#### `classify_finishing(text: str) → str`

Classifies an Arabic listing title into one of:

| Output | Meaning |
|---|---|
| `"not_finished"` | بدون تشطيب |
| `"semi_finished"` | نص / نصف تشطيب, semi-finished |
| `"finished"` | Any quality tier — super lux, hotel, lux, or plain تشطيب |
| `"unknown"` | No recognizable finishing signal |

Applies patterns in priority order: `not_finished` → `semi_finished` → quality-tiered `finished` → generic `finished`.

#### `impute_delivery_term(df) → pd.DataFrame`

Three-pass imputation for rows where `delivery term` is null:

1. **English — core & shell:** title contains `"core & shell"` → `"core & shell"`
2. **English — finished variants:** title contains `"finished"` → resolved via regex into `"semi finished"`, `"not finished"`, or `"finished"`
3. **Arabic — تشطيب:** title is Arabic and contains تشطيب → classified via `classify_finishing()`

> Even after imputation, `delivery term` remains ~71% missing. It is excluded from the model feature matrix and retained for EDA and the RAG chatbot only.

---

### Stage 6 — Rental Frequency Imputation

#### `impute_rental_frequency(df) → pd.DataFrame`

Fills null `rental frequency` for all rental listings (`sale_or_rent == "rent"`) with `"monthly"`.

---

### Stage 7 — Derive `is_off_plan`

#### `derive_off_plan(df) → pd.DataFrame`

Creates a boolean column `is_off_plan` flagging listings whose `delivery date` is a future year (2026 or later). Drops the raw `delivery date` column afterward.

Garbage values found in the raw column (`"soon"`, `"within 6 months"`, `7`, `13`, etc.) are ignored and map to `False`.

---

### Stage 8 — Clean Bedrooms & Bathrooms

#### `clean_room_column(series: pd.Series, col_name: str) → pd.Series`

Normalizes a room count column:

1. Casts to `str` and strips whitespace
2. Replaces `"10+"` with `"10"`
3. Converts via `pd.to_numeric` — collapses `"3"` and `"3.0"` to the same value
4. Clips to `[1, 10]`
5. Casts to nullable `Int64`

#### `clean_room_columns(df) → pd.DataFrame`

Thin wrapper that applies `clean_room_column()` to both `bedrooms` and `bathrooms`.

---

### Stage 9 — Save

#### `save_cleaned_data(df, config) → None`

Writes the final DataFrame to Parquet at the path in `config["data_source"]["file_paths"]["cleaned_dataset"]`. Parquet is used over CSV to preserve nullable integer types, boolean dtypes, and `datetime64` without dtype drift on reload.

---

## Cleaning Decisions Summary

| Column | Action | Reason |
|---|---|---|
| `compound` | Dropped | 3 non-null values |
| `price type` | Dropped | Redundant |
| `area (mÂ²)` | Dropped | Encoding artifact duplicate |
| `monthly installments` | Dropped | Out of scope |
| `payment period (years)` | Dropped | Out of scope |
| `price` | Cleaned → `Int64` | Strip currency formatting |
| `listing_date` | Parsed → `datetime64` | Enable temporal features |
| `area (m²)` | Cleaned → `float` | Strip comma separators |
| `level` | Imputed (3 layers) → `level_clean` | 6k → 50k+ coverage |
| `delivery date` | Derived `is_off_plan` → dropped | ~75k nulls; future year is the only signal |
| `delivery term` | Partially imputed from titles | 71% missing; EDA and RAG only |
| `rental frequency` | Nulls → `"monthly"` | KDE confirmed price alignment with monthly |
| `deposit` / `insurance` | Cleaned → `Int64` | Strip comma separators |
| `bedrooms` / `bathrooms` | Normalized → `Int64` | Collapse float/int/string variants, cap at 10 |

---

## Findings & Notes

These are the key findings from the exploratory cleaning process. For the full analysis, KDE plots, and deeper investigation, see `data_cleaner.ipynb`.

**Level imputation:** Most of the ~44k listings that had no level info simply didn't include it in the listing at all — this is common for ground-floor apartments and mid-rise buildings in informal areas. It is not a scraping gap. The `private garden` flag turned out to be building-level information, not unit-level — advertisers apply it to any apartment with access to a shared garden or even a small landscape in front of the building.

**Delivery term:** Even after imputing ~13k values from titles, the column is still 71% missing. The missingness is not random — sellers of ready units rarely mention finishing in the title, so the missing values are likely finished units. This is retained for EDA and the RAG chatbot but excluded from the model.

**Rental frequency:** 2,430 rental listings had no frequency. KDE analysis confirmed their price distribution is nearly identical to monthly rentals. Daily rentals are a separate, clearly distinct segment (peaked at 2k–5k EGP vs ~50k median for monthly) and account for only 283 listings out of 14k total rentals. Imputing unknowns as monthly is well-justified.

**Deposit & insurance:** Only ~21% of rental listings have these fields filled. They are concentrated in New Cairo (948 listings) and Madinaty (938 listings) — together 63% of all deposit/insurance records. This reflects a compound rental culture norm in those areas, not a city-wide standard. Both columns are dropped from the model and retained for the RAG chatbot, which can use them to advise landlords listing in those districts.

**Off-plan:** The `delivery date` column had ~75k nulls and inconsistent garbage values. The only meaningful signal was whether the delivery year is in the future, which was extracted as the `is_off_plan` boolean. Off-plan properties price differently from ready units and this flag should be treated as a significant feature in modeling.

**Bilingual data:** The dataset mixes Arabic and English, often within the same title. Egyptian listings also use heavily colloquial Arabic (دور تالت instead of الدور الثالث, نص instead of نصف). Every regex-based extraction step had to handle both languages and informal spellings separately.

**New Cairo dominance:** New Cairo appears disproportionately across almost every segment — rental frequency unknowns, deposit/insurance records, level data gaps. Any model trained on this dataset should be evaluated per district if possible, to avoid New Cairo skewing the overall metrics.