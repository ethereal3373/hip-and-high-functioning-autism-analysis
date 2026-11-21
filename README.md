# High Intellectual Potential and High Functioning Autism: Data Analysis
Project baseed on the paper "High Intellectual Potential and High Functioning Autism: CLinical and Neurophysiological in a Pediatric Sample", published by NCBI/PubMed Central.

Riccioni et al. (2021). "High Intellectual Potential and High Functioning Autism: Clinical and Neurophysiological Features in a Pediatric Sample". Brain Sciences, 11(12), 1607. https://doi.org/10.3390/brainsci11121607

## Goal
Learn data analysis and the functioning of GitHub by exploring data of personal interest.

## What this project currently does
- Stores the summary values of Table 1 of the paper (which contains data results of behavioural analysis on the various groups: means, standard deviations and group sizes for HIP, HFA and NTD).
- Recomputes Cohen's d for HIP vs. HFA and compares it with the paper's values (all within 0.02).

## FIles
- `data/table1_summary.csv`: Table 1 summary data
- `analysis/01_load_and_pivot.py`: loads the data and reshapes it
- `analysis/02_cohens_d.py`: recomputes effect sizes
- `analysis/03_plot_ados_css.py`: makes the bar chart

## How to run
Install the libraries (`piip install pandas matplotlib`), then run any script, for example: `python analysis/02_cohens_d.py`

## Limits
The data presented in the paper is rappresented by averages of the scores, separated by group, not individual records.
