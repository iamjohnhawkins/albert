"""Smoke test proving the package imports and the CI pipeline runs tests."""

import albert


def test_package_exposes_a_version() -> None:
    assert albert.__version__ == "0.0.0"
