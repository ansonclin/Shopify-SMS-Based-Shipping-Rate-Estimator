# CLAUDE.md — Shipping Rate Estimator

## What this is
An MVP data pipeline that takes an SMS signup CSV, uses each subscriber's
phone area code as a location proxy, gets real USPS postage for each, and
computes a signup-weighted average shipping cost. Purpose: replace a guessed
flat shipping rate with a data-backed one, and produce metrics that validate
whether the approach works. Built for a resume project and for real use on
the Velori Hills clothing brand's next drop.

## How Valk wants to work on this
Valk is learning. Explain the reasoning and walk through a small concrete
example by hand before writing or showing code. Don't hand over a complete
working implementation in one shot — build it in pieces, and check
understanding before moving to the next piece. Plain-English first, code
second.

## Tech stack for this project
Python. pandas for CSV handling. No web framework needed for the MVP — this
is a script/notebook that produces metrics and a chart, not a live app.
(If it later becomes a repeat-use tool, a thin FastAPI wrapper is the
natural next step, consistent with the FastAPI/Next.js stack used elsewhere,
but that's a post-MVP decision, not part of validating the idea.)

## Decisions already made (don't re-litigate these)
- Use a representative ZIP code per area code + live USPS postage lookup,
  rather than computing distance or hand-built shipping tiers.
- Weight the average by signup count per area code, not by unique area code
  count (a big cluster of nearby signups should dominate a handful of far
  ones — see PROJECT_NOTES.md for the worked example).

## Weighted average formula (generalizes to any number of area codes)
The grouping is by area code, not by state or city, and it isn't chosen by
hand — every unique area code present in the CSV automatically becomes its
own group. The formula is:

```
weighted average = (count_1 * rate_1 + count_2 * rate_2 + ... + count_n * rate_n) / total signups
```

where `n` is however many distinct area codes actually appear in the data,
could be 8, could be 80. `count_i` comes from tallying signups per area code
in the CSV; `rate_i` comes from the cached USPS lookup for that area code
(one lookup per unique area code, reused for every signup that shares it).

Worked example:

| Area code | City    | Signups | USPS rate |
|-----------|---------|---------|-----------|
| 415       | SF      | 45      | $6.00     |
| 212       | NYC     | 25      | $9.00     |
| 305       | Miami   | 10      | $8.50     |
| 702       | Vegas   | 8       | $7.00     |
| 313       | Detroit | 5       | $7.50     |

Total signups: 93. Weighted average = (45x6 + 25x9 + 10x8.5 + 8x7 + 5x7.5) /
93 = 673.5 / 93 ~= $7.24.

A long tail of area codes with just 1-2 signups each doesn't need special
handling or manual curation of "major" groups — a rare area code just
contributes a small term to the sum, so its influence on the final number
is naturally proportional to how rare it is. No branching logic for "is
this group big enough to count."

State/region rollups (e.g. "average cost in the Northeast") are fine as a
reporting layer on top of this once the area-code-level numbers exist, but
the calculation itself should stay at area-code granularity — state lines
don't track USPS zone/distance cost well (California alone spans a wide
cost range; Alaska/Hawaii would skew a "West Coast" bucket if lumped in).

## Pipeline stages
1. **Ingest**: read the SMS export CSV, identify the phone number column,
   normalize to digits only.
2. **Extract area code**: first 3 digits after the country code.
3. **Map area code -> location**: static reference table
   (`data/area_code_reference.csv`), columns:
   `area_code, representative_zip, city, region, country` (country is US or
   CA — NANP area codes are a known, determinable set per country). Built
   once, checked into the repo. No live geocoding API needed for this step.
4. **Get postage**: for each *unique* area code present in the uploaded
   list, call the rate API once (origin ZIP + package weight/dims +
   the area code's representative ZIP). Cache by area code so repeat
   signups from the same area code don't trigger repeat calls.
   - Using EasyPost (easypost.com), not USPS's own Developer Portal API
     directly. Reason: USPS's own OAuth-based Developer Portal requires
     manual approval that takes 1-4 weeks (confirmed via their own docs
     and real developer reports); EasyPost gives instant, free test API
     keys and returns real USPS rates (Commercial Base pricing) by
     default, with no manual approval step. Auth is a plain API key sent
     as HTTP Basic Auth (key as username, no password) — no OAuth token
     exchange needed.
   - Endpoint: `POST /shipments`, with `to_address`, `from_address`, and
     `parcel` (weight/dims) — response includes a `rates` array covering
     every carrier on the account (USPS, FedEx, etc.), and multiple
     service levels per carrier.
   - Filter to `carrier == "USPS"`, then to `service == "GroundAdvantage"`
     specifically — USPS's standard low-cost e-commerce tier, and the
     closest match to the $6.99/$8.99 candidate flat rates. Other USPS
     tiers (Priority, Express) are premium/expedited and out of scope for
     this comparison.
5. **Aggregate**: signup-weighted average, plus domestic-only average,
   spread (std dev/min/max), and overpay/underpay percentages relative to
   a candidate flat rate. See PROJECT_NOTES.md for exact metric
   definitions.

## Open parameters to fill in before running for real
- `SELLER_ORIGIN_ZIP` — VeloriHills's ship-from ZIP
- package weight and box dimensions for a hoodie shipment
- EasyPost API key (sign up at easypost.com — instant, free test key, no
  approval wait, unlike USPS's own Developer Portal)
- candidate flat rate(s) to test against: $8.99 and $6.99 at minimum

## Suggested repo structure
```
shipping-estimator/
  data/
    area_code_reference.csv     # static area_code -> zip/city/region/country
    sms_signups.csv              # input, gitignored (customer data)
  src/
    ingest.py                    # CSV loading + phone normalization
    area_codes.py                # extraction + reference table lookup
    rates.py                     # EasyPost API client + caching
    metrics.py                   # weighted average, spread, overpay/underpay
  main.py                        # runs the pipeline end to end
  PROJECT_NOTES.md
  CLAUDE.md
```

## Things to watch for
- Real customer phone numbers are personal data — keep the input CSV out of
  version control.
- EasyPost API key should live in environment variables, never committed.
- Cache EasyPost responses per area code; don't re-call the API for every
  row.
