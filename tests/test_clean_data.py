import pandas as pd
from pipeline.clean_data import remove_duplicates


def test_remove_duplicates_removes_exact_duplicates():
    df = pd.DataFrame({
        "a": [1, 1, 2, 3],
        "b": ["x", "x", "y", "z"]
    })
    result = remove_duplicates(df)
    assert len(result) == 3


def test_remove_duplicates_keeps_non_duplicates_unchanged():
    df = pd.DataFrame({
        "a": [1, 2, 3],
        "b": ["x", "y", "z"]
    })
    result = remove_duplicates(df)
    assert len(result) == 3


def test_remove_duplicates_handles_empty_dataframe():
    df = pd.DataFrame({"a": [], "b": []})
    result = remove_duplicates(df)
    assert len(result) == 0