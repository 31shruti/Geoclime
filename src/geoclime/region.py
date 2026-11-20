"""Regions: where on Earth a dataset applies.

MVP note: every bundled dataset is a *global* series, so only the "global"
region is available today. The Region class (with an optional bounding box)
is the extension point for gridded or regional datasets later.
"""
from dataclasses import dataclass
from typing import Optional, Tuple, Union


@dataclass(frozen=True)
class Region:
    name: str
    # (lat_min, lat_max, lon_min, lon_max) in degrees; None means "whole Earth"
    bbox: Optional[Tuple[float, float, float, float]] = None

    def contains(self, lat: float, lon: float) -> bool:
        if self.bbox is None:
            return True
        lat_min, lat_max, lon_min, lon_max = self.bbox
        return lat_min <= lat <= lat_max and lon_min <= lon <= lon_max


GLOBAL = Region("global")

_KNOWN = {
    "global": GLOBAL,
    "arctic": Region("arctic", (66.5, 90.0, -180.0, 180.0)),
    "tropics": Region("tropics", (-23.5, 23.5, -180.0, 180.0)),
    "india": Region("india", (6.0, 37.0, 68.0, 98.0)),
}


def resolve(region: Union[str, Region, None]) -> Region:
    """Turn a name (or Region) into a Region. None means global."""
    if region is None:
        return GLOBAL
    if isinstance(region, Region):
        return region
    key = str(region).strip().lower()
    if key not in _KNOWN:
        raise ValueError(f"Unknown region '{region}'. Known regions: {sorted(_KNOWN)}")
    return _KNOWN[key]
