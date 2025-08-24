import importlib


def test_imports():
    mini_search = importlib.import_module("mini_search")
    assert mini_search is not None


def test_sanity():
    assert True
