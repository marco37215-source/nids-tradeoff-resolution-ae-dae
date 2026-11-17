"""Paired loss-difference analysis across cost ratios (Sections 3.11 and 4.7).

Added after the primary decision analysis. For each dataset and seed s, the
linear loss difference per unit cost of a missed attack is

    Delta L_s(rho) / C_FN = rho * Delta FP_s - Delta TP_s,     rho = C_FP / C_FN,

so positive values favour the AE and negative values favour the DAE. Unlike two
separate intervals for Delta TP and Delta FP, this quantity keeps the pairing of
the two count differences within each seed.

For a fixed rho I report the mean over the five seeds, its nominal 95% paired t
interval (df = 4) and p-value, and the number of seeds favouring each model. The
interval is pointwise: it holds for one rho at a time and is not a simultaneous
band over the rho-axis.

The cost ratios at which the pointwise interval excludes zero are found exactly,
not by scanning a grid. Writing a = mean Delta FP, b = mean Delta TP,
s_ff, s_tt, s_ft for the sample variances and covariance of the seed-level
differences, n = 5 and q for the 0.975 quantile of t(4), the interval excludes
zero where

    (rho * a - b)^2 > (q^2 / n) * (rho^2 s_ff - 2 rho s_ft + s_tt),

a quadratic inequality in rho, which this module solves in closed form.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
from scipy import stats

from .constants import CONFIDENCE_LEVEL, DATASETS, SEEDS

# Cost ratios printed in Table 10: four decades that span the observed
# seed-level break-even thresholds (about 1.3 to 91). Figure 3 shows every
# rho in between, so the choice of tabulated points selects nothing.
TABLE_RHOS = (0.1, 1.0, 10.0, 100.0)

# Range of the rho-axis shown in Figure 3 (log scale).
FIGURE_RHO_MIN, FIGURE_RHO_MAX, FIGURE_RHO_POINTS = 0.01, 1000.0, 801


def seed_differences(seed_metrics: pd.DataFrame, dataset: str) -> tuple[np.ndarray, np.ndarray]:
    """Return (Delta TP, Delta FP) as arrays ordered by seed."""
    g = seed_metrics[seed_metrics.dataset == dataset].set_index(["model", "seed"])
    d_tp = np.array([g.loc[("DAE", s), "TP"] - g.loc[("AE", s), "TP"] for s in SEEDS], dtype=float)
    d_fp = np.array([g.loc[("DAE", s), "FP"] - g.loc[("AE", s), "FP"] for s in SEEDS], dtype=float)
    return d_tp, d_fp


def _q(n: int) -> float:
    return float(stats.t.ppf(0.5 + CONFIDENCE_LEVEL / 2, df=n - 1))


def loss_summary(d_tp: np.ndarray, d_fp: np.ndarray, rho: float) -> dict:
    """Mean, pointwise 95% t interval, p-value and seed counts of rho * dFP - dTP."""
    loss = rho * d_fp - d_tp
    n = len(loss)
    mean = float(loss.mean())
    sd = float(loss.std(ddof=1))
    half = _q(n) * sd / math.sqrt(n)
    p = float(stats.ttest_1samp(loss, 0.0).pvalue)
    return dict(rho=rho, mean=mean, sd=sd, t_lo=mean - half, t_hi=mean + half, p=p,
                n_favour_AE=int((loss > 0).sum()), n_favour_DAE=int((loss < 0).sum()),
                n_tie=int((loss == 0).sum()))


def resolved_intervals(d_tp: np.ndarray, d_fp: np.ndarray) -> list[dict]:
    """Open intervals of rho > 0 on which the pointwise interval excludes zero, with the favoured model.

    Solves A rho^2 - 2 B rho + Cc > 0, where
    A = a^2 - k s_ff, B = a b - k s_ft, Cc = b^2 - k s_tt, k = q^2 / n.
    """
    n = len(d_tp)
    k = _q(n) ** 2 / n
    a, b = float(d_fp.mean()), float(d_tp.mean())
    cov = np.cov(np.vstack([d_fp, d_tp]), ddof=1)
    s_ff, s_ft, s_tt = float(cov[0, 0]), float(cov[0, 1]), float(cov[1, 1])
    A, B, Cc = a * a - k * s_ff, a * b - k * s_ft, b * b - k * s_tt

    # Boundary points of {rho > 0 : f(rho) > 0}, f(rho) = A rho^2 - 2 B rho + Cc.
    roots: list[float] = []
    if A != 0:
        disc = B * B - A * Cc
        if disc >= 0:
            for r in ((B - math.sqrt(disc)) / A, (B + math.sqrt(disc)) / A):
                if r > 0:
                    roots.append(r)
    elif B != 0:
        r = Cc / (2 * B)
        if r > 0:
            roots.append(r)
    edges = [0.0] + sorted(roots) + [math.inf]

    out = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        mid = (lo + 1.0) if math.isinf(hi) else (hi / 2 if lo == 0 else math.sqrt(lo * hi))
        if A * mid * mid - 2 * B * mid + Cc > 0:
            favoured = "AE" if mid * a - b > 0 else "DAE"
            out.append(dict(rho_lower=lo, rho_upper=hi, favoured=favoured))
    return out


def loss_table(seed_metrics: pd.DataFrame) -> pd.DataFrame:
    """Table 10: paired loss differences at the fixed cost ratios."""
    rows = []
    for ds in DATASETS:
        d_tp, d_fp = seed_differences(seed_metrics, ds)
        for rho in TABLE_RHOS:
            rows.append(dict(dataset=ds, **loss_summary(d_tp, d_fp, rho)))
    return pd.DataFrame(rows)


def resolved_table(seed_metrics: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for ds in DATASETS:
        d_tp, d_fp = seed_differences(seed_metrics, ds)
        for r in resolved_intervals(d_tp, d_fp):
            rows.append(dict(dataset=ds, **r))
    return pd.DataFrame(rows)


def loss_curve(seed_metrics: pd.DataFrame) -> pd.DataFrame:
    """Normalised loss differences on a log-spaced rho grid, for Figure 3.

    The plotted quantity is (rho dFP - dTP) / (1 + rho), the loss difference when
    the two error costs are scaled to sum to one (C_FN + C_FP = 1). Dividing by
    the positive constant 1 + rho changes neither the sign of the mean nor
    whether its pointwise interval excludes zero; it keeps the curve bounded,
    running from -dTP as rho -> 0 to dFP as rho -> infinity.
    """
    grid = np.geomspace(FIGURE_RHO_MIN, FIGURE_RHO_MAX, FIGURE_RHO_POINTS)
    rows = []
    for ds in DATASETS:
        d_tp, d_fp = seed_differences(seed_metrics, ds)
        for rho in grid:
            s = loss_summary(d_tp, d_fp, float(rho))
            w = 1.0 + rho
            row = dict(dataset=ds, rho=float(rho), mean=s["mean"] / w, t_lo=s["t_lo"] / w, t_hi=s["t_hi"] / w)
            for seed, l in zip(SEEDS, (rho * d_fp - d_tp) / w):
                row[f"seed_{seed}"] = float(l)
            rows.append(row)
    return pd.DataFrame(rows)


def collect_values(table: pd.DataFrame, resolved: pd.DataFrame) -> dict:
    v: dict[str, float | int | str] = {}
    for r in table.itertuples(index=False):
        k = "cic" if r.dataset == "CICIDS2017" else "unsw"
        tag = f"{k}.loss.rho{r.rho:g}"
        v[f"{tag}.mean"] = r.mean
        v[f"{tag}.t_lo"] = r.t_lo
        v[f"{tag}.t_hi"] = r.t_hi
        v[f"{tag}.p"] = r.p
        v[f"{tag}.n_favour_DAE"] = r.n_favour_DAE
        v[f"{tag}.n_favour_AE"] = r.n_favour_AE
    for ds in DATASETS:
        k = "cic" if ds == "CICIDS2017" else "unsw"
        g = resolved[resolved.dataset == ds]
        v[f"{k}.loss.n_resolved_intervals"] = len(g)
        for i, r in enumerate(g.itertuples(index=False)):
            v[f"{k}.loss.resolved{i}.favoured"] = r.favoured
            v[f"{k}.loss.resolved{i}.rho_lower"] = r.rho_lower
            if not math.isinf(r.rho_upper):
                v[f"{k}.loss.resolved{i}.rho_upper"] = r.rho_upper
    return v
