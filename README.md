# Is the detection–false-alarm trade-off resolved? Reproducibility code

This repository reproduces every result, table and figure of the manuscript

> J. M. Kamara, D. M. Kaburu and M. W. Kimwele, "Is the Detection–False-Alarm Trade-Off Resolved? Decision States, Training Variability and Break-Even Costs in Autoencoder Intrusion Detection", manuscript under review.

The manuscript is a secondary decision-analytic analysis. It uses the frozen final-test predictions of a selected autoencoder (AE) and a selected denoising autoencoder (DAE) from Experiment 1 v2 of my MSc research, on CICIDS2017 and UNSW-NB15, under five paired seeds (101, 202, 303, 404, 505). It also uses the confusion counts that the Experiment 1 v2 model searches recorded for every configuration they trained.

**The guiding rule of this repository is that it contains nothing that cannot be reproduced from the deposited artefacts.** Every table and figure in `results/` was produced by the code here. The run ends by comparing 378 numbers printed in the manuscript with the numbers it has just recomputed, and it fails if any of them differs.

---

## Contents

1. [Deposited artefacts (Zenodo and GitHub)](#1-deposited-artefacts-zenodo-and-github)
2. [What this repository reproduces](#2-what-this-repository-reproduces)
3. [What it does not reproduce, and why](#3-what-it-does-not-reproduce-and-why)
4. [How to reproduce the results](#4-how-to-reproduce-the-results)
5. [How the analysis works](#5-how-the-analysis-works)
6. [Verification and determinism](#6-verification-and-determinism)
7. [Repository structure](#7-repository-structure)
8. [Relationship to the earlier repository](#8-relationship-to-the-earlier-repository)
9. [Citation, licence and contact](#9-citation-licence-and-contact)

---

## 1. Deposited artefacts (Zenodo and GitHub)

All artefacts of Experiment 1 v2 that are published are listed here. The reproduction needs only the first record and the files in `data/search_stage/`.

| Artefact | Where | Used by this repository |
| :-- | :-- | :-- |
| Observation-level final-test predictions: 20 Parquet files (2 datasets × 2 models × 5 seeds) | Zenodo, doi:[10.5281/zenodo.23559367](https://doi.org/10.5281/zenodo.23559367), CC BY 4.0 | Yes: every final-test result, Tables 4–10 and Figures 1–3 |
| Partition-membership and leakage-control records for CICIDS2017 and UNSW-NB15: 55 Parquet chunks (5,370,790 records) with a SHA-256 manifest | Zenodo, doi:[10.5281/zenodo.24132649](https://doi.org/10.5281/zenodo.24132649) | No (provenance of the partitions described in Sections 3.2 and 3.12) |
| Model-view fingerprint group mappings for CICIDS2017 and UNSW-NB15: 55 Parquet chunks (5,370,790 records) with a SHA-256 manifest | Zenodo, doi:[10.5281/zenodo.24129395](https://doi.org/10.5281/zenodo.24129395) | No (fingerprint groups and leakage control described in Section 3.2) |
| Search-stage ranked-trial files of Notebooks 01 and 02 (4 CSV files) | This repository, `data/search_stage/`, with SHA-256 digests | Yes: Table 11, Figure 4, Section 4.8 |
| Code and artefacts of the companion study (partition validity) | GitHub, [nids-partition-distortion-ae-dae](https://github.com/marco37215-source/nids-partition-distortion-ae-dae) | No |
| Code of the earlier version of this manuscript | GitHub, [nids-decision-state-ae-dae](https://github.com/marco37215-source/nids-decision-state-ae-dae), commit `40ebfc5` | No (see Section 8) |

The raw CICIDS2017 and UNSW-NB15 corpora are not redistributed; see `data/README.md`.

## 2. What this repository reproduces

Table and figure numbers are those of the typeset article. Section numbers are the same in the article and in this README.

| Manuscript item | Output file in `results/` | Code |
| :-- | :-- | :-- |
| Final-test populations and attack prevalence (Sections 3.2, 3.5, 4.4) | `tables/input_integrity_checks.csv` | `inputs.integrity_report` |
| Seed-level confusion counts and metrics (basis of Section 4.1) | `tables/seed_level_metrics.csv` | `metrics.seed_level_metrics` |
| Table 4: five-seed performance and mean counts | `tables/table04_five_seed_performance.csv` | `metrics.table_4_1` |
| Section 4.1: paired differences, d_z, bootstrap and paired *t* intervals | `tables/paired_seed_effects.csv` | `paired_stats.paired_summary` |
| Table 5: seed-level ΔTP, ΔFP, decision states and ρ\* | `tables/table05_seed_decision_states.csv` | `decision.table_4_2` |
| Table 6, Section 4.3 and Supplementary Figure S1: the 3,125 enumerated paths | `tables/table06_path_composition.csv`, `tables/path_composition_by_seed_202.csv`, `figures/figS1_path_composition.{pdf,png}` | `decision.table_4_3`, `figures.figure_s1` |
| Section 4.4: break-even thresholds, ratio of means, fold range | `computed_values.json` | `decision.ratio_of_means` |
| Table 7 and Figure 2: observed-seed decision map over ρ | `tables/table07_decision_map_unsw_nb15.csv`, `figures/fig2_cost_ratio_staircase.{pdf,png}` | `decision.table_4_4`, `figures.figure_2` |
| Section 4.5: exact McNemar tests | `tables/mcnemar_by_seed.csv` | `diagnostics.mcnemar_by_seed` |
| Table 8 and Section 4.6: reconstruction-score diagnostics | `tables/table08_score_diagnostics.csv`, `tables/score_diagnostics_by_run.csv` | `diagnostics` |
| Table 9, Section 4.7 and Figure 1: nominal resolution of the mean count differences, exact sign tests, seed-matched correlations, 25 unmatched seed combinations | `tables/table09_count_resolution.csv`, `tables/cross_seed_states.csv`, `figures/fig1_decision_state_plane.{pdf,png}` | `resolution.count_resolution`, `resolution.cross_seed_states`, `figures.figure_1` |
| Table 10, Section 4.7 and Figure 3: paired loss differences across cost ratios, with the exact cost ratios at which the pointwise interval excludes zero | `tables/table10_loss_differences.csv`, `tables/loss_resolved_cost_ratios.csv`, `tables/fig3_loss_curve_data.csv`, `figures/fig3_loss_difference.{pdf,png}` | `loss`, `figures.figure_3` |
| Table 11, Section 4.8 and Figure 4: the 800 search-stage configuration pairs | `tables/table11_configuration_pairs.csv`, `tables/configuration_pairs.csv`, `figures/fig4_configuration_states.{pdf,png}` | `resolution.configuration_pairs`, `resolution.configuration_summary`, `figures.figure_4` |
| Section 5.2: false-positive changes in percentage points of FPR | `computed_values.json` | `scripts/reproduce_all.py` |
| Section 5.3: prevalence-rescaling illustration at π = 0.01 | `tables/prevalence_rescaling_illustration_unsw_nb15.csv` | `decision.prevalence_rescaled` |
| Every number above, checked against the manuscript | `manuscript_comparison.csv` | `check.compare_with_manuscript` |

The same quantities appear again in the Abstract and in Sections 5 and 6, and are covered by the same check.

## 3. What it does not reproduce, and why

I left out every part of the manuscript that rests on artefacts that are not deposited. I did not copy those numbers into this repository, because you could not reproduce them from it. They are:

- **Model training, search, selection and evaluation.** This covers Notebooks 01–07 of Experiment 1 v2, which ran on Google Colab with an NVIDIA A100 GPU, and the settings in Table 2 that came out of them. Trained weights and training data are not part of the deposits. The confusion counts that the searches recorded are included (`data/search_stage/`), but the runs that produced them cannot be re-executed from this repository.
- **Training-horizon records** used in Section 5.8.4: the best epochs and search-level epoch counts.
- **Development-partition results** used in Sections 5.8.1 and 5.8.6: the confirmation-seed decision states and the Notebook 05 threshold-sensitivity states.
- **Partition construction and leakage control.** These are reported in the companion manuscript and its own repository. The partition-membership records and the fingerprint group mappings are on Zenodo (Section 1) and allow the partitions to be audited independently, but this repository does not recompute them.
- **The computational environment of the training runs** (Section 3.12).

The decision analysis does not depend on any of these. It starts from the frozen predictions and the recorded search-stage counts, and every quantity it reports is reproduced here.

## 4. How to reproduce the results

### Option A: Google Colab (no installation)

1. Open `notebooks/reproduce_manuscript_colab.ipynb` in Google Colab.
2. Run all cells. The notebook clones this repository, downloads the Zenodo record, runs the full reproduction and shows the tables, the figures and the manuscript check.

A CPU runtime is sufficient.

### Option B: your own computer

You need Python 3.11 or later; I tested the code with Python 3.13. You also need about 3 GB of free memory and 0.4 GB of disk space for the data.

```bash
git clone https://github.com/marco37215-source/nids-tradeoff-resolution-ae-dae.git && cd nids-tradeoff-resolution-ae-dae
python -m venv .venv && source .venv/bin/activate      # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Download the 20 Parquet files from the Zenodo record into `data/raw/`. Either download them by hand from the record page, or run:

```bash
pip install zenodo_get
zenodo_get 10.5281/zenodo.23559367 -o data/raw
```

Then run the reproduction:

```bash
python scripts/reproduce_all.py --data-dir data/raw
```

The run takes under a minute on a two-core machine and should end with:

```
378 of 378 manuscript values reproduced.
All values printed in the manuscript were reproduced from the deposited artefacts.
```

The outputs are written to `results/`, overwriting the copies stored in the repository. To keep the stored copies, pass another folder with `--out-dir`.

## 5. How the analysis works

I describe each step in the order in which `scripts/reproduce_all.py` runs it. Section numbers refer to the manuscript.

**Authentication of the inputs.** I match every Parquet file to `data/input_manifest.csv` by its MD5 checksum, and confirm the match with SHA-256. I then check, inside each file, that the model, seed, configuration hash and run hash are the expected ones and that the file carries a single threshold. The run stops if any of the 20 files is missing or does not match. The four search-stage files are checked against the SHA-256 digests in `data/search_stage/search_stage_manifest.csv`.

**The paired design.** Within each dataset, I check that all ten runs contain the same final-test observations with the same labels, and that the stored prediction equals the frozen rule ŷ = 1 if e > T₉₉, and 0 otherwise, on every observation (Equation 3).

**Seed-level metrics (Section 3.4).** I recompute TP, FP, FN and TN from the stored labels and predictions, and from them MCC, recall, precision, F1, FPR, false positives per 1,000 benign observations and balanced accuracy. PR-AUC is the trapezoidal area under the precision–recall curve, `sklearn.metrics.auc(recall, precision)`, as in Experiment 1; it is not average precision.

**Paired statistics (Section 3.11).** The inferential unit is the paired final seed, so n = 5. For each metric I compute the five differences DAE − AE, their mean, d_z, the direction consistency, a percentile bootstrap interval (10,000 resamples from one `numpy.random.default_rng(2026)` stream per dataset, shared by the metrics in a fixed order, as in Notebook 08) and the paired *t* interval and *p*-value.

**Decision states, break-even thresholds, path enumeration and decision map (Sections 3.6–3.9).** Each seed's (ΔTP, ΔFP) is classified into States I–IV with boundaries at exactly zero. For State II seeds only, ρ\* = ΔTP/ΔFP, kept as an exact fraction. All 5⁵ = 3,125 ordered five-seed paths are enumerated and classified; they are deterministic recombinations, not experiments. The finite thresholds divide the ρ-axis into open intervals, and each seed's preference is evaluated at an interior point of each.

**McNemar tests and score diagnostics (Sections 3.10, 3.11).** Exact two-sided binomial tests on the discordant observations of each seed (these speak only to ρ = 1), and, per run, the median of e / T₉₉ over missed attacks and the share of attacks below the benign median error.

**Resolution of the count differences (Sections 3.11 and 4.7).** Added after the primary decision analysis; exploratory. For TP and FP separately: each model's seed-to-seed mean and standard deviation, the correlation of the two models' counts across matched seeds, the post hoc, nominal 95% paired *t* interval and *p*-value of the mean difference, and the exact two-sided sign test (whose smallest attainable value with five seeds is 0.0625). A mean difference is called *nominally resolved* when its *t* interval excludes zero. This concerns the mean across training realisations, not the exactly known states of the observed seeds. I also classify all 25 combinations AE_i versus DAE_j, ignoring the seed pairing.

**Paired loss differences (Sections 3.11 and 4.7).** For each seed, ΔL_s(ρ)/C_FN = ρ ΔFP_s − ΔTP_s (positive favours the AE). At ρ = 0.1, 1, 10 and 100 I report the mean, its pointwise nominal 95% paired *t* interval, the *p*-value and the seeds favouring each model. The cost ratios at which the pointwise interval excludes zero are found exactly by solving a quadratic inequality in ρ (`loss.resolved_intervals`), not by scanning a grid. Figure 3 plots the mean and interval of (ρ ΔFP − ΔTP)/(1 + ρ) over 801 log-spaced values of ρ from 0.01 to 1,000; dividing by 1 + ρ changes neither the sign nor whether the interval excludes zero.

**Configuration pairs (Sections 3.3 and 4.8).** I read the four ranked-trial files, check that each holds 20 distinct configurations trained under seed 101 and that all 40 runs of a dataset were scored on one development population, pair every AE configuration with every DAE configuration (400 pairs per dataset), classify each pair, and tabulate the states against the sign of ΔMCC. For the resumed UNSW-NB15 DAE search, the file holds the canonical run of each configuration; `canonical_complete_run_selection_NB02_unsw.json` records the rule, which does not use performance.

**Figures.** Every figure is drawn by `src/decision_state/figures.py` from the reproduced tables only. Colour encodes the sign of ΔTP and fill the type of state (solid: dominance; hollow or hatched: trade-off), so states are never distinguished by colour alone.

## 6. Verification and determinism

**Check against the manuscript.** `data/manuscript_reported_values.json` lists 378 values exactly as the manuscript prints them, with their location and printed precision. A value matches when the recomputed number, rounded to the printed precision, equals the printed number; where the manuscript states a bound (for example *p* < 10⁻⁴¹), the bound is checked instead. The comparison is written to `results/manuscript_comparison.csv`.

**Determinism.** The only random step is the bootstrap, which uses a fixed seed. With the pinned versions in `requirements.txt`, two consecutive runs produced byte-identical tables, figures and comparison files. `run_environment.json` records the versions and input checksums of each run.

I also ran the code with newer libraries: NumPy 2.5.3, pandas 3.0.5, SciPy 1.18.1, scikit-learn 1.9.1, PyArrow 26.0.0 and Matplotlib 3.11.2. The recomputed values then differed from the stored outputs by at most 1.4 × 10⁻¹³ in relative terms, and all 378 manuscript values were still reproduced.

## 7. Repository structure

```
.
├── README.md
├── LICENSE
├── CITATION.cff
├── requirements.txt
├── data/
│   ├── input_manifest.csv               # checksums of the 20 deposited Parquet files
│   ├── manuscript_reported_values.json  # values printed in the manuscript, for the final check
│   ├── search_stage/                    # ranked-trial files of Notebooks 01-02 and their SHA-256 manifest
│   └── raw/                             # place the downloaded Parquet files here (not tracked)
├── external_artifacts/                  # description of the Zenodo prediction archive
├── notebooks/
│   ├── reproduce_manuscript_colab.ipynb # one-click reproduction in Google Colab
│   ├── cicids2017/                      # Experiment 1 v2 notebooks of record (CICIDS2017)
│   └── unsw_nb15/                       # Experiment 1 v2 notebooks of record (UNSW-NB15)
├── scripts/
│   └── reproduce_all.py                 # runs the whole analysis and the check
├── src/decision_state/
│   ├── constants.py                     # seeds, configuration hashes, bootstrap settings
│   ├── inputs.py                        # authentication, loading and integrity checks
│   ├── metrics.py                       # counts, metrics, Table 4
│   ├── paired_stats.py                  # paired differences, bootstrap, t intervals
│   ├── decision.py                      # states, thresholds, enumeration, decision map
│   ├── diagnostics.py                   # McNemar tests, score diagnostics
│   ├── resolution.py                    # resolution check, unmatched seed combinations, configuration pairs
│   ├── loss.py                          # paired loss differences across cost ratios
│   ├── figures.py                       # Figures 1-4 and Supplementary Figure S1
│   └── check.py                         # comparison with the manuscript
└── results/                             # outputs of the reference run
    ├── tables/  figures/
    ├── computed_values.json  manuscript_comparison.csv  run_environment.json
```

`results/README.md` describes every output file.

## 8. Relationship to the earlier repository

An earlier version of this manuscript, titled "When Model Choice Changes with the Seed: Decision-State Uncertainty and Break-Even Costs in Autoencoder Intrusion Detection", was reproduced by [nids-decision-state-ae-dae](https://github.com/marco37215-source/nids-decision-state-ae-dae) at commit `40ebfc5d706de72100f2f690ba839575d22c3028`. That repository is kept unchanged as the record of that version. This repository starts from the same code and adds:

- the resolution check, the exact sign tests and the 25 unmatched seed combinations;
- the paired loss-difference analysis, which replaces the earlier corner bound built from two marginal intervals;
- the search-stage configuration-pair analysis and its four input files;
- Figures 1, 3 and 4 in their new form, and the path-composition figure moved to the supplementary material;
- table, figure and output-file numbering that follows the typeset article.

All 243 values registered for the earlier version are still checked here; their locations now use the typeset numbering.

## 9. Citation, licence and contact

If you use this code, please cite the manuscript and the data deposits:

> J. M. Kamara, M. Kimwele and D. M. Kaburu, "Observation-level final-test predictions of autoencoder and denoising-autoencoder intrusion detectors on CICIDS2017 and UNSW-NB15 (Experiment 1 v2, known attacks)", Zenodo, 2026, doi:10.5281/zenodo.23559367.

> J. M. Kamara, D. M. Kaburu and M. W. Kimwele, "Experiment 1 v2: Partition Membership and Leakage-Control Records for CICIDS2017 and UNSW-NB15 — Known/Documented Network-Attack Detection Using Autoencoders", Zenodo, 2026, doi:10.5281/zenodo.24132649.

> J. M. Kamara, M. W. Kimwele and D. M. Kaburu, "Experiment 1 v2: Model-View Fingerprint Group Mappings for CICIDS2017 and UNSW-NB15 — Known/Documented Network-Attack Detection with Autoencoders", Zenodo, 2026, doi:10.5281/zenodo.24129395.

`CITATION.cff` gives the citation in machine-readable form.

The code is released under the licence in `LICENSE`. The data remain under their own Creative Commons Attribution 4.0 International licence on Zenodo.

The datasets behind the predictions are CICIDS2017 (Canadian Institute for Cybersecurity) and UNSW-NB15 (UNSW Canberra). Please cite and respect their original terms of use if you work with the underlying traffic records.

**Contact:** Joseph Marco Kamara, Department of Mathematical Sciences, Pan African University Institute for Basic Sciences, Technology and Innovation (PAUSTI), Nairobi, Kenya, marco37215@gmail.com, ORCID [0009-0009-2455-1222](https://orcid.org/0009-0009-2455-1222).
