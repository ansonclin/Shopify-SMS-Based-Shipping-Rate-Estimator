import json
import os
import time

from src.load import load_signups
from src.area_codes import add_area_code_column
from src.metrics import count_signups_by_area_code, calculate_weighted_average
from src.rates import get_rate_for_area_code, reference_df

df = load_signups("SMS_Subscribers2.csv")
df = add_area_code_column(df)

# domestic-only for now: drop any signups whose area code maps to a Canadian
# postal code (Canadian postal codes contain letters, US ZIPs are all digits)
domestic_area_codes = set(reference_df[~reference_df["representative_zip"].str.contains(r"[A-Za-z]")]["area_code"])
excluded_count = (~df["area_code"].isin(domestic_area_codes)).sum()
df = df[df["area_code"].isin(domestic_area_codes)]
print(f"Excluded {excluded_count} non-domestic (Canada) signups; {len(df)} domestic signups remain.")

counts = count_signups_by_area_code(df)

if os.path.exists("data/rate_cache.json"): # checking for the existing cached rates from before, returns t/f boolean
    with open("data/rate_cache.json") as f:
        rate_cache = json.load(f) # read json data and convert into native Python object (dictionary or list)
else:
    rate_cache = {}

for area_code in df["area_code"].unique():
    if area_code not in rate_cache:
        rate_cache[area_code] = get_rate_for_area_code(area_code)
        time.sleep(0.5)  # avoid overwhelming EasyPost's test API with rapid back-to-back calls

with open("data/rate_cache.json", "w") as f:
    json.dump(rate_cache, f)

weighted_average = calculate_weighted_average(counts, rate_cache)
print(f"Signup-weighted average shipping cost: ${weighted_average:.2f}")
