"""Data file loading: CSV, Excel, Parquet -> pandas DataFrame."""

from pathlib import Path

import pandas as pd


FILTER_STRING = (
    "対応ファイル (*.csv *.tsv *.xlsx *.xls *.parquet *.pq);;"
    "CSV ファイル (*.csv *.tsv);;"
    "Excel ファイル (*.xlsx *.xls);;"
    "Parquet ファイル (*.parquet *.pq);;"
    "すべてのファイル (*)"
)


def load_file(filepath: str | Path) -> pd.DataFrame:
    """Load a data file and return a DataFrame."""
    path = Path(filepath)
    suffix = path.suffix.lower()

    if suffix in (".csv", ".tsv"):
        sep = "\t" if suffix == ".tsv" else ","
        return pd.read_csv(path, sep=sep)
    elif suffix in (".xlsx", ".xls"):
        return pd.read_excel(path)
    elif suffix in (".parquet", ".pq"):
        return pd.read_parquet(path)
    else:
        raise ValueError(f"Unsupported file format: {suffix}")
