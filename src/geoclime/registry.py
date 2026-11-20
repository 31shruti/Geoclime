"""Dataset registry: each bundled dataset described once, loaded the same way."""
from dataclasses import dataclass
from importlib import resources
from typing import Dict, List, Optional, Union

import pandas as pd

from .region import Region, resolve
from .timeseries import TimeSeries


@dataclass(frozen=True)
class DatasetSpec:
    name: str
    domain: str
    file: str
    year_col: str
    value_col: str
    unit: str
    source: str
    description: str
    region: str = "global"
    scale: float = 1.0                 # multiply raw values by this
    row_filter: Optional[tuple] = None  # (column, value) to keep


REGISTRY: Dict[str, DatasetSpec] = {
    "temperature": DatasetSpec(
        "temperature", "climate", "temperature_gistemp_hadcrut.csv", "Year", "Mean",
        "°C (anomaly)", "NASA GISTEMP via datahub.io/core/global-temp (CC-BY-4.0)",
        "Global mean surface temperature anomaly, annual.",
        row_filter=("Source", "GISTEMP")),
    "co2": DatasetSpec(
        "co2", "climate", "co2_mauna_loa_annual.csv", "Year", "Mean",
        "ppm", "NOAA Mauna Loa via datahub.io/core/co2-ppm (ODC-PDDL-1.0)",
        "Atmospheric CO2 annual mean at Mauna Loa."),
    "co2_global": DatasetSpec(
        "co2_global", "climate", "co2_global_annual.csv", "Year", "Mean",
        "ppm", "NOAA global marine average via datahub.io/core/co2-ppm (ODC-PDDL-1.0)",
        "Atmospheric CO2 annual mean, global average."),
    "sea_level": DatasetSpec(
        "sea_level", "ocean", "sea_level_epa.csv", "Year", "CSIRO Adjusted Sea Level",
        "cm", "CSIRO via EPA, datahub.io/core/sea-level-rise (ODC-PDDL-1.0)",
        "Cumulative global mean sea-level change since 1880 (converted from inches).",
        scale=2.54),
    "glacier_mass_balance": DatasetSpec(
        "glacier_mass_balance", "glaciology", "glacier_mass_balance.csv", "Year",
        "Mean cumulative mass balance", "m w.e.",
        "EPA via datahub.io/core/glacier-mass-balance (ODC-PDDL-1.0)",
        "Average cumulative mass balance of reference glaciers worldwide "
        "(metres of water equivalent; negative = net ice loss)."),
}


def list_datasets(domain: Optional[str] = None) -> pd.DataFrame:
    rows = [{"name": s.name, "domain": s.domain, "region": s.region, "unit": s.unit}
            for s in REGISTRY.values() if domain in (None, s.domain)]
    return pd.DataFrame(rows)


def describe(name: str) -> DatasetSpec:
    if name not in REGISTRY:
        raise KeyError(f"Unknown dataset '{name}'. Available: {sorted(REGISTRY)}")
    return REGISTRY[name]


def _read_csv(filename: str) -> pd.DataFrame:
    path = resources.files("geoclime").joinpath("data", filename)
    with resources.as_file(path) as p:
        return pd.read_csv(p)


def load(name: str, region: Union[str, Region, None] = "global",
         start: Optional[int] = None, end: Optional[int] = None) -> TimeSeries:
    """Load any dataset as a TimeSeries, optionally limited to a year range."""
    spec = describe(name)
    wanted = resolve(region)
    if wanted.name != spec.region:
        raise ValueError(f"Dataset '{name}' only provides region '{spec.region}', "
                         f"not '{wanted.name}'.")
    df = _read_csv(spec.file)
    if spec.row_filter:
        col, val = spec.row_filter
        df = df[df[col] == val]
    df = df[[spec.year_col, spec.value_col]].dropna()
    index = pd.to_datetime(df[spec.year_col].astype(int).astype(str), format="%Y")
    values = pd.Series(df[spec.value_col].to_numpy() * spec.scale, index=index, name=name)
    ts = TimeSeries(name, values.sort_index(), spec.unit, spec.domain,
                    spec.region, spec.source, spec.description)
    return ts.between(start, end)