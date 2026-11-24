"""Shared constants and helpers."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
IMAGES = DATA / "images"
RESULTS = ROOT / "results"
METADATA_CSV = DATA / "metadata.csv"

# Epoch classes for the temporal classifier. Adjust to your annotation schema.
EPOCHS = [
    ("vor_1900", None, 1899),
    ("1900_1945", 1900, 1945),
    ("1946_1989", 1946, 1989),
    ("ab_1990", 1990, None),
]


def year_to_epoch(year):
    if year is None or year != year:  # None or NaN
        return None
    year = int(year)
    for name, lo, hi in EPOCHS:
        if (lo is None or year >= lo) and (hi is None or year <= hi):
            return name
    return None


def device():
    import torch
    return "cuda" if torch.cuda.is_available() else "cpu"
