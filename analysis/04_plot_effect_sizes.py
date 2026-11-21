from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Patch

# Formulas used below (same as analysis/02_cohens_d.py; group 1 = HIP, group 2 = HFA):
#
#   Pooled SD:  sp = sqrt( ((n1 - 1) * sd1**2 + (n2 - 1) * sd2**2) / (n1 + n2 - 2) )
#   Cohen's d:  d  = (mean1 - mean2) / sp

# Find the project folder relative to this script, so the script works
# no matter which folder you run it from.
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_DIR / "data" / "table1_summary.csv"
OUTPUT_FILE = PROJECT_DIR / "figures" / "effect_sizes_hip_vs_hfa.png"

# Colors for the two kinds of bars (a blue/orange pair that colorblind readers can tell apart).
COLOR_HIGHER = "#1f77b4"  # blue: HIP scored higher than HFA
COLOR_LOWER = "#e66100"   # orange: HIP scored lower than HFA

# Which test each measure comes from. The order of the categories here is the
# order they appear in the chart, from top to bottom.
CATEGORIES = {
    "WISC-IV": ["IQ", "VCI", "PRI", "WMI", "PSI"],
    "ABAS-II": ["ABAS_GAC", "ABAS_CAD", "ABAS_SAD", "ABAS_PAD"],
    "ADOS-2": ["ADOS_SA", "ADOS_RRB", "ADOS_CSS"],
    "SRS": ["SRS_T", "SRS_SA", "SRS_SC", "SRS_SCo", "SRS_SM", "SRS_AM"],
}

# Step 1: Read the CSV file into a table (a pandas "DataFrame").
df = pd.read_csv(DATA_FILE)

# Step 2: Put the HIP and HFA rows side by side (keeping only measures both groups have),
# then calculate the pooled SD and Cohen's d for each measure.
hip = df[df["group"] == "HIP"]
hfa = df[df["group"] == "HFA"]
both = hip.merge(hfa, on="measure", suffixes=("_hip", "_hfa"))
pooled_sd = (
    ((both["n_hip"] - 1) * both["sd_hip"] ** 2 + (both["n_hfa"] - 1) * both["sd_hfa"] ** 2)
    / (both["n_hip"] + both["n_hfa"] - 2)
) ** 0.5
both["d"] = (both["mean_hip"] - both["mean_hfa"]) / pooled_sd

# Step 3: Label each measure with its category. Any measure that isn't in the
# list above is left out of the chart, and the script prints its name so you notice.
measure_to_category = {m: cat for cat, measures in CATEGORIES.items() for m in measures}
both["category"] = both["measure"].map(measure_to_category)
unlisted = both.loc[both["category"].isna(), "measure"].tolist()
if unlisted:
    print(f"Not in any category, left out of the chart: {', '.join(unlisted)}")
both = both.dropna(subset=["category"])

# Step 4: Work out where each row goes, from the top of the chart down.
# Each category block gets one row for its bold title, followed by its bars
# sorted by d (most positive first, so it sits at the top of the block).
# Between blocks we remember a position for a thin separator line.
bar_rows, bar_values = [], []
label_rows, label_texts, label_is_title = [], [], []
separator_rows = []
row = 0
for category in CATEGORIES:
    block = both[both["category"] == category].sort_values("d", ascending=False)
    if block.empty:
        continue
    if row > 0:
        separator_rows.append(row - 0.5)
    label_rows.append(row)
    label_texts.append(category)
    label_is_title.append(True)
    row += 1
    for measure, d in zip(block["measure"], block["d"]):
        bar_rows.append(row)
        bar_values.append(d)
        label_rows.append(row)
        label_texts.append(measure)
        label_is_title.append(False)
        row += 1

# Step 5: Pick a color for each bar: one color when d is positive (HIP higher),
# another when d is negative (HIP lower). Then draw the bars and a legend.
colors = [COLOR_HIGHER if d > 0 else COLOR_LOWER for d in bar_values]
fig, ax = plt.subplots(figsize=(7, 8))
ax.barh(bar_rows, bar_values, color=colors)
ax.legend(
    handles=[
        Patch(color=COLOR_HIGHER, label="HIP scored higher"),
        Patch(color=COLOR_LOWER, label="HIP scored lower"),
    ],
    loc="lower right",
)

# Step 6: Write the measure names and the bold category titles on the left,
# flip the axis so row 0 is at the top, and draw the thin lines between blocks.
ax.set_yticks(label_rows)
ax.set_yticklabels(label_texts)
for tick_label, is_title in zip(ax.get_yticklabels(), label_is_title):
    if is_title:
        tick_label.set_fontweight("bold")
ax.tick_params(axis="y", length=0)
ax.invert_yaxis()
for y in separator_rows:
    ax.axhline(y, color="gray", linewidth=0.6)

# Step 7: Add a vertical line at 0 (no difference), a title, and an x-axis label.
ax.axvline(0, color="black", linewidth=1)
ax.set_title("Effect sizes: HIP vs HFA")
ax.set_xlabel("Cohen's d (HIP minus HFA)")

# Step 8: Create the "figures" folder if it doesn't exist yet,
# then save the chart there as a PNG image.
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
fig.tight_layout()
fig.savefig(OUTPUT_FILE, dpi=150)
print(f"Saved chart to {OUTPUT_FILE}")
