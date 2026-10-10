# Functional Requirements: Used-Car Price Estimator

Based on `PRD.md`. Dataset is `used-cars.csv` (3915 listings).

## 1. Inputs

The app accepts 6 inputs, matching dataset columns. All are required except where noted.

- **Brand**: must be one of the 56 brands in the dataset (e.g. Ford, BMW, Toyota, Honda). Note: three makes are split in the data - `Land` (= Land Rover), `Alfa` (= Alfa Romeo), `Aston` (= Aston Martin). The app must show the full names but match them to the dataset.
- **Model**: trim-level text, 1849 values in data (e.g. `ILX 2.0L w/Premium Package`). User picks a model after picking brand. Rare models with few listings are allowed but flagged as low-confidence (see below).
- **Year**: whole number, 1998–2024. Anything outside this range is rejected with a message.
- **Mileage**: whole number in miles, 100–300000. Anything outside this range is rejected with a message.
- **Fuel type**: must be one of 6 dataset values: Gasoline, Hybrid, E85 Flex Fuel, Diesel, Plug-In Hybrid, Unknown. `Unknown` means the seller didn't state it - accepted, treated as its own group.
- **Transmission**: the dataset has 60 raw values (e.g. `A/T`, `8-Speed A/T`, `6-Speed M/T`, `CVT Transmission`, plus junk codes `F` and `2`). The user picks from a short list - Automatic, Manual, CVT, Unknown - and the app maps dataset values onto it.

Missing or mistyped input: the app blocks estimation and names the field to fix. It never guesses a price from partial input.

## 2. Output

Every successful estimate shows three things:

1. **Estimated fair price**: a single dollar figure, rounded to the nearest $100.
2. **Low–high range**: a range around the estimate (e.g. $13,500 – $16,500) showing where similar listings fall. Wide range = few similar cars or high price spread; narrow range = many close matches.
3. **Top factors**: up to 3 short reasons in plain language, e.g. "Lower mileage than average raises the price", "Older year lowers the price", "Hybrid fuel type raises the price vs. gasoline". No numbers or model internals.

Plus a confidence note when relevant: "Low confidence - few similar cars in the data."

## 3. Unusual inputs

- **Very old car (e.g. 1998–2002)**: accepted if in range. Expect a low estimate near the bottom of the dataset (~$2,000–$8,000) and a wide range, since old cars vary a lot by condition.
- **Very high mileage (e.g. 200,000–300,000 miles)**: accepted if in range. Expect the estimate to drop clearly below the same car with average mileage, with a note that mileage lowered the price.
- **Out-of-range values (year before 1998 / after 2024, mileage below 100 / above 300,000, negative numbers)**: rejected before estimation with a message stating the allowed range.
- **Unknown fuel type or uncommon transmission**: accepted, grouped with matching listings, usually with lower confidence.
- **Brand/model never seen in the data**: rejected with "we don't have enough listings for this car yet", not a made-up price.

## 4. Examples

1. **Common car - 2018 Honda Accord-type, 60,000 miles, Gasoline, Automatic.**
   Expect: a mid-range estimate matching typical listings, narrow range, no low-confidence note. Factors mention average year and mileage.

2. **Old, high-mileage car - 2005 Ford truck-type, 220,000 miles, Gasoline, Automatic.**
   Expect: a low estimate, clearly below the same model with 80,000 miles. Factors call out high mileage and old year as lowering the price. Range may be wide.

3. **New, low-mileage car - 2022 compact SUV-type, 15,000 miles, Hybrid, Automatic.**
   Expect: a high estimate near the top for that model. Factors call out low mileage, recent year, and hybrid fuel type as raising the price. Narrow range if the dataset has many similar cars, otherwise a low-confidence note.
