# 🏠 Immo Eliza — Belgian Real Estate Market Analysis

> A data analysis of **~13,500 Belgian property listings** that helps a buy-to-let investor answer two questions: **where should I buy, and what should I look for?**

This is the *analysis* stage of the Immo Eliza project. In the previous stage the team scraped property listings from [immovlan.be](https://immovlan.be); here we clean that dataset, explore it, and turn it into clear, non-technical insights and recommendations.

---

## 📋 Description

The real estate company **Immo Eliza** wants to estimate property values across Belgium faster and more accurately than its competitors. Before building a price-prediction model, management — who have **no technical background** — asked two questions:

1. What are the most interesting insights about the Belgian real estate market?
2. Which variables matter most when determining a property's price?

To make those insights concrete, we framed the analysis around a **client persona**:

> **Marc, 45 — a buy-to-let investor.** He has capital to deploy and wants steady monthly income from rent (not a quick flip). He is open to buying a house *or* an apartment, and cares most about the **return on the money he puts in**.

Every visual in the project answers one of Marc's two questions: *where to buy* and *what to look for*.

---

## 🗂️ Repository structure

```
immoeliza_data_analysis/
├── Analysis/
│   ├── analysis_GB.ipynb        # Main analysis notebook (shape, missing values,
│   └── ...                      # correlations, price maps)                        
├── Data/
│   ├── Raw/
│   │   ├── PropertyData.csv       # Original scraped dataset (14,027 listings)
│   │   └── emissions.csv          # CodeCarbon tracking of the scraping run
│   ├── Clean/
│   │   ├── SaleCleanForAnalysis.csv   # Cleaned properties for sale  (9,712 rows)
│   │   └── RentCleanForAnalysis.csv   # Cleaned properties to rent   (3,797 rows)
│   └── cleanData.py               # Cleaning pipeline (raw → cleaned CSVs)
├── Images/                        # Exported visuals (charts & maps)
├── Reports/                       # Final presentation in PDF
└── README.md
```

> **Note (per the project brief):** the brief also asks for a `main.py` that regenerates and saves every visual into `Images/`. The exploratory work currently lives in the notebook; consolidating the final figure-generating code into `main.py` is the remaining step before the repo fully matches the brief.

---

## 📊 The dataset

| | |
|---|---|
| **Source** | Scraped from immovlan.be (previous project stage) |
| **Raw size** | 14,027 listings × 26 features |
| **After cleaning** | 9,712 for sale · 3,797 to rent |
| **Coverage** | All 11 Belgian provinces; houses & apartments |
| **Median sale price** | €329,000 (median surface 146 m²) |
| **Median monthly rent** | €1,050 (median surface 93 m²) |

### Data dictionary

| Column | Type | Description |
|---|---|---|
| `longitude` | float | Geographic longitude |
| `latitude` | float | Geographic latitude |
| `transaction_type` | category | `Sale` or `Rent` |
| `price` | integer (€) | Asking price (sale) **or** monthly rent (rent) |
| `property_type` | category | `House` or `Appartment` |
| `property_subtype` | category | More specific type (Flat, Duplex, Villa, …) |
| `seller_id` | integer | Anonymised ID of the listing agency |
| `postal_code` | integer (identifier) | Belgian postal code — an identifier, not a quantity |
| `date_of_construction` | integer (year) | Year built |
| `property_condition` | category | New, Normal, Excellent, Fully renovated, … |
| `livable_surface` | integer (m²) | Habitable floor area |
| `number_of_bedrooms` | integer | Bedroom count |
| `number_of_bathrooms` | integer | Bathroom count |
| `elevator` | boolean | Building has a lift |
| `terrace` | integer (m²) | Terrace area (blank = none) |
| `furnished` | boolean | Property is furnished |
| `availability` | string | When the property becomes available |
| `province` | category | One of the 11 Belgian provinces |
| `street` | string | Street name (lower-cased, trimmed) |
| `street_number` | integer | House / door number |
| `garage` | integer | Number of garage / parking spaces |
| `land_surface` | integer (m²) | Plot area (mostly houses) |
| `energy_consumption` | integer | Energy-consumption value (EPC) |
| `garden` | integer (m²) | Garden area |
| `balcony` | boolean | Property has a balcony |
| `swimming_pool` | boolean | Property has a pool |

---

## 🧹 Data cleaning

`Data/cleanData.py` takes the raw scraped file and produces analysis-ready data. It:

1. **Standardises text** — lower-cases and trims street names, collapses repeated spaces.
2. **Fixes data types** — categoricals, nullable integers (`Int64`), nullable booleans, and floats for coordinates, so each column behaves correctly in pandas.
3. **Repairs swapped coordinates** — some rows had latitude/longitude reversed; these are detected (`longitude > 10`) and swapped back.
4. **Removes out-of-range values** — filters impossible values for surface, terrace, garage, land, garden and energy.
5. **Removes duplicates** — both exact duplicates and "suspicious" duplicates (same location, price, type, surface, …).
6. **Splits by transaction type** — separates the dataset into properties **for sale** and **to rent**.

---

## 🔧 Installation

This project uses **Python 3** and a handful of data libraries.

```bash
# 1. Clone the repository
git clone https://github.com/<your-team>/immoeliza_data_analysis.git
cd immoeliza_data_analysis

# 2. (Recommended) create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install the dependencies
pip install pandas numpy matplotlib seaborn jupyter
```

> 💡 Consider adding a `requirements.txt` so collaborators can install everything with `pip install -r requirements.txt`.

---

## ▶️ Usage

```bash
# (Optional) regenerate the cleaned datasets from the raw file
python Data/cleanData.py

# Open the analysis notebook and run all cells
jupyter notebook Analysis/soo_notebook.ipynb
```

The cleaned datasets are already provided in `Data/Clean/`, so you can open the notebook and explore straight away. The final, non-technical story is in the presentation in `Reports/`.

---

## 📈 Key findings & recommendations

The analysis builds toward a single, practical answer for Marc.

**What drives price?**
- **Living space is the strongest driver** of price.
- On the sale data, every extra **m² of living space adds roughly €1,833** to the price.
- *Takeaway:* pay for usable space, not just the number of rooms.

**Where is it cheapest to buy?**
- **Wallonia** (Hainaut, Liège, Namur, Luxembourg) is the most affordable region.
- **Brussels** and the **Brabant** provinces are the most expensive per m².

**Where are rents highest?**
- **Brussels, Vlaams-Brabant and Brabant Wallon** command the highest rents; Hainaut, Luxembourg and Liège the lowest.
- But high rent alone ≠ a good investment — what matters is rent **relative to purchase price**.

**The bottom line — gross rental yield by province**

| Rank | Province | Gross yield |
|---|---|---|
| 1 | **Hainaut** | **~7.6 %** |
| 2 | Namur | ~6.0 % |
| 3 | Liège | ~5.9 % |
| … | Brussels | ~5.7 % |
| 11 | West-Vlaanderen | ~4.7 % |

> **Insight:** **Hainaut** is cheapest to buy while rents hold up, giving the strongest cash return.

**Recommendations for Marc**
1. **Chase yield** — for rental income, target Hainaut, Namur and Liège.
2. **Buy on usable space** — living space drives both rent and resale value.
3. **Mind the biases** — Brussels & Brabant cost most but return least in yield; enter only for long-term capital growth.
4. **Yield isn't the whole story** — gross yield ignores taxes, renovations, etc.; use it to shortlist, then dig deeper.

---

## 🧠 Analysis questions covered

The notebook and presentation address the brief's core questions, including: number of observations & features; proportion of missing values per column; correlation between variables and price; how variables correlate with each other; the five most important variables; and the least/most expensive regions by **price per m²**, average and median price.

---

## 👥 Contributors

**Team Horse** — BeCode AI & Data Science Bootcamp

| Member | Role |
|---|---|
| Gaetan Bricteux | Project Lead *(Agile Master)* |
| Gunay Bayramova | Git Commander *(Repo Manager)* |
| Hussein Abuammar | Documentation Specialist / QA & Data Architect |
| Sooyoung Lee | Documentation Specialist / QA & Data Architect |

---

## 🗓️ Timeline

5-day team project — **June 2026** — completed during the BeCode AI & Data Science bootcamp.

---

## 🎓 Context

Built as a learning-and-consolidation project at **BeCode** (Brussels). Goals practised: cleaning a dataset with `pandas`, exploring relationships with `matplotlib`/`seaborn`, drawing conclusions from data, collaborating with Git, and presenting insights to a non-technical audience.

---

## 🛠️ Tools

`Python` · `pandas` · `NumPy` · `matplotlib` · `seaborn` · `Jupyter` · `Git` / `GitHub`
