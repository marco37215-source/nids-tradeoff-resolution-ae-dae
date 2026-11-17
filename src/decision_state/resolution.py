"""Resolution of the count differences and the configuration-pair analysis (Sections 3.3, 3.11, 4.7 and 4.8).

These analyses were added after the primary decision analysis of Sections 3.5-3.9,
in response to editorial review. They use the same frozen final-test predictions
as every other module, plus the four search-stage ranked-trial files of Notebooks
01 and 02 (data/search_stage/). No model was trained, retrained or re-selected.

Two questions are answered:

1. Is each mean paired count difference (Delta TP, Delta FP) distinguishable
   from zero given the variation between training seeds? I call a mean
   difference *nominally resolved* when its post hoc, nominal two-sided 95%
   paired t interval over the five seeds excludes zero. The target is the mean
   difference across training realisations; the decision state of each observed
   seed is known exactly and is not in question. I also report the exact
   two-sided sign test, whose smallest attainable p-value with five seeds is
   0.0625.
2. Across all AE-DAE configuration pairs evaluated during the searches (20 x 20
   per dataset, development partition, search seed 101), how are the decision
   states distributed, and does a higher MCC imply dominance?
"""

from __future__ import annotations

import hashlib
from fractions import Fraction
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from .constants import CONFIDENCE_LEVEL, DATASETS, SEEDS
from .decision import classify_state

# Search-stage ranked-trial files (Notebook 01 = AE search, Notebook 02 = DAE search),
# each with 20 uniquely completed configurations trained under search seed 101 and
# scored on the development partition. Their SHA-256 digests are listed in
# data/search_stage/search_stage_manifest.csv and checked before use.
DEFAULT_SEARCH_DIR = Path(__file__).resolve().parents[2] / "data" / "search_stage"
SEARCH_MANIFEST = "search_stage_manifest.csv"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# --------------------------------------------------------------------------------------
# 1. Resolution of the final-test count differences
# --------------------------------------------------------------------------------------

def _t_interval(x: np.ndarray) -> tuple[float, float, float, float]:
    """Mean, two-sided 95% t interval and p-value for the mean of x (df = n - 1)."""
    n = len(x)
    mean = float(np.mean(x))
    se = float(np.std(x, ddof=1)) / np.sqrt(n)
    q = stats.t.ppf(0.5 + CONFIDENCE_LEVEL / 2, df=n - 1)
    p = float(stats.ttest_1samp(x, 0.0).pvalue)
    return mean, mean - q * se, mean + q * se, p


def count_resolution(seed_metrics: pd.DataFrame) -> pd.DataFrame:
    """Per dataset and count (TP, FP): seed variability of each model and resolution of the paired difference."""
    rows = []
    for ds in DATASETS:
        g = seed_metrics[seed_metrics.dataset == ds].set_index(["model", "seed"])
        n_benign = int(g.loc[("AE", SEEDS[0]), "FP"] + g.loc[("AE", SEEDS[0]), "TN"])
        for count in ("TP", "FP"):
            ae = np.array([g.loc[("AE", s), count] for s in SEEDS], dtype=float)
            dae = np.array([g.loc[("DAE", s), count] for s in SEEDS], dtype=float)
            diff = dae - ae
            mean, lo, hi, p = _t_interval(diff)
            nz = diff[diff != 0]
            sign_p = float(stats.binomtest(int((nz > 0).sum()), len(nz), 0.5).pvalue) if len(nz) else 1.0
            rows.append(dict(
                dataset=ds, count=count,
                AE_mean=ae.mean(), AE_sd=ae.std(ddof=1), AE_min=ae.min(), AE_max=ae.max(),
                DAE_mean=dae.mean(), DAE_sd=dae.std(ddof=1), DAE_min=dae.min(), DAE_max=dae.max(),
                seed_matched_correlation=float(np.corrcoef(ae, dae)[0, 1]),
                diff_mean=mean, diff_sd=diff.std(ddof=1), diff_t_lo=lo, diff_t_hi=hi, diff_t_p=p,
                n_DAE_higher=int((diff > 0).sum()), sign_test_p=sign_p,
                resolved=bool(lo > 0 or hi < 0),
                nominal_FP_at_1pct=0.01 * n_benign if count == "FP" else np.nan,
                n_benign=n_benign,
            ))
    return pd.DataFrame(rows)


def identified_state(res: pd.DataFrame, dataset: str) -> str:
    """Decision state(s) of the mean differences compatible with the two marginal nominal 95% t intervals.

    One state if both mean differences are nominally resolved; otherwise the set of
    states that the interval end points admit. This concerns the mean differences
    across training realisations, not the exactly known states of the observed seeds.
    """
    r = res[res.dataset == dataset].set_index("count")
    states = set()
    for tp in (r.loc["TP", "diff_t_lo"], r.loc["TP", "diff_t_hi"]):
        for fp in (r.loc["FP", "diff_t_lo"], r.loc["FP", "diff_t_hi"]):
            states.add(classify_state(int(np.sign(tp)), int(np.sign(fp))))
    return " or ".join(sorted(states))


def cross_seed_states(seed_metrics: pd.DataFrame) -> pd.DataFrame:
    """States of all 25 combinations AE_i versus DAE_j, ignoring the seed pairing."""
    rows = []
    for ds in DATASETS:
        g = seed_metrics[seed_metrics.dataset == ds].set_index(["model", "seed"])
        for si in SEEDS:
            for sj in SEEDS:
                d_tp = int(g.loc[("DAE", sj), "TP"] - g.loc[("AE", si), "TP"])
                d_fp = int(g.loc[("DAE", sj), "FP"] - g.loc[("AE", si), "FP"])
                rows.append(dict(dataset=ds, AE_seed=si, DAE_seed=sj, matched=si == sj,
                                 dTP=d_tp, dFP=d_fp, state=classify_state(d_tp, d_fp)))
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------------------
# 2. Configuration pairs from the searches (development partition, seed 101)
# --------------------------------------------------------------------------------------

def load_search_stage(search_dir: Path = DEFAULT_SEARCH_DIR) -> pd.DataFrame:
    """Load and authenticate the four ranked-trial files; check the common development population."""
    search_dir = Path(search_dir)
    man = pd.read_csv(search_dir / SEARCH_MANIFEST)
    frames = []
    for r in man.itertuples(index=False):
        path = search_dir / r.file
        digest = _sha256(path)
        if digest != r.sha256:
            raise ValueError(f"{r.file}: SHA-256 {digest} does not match the manifest")
        df = pd.read_csv(path)
        if len(df) != 20 or set(df.seed) != {101} or set(df.model_type) != {r.model}:
            raise ValueError(f"{r.file}: expected 20 {r.model} trials under seed 101")
        if df.config_hash.duplicated().any():
            raise ValueError(f"{r.file}: duplicate configurations")
        df.insert(0, "dataset", r.dataset)
        frames.append(df)
    out = pd.concat(frames, ignore_index=True)
    for ds, g in out.groupby("dataset"):
        if (g.TP + g.FN).nunique() != 1 or (g.FP + g.TN).nunique() != 1:
            raise ValueError(f"{ds}: trials were not scored on one common development population")
    return out


def configuration_pairs(search: pd.DataFrame) -> pd.DataFrame:
    """Every AE configuration paired with every DAE configuration of the same dataset (400 per dataset)."""
    rows = []
    for ds in DATASETS:
        g = search[search.dataset == ds]
        ae, dae = g[g.model_type == "AE"], g[g.model_type == "DAE"]
        for a in ae.itertuples(index=False):
            for d in dae.itertuples(index=False):
                d_tp, d_fp = int(d.TP - a.TP), int(d.FP - a.FP)
                rows.append(dict(dataset=ds, AE_rank=a.rank, DAE_rank=d.rank,
                                 dTP=d_tp, dFP=d_fp, dMCC=d.MCC - a.MCC,
                                 state=classify_state(d_tp, d_fp)))
    return pd.DataFrame(rows)


def configuration_summary(search: pd.DataFrame, pairs: pd.DataFrame) -> pd.DataFrame:
    """Table 11: state distribution of the configuration pairs and its relation to the sign of Delta MCC."""
    rows = []
    for ds in DATASETS:
        p = pairs[pairs.dataset == ds]
        g = search[search.dataset == ds]
        n_benign = int((g.FP + g.TN).iloc[0])
        pos = p[p.dMCC > 0]
        row = dict(dataset=ds, n_pairs=len(p), n_benign_dev=n_benign, n_attack_dev=int((g.TP + g.FN).iloc[0]),
                   FP_min=int(g.FP.min()), FP_max=int(g.FP.max()),
                   FPR_min_pct=100 * g.FP.min() / n_benign, FPR_max_pct=100 * g.FP.max() / n_benign,
                   median_abs_dTP=float(p.dTP.abs().median()), median_abs_dFP=float(p.dFP.abs().median()),
                   n_dMCC_pos=len(pos), sign_dMCC_equals_sign_dTP=int((np.sign(p.dMCC) == np.sign(p.dTP)).sum()))
        for st in ("I", "II", "III", "IV"):
            row[f"n_{st}"] = int((p.state == st).sum())
            row[f"n_{st}_given_dMCC_pos"] = int((pos.state == st).sum())
        def _mixed(states) -> bool:
            s = set(states)
            return bool(s & {"I", "III"}) and bool(s & {"II", "IV"})
        row["n_AE_configs_in_dominance_and_tradeoff"] = int(p.groupby("AE_rank").state.agg(_mixed).sum())
        row["n_DAE_configs_in_dominance_and_tradeoff"] = int(p.groupby("DAE_rank").state.agg(_mixed).sum())
        row["pct_II_given_dMCC_pos"] = 100 * row["n_II_given_dMCC_pos"] / len(pos)
        row["pct_I_given_dMCC_pos"] = 100 * row["n_I_given_dMCC_pos"] / len(pos)
        rows.append(row)
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------------------
# Named values for data/manuscript_reported_values.json
# --------------------------------------------------------------------------------------

def collect_values(res: pd.DataFrame, cross: pd.DataFrame, conf: pd.DataFrame) -> dict:
    v: dict[str, float | int | str] = {}
    for ds in DATASETS:
        k = "cic" if ds == "CICIDS2017" else "unsw"
        for r in res[res.dataset == ds].itertuples(index=False):
            c = r.count
            for m in ("AE", "DAE"):
                v[f"{k}.res.{c}.{m.lower()}_sd"] = float(getattr(r, f"{m}_sd"))
                v[f"{k}.res.{c}.{m.lower()}_min"] = float(getattr(r, f"{m}_min"))
                v[f"{k}.res.{c}.{m.lower()}_max"] = float(getattr(r, f"{m}_max"))
            v[f"{k}.res.{c}.corr"] = r.seed_matched_correlation
            v[f"{k}.res.{c}.diff_sd"] = r.diff_sd
            v[f"{k}.res.{c}.t_lo"] = r.diff_t_lo
            v[f"{k}.res.{c}.t_hi"] = r.diff_t_hi
            v[f"{k}.res.{c}.t_p"] = r.diff_t_p
            v[f"{k}.res.{c}.resolved"] = "yes" if r.resolved else "no"
            v[f"{k}.res.{c}.sign_test_p"] = r.sign_test_p
            if c == "FP":
                v[f"{k}.res.FP.nominal_1pct"] = r.nominal_FP_at_1pct
        v[f"{k}.res.identified_state"] = identified_state(res, ds)
        cs = cross[cross.dataset == ds]
        for st in ("I", "II", "III", "IV"):
            v[f"{k}.cross25.n_{st}"] = int((cs.state == st).sum())
        row = conf[conf.dataset == ds].iloc[0]
        for col in ("n_pairs", "n_benign_dev", "n_attack_dev", "FP_min", "FP_max", "FPR_min_pct", "FPR_max_pct",
                    "median_abs_dTP", "median_abs_dFP", "n_dMCC_pos", "sign_dMCC_equals_sign_dTP",
                    "n_I", "n_II", "n_III", "n_IV", "n_I_given_dMCC_pos", "n_II_given_dMCC_pos",
                    "n_III_given_dMCC_pos", "n_IV_given_dMCC_pos", "pct_II_given_dMCC_pos", "pct_I_given_dMCC_pos",
                    "n_AE_configs_in_dominance_and_tradeoff", "n_DAE_configs_in_dominance_and_tradeoff"):
            val = row[col]
            v[f"{k}.conf.{col}"] = float(val) if isinstance(val, (float, np.floating)) else int(val)
    return v
