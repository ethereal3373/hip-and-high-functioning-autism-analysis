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
TABLE2_FILE = PROJECT_DIR / "data" / "table2_summary.csv"
TABLE3_FILE = PROJECT_DIR / "data" / "table3_summary.csv"
EFFECT_SIZES_FILE = PROJECT_DIR / "figures" / "effect_sizes_table2.png"
MMN_FILE = PROJECT_DIR / "figures" / "mmn_table3.png"

# Colors for the two kinds of bars (same blue/orange pair as analysis/04_plot_effect_sizes.py).
COLOR_HIGHER = "#1f77b4"  # blue: HIP scored higher than HFA
COLOR_LOWER = "#e66100"   # orange: HIP scored lower than HFA

# Which test each Table 2 measure comes from. The order of the categories here
# is the order they appear in the chart, from top to bottom.
CATEGORIES = {
    "CPRS-R": ["Oppositional", "Cognitive_pr", "Hyper_imp", "Anx_shy", "Perfectionism",
               "Social_probl", "Psychosomatic", "ADHD_Index", "DSM_IV_Tot"],
    "NEPSY-II": ["Design_fluency", "Visual_attention", "Inhibition",
                 "Auditory_attention", "Response_set"],
}

# Groups and colors for the MMN chart (one neutral color per group).
GROUPS = ["HIP", "HFA", "NTD"]
GROUP_COLORS = {"HIP": "#1f77b4", "HFA": "#e66100", "NTD": "#7f7f7f"}

# ---------------------------------------------------------------------------
# Chart 1: effect sizes for Table 2
# ---------------------------------------------------------------------------

# Step 1: Read the Table 2 CSV file into a table (a pandas "DataFrame").
df = pd.read_csv(TABLE2_FILE)

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

# Step 5: Pick a color for each bar (blue if HIP higher, orange if HIP lower),
# then draw the bars and a legend.
colors = [COLOR_HIGHER if d > 0 else COLOR_LOWER for d in bar_values]
fig, ax = plt.subplots(figsize=(7, 7))
ax.barh(bar_rows, bar_values, color=colors)
ax.legend(
    handles=[
        Patch(color=COLOR_HIGHER, label="HIP scored higher"),
        Patch(color=COLOR_LOWER, label="HIP scored lower"),
    ],
    loc="lower right",
)

# Step 6: Write the measure names and the bold category titles on the left,
# flip the axis so row 0 is at the top, and draw the thin line between blocks.
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
ax.set_title("Effect sizes (Table 2): HIP vs HFA")
ax.set_xlabel("Cohen's d (HIP minus HFA)")

# Step 8: Create the "figures" folder if needed, then save the chart as a PNG image.
EFFECT_SIZES_FILE.parent.mkdir(parents=True, exist_ok=True)
fig.tight_layout()
fig.savefig(EFFECT_SIZES_FILE, dpi=150)
plt.close(fig)
print(f"Saved chart to {EFFECT_SIZES_FILE}")

# ---------------------------------------------------------------------------
# Chart 2: MMN amplitude and latency for Table 3
# ---------------------------------------------------------------------------

# Step 9: Read the Table 3 CSV file.
t3 = pd.read_csv(TABLE3_FILE)

# Step 10: Make two charts side by side, one for each MMN measure.
panels = [("MMN_amplitude", "MMN amplitude", "Amplitude"),
          ("MMN_latency", "MMN latency", "Latency (ms)")]
fig, axes = plt.subplots(1, 2, figsize=(9, 4))

# Step 11: In each chart, draw one bar per group (mean) with an SD error bar,
# and put the group size (n) under each group name.
for ax, (measure, title, ylabel) in zip(axes, panels):
    rows = t3[t3["measure"] == measure].set_index("group").loc[GROUPS]
    labels = [f"{g}\n(n={int(n)})" for g, n in zip(rows.index, rows["n"])]
    ax.bar(labels, rows["mean"], yerr=rows["sd"], capsize=5,
           color=[GROUP_COLORS[g] for g in rows.index])
    ax.set_title(title)
    ax.set_ylabel(ylabel)

# Step 12: Add an overall title, then save the chart as a PNG image.
fig.suptitle("Table 3: MMN by group (mean ± SD)")
fig.tight_layout()
fig.savefig(MMN_FILE, dpi=150)
plt.close(fig)
print(f"Saved chart to {MMN_FILE}")
