import re
import yaml
import numpy as np
import pandas as pd

from src.utils import get_logger

logger = get_logger('cleaning_pipline')




def load_data(config: dict) -> pd.DataFrame:
    path = config["data_source"]["file_paths"]["raw_file"]
    try:
        df = pd.read_csv(path)
        logger.info(f"Loaded raw data from '{path}' — shape: {df.shape}")
        return df
    except Exception as e:
        logger.error(f"Failed to load data from '{path}': {e}")
        raise




def drop_irrelevant_columns(df: pd.DataFrame) -> pd.DataFrame:
    cols = ["compound", "area (mÂ²)", "monthly installments", "payment period (years)", "price type"]
    try:
        df = df.drop(columns=cols)
        logger.info(f"Dropped columns: {cols}")
        return df
    except Exception as e:
        logger.error(f"Failed to drop irrelevant columns: {e}")
        raise




def fix_boolean_features(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    try:
        cols = config["data_source"]["realstate_website"]["features_list"]
        df[cols] = df[cols].astype(bool)
        logger.info(f"Cast {len(cols)} feature columns to bool")
        return df
    except Exception as e:
        logger.error(f"Failed to cast boolean features: {e}")
        raise


def fix_listing_date(df: pd.DataFrame) -> pd.DataFrame:
    try:
        df["listing_date"] = pd.to_datetime(df["listing_date"], errors="coerce")
        n_nulls = df["listing_date"].isna().sum()
        logger.info(f"Parsed 'listing_date' — unparseable values coerced to NaT: {n_nulls}")
        return df
    except Exception as e:
        logger.error(f"Failed to parse listing_date: {e}")
        raise


def fix_price(df: pd.DataFrame) -> pd.DataFrame:
    try:
        df["price"] = (
            df["price"]
            .str.replace(",", "", regex=False)
            .str.replace("EGP", "", regex=False)
            .replace("nan", pd.NA)
            .astype("Int64")
        )
        logger.info("Cleaned 'price' column → Int64")
        return df
    except Exception as e:
        logger.error(f"Failed to clean price column: {e}")
        raise


def fix_delivery_date(df: pd.DataFrame) -> pd.DataFrame:
    try:
        df["delivery date"] = df["delivery date"].astype(str)
        logger.info("Cast 'delivery date' to string (kept as-is for downstream derivation)")
        return df
    except Exception as e:
        logger.error(f"Failed to cast delivery date: {e}")
        raise


def fix_area(df: pd.DataFrame) -> pd.DataFrame:
    try:
        df["area (m²)"] = (
            df["area (m²)"]
            .astype(str)
            .str.replace(",", "", regex=False)
            .replace("nan", pd.NA)
            .pipe(pd.to_numeric, errors="coerce")
        )
        logger.info("Cleaned 'area (m²)' column")
        return df
    except Exception as e:
        logger.error(f"Failed to clean area column: {e}")
        raise


def fix_object_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    try:
        object_cols = df.select_dtypes(include="object").columns.tolist()
        for col in object_cols:
            df[col] = df[col].convert_dtypes()
        logger.info(f"Converted {len(object_cols)} object columns with convert_dtypes()")
        return df
    except Exception as e:
        logger.error(f"Failed to convert object dtypes: {e}")
        raise


def fix_deposit_insurance(df: pd.DataFrame) -> pd.DataFrame:
    try:
        df["deposit"] = (
            df["deposit"]
            .str.replace(",", "", regex=False)
            .replace("nan", pd.NA)
            .astype("Int64")
        )
        df["insurance"] = (
            df["insurance"]
            .str.replace(",", "", regex=False)
            .replace("nan", pd.NA)
            .astype("Int64")
        )
        logger.info("Cleaned 'deposit' and 'insurance' columns → Int64")
        return df
    except Exception as e:
        logger.error(f"Failed to clean deposit/insurance columns: {e}")
        raise



def drop_missing_prices(df: pd.DataFrame) -> pd.DataFrame:
    try:
        no_price_idx = df[df["price"].isnull()].index
        df = df.drop(index=no_price_idx)
        logger.info(f"Dropped {len(no_price_idx)} rows with missing price")
        return df
    except Exception as e:
        logger.error(f"Failed to drop missing-price rows: {e}")
        raise



def extract_floor_info(text: str) -> str | None:
    text = text.lower()
    patterns = [
        r"\b(1|2|3|4|5|6|basement|10th|upper|high|last|recurring|top|afirst|garden|ground|repetitive|repeated|rep|first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|eleventh|twelfth)\s+floor(?:s)?\b",
        r"\b\d+(?:st|nd|rd|th)\s+floor\b",
        r"\bfloor\s+\d+\b",
        r"\broof\s+floor\b",
        r"\btypical\s+floor\b",
        r"\b(?:one|two|three|\d+)[-\s]?floor\b",
        r"(\w+)-floor",
        r"floor:\s*[^a-zA-Z\d]*(\S+)",
        r"\b(\w+)\s+floors\s",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group()
    return None


def extract_arabic_floor_info(title: str) -> str | None:
    patterns = [
        r"بالدور\s*:?\s*\S+",
        r"الدور\s*:?\s*\S+",
        r"دور\s+\S+",
    ]
    for pattern in patterns:
        match = re.search(pattern, title, re.IGNORECASE)
        if match:
            return match.group()
    return None


def impute_level(row: pd.Series) -> str | None:
    if pd.isna(row["imputed_level"]):
        if row["property_type"] == "apartments":
            if row["property_subtype"] == "Penthouse":
                return "top floor"
            if row["property_subtype"] == "Roof":
                return "roof"
        elif row["property_type"] == "villas":
            return "Independent Unit"
    return None


def standardize_level(val) -> int | str | None:
    if pd.isna(val):
        return None

    val = str(val).lower().strip()

    if any(x in val for x in ["ground", "garden floor", "floor:** gro"]):
        return "ground"
    if any(x in val for x in ["roof", "top", "last", "highest", "high", "99"]):
        return "top"
    if any(x in val for x in ["recurring", "repeated", "repetitive", "typical", "full"]):
        return "recurring"
    if "basement" in val:
        return "basement"
    if "hdf" in val:
        return None

    word_map = {
        "one": 1, "first": 1, "afirst": 1,
        "two": 2, "second": 2,
        "three": 3, "third": 3,
        "four": 4, "fourth": 4,
        "five": 5, "fifth": 5,
        "six": 6, "sixth": 6,
        "seven": 7, "seventh": 7,
        "eight": 8, "eighth": 8,
        "nine": 9, "ninth": 9,
        "ten": 10, "tenth": 10,
        "eleven": 11, "eleventh": 11,
        "top": 99,
        "floor:** se": 2,
    }
    for word, num in word_map.items():
        if word in val:
            return num

    match = re.search(r"\d+", val)
    if match:
        num = int(match.group())
        return "top" if num > 50 else num

    return val


def standardize_arabic_level(match: str) -> int | str | None:
    if pd.isna(match):
        return None
    if "متكرر" in match:
        return "recurring"
    if any(x in match for x in ["الأرضي", "ارضي", "الارضى"]):
        return "ground"
    word_map = {
        "دور أول": 1, "الدور الأول": 1, "دور اول": 1, "دور ثالث": 3,
        "دور تاني": 2, "دور تالت": 3,
        "دور ثانى": 2,
        "الدور: الثالث": 3,
        "دور رابع": 4, "دور 4": 4,
        "الدور ١١": 11, "بالدور 11قبل": 11, "دور عاشر": 10,
        "دور حادى": 11,
    }
    for word, val in word_map.items():
        if word in match:
            return val
    return pd.NA


def build_level_clean(df: pd.DataFrame) -> pd.DataFrame:
    try:
        df["imputed_level"] = df["level"]

        for index, row in df.iterrows():
            if pd.isna(row["imputed_level"]):
                imputed = impute_level(row)
                if imputed is not None:
                    df.loc[index, "imputed_level"] = imputed
                elif "floor" in str(row["title"]).lower():
                    match = extract_floor_info(row["title"])
                    if match:
                        df.loc[index, "imputed_level"] = match

        # Edge case: index 32481
        if 32481 in df.index:
            df.loc[32481, "imputed_level"] = "ground"

        # Garden-in-title imputation
        null_imputed = df[df["imputed_level"].isnull()]
        garden_in_title = null_imputed[null_imputed["title"].str.contains("with garden", case=False, na=False)]
        for index, row in garden_in_title.iterrows():
            df.loc[index, "private garden"] = True
            level = impute_level(df.loc[index])
            if level is not None:
                df.loc[index, "imputed_level"] = level

        df["level_clean"] = df["imputed_level"].apply(standardize_level)

        # Arabic floor imputation
        arabic_pattern = r"[\u0600-\u06FF]"
        arabic_mask = df["title"].str.contains(arabic_pattern, regex=True, na=False)
        arabic_df = df[arabic_mask]
        no_level_arabic = arabic_df[arabic_df["level_clean"].isnull()]
        no_level_arabic = no_level_arabic[no_level_arabic["title"].str.contains("دور", na=False)]

        floor_items = []
        for index, row in no_level_arabic.iterrows():
            match = extract_arabic_floor_info(row["title"])
            if match:
                floor_items.append({"index": index, "match": match})

        for item in floor_items:
            item["match"] = standardize_arabic_level(item["match"])

        for item in floor_items:
            df.loc[item["index"], "level_clean"] = item["match"]

        df["level_clean"] = df["level_clean"].convert_dtypes()
        df = df.drop(columns=["level", "imputed_level"])

        logger.info("Built 'level_clean' column and dropped raw level columns")
        return df
    except Exception as e:
        logger.error(f"Failed to build level_clean: {e}")
        raise




def classify_finishing(text: str) -> str:
    if not isinstance(text, str):
        return "unknown"

    t = text.strip()

    if re.search(r"بدون\s*تشطيب", t):
        return "not_finished"
    if re.search(r"unfurnished.*old reservation", t, re.IGNORECASE):
        return "not_finished"

    semi_patterns = [
        r"نص\s*تشطيب", r"نصف\s*تشطيب",
        r"semi.?finished", r"3\s*/\s*4\s*تشطيب",
    ]
    if any(re.search(p, t, re.IGNORECASE) for p in semi_patterns):
        return "semi_finished"

    ultra_patterns = [r"الترا\s*سوبر\s*لوكس", r"التر\s*سوبر\s*لوكس", r"ultra\s*super\s*lux"]
    if any(re.search(p, t, re.IGNORECASE) for p in ultra_patterns):
        return "finished"

    high_patterns = [r"هاي\s*سوبر\s*لوكس", r"هاي\s*لوكس", r"high\s*super\s*lux"]
    if any(re.search(p, t, re.IGNORECASE) for p in high_patterns):
        return "finished"

    super_lux_patterns = [r"سوبر\s*لوكس", r"سوبرلوكس", r"super\s*lux"]
    if any(re.search(p, t, re.IGNORECASE) for p in super_lux_patterns):
        return "finished"

    hotel_patterns = [r"تشطيب\s*فندق[يى]", r"فندق[يى]\s*تشطيب", r"تشطيب\s*VIP", r"VIP\s*تشطيب"]
    if any(re.search(p, t, re.IGNORECASE) for p in hotel_patterns):
        return "finished"

    lux_patterns = [r"تشطيب\s*(لوكس|الترا\s*لوكس)", r"لوكس\s*تشطيب"]
    if any(re.search(p, t, re.IGNORECASE) for p in lux_patterns):
        return "finished"

    generic_finished_patterns = [
        r"تشطيب\s*كامل", r"كامل\s*التشطيب", r"كامله\s*التشطيب", r"بالتشطيب",
        r"تشطيب\s*(فاخر|مميز|خاص|راقي|راقٍ|جديد|ممتاز|كلاسيك)",
        r"(فاخر|مميز|خاص|راقي|ممتاز)\s*تشطيب",
        r"تشطيبات\s*(خاصة|خاصه|مميزة|راقية)",
        r"تشطيب\s*شركة", r"تشطيب\s*مجموعة",
        r"with\s*finishing", r"full\s*finishing", r"fully\s*(equipped|finished)",
        r"تشطيب",
    ]
    if any(re.search(p, t, re.IGNORECASE) for p in generic_finished_patterns):
        return "finished"

    return "unknown"


def impute_delivery_term(df: pd.DataFrame) -> pd.DataFrame:
    try:
        semi_finished_pattern = r"semi[\s\-]*finished"
        not_finished_pattern = r"not[\s\-]*finished"

        # English: core & shell
        core_shell_mask = df["title"].str.contains("core & shell", case=False, na=False) & df["delivery term"].isnull()
        df.loc[core_shell_mask, "delivery term"] = "core & shell"

        # English: finished / semi / not
        titles_mask = df["title"].str.contains("finished", case=False, na=False) & df["delivery term"].isnull()
        for index, row in df[titles_mask].iterrows():
            title = row["title"]
            if re.search(semi_finished_pattern, title, re.IGNORECASE):
                df.loc[index, "delivery term"] = "semi finished"
            elif re.search(not_finished_pattern, title, re.IGNORECASE):
                df.loc[index, "delivery term"] = "not finished"
            elif "finished" in title.lower():
                df.loc[index, "delivery term"] = "finished"

        # Arabic: تشطيب
        arabic_pattern = r"[\u0600-\u06FF]"
        arabic_mask = df["title"].str.contains(arabic_pattern, regex=True, na=False)
        arabic_no_term = df[arabic_mask & df["delivery term"].isnull() & df["title"].str.contains("تشطيب", na=False)]
        for index, row in arabic_no_term.iterrows():
            result = classify_finishing(row["title"])
            df.loc[index, "delivery term"] = result

        logger.info("Imputed 'delivery term' from English and Arabic titles")
        return df
    except Exception as e:
        logger.error(f"Failed to impute delivery term: {e}")
        raise


def impute_rental_frequency(df: pd.DataFrame) -> pd.DataFrame:
    try:
        mask = df["rental frequency"].isnull() & (df["sale_or_rent"] == "rent")
        df.loc[mask, "rental frequency"] = "monthly"
        logger.info(f"Imputed {mask.sum()} missing 'rental frequency' values as 'monthly'")
        return df
    except Exception as e:
        logger.error(f"Failed to impute rental frequency: {e}")
        raise




def derive_off_plan(df: pd.DataFrame) -> pd.DataFrame:
    try:
        off_plan_values = ["2027", "2028", "2029", "2030", "2027.0", "2028.0"]
        df["is_off_plan"] = df["delivery date"].isin(off_plan_values)
        df = df.drop(columns=["delivery date"])
        logger.info("Derived 'is_off_plan' boolean and dropped 'delivery date'")
        return df
    except Exception as e:
        logger.error(f"Failed to derive is_off_plan: {e}")
        raise


def clean_room_column(series: pd.Series, col_name: str) -> pd.Series:
    try:
        cleaned = (
            series
            .astype(str)
            .str.strip()
            .str.replace(r"^\s*10\+\s*$", "10", regex=True)
            .pipe(pd.to_numeric, errors="coerce")
            .clip(lower=1, upper=10)
            .astype("Int64")
        )
        n_nulls = cleaned.isna().sum()
        n_capped = (cleaned == 10).sum()
        logger.info(f"Cleaned '{col_name}' — nulls: {n_nulls} | values capped at 10: {n_capped}")
        return cleaned
    except Exception as e:
        logger.error(f"Failed to clean room column '{col_name}': {e}")
        raise


def clean_room_columns(df: pd.DataFrame) -> pd.DataFrame:
    df["bedrooms"] = clean_room_column(df["bedrooms"], "bedrooms")
    df["bathrooms"] = clean_room_column(df["bathrooms"], "bathrooms")
    return df


# ─────────────────────────────────────────────
# 9. Save
# ─────────────────────────────────────────────

def save_cleaned_data(df: pd.DataFrame, config: dict) -> None:
    path = config["data_source"]["file_paths"]["cleaned_dataset"]
    try:
        df.to_parquet(path, index=False)
        logger.info(f"Saved cleaned dataset to '{path}' — shape: {df.shape}")
    except Exception as e:
        logger.error(f"Failed to save cleaned dataset to '{path}': {e}")
        raise




def main():
    logger.info("Starting data cleaning pipeline")

    try:
        with open("../config.yaml", "r") as f:
            config = yaml.safe_load(f)
        logger.info("Loaded config.yaml")
    except Exception as e:
        logger.error(f"Failed to load config.yaml: {e}")
        raise

    df = load_data(config)

    df = drop_irrelevant_columns(df)

    df = fix_boolean_features(df, config)
    df = fix_listing_date(df)
    df = fix_price(df)
    df = fix_delivery_date(df)
    df = fix_area(df)
    df = fix_object_dtypes(df)

    df = drop_missing_prices(df)

    df = build_level_clean(df)

    df = impute_delivery_term(df)

    df = impute_rental_frequency(df)

    df = fix_deposit_insurance(df)

    df = derive_off_plan(df)

    df = clean_room_columns(df)

    save_cleaned_data(df, config)

    logger.info("Data cleaning pipeline completed successfully")


