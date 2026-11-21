from pathlib import Path

import pandas as pd

# Find the CSV file relative to this script, so the script works
# no matter which folder you run it from.
DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "table1_summary.csv"

# Step 1: Read the CSV file into a table (a pandas "DataFrame").
df = pd.read_csv(DATA_FILE)

# Step 2: Print the data exactly as it was read, one row per measure-and-group pair.
print("Original data (long format):")
print(df.to_string(index=False))
print()

# Step 3: Reshape the table so there is one row per measure and one column
# of mean values for each group. If a group has no value for a measure,
# that cell is shown as NaN ("not a number", meaning missing).
wide = df.pivot(index="measure", columns="group", values="mean")
wide = wide[["HIP", "HFA", "NTD"]]  # put the group columns in a fixed order
print("Means by group (wide format):")
print(wide.to_string())
