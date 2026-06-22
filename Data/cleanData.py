import pandas as pd

# Clean data from immovlan properties

# import data from csv file
df = pd.read_csv("Data/Raw/PropertyData.csv", index_col=0)

# 1. standardise adress
df["street"] = df["street"].str.lower()

# 2. fix types
df[~df["livable_surface"].isna()]["livable_surface"].astype(int)

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

# --- DATE ---
#df['availability'] = pd.to_datetime(df['availability'], errors='coerce')

# --- STRING ---
str_cols = ['street']
for col in str_cols:
    df[col] = df[col].astype('string')

# 3. fix longitude/latitude that are swapped


# 4. remove data with values out of bounds
# price
# livable_surface
# terrasse
# garage
# land_surface
# energy_consumption
# garden

# 5. remove duplicates

# 6. separate properties to rent and to sale
