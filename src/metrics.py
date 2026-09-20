#3
import json

import pandas as pd

from load import load_signups
from area_codes import add_area_code_column
from rates import reference_df

def count_signups_by_area_code(df): # total signups 
    count_amount = df["area_code"].value_counts()
    return count_amount

def calculate_weighted_average(counts,rate_cache): #formula 
    total_signups = counts.sum()
    weighted_sum = 0
    for area_code, count in counts.items():
        rate = rate_cache[area_code]
        weighted_sum += count * rate
    return weighted_sum / total_signups

def count_signups_by_rate(counts, rate_cache):
    signups_by_rate = {}
    for area_code, count in counts.items():
        rate = rate_cache[area_code]
        if rate in signups_by_rate:
            signups_by_rate[rate] += count
        else:
            signups_by_rate[rate] = count
    return signups_by_rate

df = load_signups("SMS_Subscribers2.csv")
df = add_area_code_column(df)
domestic_area_codes = set(reference_df[~reference_df["representative_zip"].str.contains(r"[A-Za-z]")]["area_code"])
df = df[df["area_code"].isin(domestic_area_codes)]
counts = count_signups_by_area_code(df)

with open("data/rate_cache.json") as f:
    rate_cache = json.load(f)

result = pd.Series(count_signups_by_rate(counts,rate_cache))
result = result.sort_index(ascending= False)

print(result)

