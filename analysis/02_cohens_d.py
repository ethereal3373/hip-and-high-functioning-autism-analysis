from pathlib import Path

import pandas as pd

# Formulas used below (group 1 = HIP, group 2 = HFA):
#
#   Pooled SD:  sp = sqrt( ((n1 - 1) * sd1**2 + (n2 - 1) * sd2**2) / (n1 + n2 - 2) )
#   Cohen's d:  d  = (mean1 - mean2) / sp
#
# A positive d means HIP scored higher than HFA on that measure;
# a negative d means HIP scored lower.

# Find the CSV file relative to this script, so the script works
# no matter which folder you run it from.
DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "table1_summary.csv"

# Step 1: Read the CSV file into a table (a pandas "DataFrame").
df = pd.read_csv(DATA_FILE)

# Step 2a: Make one small table per group, then join them side by side on
# "measure". The join keeps only measures that appear in BOTH groups.
hip = df[df["group"] == "HIP"]
hfa = df[df["group"] == "HFA"]
both = hip.merge(hfa, on="measure", suffixes=("_hip", "_hfa"))

# Step 2b: Work out the pooled standard deviation for each measure,
# using each group's own sample size (n) from the file.
pooled_sd = (
    ((both["n_hip"] - 1) * both["sd_hip"] ** 2 + (both["n_hfa"] - 1) * both["sd_hfa"] ** 2)
    / (both["n_hip"] + both["n_hfa"] - 2)
) ** 0.5

# Step 2c: Cohen's d = difference in means (HIP minus HFA) divided by the pooled SD.
both["d"] = (both["mean_hip"] - both["mean_hfa"]) / pooled_sd

# Step 3: Print one line per measure: its name and d rounded to 2 decimals.
for measure, d in zip(both["measure"], both["d"]):
    print(f"{measure}: {d:.2f}")
