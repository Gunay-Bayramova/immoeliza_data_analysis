from pathlib import Path
import pandas as pd

RAW_FILES = [Path("Data/Raw/rent_raw.csv"), Path("Data/Raw/sale_raw.csv")]
OUTPUT_DIR = Path("Data/Raw")

SUSPICIOUS_COLUMNS = [
    "longitude",
    "latitude",
    "price",
    "property_type",
    "property_subtype",
    "postal_code",
    "street",
    "street_number",
    "livable_surface",
]

def mini_cleaning(df):
    df_clean = df.copy()

    # Converts text columns
    str_cols  = [
        "property_type",
        "property_subtype",
        "street",
        "street_number",
        "postal_code",
    ]
    for col in str_cols:
        df_clean[col] = (
            df_clean[col]
            .astype("string")
            .str.strip()
            .str.lower()
            .str.replace(r"\s+", " ", regex=True)
        )
    
    # Converts float columns
    float_cols = [
        "longitude",
        "latitude",
    ]
    for col in float_cols:
        df_clean[col] = df_clean[col].astype(float)
    
    # Converts integer columns
    integer_columns = [
        "price",
        "livable_surface",
    ]
    for col in integer_columns:
        df_clean[col] = pd.to_numeric(df_clean[col]).astype("Int64")

    return df_clean

def check_duplicates(filepath):

    # Load CSV
    df = pd.read_csv(filepath)
    df = df.rename(columns={df.columns[1]: "referenceID"})
    df = df.drop(columns=[df.columns[0]])

    # Header printing
    print(f"\n{'=' * 60}")
    print(f"Duplicate check for: {filepath}")
    print(f"{'=' * 60}")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    # Check for exact duplicates
    exact_duplicates = df.duplicated(keep=False) # Is the row a duplicate of another row? keep=False marks every row that has dup as True
    extra_copies = df.duplicated(keep="first").sum() # "How many duplicate rows exist after keeping the first occurrence?" Counts all True, excludes first occurence
    
    print("\nExact duplicates:")
    print("Rows involved:", exact_duplicates.sum())
    print("Extra duplicate rows:", extra_copies)

    # Check for potential duplicates
    df_clean = mini_cleaning(df)
    suspicious_dupes = df_clean.duplicated(subset=SUSPICIOUS_COLUMNS, keep=False)
    extra_suspicious = df_clean.duplicated(subset=SUSPICIOUS_COLUMNS, keep="first").sum()

    print("\nSuspicious duplicates:")
    print("Rows involved:", suspicious_dupes.sum())
    print("Extra duplicate rows:", extra_suspicious)

    export_suspicious_dupes(df, df_clean, suspicious_dupes, filepath)

def export_suspicious_dupes(df, df_clean, sus_dupes, filepath):
    duplicate_keys = df_clean.loc[sus_dupes, SUSPICIOUS_COLUMNS]
    
    # Groups dupes by group 
    dupe_group_ids = (
        duplicate_keys
        .groupby(SUSPICIOUS_COLUMNS, dropna=False)
        .ngroup() + 1
    )

    # Copies from the ORIGINAL df not df_clean
    duplicates_to_review = df.loc[sus_dupes].copy()
    duplicates_to_review.insert(
        0,
        "duplicate_group_id",
        dupe_group_ids.values
    )
    duplicates_to_review = duplicates_to_review.sort_values(by="duplicate_group_id")

    # Creates a column to store decision to keep/remove
    duplicates_to_review["decision"] = ""

    # Saves to .csv
    output_path = OUTPUT_DIR / f"{filepath.stem}_sus_dupes.csv"
    duplicates_to_review.to_csv(output_path, index=False)
    print(f"Suspicious duplicates exported to: {output_path}")


def main():
    for file_path in RAW_FILES:
        check_duplicates(file_path)

if __name__ == "__main__":
    main()