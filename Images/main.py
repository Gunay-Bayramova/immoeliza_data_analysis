import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import scipy.stats as stats
import warnings
from matplotlib.patches import Circle
import matplotlib.patheffects as pe
from pyproj import Transformer
import contextily as cx

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

### Graph 6 : Map for sales in Belgium

df_map = dfs[
    dfs["latitude"].between(49.4, 51.6) &
    dfs["longitude"].between(2.5, 6.5)
].copy()

to_mercator = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
df_map["x"], df_map["y"] = to_mercator.transform(
    df_map["longitude"].values, df_map["latitude"].values
)

province_stats = (
    df_map.groupby("province")
    .agg(median_price=("price", "median"), x=("x", "mean"), y=("y", "mean"), n=("price", "size"))
    .reset_index()
)

x_range = df_map["x"].max() - df_map["x"].min()
RADIUS_MIN, RADIUS_MAX = x_range * 0.018, x_range * 0.060
pmin, pmax = province_stats["median_price"].min(), province_stats["median_price"].max()
t = (province_stats["median_price"] - pmin) / (pmax - pmin)
province_stats["radius"] = np.sqrt(RADIUS_MIN**2 + t * (RADIUS_MAX**2 - RADIUS_MIN**2))

anchors = province_stats[["x", "y"]].to_numpy().astype(float)
radii = province_stats["radius"].to_numpy()
positions = anchors.copy()
pad = x_range * 0.006
spring = 0.018

for _ in range(800):
    moved = False
    for i in range(len(positions)):
        for j in range(i + 1, len(positions)):
            dx, dy = positions[j, 0] - positions[i, 0], positions[j, 1] - positions[i, 1]
            dist = np.hypot(dx, dy)
            min_dist = radii[i] + radii[j] + pad
            if dist < min_dist:
                if dist < 1e-6:
                    dx, dy = np.random.uniform(-1, 1, 2)
                    dist = np.hypot(dx, dy)
                push = (min_dist - dist) / 2
                ux, uy = dx / dist, dy / dist
                positions[i] -= [ux * push, uy * push]
                positions[j] += [ux * push, uy * push]
                moved = True
    positions += (anchors - positions) * spring
    if not moved:
        break

for _ in range(300):
    moved = False
    for i in range(len(positions)):
        for j in range(i + 1, len(positions)):
            dx, dy = positions[j, 0] - positions[i, 0], positions[j, 1] - positions[i, 1]
            dist = np.hypot(dx, dy)
            min_dist = radii[i] + radii[j] + pad
            if dist < min_dist:
                if dist < 1e-6:
                    dx, dy = np.random.uniform(-1, 1, 2)
                    dist = np.hypot(dx, dy)
                push = (min_dist - dist) / 2
                ux, uy = dx / dist, dy / dist
                positions[i] -= [ux * push, uy * push]
                positions[j] += [ux * push, uy * push]
                moved = True
    if not moved:
        break

province_stats["cx_pos"], province_stats["cy_pos"] = positions[:, 0], positions[:, 1]
province_stats["displaced"] = (
    np.hypot(positions[:, 0] - anchors[:, 0], positions[:, 1] - anchors[:, 1]) > radii * 0.6
)

province_stats = province_stats.sort_values("radius", ascending=False).reset_index(drop=True)

plt.rcParams["font.family"] = "DejaVu Sans"
fig, ax = plt.subplots(figsize=(11, 9), dpi=130)
fig.patch.set_facecolor("white")

for _, row in province_stats.iterrows():
    if row["displaced"]:
        ax.plot([row["x"], row["cx_pos"]], [row["y"], row["cy_pos"]],
                color="#1d3557", linewidth=0.9, alpha=0.6, zorder=3)
        ax.scatter([row["x"]], [row["y"]], s=16, color="#1d3557", zorder=3)

shift = x_range * 0.0025
for i, row in province_stats.iterrows():
    z = 4 + i * 0.01
    ax.add_patch(Circle((row["cx_pos"] + shift, row["cy_pos"] - shift), row["radius"],
                         facecolor="black", edgecolor="none", alpha=0.10, zorder=z))
    ax.add_patch(Circle((row["cx_pos"], row["cy_pos"]), row["radius"],
                         facecolor="#2a4d7a", edgecolor="white", linewidth=1.8,
                         alpha=0.78, zorder=z + 0.005))
    ax.annotate(
        f"{row['province']}\n€{row['median_price']/1e3:.0f}k",
        (row["cx_pos"], row["cy_pos"]), ha="center", va="center",
        fontsize=8.3, fontweight="bold", color="white",
        path_effects=[pe.withStroke(linewidth=2.2, foreground="#1d3557")],
        zorder=z + 0.01,
    )

belgium_lons = [2.5, 6.5]
belgium_lats = [49.4, 51.6]
bx, by = to_mercator.transform(belgium_lons, belgium_lats)

margin = 0.04  
x_pad = (bx[1] - bx[0]) * margin
y_pad = (by[1] - by[0]) * margin

ax.set_xlim(bx[0] - x_pad, bx[1] + x_pad)
ax.set_ylim(by[0] - y_pad, by[1] + y_pad)

cx.add_basemap(ax, crs="EPSG:3857", source=cx.providers.CartoDB.Positron, zorder=1)
ax.set_aspect("equal")

fig.suptitle("Belgian Property Prices by Location", fontsize=15, weight="bold",
             color="#1d3557", y=0.975)
ax.set_title("Circle size = median price per province", fontsize=9.5, color="#666", pad=12)
ax.set_xticks([]); ax.set_yticks([])
for spine in ax.spines.values():
    spine.set_visible(False)

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.tight_layout()
plt.savefig("map_for_sales_in_Belgium.jpg", dpi=300)
plt.close()

### Graph 7 : Gross Rental Yield

dfs_cor = dfs[["price","province","livable_surface"]].dropna(how='any')
dfs_cor["price_surf"] = dfs_cor["price"]/dfs_cor["livable_surface"]
dfs_per_prov = dfs_cor.groupby("province")["price_surf"].agg(["mean","median"])
dfr_cor = dfr[["price","province","livable_surface"]].dropna(how='any')
dfr_cor["price_surf"] = dfr_cor["price"]/dfr_cor["livable_surface"]
dfr_per_prov = dfr_cor.groupby("province")["price_surf"].agg(["mean","median"])

dfgry = dfs_per_prov.merge(dfr_per_prov,on="province",how="inner",suffixes=["_s","_r"])
dfgry["gry"] = dfgry["median_r"]*12/dfgry["median_s"]*100
dfgry = dfgry.sort_values("gry",ascending=True)
print(dfgry.head(11))

bars = plt.barh(dfgry.index, dfgry['gry'],
                   capsize=4,
                   color=BLUE, alpha=0.8, edgecolor='white')
overall_rate = dfgry['gry'].median()
plt.axvline(overall_rate, color=ORANGE, lw=2, ls='--',
                label=f"Country avg : {overall_rate:.02f}")
plt.title('Gross rental yield per province')
plt.legend()
plt.tight_layout()
plt.savefig("gross_rental_yield.jpg")
plt.close()