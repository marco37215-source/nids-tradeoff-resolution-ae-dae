# Outputs of the reference run

I produced every file in this folder by running `python scripts/reproduce_all.py --data-dir data/raw` with the pinned versions in `requirements.txt`. If you run the script again, these files are overwritten with your own outputs, which you can compare with the ones stored here.

In every file, differences are DAE minus AE, and the cost ratio is ρ = C_FP / C_FN. Table and figure numbers are those of the typeset article.

## Tables (`tables/`)

| File | Contents | Manuscript |
| :-- | :-- | :-- |
| `input_integrity_checks.csv` | One row per run: population size and class counts; whether row identifiers and labels match the other runs of the dataset; the threshold T₉₉; whether the stored predictions follow ŷ = 1 if e > T₉₉; the smallest distance between an error and the threshold. | Sections 3.2, 3.5 |
| `seed_level_metrics.csv` | TP, FP, FN, TN, MCC, recall, F1, precision, PR-AUC, FPR, FP per 1,000 benign and balanced accuracy, for each dataset, model and seed. | Basis of Section 4 |
| `table04_five_seed_performance.csv` | Five-seed mean and sample SD of MCC, recall, PR-AUC and FPR; mean FP per 1,000 benign; mean TP, FP and FN. | Table 4 |
| `paired_seed_effects.csv` | For each metric: mean, median and SD of the five paired differences; d_z; seeds favouring each model; bootstrap and paired *t* intervals; paired *t* *p*-value. | Section 4.1 |
| `table05_seed_decision_states.csv` | ΔTP, ΔFP, the decision state and ρ\* (exact fraction and decimal) for every seed. | Table 5 |
| `table06_path_composition.csv` | Number and percentage of the 3,125 enumerated paths in each state. | Table 6 |
| `path_composition_by_seed_202.csv` | The same counts, split by whether a path contains seed 202. | Section 4.3 |
| `table07_decision_map_unsw_nb15.csv` | For each open interval of ρ: seeds favouring the DAE, seeds favouring the AE, and the count favouring the DAE. | Table 7 |
| `prevalence_rescaling_illustration_unsw_nb15.csv` | Seed-specific and ratio-of-means thresholds and their values under Equation 10 at π = 0.01 (an arithmetic illustration, not an observed result). | Section 5.3 |
| `mcnemar_by_seed.csv` | Discordant counts, net gain of the DAE and the exact two-sided *p*-value, per dataset and seed. | Section 4.5 |
| `score_diagnostics_by_run.csv` | Per run: median and maximum of e / T₉₉ over missed attacks; benign median error; number and percentage of attacks below that median. | Section 4.6 |
| `table08_score_diagnostics.csv` | Mean over seeds, with the range across seeds, of the two diagnostics. | Table 8 |
| `table09_count_resolution.csv` | For TP and FP, per dataset: each model's mean, SD and range over the five seeds; the seed-matched correlation; the mean paired difference with its post hoc, nominal 95% *t* interval and *p*-value; the exact two-sided sign test; whether the mean difference is nominally resolved. | Table 9, Section 4.7, Figure 1 |
| `cross_seed_states.csv` | ΔTP, ΔFP and the decision state for all 25 combinations AE_i versus DAE_j per dataset, ignoring the seed pairing. | Section 4.7 |
| `table10_loss_differences.csv` | Mean paired loss difference ρΔFP − ΔTP at ρ = 0.1, 1, 10, 100, with its pointwise nominal 95% *t* interval, *p*-value and seeds favouring each model. | Table 10, Section 4.7 |
| `loss_resolved_cost_ratios.csv` | The exact intervals of ρ on which the pointwise interval of the mean loss difference excludes zero, and the model favoured there. | Section 4.7, Figure 3 |
| `fig3_loss_curve_data.csv` | The plotted values of Figure 3: mean, pointwise interval and individual seeds of (ρΔFP − ΔTP)/(1 + ρ) on 801 log-spaced values of ρ. | Figure 3 |
| `configuration_pairs.csv` | ΔTP, ΔFP, ΔMCC and the decision state for each of the 400 search-stage AE–DAE configuration pairs per dataset (development partition, seed 101). | Section 4.8, Figure 4 |
| `table11_configuration_pairs.csv` | State counts of those pairs, their split by the sign of ΔMCC, median absolute count differences, the range of false-positive rates across the 40 configurations, and the number of configurations that occur in both a dominance and a trade-off state. | Table 11, Section 4.8 |

## Figures (`figures/`)

Each figure is saved as a vector PDF and as a 300 dpi PNG, drawn by `src/decision_state/figures.py` from the tables above.

| File | Manuscript |
| :-- | :-- |
| `fig1_decision_state_plane` | Figure 1 |
| `fig2_cost_ratio_staircase` | Figure 2 |
| `fig3_loss_difference` | Figure 3 |
| `fig4_configuration_states` | Figure 4 |
| `figS1_path_composition` | Supplementary Figure S1 |

## Other files

| File | Contents |
| :-- | :-- |
| `computed_values.json` | Every recomputed quantity under the name that `data/manuscript_reported_values.json` uses. |
| `manuscript_comparison.csv` | One row per value printed in the manuscript, showing where it is printed, the printed value, the reproduced value and whether they match. |
| `run_environment.json` | The Python and library versions of the run, and the MD5 checksum of each input file. |
