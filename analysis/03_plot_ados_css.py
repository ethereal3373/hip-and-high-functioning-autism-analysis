from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

# Find the project folder relative to this script, so the script works
# no matter which folder you run it from.
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_DIR / "data" / "table1_summary.csv"
OUTPUT_FILE = PROJECT_DIR / "figures" / "ados_css.png"

# Step 1: Read the CSV file into a table (a pandas "DataFrame").
df = pd.read_csv(DATA_FILE)

# Step 2: Keep only the ADOS_CSS rows, and put the groups in a fixed order
# (HIP, HFA, NTD) so the bars always appear in that order.
ados = df[df["measure"] == "ADOS_CSS"].set_index("group")
ados = ados.loc[["HIP", "HFA", "NTD"]]

# Step 3: Draw one bar per group. The bar height is the group's mean,
# and the thin line on top (the error bar) shows one SD above and below it.
fig, ax = plt.subplots(figsize=(6, 4.5))
ax.bar(ados.index, ados["mean"], yerr=ados["sd"], capsize=6, color="steelblue")

# Step 4: Add a title, a y-axis label, and x-axis labels that include
# each group's size, for example "HIP (n=16)".
ax.set_title("ADOS-2 Calibrated Severity Score by group")
ax.set_ylabel("ADOS CSS (mean ± SD)")
labels = [f"{group} (n={n})" for group, n in zip(ados.index, ados["n"])]
ax.set_xticks(range(len(labels)))
ax.set_xticklabels(labels)

# Step 5: Create the "figures" folder if it doesn't exist yet,
# then save the chart there as a PNG image.
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
fig.tight_layout()
fig.savefig(OUTPUT_FILE, dpi=150)
print(f"Saved chart to {OUTPUT_FILE}")
