"""Used-car price estimator.

Loads used-cars.csv with pandas, trains a RandomForestRegressor on startup,
and shows a Streamlit form. See TECHNICAL.md for the plan.
"""

from pathlib import Path

import pandas as pd
import streamlit as st
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

st.set_page_config(page_title="Used Car Price Estimator", page_icon="🚗")

CSV_PATH = Path(__file__).with_name("used-cars.csv")

YEAR_MIN, YEAR_MAX = 1998, 2024
MILEAGE_MIN, MILEAGE_MAX = 100, 300000

CATEGORICAL_COLS = ["full_brand", "model", "fuel_type", "trans_simple"]
NUMERIC_COLS = ["year", "mileage_miles"]

FUEL_CHOICES = [
    "Gasoline",
    "Hybrid",
    "E85 Flex Fuel",
    "Diesel",
    "Plug-In Hybrid",
    "Unknown",
]
TRANSMISSION_CHOICES = ["Automatic", "Manual", "CVT", "Unknown"]


def full_brand_name(brand: str, model: str) -> str:
    """Rejoin the three split makes so users see full names."""
    if brand == "Land" and model.startswith("Rover"):
        return "Land Rover"
    if brand == "Alfa" and model.startswith("Romeo"):
        return "Alfa Romeo"
    if brand == "Aston" and model.startswith("Martin"):
        return "Aston Martin"
    return brand


def simplify_transmission(value: str) -> str:
    """Shrink the 60 raw transmission values into 4 user-facing groups."""
    text = str(value).strip()
    upper = text.upper()
    if text in ("F", "2", "") or upper in (
        "�",
        "SCHEDULED FOR OR IN PRODUCTION",
        "TRANSMISSION OVERDRIVE SWITCH",
        "6-SPEED",
    ):
        return "Unknown"
    if "CVT" in upper or upper in ("VARIABLE", "CVT-F"):
        return "CVT"
    if upper == "6 SPEED AT/MT":
        return "Automatic"
    if "MANUAL" in upper or "M/T" in upper or " MT" in upper:
        return "Manual"
    if "AUTO" in upper or "A/T" in upper or "DCT" in upper or "PDK" in upper:
        return "Automatic"
    if "SPEED" in upper or "TRANSMISSION" in upper or "GEAR" in upper:
        return "Automatic"
    return "Unknown"


def load_and_clean(path: Path) -> pd.DataFrame:
    """Load the CSV and apply the cleaning described in TECHNICAL.md."""
    df = pd.read_csv(path, dtype=str)
    df["full_brand"] = [
        full_brand_name(brand, model)
        for brand, model in zip(df["brand"], df["model"])
    ]
    df["trans_simple"] = df["transmission"].apply(simplify_transmission)
    # Unknown fuel type stays as its own group; just normalize blanks.
    df["fuel_type"] = df["fuel_type"].fillna("Unknown")
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df["mileage_miles"] = pd.to_numeric(df["mileage_miles"], errors="coerce")
    df["price_usd"] = pd.to_numeric(df["price_usd"], errors="coerce")
    return df.dropna(
        subset=[
            "full_brand",
            "model",
            "year",
            "mileage_miles",
            "fuel_type",
            "trans_simple",
            "price_usd",
        ]
    )


def build_pipeline() -> Pipeline:
    encoder = OneHotEncoder(handle_unknown="ignore")
    preprocessor = ColumnTransformer(
        [
            ("cat", encoder, CATEGORICAL_COLS),
            ("num", "passthrough", NUMERIC_COLS),
        ]
    )
    model = RandomForestRegressor(
        n_estimators=200, random_state=42, n_jobs=-1
    )
    return Pipeline([("preprocessor", preprocessor), ("model", model)])


@st.cache_resource
def get_trained():
    """Train once when the app starts; reuse for every estimate."""
    df = load_and_clean(CSV_PATH)
    features = df[
        ["full_brand", "model", "year", "mileage_miles", "fuel_type", "trans_simple"]
    ]
    target = df["price_usd"]
    pipeline = build_pipeline()
    pipeline.fit(features, target)
    return pipeline, df


def round_to_100(value: float) -> int:
    return int(round(float(value) / 100.0) * 100)


def similar_prices(df: pd.DataFrame, brand: str, year: int) -> pd.Series:
    """Prices of nearby listings used to build the low-high range."""
    nearby = df[(df["full_brand"] == brand) & (df["year"] - year).abs() <= 2]
    if len(nearby) < 10:
        nearby = df[df["full_brand"] == brand]
    if len(nearby) < 10:
        nearby = df
    return nearby["price_usd"]


def top_factors(df: pd.DataFrame, brand: str, year: int, mileage: int, fuel: str):
    """Up to 3 plain-language reasons behind the estimate."""
    factors = []
    brand_cars = df[df["full_brand"] == brand]
    baseline = brand_cars if len(brand_cars) >= 10 else df

    median_year = float(baseline["year"].median())
    if year <= median_year - 3:
        factors.append("Older year than similar cars lowers the price")
    elif year >= median_year + 3:
        factors.append("Newer year than similar cars raises the price")

    median_mileage = float(baseline["mileage_miles"].median())
    if mileage >= median_mileage + 20000:
        factors.append("Higher mileage than similar cars lowers the price")
    elif mileage <= median_mileage - 20000:
        factors.append("Lower mileage than similar cars raises the price")

    fuel_mean = float(df[df["fuel_type"] == fuel]["price_usd"].mean())
    overall_mean = float(df["price_usd"].mean())
    if fuel_mean > overall_mean * 1.05:
        factors.append(f"{fuel} fuel type raises the price vs. average")
    elif fuel_mean < overall_mean * 0.95:
        factors.append(f"{fuel} fuel type lowers the price vs. average")

    return factors[:3]


pipeline, listings = get_trained()

st.title("🚗 Used Car Price Estimator")
st.write(
    f"Trained on {len(listings)} real listings. "
    "Pick a car to get a fair-price estimate."
)

brands = sorted(listings["full_brand"].unique())
brand = st.selectbox("Brand", brands)

brand_models = sorted(listings[listings["full_brand"] == brand]["model"].unique())
model = st.selectbox("Model", brand_models)

fuel_type = st.selectbox("Fuel type", FUEL_CHOICES)
transmission = st.selectbox("Transmission", TRANSMISSION_CHOICES)

year = st.number_input(
    "Year", min_value=YEAR_MIN, max_value=YEAR_MAX, value=2018, step=1
)
mileage = st.number_input(
    "Mileage (miles)",
    min_value=MILEAGE_MIN,
    max_value=MILEAGE_MAX,
    value=60000,
    step=1000,
)

if st.button("Estimate price"):
    if not (YEAR_MIN <= int(year) <= YEAR_MAX):
        st.error(f"Year must be between {YEAR_MIN} and {YEAR_MAX}.")
    elif not (MILEAGE_MIN <= int(mileage) <= MILEAGE_MAX):
        st.error(
            f"Mileage must be between {MILEAGE_MIN} and {MILEAGE_MAX} miles."
        )
    else:
        match_count = len(
            listings[
                (listings["full_brand"] == brand) & (listings["model"] == model)
            ]
        )
        if match_count == 0:
            st.error("We don't have enough listings for this car yet.")
        else:
            car = pd.DataFrame(
                [
                    {
                        "full_brand": brand,
                        "model": model,
                        "year": int(year),
                        "mileage_miles": int(mileage),
                        "fuel_type": fuel_type,
                        "trans_simple": transmission,
                    }
                ]
            )
            prediction = float(pipeline.predict(car)[0])
            estimate = round_to_100(prediction)

            spread = float(similar_prices(listings, brand, int(year)).std())
            if pd.isna(spread) or spread <= 0:
                spread = prediction * 0.10
            low = round_to_100(max(2000, prediction - spread))
            high = round_to_100(prediction + spread)

            st.subheader(f"Estimated fair price: ${estimate:,} USD")
            st.write(f"Expected range: ${low:,} – ${high:,} USD")

            if match_count < 5:
                st.warning("Low confidence - few similar cars in the data.")

            same = listings[
                (listings["full_brand"] == brand) & (listings["model"] == model)
            ]
            st.subheader("About this car in our data")
            st.write(f"Similar listings: {len(same)}")
            st.write(
                f"Average price: ${round_to_100(float(same['price_usd'].mean())):,} USD"
            )
            st.write(
                f"Price span: ${round_to_100(float(same['price_usd'].min())):,} "
                f"to ${round_to_100(float(same['price_usd'].max())):,} USD"
            )
            st.write(
                f"Years in data: {int(same['year'].min())} "
                f"to {int(same['year'].max())}"
            )
            st.write(
                f"Average mileage: {int(float(same['mileage_miles'].mean())):,} miles"
            )

            for factor in top_factors(
                listings, brand, int(year), int(mileage), fuel_type
            ):
                st.write(f"- {factor}")

st.divider()
st.subheader("Explore the market")
st.write("Browse the most extreme listings in the dataset.")

highlight = st.selectbox(
    "Show me",
    [
        "Cheapest in the market",
        "Most expensive in the market",
        "Lowest mileage",
        "Highest mileage",
        "Oldest cars",
        "Newest cars",
    ],
)

if highlight == "Cheapest in the market":
    picks = listings.nsmallest(10, "price_usd")
elif highlight == "Most expensive in the market":
    picks = listings.nlargest(10, "price_usd")
elif highlight == "Lowest mileage":
    picks = listings.nsmallest(10, "mileage_miles")
elif highlight == "Highest mileage":
    picks = listings.nlargest(10, "mileage_miles")
elif highlight == "Oldest cars":
    picks = listings.nsmallest(10, "year")
else:
    picks = listings.nlargest(10, "year")

table = picks[
    ["full_brand", "model", "year", "mileage_miles", "fuel_type", "price_usd"]
].rename(
    columns={
        "full_brand": "Brand",
        "model": "Model",
        "year": "Year",
        "mileage_miles": "Mileage (miles)",
        "fuel_type": "Fuel",
        "price_usd": "Price (USD)",
    }
)
st.dataframe(table, hide_index=True, use_container_width=True)
