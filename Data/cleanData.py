import pandas as pd
from pathlib import Path

# Clean data from immovlan properties

# import data from csv file
df = pd.read_csv("./Raw/PropertyData.csv", index_col=0)

# 1. standardise adress
df["street"] = df["street"].str.lower()

# 2. fix types

# --- CATEGORICAL ---
cat_cols = ['transaction_type', 'province', 'property_type', 
            'property_subtype', 'property_condition']
for col in cat_cols:
    df[col] = pd.Categorical(df[col])

# --- INTEGER ---
int_cols = ['price', 'date_of_construction', 'land_surface', 'livable_surface',
            'energy_consumption', 'number_of_bedrooms', 'number_of_bathrooms',
            'garage', 'garden', 'terrace', 'postal_code', 'street_number', 'seller_id']
for col in int_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')  # Int64 handles NaN

# --- BOOLEAN ---
bool_cols = ['elevator', 'swimming_pool', 'balcony', 'furnished']
for col in bool_cols:
    df[col] = df[col].astype('boolean')  # nullable boolean, handles NaN

# --- FLOAT ---
float_cols = ['latitude', 'longitude']
for col in float_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# --- STRING ---
str_cols = ['street']
for col in str_cols:
    df[col] = df[col].astype('string').str.strip().str.replace(r"\s+", " ", regex=True)

# 3. fix longitude/latitude that are swapped
swapped = df["longitude"] > 10
long_lat = df[swapped][["longitude","latitude"]].copy()
df.loc[swapped,["longitude","latitude"]] = long_lat[["latitude","longitude"]].values

# 4. remove data with values out of bounds
def removeDataOutOfBounds(df, column : str, min_val, max_val):
    rows = df[~df[column].between(min_val, max_val)]
    nbRows = len(df)
    df.drop(rows.index, inplace = True)
    print(f"Removed {nbRows-len(df)} rows where {column} is smaller than {min_val} or bigger than {max_val}.")
    print(rows[column])

# price
removeDataOutOfBounds(df[df["transaction_type"]=="Rent"], "price", 100, 15000)
removeDataOutOfBounds(df[df["transaction_type"]=="Sale"], "price", 1000, 10000000)
# livable_surface
removeDataOutOfBounds(df, "livable_surface", 5, 2000)
# terrace
removeDataOutOfBounds(df, "terrace", 1, 1000)
# garage
removeDataOutOfBounds(df, "garage", 0, 10)
# land_surface
removeDataOutOfBounds(df, "land_surface", 4, 100000)
# energy_consumption
removeDataOutOfBounds(df, "energy_consumption", 1000, 1000000)
# garden
removeDataOutOfBounds(df, "garden", 1, 100000)

# 5. remove duplicates

## Duplicates check
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

    # export_suspicious_dupes(df, df_clean, suspicious_dupes, filepath)

    # Keep first occurrence of each suspicious duplicates and removes the others
    df_deduped = remove_suspicious_dupes(df, df_clean)
    output_path = OUTPUT_DIR/f"{filepath.stem}_deduped.csv"
    df_deduped.to_csv(output_path, index=False)
    print(f"\nDeduped file saved to: {output_path}")
    print("Rows after removing suspicious duplicates:", len(df_deduped))
    print("Rows removed:", len(df) - len(df_deduped))

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

def remove_suspicious_dupes(df, df_clean):
    extra_dupes = df_clean.duplicated(subset=SUSPICIOUS_COLUMNS, keep="first")
    df_deduped = df.loc[~extra_dupes].copy() # !! Reverse selection 
    return df_deduped

# def main():
#     for file_path in RAW_FILES:
#         check_duplicates(file_path)

# if __name__ == "__main__":
#     main()

# 6. separate properties to rent and to sale
RAW_CSV = Path("Data/Raw/PropertyData.csv")
OUTPUT_DIR = Path("Data/Raw")

def separate_by_type():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True) # Safety check for missing directory

    df = pd.read_csv(RAW_CSV)

    # df["og_row_number"] = df.index + 2

    df["transaction_type"] = df["transaction_type"].astype(str).str.strip()
    
    print()
    print(" SEPARATING RENT FROM SALE ".center(60, "="))
    print("Initial df shape: ", df.shape)
    print("\nTransaction types:")
    print(df["transaction_type"].value_counts(dropna=False))

    sale_df = df[df["transaction_type"] == "Sale"].copy()
    rent_df = df[df["transaction_type"] == "Rent"].copy()

    print("\nsale_df shape: ", sale_df.shape)
    print("rent_df shape: ", rent_df.shape)

    sale_df.to_csv(OUTPUT_DIR/"sale_raw.csv")
    rent_df.to_csv(OUTPUT_DIR/"rent_raw.csv")

    print("\nFiles created:")
    print(OUTPUT_DIR/"sale_raw.csv")
    print(OUTPUT_DIR/"rent_raw.csv")
    print(" FINISHED ".center(60, "="))


