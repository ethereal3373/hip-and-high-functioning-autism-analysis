from pathlib import Path

import pandas as pd
from scipy.stats import ttest_ind_from_stats

# Formulas used below (same as analysis/02_cohens_d.py; group 1 = HIP, group 2 = HFA):
#
#   Pooled SD:  sp = sqrt( ((n1 - 1) * sd1**2 + (n2 - 1) * sd2**2) / (n1 + n2 - 2) )
#   Cohen's d:  d  = (mean1 - mean2) / sp
#
# The p-value comes from a two-sided Student's t-test (equal variances assumed),
# calculated straight from the means, SDs and group sizes.

# Find the project folder relative to this script, so the script works
# no matter which folder you run it from.
PROJECT_DIR = Path(__file__).resolve().parent.parent
TABLE2_FILE = PROJECT_DIR / "data" / "table2_summary.csv"
TABLE3_FILE = PROJECT_DIR / "data" / "table3_summary.csv"
REPORTED_FILE = PROJECT_DIR / "data" / "reported_stats_hip_vs_hfa.csv"
OUTPUT_FILE = PROJECT_DIR / "results" / "table2_3_consistency_check.csv"

# How big a difference counts as "worth checking".
D_TOLERANCE = 0.05  # flag d if recomputed and reported differ by more than this
P_FACTOR = 10       # flag p if one is more than 10 times the other

# Step 1: Read the two summary tables and stack them into one table.
df = pd.concat([pd.read_csv(TABLE2_FILE), pd.read_csv(TABLE3_FILE)], ignore_index=True)

# Step 2: Read the reported values. We read p as text so "<0.001" stays as written.
reported = pd.read_csv(REPORTED_FILE, dtype={"p_reported": str})

# Step 3: Put the HIP and HFA rows side by side (keeping only measures both groups have),
# and drop any measure without SDs (P300_ms), because d and p need them.
hip = df[df["group"] == "HIP"]
hfa = df[df["group"] == "HFA"]
both = hip.merge(hfa, on="measure", suffixes=("_hip", "_hfa"))
skipped = both.loc[both["sd_hip"].isna() | both["sd_hfa"].isna(), "measure"].tolist()
if skipped:
    print(f"Skipped (no SDs): {', '.join(skipped)}")
both = both.dropna(subset=["sd_hip", "sd_hfa"])

# Step 4: Calculate the pooled SD and Cohen's d for each measure.
pooled_sd = (
    ((both["n_hip"] - 1) * both["sd_hip"] ** 2 + (both["n_hfa"] - 1) * both["sd_hfa"] ** 2)
    / (both["n_hip"] + both["n_hfa"] - 2)
) ** 0.5
both["d_recomputed"] = (both["mean_hip"] - both["mean_hfa"]) / pooled_sd

# Step 5: Calculate the two-sided p-value for each measure from the summary numbers.
result = ttest_ind_from_stats(
    both["mean_hip"], both["sd_hip"], both["n_hip"],
    both["mean_hfa"], both["sd_hfa"], both["n_hfa"],
    equal_var=True,
)
both["p_recomputed"] = result.pvalue

# Step 6: Add the reported values next to the recomputed ones.
both = both.merge(reported, on="measure", how="left")
both["d_difference"] = both["d_recomputed"] - both["d_reported"]


# Step 7: Decide whether a recomputed p and a reported p are too far apart.
# "<0.001" only tells us p is below 0.001, so we only flag it if the
# recomputed p is above 0.01 (more than 10 times the upper bound).
def p_needs_check(p_recomputed, p_reported_text):
    if p_reported_text.startswith("<"):
        upper_bound = float(p_reported_text[1:])
        return p_recomputed > upper_bound * P_FACTOR
    p_reported = float(p_reported_text)
    bigger = max(p_recomputed, p_reported)
    smaller = min(p_recomputed, p_reported)
    return bigger > smaller * P_FACTOR


# Step 8: Build the flag text for each measure ("ok" if nothing to check).
flags = []
for d_diff, p_rec, p_rep in zip(both["d_difference"], both["p_recomputed"], both["p_reported"]):
    flag = []
    if abs(d_diff) > D_TOLERANCE:
        flag.append("check d")
    if p_needs_check(p_rec, p_rep):
        flag.append("check p")
    flags.append(", ".join(flag) if flag else "ok")
both["flag"] = flags

# Step 9: Print one line per measure.
print(f"{'measure':<20}{'d recomp':>9}{'d rep':>7}{'diff':>7}{'p recomp':>10}{'p rep':>8}  flag")
for _, r in both.iterrows():
    print(
        f"{r['measure']:<20}{r['d_recomputed']:>9.2f}{r['d_reported']:>7.2f}"
        f"{r['d_difference']:>7.2f}{r['p_recomputed']:>10.4f}{r['p_reported']:>8}  {r['flag']}"
    )

# Step 10: Create the "results" folder if needed and save the full table there.
columns = ["measure", "d_recomputed", "d_reported", "d_difference",
           "p_recomputed", "p_reported", "flag"]
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
both[columns].to_csv(OUTPUT_FILE, index=False)
print(f"\nSaved full result to {OUTPUT_FILE}")

# Step 11: Say how many measures were flagged and which ones.
flagged = both[both["flag"] != "ok"]
print(f"{len(flagged)} of {len(both)} measures flagged:")
for measure, flag in zip(flagged["measure"], flagged["flag"]):
    print(f"  {measure} ({flag})")
