import pytest

import geoclime as gc


def test_list_covers_three_domains():
    df = gc.list_datasets()
    assert set(df["domain"]) == {"climate", "ocean", "glaciology"}
    assert len(df) == 5


@pytest.mark.parametrize("name", ["temperature", "co2", "sea_level", "glacier_mass_balance"])
def test_every_dataset_loads_the_same_way(name):
    ts = gc.load(name)
    assert len(ts) > 30
    assert ts.values.index.is_monotonic_increasing
    assert ts.values.notna().all()


def test_between_is_inclusive():
    ts = gc.load("co2", start=1990, end=2000)
    assert ts.years.min() == 1990 and ts.years.max() == 2000 and len(ts) == 11


def test_sea_level_converted_to_cm():
    ts = gc.load("sea_level")
    assert ts.unit == "cm"
    assert ts.values.iloc[0] == 0.0
    assert ts.values.iloc[-1] > 15  # about 9 inches = 23 cm by 2013


def test_trends_have_expected_sign():
    assert gc.load("temperature", start=1959, end=2013).trend_per_decade() > 0
    assert gc.load("co2").trend_per_decade() > 0
    assert gc.load("glacier_mass_balance").trend_per_decade() < 0


def test_compare_aligns_on_common_years():
    df = gc.compare([gc.load("temperature", start=1959, end=2013),
                     gc.load("sea_level", start=1959, end=2013),
                     gc.load("co2", start=1959, end=2013)])
    assert df.shape == (55, 3)
    assert not df.isna().any().any()


def test_temperature_and_co2_strongly_correlated():
    r = gc.correlation(gc.load("temperature"), gc.load("co2"))
    assert r > 0.9
    r_diff = gc.correlation(gc.load("temperature"), gc.load("co2"), differenced=True)
    assert abs(r_diff) < r


def test_anomaly_baseline_mean_is_zero():
    ts = gc.load("co2").anomaly(1960, 1970)
    assert abs(ts.between(1960, 1970).values.mean()) < 1e-9


def test_unknown_dataset_and_region_raise_clear_errors():
    with pytest.raises(KeyError):
        gc.load("rainfall")
    with pytest.raises(ValueError):
        gc.load("co2", region="arctic")
    with pytest.raises(ValueError):
        gc.load("co2", region="atlantis")

def test_added_dataset_global_co2():
    ts = gc.load("co2_global")
    assert ts.years.min() == 1979
    assert gc.correlation(ts, gc.load("co2")) > 0.99
