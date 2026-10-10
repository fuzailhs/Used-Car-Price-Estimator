# PRD: Used-Car Price Estimator

## Problem
Buying or selling a used car is guesswork. Sellers don't know a fair asking price, and buyers can't tell if a listing is overpriced. Both sides need a quick, data-backed estimate.

## Who it's for
- People selling their car who want a fair asking price.
- People buying a used car who want to check a listing before negotiating.

## Goals
- A user can enter a car's details and get a fair price estimate in seconds.
- Estimates are based on real listings in `used-cars.csv` (3915 listings), not guesses.
- The app is simple enough for a non-expert to use on the first try.

## In scope
- Input form: brand, model, year, mileage, fuel type, transmission.
- Price estimate shown with a sensible range (low–fair–high).
- Basic guidance with the estimate, e.g. how mileage and year affect the price.
- Handling messy data gracefully (unknown fuel type, uncommon transmissions, rare models).

## Out of scope
- No buying, selling, or contacting dealers inside the app.
- No live market data, price history charts, or location-based pricing.
- No accounts, saved searches, or listing management.
- No guarantee of sale price - the estimate is guidance only.

## How we'll know it works
- A user can go from opening the app to seeing an estimate in under a minute with no help.
- Estimates for common cars land near real listing prices in the dataset.
- Very high or very low mileage clearly moves the estimate down or up.
- Invalid or missing inputs give a clear message instead of a wrong price or a crash.
