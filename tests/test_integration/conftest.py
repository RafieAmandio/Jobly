import pytest


def pytest_collection_modifyitems(config, items):
    if config.getoption("-m", default=None):
        return
    skip = pytest.mark.skip(reason="use -m integration to run live API tests")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip)
