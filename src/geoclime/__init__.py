"""geoclime: climate, ocean and glaciology data behind one region + time-series API."""
from .region import GLOBAL, Region
from .registry import describe, list_datasets, load
from .timeseries import TimeSeries, compare, correlation

__version__ = "0.1.0"
__all__ = ["GLOBAL", "Region", "TimeSeries", "compare", "correlation",
           "describe", "list_datasets", "load"]
