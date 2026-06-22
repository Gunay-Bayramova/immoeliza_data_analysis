import pandas as pd

# Clean data from immovlan properties

# import data from csv file
df = pd.read_csv("./Raw/PropertyData.csv", index_col=0)

# 1. standardise adress
df["street"] = df["street"].str.lower()

# 2. fix types
df[~df["livable_surface"].isna()]["livable_surface"].astype(int)

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