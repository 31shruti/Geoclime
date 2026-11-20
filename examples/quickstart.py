"""Run: python examples/quickstart.py  ->  prints a summary and saves quickstart.png"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import geoclime as gc

print(gc.list_datasets().to_string(index=False), "\n")

names = ["temperature", "co2", "sea_level", "glacier_mass_balance"]
series = [gc.load(n, start=1959, end=2013) for n in names]
for s in series:
    print(f"{s.name:>22}: {s.trend_per_decade():+.3f} {s.unit} per decade")

print("\ntemperature vs co2, r =", round(gc.correlation(series[0], series[1]), 3))
print("year-to-year changes,   r =", round(gc.correlation(series[0], series[1], differenced=True), 3))

fig, axes = plt.subplots(2, 2, figsize=(10, 6), sharex=True)
for ax, s in zip(axes.flat, series):
    ax.plot(s.years, s.values.to_numpy())
    ax.set_title(f"{s.name} ({s.domain})")
    ax.set_ylabel(s.unit)
fig.tight_layout()
fig.savefig("quickstart.png", dpi=120)
print("\nSaved quickstart.png")
