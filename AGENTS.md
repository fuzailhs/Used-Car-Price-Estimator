# AGENTS.md - Car Price-Estimator

Data-only repo. Single source of truth is `used-cars.csv` (3915 rows, 9 cols, header + no missing empties). No code, build, test, lint, or CI config exists yet.

## Dataset

`brand,model,year,mileage_miles,fuel_type,transmission,accident_reported,clean_title,price_usd`
- `year`: 1998–2024 (int-like strings). `mileage_miles`: 100–300000. `price_usd`: 2000–250000 (target).
- `brand`: 56 values, `model`: 1849 unique (trim-level detail, e.g. `ILX 2.0L w/Premium Package`). Do not one-hot `model` naively.
- `fuel_type`: Gasoline (3247) / Hybrid (194) / Unknown (189) / E85 Flex Fuel (139) / Diesel (112) / Plug-In Hybrid (34).
- `accident_reported`: only `Yes`/`No`. `clean_title`: only `Yes`/`Unknown` - there is no `No`, so `Unknown` ≠ clean; treat as its own category, not as missing-to-impute-to-No.

## Data gotchas (verified - handle before modeling)

- **Split two-word brands.** `brand` is truncated at the first space: `Land` + `Rover Defender...`, `Alfa` + `Romeo Giulia...`, `Aston` + `Martin DB...`. Hyphenated brands (`Mercedes-Benz`, `Rolls-Royce`) are intact. Reconstruct (`brand + " " + model` split) or group by full make; do not trust `brand` alone.
- **`transmission` is noisy: 60 distinct values.** Top is generic `A/T` (1011 rows). Near-duplicates abound (`8-Speed A/T` vs `8-Speed Automatic`, `M/T` vs `5-Speed M/T`, `CVT Transmission` vs `Automatic CVT`). Contains junk single-char codes (`F`, `2`). Normalize into a small set (e.g. automatic / manual / CVT / unknown) before encoding.
- **`fuel_type = Unknown` (189 rows) is a real category**, not skippable nulls.
- All fields are strings on disk; cast `year`, `mileage_miles`, `price_usd` to numeric after load.

## Working in this repo

- No runner, deps, or tests to discover - this is greenfield. If adding Python, use `python` (not `python3`) on this Windows host; `python3` is not on PATH.
- Keep new code beside the CSV at repo root; do not restructure until a real app shape emerges.
- Verify any parse/clean step by running it against `used-cars.csv` before finalizing.
