## CICIDS2017 Experiment 1 v2 Notebook Provenance

The notebooks provided in this repository correspond to the original CICIDS2017 Experiment 1 v2 workflow developed prior to an interruption of the Google Colab runtime.

During execution, a Colab disconnection interrupted an ongoing experimental stage before all scheduled runs had completed. To preserve the completed work and avoid unnecessary retraining, a resume-safe continuation notebook was subsequently developed. This notebook was designed to recover the existing experimental state, validate previously completed runs and available checkpoints, and continue only the unfinished work from the latest scientifically valid checkpoint.

Accordingly, the original notebooks are retained here as the primary record of the initially designed CICIDS2017 Experiment 1 v2 workflow, while the resume-safe notebook documents the recovery and continuation procedure used after the runtime interruption.

The continuation procedure did not intentionally redefine the experimental protocol, model-selection criteria, dataset partitions, preprocessing policy, evaluation metrics, or frozen experimental decisions. Its purpose was operational recovery and completion of the interrupted execution while preserving the established Experiment 1 v2 methodology.

**Note on what is included.** The resume-safe continuation notebook described above is not included in this repository. The completed runs of each CICIDS2017 search that enter the manuscript are listed in `data/search_stage/ranked_trials_NB01_cicids.csv` and `data/search_stage/ranked_trials_NB02_cicids.csv`.

