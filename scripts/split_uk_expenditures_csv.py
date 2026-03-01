#!/usr/bin/env python3
"""
Split the UK expenditures source CSV into:
1. uk_income.csv - yearly income and post-tax income by quintile and age group
2. uk_expenditures_by_age.csv - all expenditure breakdowns by age group and quintile
"""
import csv
import re
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
DOWNLOADS = Path.home() / "Downloads"
SOURCE_CSV = DOWNLOADS / "M3 Challenge Problem Data .xlsx - nf (exp, uk) converted to USD.csv"
OUT_INCOME = PROJECT_ROOT / "uk_income.csv"
OUT_EXPENDITURES = PROJECT_ROOT / "uk_expenditures_by_age.csv"

AGE_GROUPS = [
    "Age < 30",
    "Age 30-49",
    "Age 50-64",
    "Age 65-74",
    "Age > 74",
]
QUINTILES = ["Lowest 20%", "Second 20%", "Third 20%", "Fourth 20%", "Highest 20%", "All"]
# Each age block: 1 label col + 6 data cols + 1 blank = 8 columns. First column (0) is row label.
BLOCK_SIZE = 8
N_AGE_BLOCKS = 5


def parse_number(s: str):
    """Parse a number, handling '..' and comma-separated thousands."""
    if not s or s.strip() in ("", ".."):
        return None
    s = s.strip().replace(",", "")
    try:
        return float(s)
    except ValueError:
        return None


def read_source_rows():
    """Read source CSV and return list of rows (list of cells)."""
    with open(SOURCE_CSV, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        return list(reader)


def get_block_values(row, block_index):
    """Get the 6 values (quintiles + All) for one age block. block_index 0..4."""
    start = 1 + block_index * BLOCK_SIZE
    return [row[i] if i < len(row) else "" for i in range(start, start + 6)]


def build_income_csv(rows):
    """Build income CSV with income, necessary expenses, and ratios by age and quintile."""
    # Row indices (0-based): 20=Weekly Necessary, 21=Yearly Necessary, 22=Weekly income, 23=Yearly Income, 24=posttax, 25=disposable, 26=disposable/posttax
    weekly_necessary_row = rows[20]
    yearly_necessary_row = rows[21]
    weekly_income_row = rows[22]
    year_row = rows[23]
    posttax_row = rows[24]
    disposable_row = rows[25]
    ratio_row = rows[26]

    out = []
    out.append([
        "age_group", "quintile",
        "yearly_income_usd", "posttax_income_usd",
        "weekly_necessary_expenses_usd", "yearly_necessary_expenses_usd",
        "weekly_income_usd", "disposable_income_usd", "disposable_income_posttax_ratio",
    ])

    for age_idx, age_name in enumerate(AGE_GROUPS):
        year_vals = get_block_values(year_row, age_idx)
        posttax_vals = get_block_values(posttax_row, age_idx)
        weekly_necessary_vals = get_block_values(weekly_necessary_row, age_idx)
        yearly_necessary_vals = get_block_values(yearly_necessary_row, age_idx)
        weekly_income_vals = get_block_values(weekly_income_row, age_idx)  # often only block 0 has data; others get ""
        disposable_vals = get_block_values(disposable_row, age_idx)
        ratio_vals = get_block_values(ratio_row, age_idx)
        for q_idx, q in enumerate(QUINTILES):
            y = parse_number(year_vals[q_idx])
            p = parse_number(posttax_vals[q_idx])
            wn = parse_number(weekly_necessary_vals[q_idx])
            yn = parse_number(yearly_necessary_vals[q_idx])
            wi = parse_number(weekly_income_vals[q_idx])
            if wi is None and age_idx > 0:
                wi = parse_number(get_block_values(weekly_income_row, 0)[q_idx])  # fallback to first age block
            d = parse_number(disposable_vals[q_idx])
            r = parse_number(ratio_vals[q_idx])
            if y is not None or p is not None or wn is not None or yn is not None or wi is not None or d is not None or r is not None:
                out.append([
                    age_name, q,
                    y if y is not None else "",
                    p if p is not None else "",
                    wn if wn is not None else "",
                    yn if yn is not None else "",
                    wi if wi is not None else "",
                    d if d is not None else "",
                    r if r is not None else "",
                ])
    return out


def build_expenditures_csv(rows):
    """Build expenditures CSV: age_group, quintile, category, average_weekly_expenditure_gbp."""
    # Expenditure data: rows 7 (persons), 9 (commodity header), 10-21 (categories), 22-23 (necessary expenses)
    # Skip row 8 (header "Commodity or service") and skip income rows 24-28
    # Row 7 = persons, 9-20 = commodity rows, 20 = Weekly Necessary, 21 = Yearly Necessary (do not include income rows 22+)
    EXPENDITURE_ROW_INDICES = [7] + list(range(9, 21)) + [20, 21]

    out = []
    out.append(["age_group", "quintile", "category", "amount_usd", "unit"])

    for age_idx, age_name in enumerate(AGE_GROUPS):
        for row_idx in EXPENDITURE_ROW_INDICES:
            if row_idx >= len(rows):
                continue
            row = rows[row_idx]
            label = (row[0] or "").strip()
            if not label:
                continue
            if label == "Commodity or service" or "Average weekly household expenditure" in label:
                continue
            unit = "yearly" if "Yearly Necessary" in label else "weekly"
            vals = get_block_values(row, age_idx)
            for q_idx, q in enumerate(QUINTILES):
                v = parse_number(vals[q_idx])
                out.append([age_name, q, label, v if v is not None else "", unit])
    return out


def main():
    if not SOURCE_CSV.exists():
        raise FileNotFoundError(f"Source file not found: {SOURCE_CSV}")

    rows = read_source_rows()
    if len(rows) < 27:
        raise ValueError("Source CSV has too few rows")

    # Income CSV
    income_data = build_income_csv(rows)
    with open(OUT_INCOME, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(income_data)
    print(f"Wrote {len(income_data)-1} income rows to {OUT_INCOME}")

    # Expenditures CSV (use same column name; for yearly necessary we store the yearly value)
    exp_data = build_expenditures_csv(rows)
    with open(OUT_EXPENDITURES, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(exp_data)
    print(f"Wrote {len(exp_data)-1} expenditure rows to {OUT_EXPENDITURES}")


if __name__ == "__main__":
    main()
