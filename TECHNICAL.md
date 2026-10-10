# Technical Plan: Used-Car Price Estimator

Based on `PRD.md` and `FUNCTIONAL.md`. Beginner-friendly Python app. No saved model file in v1 - the app trains when it starts.

## Files to create

- `app.py` - the whole v1 app in one file: load the dataset, train the model, show the input form, show the estimate. One file keeps it easy to read and run.
- `requirements.txt` - the list of libraries, so local setup and Railway install the same thing.

Already in the repo: `used-cars.csv` (the data), `.venv` (local Python environment), `.gitignore` (keeps `.venv` out of git).

## Columns the model uses

Features (inputs), all from `used-cars.csv`:
- Brand, model, year, mileage in miles, fuel type, and simplified transmission.

Target (what it learns to predict):
- Price in US dollars.

Two columns in the CSV are deliberately not used in v1: accident history and clean title. They exist in the data but are not part of the PRD input form, so v1 ignores them to keep the app to 6 fields.

Cleaning the app must do before training:
- Rejoin the three split brands (Land plus Rover, Alfa plus Romeo, Aston plus Martin) so makes match what users expect.
- Shrink the 60 raw transmission values into the 4 user-facing groups (Automatic, Manual, CVT, Unknown), including the junk codes.
- Treat Unknown fuel type as its own group, not as a blank.
- Convert year, mileage, and price to numbers.
- Treat very rare models as valid but low-confidence, since the model has little to learn from.

## How the model trains when the app starts

When the app starts it loads `used-cars.csv` with pandas, applies the cleaning above, turns text columns into a form the model can use, and trains a RandomForestRegressor from scikit-learn on all listings. The trained model stays in memory through Streamlit caching, so it trains once per start rather than on every button click.

When the user submits the form, the app cleans that one car the same way, asks the trained model for a price, then builds the range from similar listings and picks up to 3 plain-language factors (year, mileage, fuel type effect). Out-of-range or unknown cars are rejected before prediction, per `FUNCTIONAL.md`.

## Libraries needed

All listed in `requirements.txt`:
- pandas - loads and cleans `used-cars.csv`.
- scikit-learn - provides the RandomForestRegressor that learns prices.
- streamlit - turns `app.py` into the browser form and results screen.

## Run locally on Windows

In PowerShell from this folder: activate the existing virtual environment, install the libraries from `requirements.txt`, then start the app with Streamlit and open the local address it prints in the browser. Use `python` rather than `python3` on this machine.

## Deploying later to Railway

No extra files needed for v1. Railway detects Python from `requirements.txt`, installs the same three libraries, and starts the app with the Streamlit start command pointed at `app.py`, listening on the port Railway provides and on all network addresses. The dataset ships with the repo, so the deployed app trains on startup exactly like the local one.
