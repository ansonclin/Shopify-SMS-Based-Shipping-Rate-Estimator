#3 
import pandas as pd

def count_signups_by_area_code(df):
    count_amount = df["area_code"].value_counts()
    return count_amount

def calculate_weighted_average(counts,rate_cache):
    total_signups = counts.sum()
    weighted_sum = 0
    for area_code, count in counts.items():
        rate = rate_cache[area_code]
        weighted_sum += count * rate
    return weighted_sum / total_signups


test_counts = pd.Series({"415": 45, "212": 25, "305": 10, "702": 8, "313": 5})
test_rate_cache = {"415": 6.00, "212": 9.00, "305": 8.50, "702": 7.00, "313": 7.50}
print(f"{calculate_weighted_average(test_counts, test_rate_cache):.2f}")

