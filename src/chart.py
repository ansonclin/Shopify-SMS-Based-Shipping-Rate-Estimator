import matplotlib.pyplot as plt

def plot_rate_distribution(signups_by_rate, weighted_average, std_dev, top_area_code_by_rate, output_path="rate_distribution.png"):
    rates = sorted(signups_by_rate.keys())
    signup_counts = [signups_by_rate[rate] for rate in rates]
    labels = [f"${r:.2f}" for r in rates]

    plt.figure(figsize=(10, 6))
    bars = plt.bar(labels, signup_counts, color="steelblue")

    avg_index = _closest_bar_index(rates, weighted_average)
    plt.axvline(
        x=avg_index,
        color="red",
        linestyle="--",
        label=f"Weighted average: ${weighted_average:.2f}",
    )

    low_index = _closest_bar_index(rates, weighted_average - std_dev)
    high_index = _closest_bar_index(rates, weighted_average + std_dev)
    plt.axvspan(
        low_index,
        high_index,
        color="red",
        alpha=0.1,
        label=f"± 1 std dev (${std_dev:.2f})",
    )

    # label each bar with the area code contributing the most signups to it
    for bar, rate in zip(bars, rates):
        area_code = top_area_code_by_rate[rate]
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            area_code,
            ha="center",
            va="bottom",
            fontsize=8,
        )

    plt.xlabel("Shipping rate")
    plt.ylabel("Number of signups")
    plt.title("Signups by shipping rate")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

def _closest_bar_index(rates, target):
    # axvline/axvspan need bar POSITIONS (0, 1, 2...), not dollar values,
    # since each bar sits on a category axis, not a numeric one -- find
    # whichever bar's rate is closest to the target and use its position
    closest_rate = min(rates, key=lambda r: abs(r - target))
    return rates.index(closest_rate)
