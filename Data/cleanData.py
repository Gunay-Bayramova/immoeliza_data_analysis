import pandas as pd
from pathlib import Path

# Clean data from immovlan properties
RAW_FILE = Path("Data/Raw/PropertyData.csv")
OUTPUT_DIR = Path("Data/Clean")

# import data from csv file
df = pd.read_csv("Data/Raw/PropertyData.csv", index_col=0)

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
def get_index_of_rows_out_of_bounds(df, column : str, min_val, max_val) -> list[str]:
    rows = df[~df[column].between(min_val, max_val)]
    print(f"Remove {len(rows)} rows where {column} is smaller than {min_val} or bigger than {max_val}.")
    print(rows[column])
    return rows.index

# price
length = len(df)
df = df.drop(get_index_of_rows_out_of_bounds(df[df["transaction_type"]=="Rent"], "price", 100, 15000))
df = df.drop(get_index_of_rows_out_of_bounds(df[df["transaction_type"]=="Sale"], "price", 10000, 10000000))
# livable_surface
df = df.drop(get_index_of_rows_out_of_bounds(df, "livable_surface", 5, 2000))
# terrace
df = df.drop(get_index_of_rows_out_of_bounds(df, "terrace", 1, 1000))
# garage
df = df.drop(get_index_of_rows_out_of_bounds(df, "garage", 0, 10))
# land_surface
df = df.drop(get_index_of_rows_out_of_bounds(df, "land_surface", 4, 100000))
# energy_consumption
df = df.drop(get_index_of_rows_out_of_bounds(df, "energy_consumption", 1000, 1000000))
# garden
df = df.drop(get_index_of_rows_out_of_bounds(df, "garden", 1, 100000))

# 5. remove duplicates

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

def check_duplicates(df):

    # Header printing
    print(f"\n{'=' * 60}")
    print(f"Duplicate check")
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
    suspicious_dupes = df.duplicated(subset=SUSPICIOUS_COLUMNS, keep=False)
    extra_suspicious = df.duplicated(subset=SUSPICIOUS_COLUMNS, keep="first").sum()
    print("\nSuspicious duplicates:")
    print("Rows involved:", suspicious_dupes.sum())
    print("Extra duplicate rows:", extra_suspicious)

    # Keep first occurrence of each suspicious duplicates and removes the others
    df_deduped = remove_suspicious_dupes(df)
    print("Rows after removing suspicious duplicates:", len(df_deduped))
    print("Rows removed:", len(df) - len(df_deduped))
    return df_deduped

def remove_suspicious_dupes(df):
    extra_dupes = df.duplicated(subset=SUSPICIOUS_COLUMNS, keep="first")
    df_deduped = df.loc[~extra_dupes].copy() # !! Reverse selection 
    return df_deduped

# 6. separate properties to rent and to sale
def separate_by_type(df):

    df = df.copy()

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

    sale_df.to_csv(OUTPUT_DIR/"SaleClean.csv", index=False)
    rent_df.to_csv(OUTPUT_DIR/"RentClean.csv", index=False)

    print("\nFiles created:")
    print(OUTPUT_DIR/"SaleClean.csv")
    print(OUTPUT_DIR/"RentClean.csv")
    print(" FINISHED ".center(60, "="))

df_deduped = check_duplicates(df)
separate_by_type(df_deduped)

