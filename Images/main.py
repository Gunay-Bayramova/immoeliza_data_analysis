import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import scipy.stats as stats
import warnings
warnings.filterwarnings('ignore')

# ── Shared style ─────────────────────────────────────────────────────────────
sns.set_theme(style='whitegrid', palette='muted', font_scale=1.1)
plt.rcParams.update({
    'figure.dpi': 120,
    'figure.figsize': (9, 5),
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.titleweight': 'bold',
    'axes.titlesize': 13,
})

# ── Colour palette we'll reuse ────────────────────────────────────────────────
BLUE   = '#2166ac'
ORANGE = '#d6604d'
GREEN  = '#4dac26'
GREY   = '#878787'
PALETTE = [BLUE, ORANGE, GREEN, '#9970ab', '#bf812d']

print("Libraries loaded ✅")
print(f"  matplotlib {plt.matplotlib.__version__}")
print(f"  seaborn    {sns.__version__}")

# Import cleaned data sets
dfr = pd.read_csv("../Data/Clean/RentCleanForAnalysis.csv")
dfs = pd.read_csv("../Data/Clean/SaleCleanForAnalysis.csv")

print(f"Dataset loaded: {dfr.shape[0]} properties to rent × {dfr.shape[1]} columns")
print(f"{len(dfr[dfr["property_type"]=="House"])/len(dfr)*100:.1f} % houses - " \
      f"{len(dfr[dfr["property_type"]=="Appartment"])/len(dfr)*100:.1f} % apartments")
print("-"*20)
print(f"Dataset loaded: {dfs.shape[0]} properties for sale × {dfs.shape[1]} columns")
print(f"{len(dfs[dfs["property_type"]=="House"])/len(dfs)*100:.1f} % houses - " \
      f"{len(dfs[dfs["property_type"]=="Appartment"])/len(dfs)*100:.1f} % apartments")

# Plot distribution of available values

cats = list(dfr.columns)
valsR = (1-dfr.isnull().sum()/len(dfr))*100
valsS = (1-dfs.isnull().sum()/len(dfs))*100

x = np.arange(len(cats))
width = 0.35
plt.bar(x - width/2, valsR, width, color=BLUE,label="Rents", edgecolor=None, linewidth=0)
plt.bar(x + width/2, valsS, width, color=ORANGE,label="Sales", edgecolor=None, linewidth=0)
plt.xticks(x,cats,rotation=90)
plt.title('Proportions of available values')
plt.xlabel("columns")
plt.ylabel("Availability (%)")
plt.legend()
plt.tight_layout()
plt.savefig("available_values.jpg")
plt.close()

# remove variables available for less than 60 %

dfr = dfr[['longitude', 'latitude', 'transaction_type', 'price', 'property_type', 'property_subtype', \
           'seller_id', 'postal_code', 'property_condition', 'livable_surface', 'number_of_bedrooms', \
            'number_of_bathrooms', 'elevator', 'furnished', 'province', 'street', 'street_number']]
dfs = dfs[['longitude', 'latitude', 'transaction_type', 'price', 'property_type', 'property_subtype', \
           'seller_id', 'postal_code', 'property_condition', 'livable_surface', 'number_of_bedrooms', \
            'number_of_bathrooms', 'elevator', 'furnished', 'province', 'street', 'street_number']]

#### Graph 1 : heat map

numerical = dfs[['price', 'livable_surface', 'number_of_bedrooms', 'number_of_bathrooms']]
corr = numerical.corr(method="spearman")

fig, ax = plt.subplots(figsize=(8, 6))
mask = np.triu(np.ones_like(corr, dtype=bool))  # hide upper triangle (redundant)

ax_labels = ["Price","Livable surface","Nb of bedrooms","Nb of bathrooms"]
sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='RdBu_r',
            center=0, vmin=-1, vmax=1, square=True,
            linewidths=0.5, ax=ax, cbar_kws={'shrink': 0.8},
            annot_kws={'size': 10}, xticklabels=ax_labels, yticklabels=ax_labels)

ax.set_title('How do variables have impact on each other ?', fontweight='bold')
plt.tight_layout()
plt.savefig('heatmap.jpg')
plt.close()

#### Graph 2 : scatter plot for sales

dfscatter = dfs 
variable = 'livable_surface' # 'livable_surface', 'number_of_bedrooms' or 'number_of_bathrooms'

plt.scatter(dfscatter[dfscatter["property_type"]=="House"][variable], \
            dfscatter[dfscatter["property_type"]=="House"]['price'], \
                alpha=0.35, color=BLUE, s=2, label = "Houses")
plt.scatter(dfscatter[dfscatter["property_type"]=="Appartment"][variable], \
            dfscatter[dfscatter["property_type"]=="Appartment"]['price'], \
                alpha=0.35, color=ORANGE, s=2, label = "Apartments")
df_cor = dfscatter[['price',variable,'property_type']].dropna(how='any')
# Add regression line
mh, bh = np.polyfit(df_cor[df_cor["property_type"]=="House"][variable], df_cor[df_cor["property_type"]=="House"]['price'], 1)
x_lineh = np.linspace(df_cor[df_cor["property_type"]=="House"][variable].min(), df_cor[df_cor["property_type"]=="House"][variable].max(), 100)
plt.plot(x_lineh, mh*x_lineh + bh, color=BLUE, lw=2.5, label=f'Slope: +€{mh:.0f}/m²')
ma, ba = np.polyfit(df_cor[df_cor["property_type"]=="Appartment"][variable], df_cor[df_cor["property_type"]=="Appartment"]['price'], 1)
x_linea = np.linspace(df_cor[df_cor["property_type"]=="Appartment"][variable].min(), df_cor[df_cor["property_type"]=="Appartment"][variable].max(), 100)
plt.plot(x_linea, ma*x_linea + ba, color=ORANGE, lw=2.5, label=f'Slope: +€{ma:.0f}/m²')
plt.xlim((0,400))
plt.ylim((0,2e6))
plt.xlabel('Livable surface (m²)')
plt.ylabel('Price (€)')
plt.title(f'Price increases with livable surface')
plt.gca().yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f'€{x/1000:.0f}k'))
plt.legend()
plt.tight_layout()
plt.savefig('scatter_sales.jpg')
plt.close()

#### Graph 3 : scatter plot for rents

dfscatter = dfr 
variable = 'livable_surface' # 'livable_surface', 'number_of_bedrooms' or 'number_of_bathrooms'

plt.scatter(dfscatter[dfscatter["property_type"]=="House"][variable], \
            dfscatter[dfscatter["property_type"]=="House"]['price'], \
                alpha=0.35, color=BLUE, s=2, label = "Houses")
plt.scatter(dfscatter[dfscatter["property_type"]=="Appartment"][variable], \
            dfscatter[dfscatter["property_type"]=="Appartment"]['price'], \
                alpha=0.35, color=ORANGE, s=2, label = "Apartments")
df_cor = dfscatter[['price',variable,'property_type']].dropna(how='any')
# Add regression line
mh, bh = np.polyfit(df_cor[df_cor["property_type"]=="House"][variable], df_cor[df_cor["property_type"]=="House"]['price'], 1)
x_lineh = np.linspace(df_cor[df_cor["property_type"]=="House"][variable].min(), df_cor[df_cor["property_type"]=="House"][variable].max(), 100)
plt.plot(x_lineh, mh*x_lineh + bh, color=BLUE, lw=2.5, label=f'Slope: +€{mh:.0f}/m²')
ma, ba = np.polyfit(df_cor[df_cor["property_type"]=="Appartment"][variable], df_cor[df_cor["property_type"]=="Appartment"]['price'], 1)
x_linea = np.linspace(df_cor[df_cor["property_type"]=="Appartment"][variable].min(), df_cor[df_cor["property_type"]=="Appartment"][variable].max(), 100)
plt.plot(x_linea, ma*x_linea + ba, color=ORANGE, lw=2.5, label=f'Slope: +€{ma:.0f}/m²')
plt.xlim((0,400))
plt.ylim((0,6000))
plt.xlabel('Livable surface (m²)')
plt.ylabel('Price (€)')
plt.title(f'Price increases with livable surface')
plt.gca().yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f'€{x/1000:.0f}k'))
plt.legend()
plt.tight_layout()
plt.savefig('scatter_rents.jpg')
plt.close()

#### Graph 4 : box plot for rents

order = list(dfr["province"].astype("category").cat.categories)
median_price_per_province = dfr.groupby("province")["price"].median().sort_values()

sns.boxplot(data=dfr, x='province', y='price', log_scale=True, order=median_price_per_province.index,
            linewidth=1.5,
            flierprops=dict(marker='o', markersize=4, alpha=0.5))
plt.gca().yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f'€{x/1000:.0f}k'))
plt.title('Rent prices per province')
plt.xlabel('Province')
plt.ylabel('Rent price (k€)')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig('box_rents.jpg')
plt.close()

#### Graph 5 : box plot for sales

order = list(dfs["province"].astype("category").cat.categories)
median_price_per_province = dfs.groupby("province")["price"].median().sort_values()

sns.boxplot(data=dfs, x='province', y='price', log_scale=True, order=median_price_per_province.index,
            linewidth=1.5,
            flierprops=dict(marker='o', markersize=4, alpha=0.5))
plt.gca().yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f'€{x/1000:.0f}k'))
plt.title('Sale prices per province')
plt.xlabel('Province')
plt.ylabel('Sale price (k€)')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig('box_sales.jpg')
plt.close()

