# geoclime

![CI](https://github.com/YOUR-USERNAME/geoclime/actions/workflows/ci.yml/badge.svg)

One consistent **region + time-series API** for climate, ocean and glaciology data.
Instead of writing different loading and cleaning code for every dataset, you call
`geoclime.load(...)` and always get the same `TimeSeries` object back.

## Install

```bash
pip install git+https://github.com/YOUR-USERNAME/geoclime.git
```

## Quick start

```python
import geoclime as gc

gc.list_datasets()                                  # what is available

temp = gc.load("temperature", start=1959, end=2013)  # climate
sea  = gc.load("sea_level",   start=1959, end=2013)  # ocean
ice  = gc.load("glacier_mass_balance")               # glaciology

temp.trend_per_decade()                              # +0.152 °C per decade
gc.compare([temp, sea]).head()                       # aligned on year
gc.correlation(temp, gc.load("co2"))                 # 0.94
gc.correlation(temp, gc.load("co2"), differenced=True)  # year-to-year changes
```

Command line:

```bash
python -m geoclime list
python -m geoclime show sea_level --start 1990
```

## Bundled datasets

| Name | Domain | Unit | Source |
|---|---|---|---|
| `temperature` | climate | °C anomaly | NASA GISTEMP via [datahub.io](https://datahub.io/core/global-temp) (CC-BY-4.0) |
| `co2` | climate | ppm | NOAA Mauna Loa via [datahub.io](https://datahub.io/core/co2-ppm) (ODC-PDDL) |
| `sea_level` | ocean | cm | CSIRO via EPA, [datahub.io](https://datahub.io/core/sea-level-rise) (ODC-PDDL) |
| `glacier_mass_balance` | glaciology | m w.e. | EPA, [datahub.io](https://datahub.io/core/glacier-mass-balance) (ODC-PDDL) |
|`co2_global`| climate| ppm | NOAA global marine average|

## What it can do today (v0.1)

- One loader for every dataset, with a year range: `load(name, region, start, end)`
- `TimeSeries` helpers: `between`, `rolling_mean`, `anomaly`, `trend_per_decade`, `summary`
- `compare()` to align series on year, `correlation()` including a differenced version

## Limits (MVP)

- All bundled datasets are global annual series, so only `region="global"` works.
  The `Region` class (with a bounding box) is where gridded and regional data will plug in.
- Annual resolution only.

## Develop

```bash
pip install -e ".[dev]"
python -m pytest
```

## License

MIT. Dataset licenses are listed in the table above.
