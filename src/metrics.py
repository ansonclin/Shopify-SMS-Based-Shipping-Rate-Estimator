#3
import pandas as pd

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


def most_common_area_code_by_rate(counts, rate_cache):
    top_area_code_by_rate = {}
    for area_code, count in counts.items():
        rate = rate_cache[area_code]
        if rate not in top_area_code_by_rate:
            top_area_code_by_rate[rate] = area_code # $5.00 : '415'
        else:
            curr_leader_area_code = top_area_code_by_rate[rate] # current most signups with this area code
            if count > counts[curr_leader_area_code]:
                top_area_code_by_rate[rate] = area_code

    return top_area_code_by_rate

def calculate_spread(counts, rate_cache):
    """
    Measures how far individual rates typically stray from the weighted average.

    For each area code: (rate - average) squared, times signup count, summed
    across all area codes = weighted_variance_sum. Dividing that by total
    signups gives variance; taking the square root gives standard deviation,
    back in dollars.
    """
    weighted_avg = calculate_weighted_average(counts, rate_cache)  # reference point to measure distance from
    total_signups = counts.sum()  # denominator, same as in calculate_weighted_average

    weighted_variance_sum = 0  # running total of "how far off, weighted by how many people" across all area codes
    all_rates = []  # plain list of each area code's rate, so we can find min/max after the loop

    for area_code, count in counts.items(): 
        rate = rate_cache[area_code]  # this area code's rate
        weighted_variance_sum += count * (rate - weighted_avg) ** 2  # (distance from average)^2, weighted by signups
        all_rates.append(rate)  # collect the rate itself for min/max later

    std_dev = (weighted_variance_sum / total_signups) ** 0.5  # variance -> std dev (square root)
    min_rate = min(all_rates)  # cheapest rate anyone actually pays
    max_rate = max(all_rates)  # most expensive rate anyone actually pays

    return std_dev, min_rate, max_rate

