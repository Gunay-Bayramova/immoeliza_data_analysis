from pathlib import Path
import pandas as pd

RAW_CSV = Path("Data/Raw/PropertyData.csv")
OUTPUT_DIR = Path("Data/Raw")

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True) # Safety check for missing directory

    df = pd.read_csv(RAW_CSV)

    df["og_row_number"] = df.index + 2

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

if __name__ == "__main__":
    main()