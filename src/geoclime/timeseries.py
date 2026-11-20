"""TimeSeries: one common shape for every dataset, whatever its domain."""
from dataclasses import dataclass
from typing import Iterable, Optional

import numpy as np
import pandas as pd


@dataclass
class TimeSeries:
    name: str
    values: pd.Series          # DatetimeIndex (annual, 1 Jan of each year)
    unit: str
    domain: str                # "climate", "ocean" or "glaciology"
    region: str
    source: str
    description: str = ""

    # ---- basics -------------------------------------------------------
    def __len__(self) -> int:
        return len(self.values)

    @property
    def years(self) -> np.ndarray:
        return self.values.index.year.to_numpy()

    def _replace(self, values: pd.Series, name: Optional[str] = None) -> "TimeSeries":
        return TimeSeries(name or self.name, values, self.unit, self.domain,
                          self.region, self.source, self.description)

    def to_frame(self) -> pd.DataFrame:
        df = self.values.rename(self.name).to_frame()
        df.index = df.index.year
        df.index.name = "year"
        return df

    # ---- operations ---------------------------------------------------
    def between(self, start: Optional[int] = None, end: Optional[int] = None) -> "TimeSeries":
        """Keep years start..end (both inclusive). None means open-ended."""
        mask = np.ones(len(self.values), dtype=bool)
        if start is not None:
            mask &= self.years >= start
        if end is not None:
            mask &= self.years <= end
        return self._replace(self.values[mask])

    def rolling_mean(self, years: int) -> "TimeSeries":
        return self._replace(self.values.rolling(years, min_periods=years).mean().dropna())

    def anomaly(self, base_start: int, base_end: int) -> "TimeSeries":
        """Subtract the mean of a baseline period."""
        base = self.between(base_start, base_end).values
        if base.empty:
            raise ValueError("Baseline period has no data.")
        return self._replace(self.values - base.mean())

    def trend_per_decade(self) -> float:
        """Least-squares linear trend, in the series' unit per 10 years."""
        clean = self.values.dropna()
        if len(clean) < 2:
            raise ValueError("Need at least 2 points to fit a trend.")
        slope, _ = np.polyfit(clean.index.year.to_numpy(), clean.to_numpy(), 1)
        return float(slope * 10)

    def summary(self) -> dict:
        v = self.values.dropna()
        return {
            "name": self.name, "domain": self.domain, "region": self.region,
            "unit": self.unit, "n": int(len(v)),
            "first_year": int(v.index.year.min()), "last_year": int(v.index.year.max()),
            "min": float(v.min()), "max": float(v.max()), "mean": float(v.mean()),
            "trend_per_decade": self.trend_per_decade(),
        }


def compare(series: Iterable[TimeSeries], how: str = "inner") -> pd.DataFrame:
    """Align several series on year. 'inner' keeps only years all have."""
    frames = [s.to_frame() for s in series]
    if not frames:
        raise ValueError("Pass at least one series.")
    return pd.concat(frames, axis=1, join=how)


def correlation(a: TimeSeries, b: TimeSeries, differenced: bool = False) -> float:
    """Pearson r on common years. differenced=True correlates year-to-year
    changes, which removes the shared long-term trend."""
    df = compare([a, b]).dropna()
    if differenced:
        df = df.diff().dropna()
    if len(df) < 3:
        raise ValueError("Need at least 3 overlapping points.")
    return float(df.iloc[:, 0].corr(df.iloc[:, 1]))
