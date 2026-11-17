"""Figures of the manuscript, drawn only from the reproduced tables.

Main text:
    Figure 1  fig1_decision_state_plane      seed-level states and marginal intervals of the mean differences
    Figure 2  fig2_cost_ratio_staircase      observed UNSW-NB15 seeds favouring the DAE across rho
    Figure 3  fig3_loss_difference           mean paired loss difference across rho with pointwise intervals
    Figure 4  fig4_configuration_states      states of the 20 x 20 search-stage configuration pairs
Supplementary material:
    Figure S1 figS1_path_composition         states of the 3,125 enumerated seed paths

Every plotted value is a recomputed count, an exact ratio of counts, or a
quantity computed from those counts by the modules of this package. Each figure
is saved as a vector PDF (for the manuscript) and as a 300 dpi PNG.

Colour encodes the sign of Delta TP (blue: the DAE detects more attacks; orange:
the AE detects more); fill encodes the type of state (solid: dominance; hollow
or hatched: trade-off). The decision state is therefore never carried by colour
alone, and the two hues pass the colour-vision-deficiency checks of the
categorical palette used.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch, Rectangle  # noqa: E402

from .constants import CONFIG_HASHES, DATASETS, SEEDS  # noqa: E402

BLUE, ORANGE, INK, MUTED, GRID = "#2a78d6", "#eb6834", "#222222", "#888888", "#e6e6e6"
TINT = {BLUE: "#d4e4f7", ORANGE: "#fbe1d6"}
STATE_HUE = {"I": BLUE, "II": BLUE, "III": ORANGE, "IV": ORANGE}
STATE_SOLID = {"I": True, "II": False, "III": True, "IV": False}
STATE_LABEL = {"I": "State I: DAE dominance", "II": "State II: genuine trade-off",
               "III": "State III: AE dominance", "IV": "State IV: inverse trade-off"}

plt.rcParams.update({
    "font.family": "serif", "font.size": 8, "pdf.fonttype": 42, "hatch.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 0.6,
    "axes.edgecolor": "#555555", "xtick.color": "#333333", "ytick.color": "#333333",
})


def _save(fig, out_dir: Path, stem: str) -> None:
    fig.savefig(out_dir / f"{stem}.pdf", metadata={"CreationDate": None, "ModDate": None}, bbox_inches="tight")
    fig.savefig(out_dir / f"{stem}.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def _state_marker(ax, x, y, state, size=34, z=3):
    hue = STATE_HUE[state]
    face = hue if STATE_SOLID[state] else "white"
    ax.scatter(x, y, s=size, facecolor=face, edgecolor=hue, linewidth=1.3, zorder=z)


# --------------------------------------------------------------------------------------
# Figure 1: decision-state plane with the marginal intervals of the mean differences
# --------------------------------------------------------------------------------------

# Seed-label offsets (points) that keep labels clear of the interval whiskers; cosmetic only.
LABEL_OFFSET = {("CICIDS2017", 303): (-5, -11), ("CICIDS2017", 505): (5, -11), ("UNSW-NB15", 505): (-5, -11)}


def figure_1(t42: pd.DataFrame, res: pd.DataFrame, out_dir: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.0))
    for ax, dataset in zip(axes, DATASETS):
        g = t42[t42.dataset == dataset]
        r = res[res.dataset == dataset].set_index("count")
        tp, fp = r.loc["TP"], r.loc["FP"]
        xr = 1.22 * max(g.dFP.abs().max(), abs(fp.diff_t_lo), abs(fp.diff_t_hi))
        yr = 1.45 * max(g.dTP.abs().max(), abs(tp.diff_t_lo), abs(tp.diff_t_hi))
        ax.set_xlim(-xr, xr)
        ax.set_ylim(-yr, yr)
        ax.axhline(0, color=MUTED, lw=0.6, zorder=1)
        ax.axvline(0, color=MUTED, lw=0.6, zorder=1)
        style = dict(color=MUTED, fontsize=6.5, style="italic")
        ax.text(-xr * 0.96, yr * 0.95, "I  DAE dominance", ha="left", va="top", **style)
        ax.text(xr * 0.96, yr * 0.95, "II  trade-off", ha="right", va="top", **style)
        ax.text(xr * 0.96, -yr * 0.95, "III  AE dominance", ha="right", va="bottom", **style)
        ax.text(-xr * 0.96, -yr * 0.95, "IV  inverse trade-off", ha="left", va="bottom", **style)
        # Mean differences with separate marginal nominal 95% t intervals.
        ax.errorbar(fp.diff_mean, tp.diff_mean,
                    xerr=[[fp.diff_mean - fp.diff_t_lo], [fp.diff_t_hi - fp.diff_mean]],
                    yerr=[[tp.diff_mean - tp.diff_t_lo], [tp.diff_t_hi - tp.diff_mean]],
                    fmt="x", color=INK, ms=6, mew=1.4, elinewidth=1.0, capsize=3, zorder=4)
        for s in g.itertuples(index=False):
            _state_marker(ax, s.dFP, s.dTP, s.state)
            dx, dy = LABEL_OFFSET.get((dataset, s.seed), (4, 3))
            ax.annotate(str(s.seed), (s.dFP, s.dTP), xytext=(dx, dy), textcoords="offset points",
                        fontsize=6.5, color=INK, ha="left" if dx >= 0 else "right")
        ax.set_xlabel(r"$\Delta$FP (DAE $-$ AE)")
        ax.set_ylabel(r"$\Delta$TP (DAE $-$ AE)")
        ax.set_title(dataset, fontsize=8.5, color=INK, loc="left")
        ax.grid(color=GRID, lw=0.4)
        ax.set_axisbelow(True)
    handles = [
        Line2D([], [], ls="", marker="o", mfc=BLUE, mec=BLUE, mew=1.3, label="Seed in State I"),
        Line2D([], [], ls="", marker="o", mfc="white", mec=BLUE, mew=1.3, label="Seed in State II"),
        Line2D([], [], ls="", marker="o", mfc=ORANGE, mec=ORANGE, mew=1.3, label="Seed in State III"),
        Line2D([], [], ls="-", marker="x", color=INK, mew=1.4, lw=1.0,
               label="Mean difference, marginal nominal 95% t intervals (n = 5)"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=4, frameon=False, fontsize=6.8,
               bbox_to_anchor=(0.5, -0.05), handletextpad=0.4, columnspacing=1.2)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    _save(fig, out_dir, "fig1_decision_state_plane")


# --------------------------------------------------------------------------------------
# Figure 2: observed-seed decision map (unchanged in content from the first version)
# --------------------------------------------------------------------------------------

def figure_2(t44: pd.DataFrame, rho_mean: float, out_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(3.5, 2.2))
    x_min, x_max = 0.1, 1000.0
    rows = list(t44.itertuples(index=False))
    for i, r in enumerate(rows):
        lo = max(r.rho_lower, x_min)
        hi = min(r.rho_upper, x_max)
        ax.hlines(r.DAE_preference_count, lo, hi, color=BLUE, lw=2)
        if i + 1 < len(rows):
            nxt = rows[i + 1]
            ax.vlines(r.rho_upper, nxt.DAE_preference_count, r.DAE_preference_count, color=BLUE, lw=0.8, linestyle=":")
            ax.annotate(f"{r.rho_upper:.3f}", (r.rho_upper, nxt.DAE_preference_count), xytext=(3, -4),
                        textcoords="offset points", fontsize=6.5, color=INK, va="top")
    ax.vlines(rho_mean, 0.6, 5.4, color=INK, lw=0.8, linestyle="--")
    ax.text(rho_mean * 1.1, 5.25, f"ratio of means {rho_mean:.3f}", fontsize=6.5, color=INK, va="center")
    ax.set_xscale("log")
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(0.3, 5.5)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_xlabel(r"Cost ratio $\rho = C_{\mathrm{FP}}/C_{\mathrm{FN}}$ (log scale)")
    ax.set_ylabel("Observed seeds favouring DAE")
    ax.grid(axis="y", color=GRID, lw=0.4)
    ax.set_axisbelow(True)
    fig.tight_layout()
    _save(fig, out_dir, "fig2_cost_ratio_staircase")


# --------------------------------------------------------------------------------------
# Figure 3: mean paired loss difference across rho with pointwise intervals
# --------------------------------------------------------------------------------------

def figure_3(curve: pd.DataFrame, resolved: pd.DataFrame, out_dir: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.9))
    for ax, dataset in zip(axes, DATASETS):
        c = curve[curve.dataset == dataset].sort_values("rho")
        for seed in SEEDS:
            ax.plot(c.rho, c[f"seed_{seed}"], color="#b8b8b8", lw=0.6, zorder=2)
        ax.fill_between(c.rho, c.t_lo, c.t_hi, color=BLUE, alpha=0.18, lw=0, zorder=1)
        ax.plot(c.rho, c["mean"], color=BLUE, lw=1.6, zorder=3)
        ax.axhline(0, color=INK, lw=0.7, zorder=2)
        for r in resolved[resolved.dataset == dataset].itertuples(index=False):
            if np.isfinite(r.rho_upper):
                ax.axvline(r.rho_upper, color=INK, lw=0.7, ls=":", zorder=2)
                ax.annotate(rf"$\rho$ = {r.rho_upper:.3f}", (r.rho_upper, 0), xytext=(4, 6),
                            textcoords="offset points", fontsize=6.5, color=INK)
        ax.set_xscale("log")
        ax.set_xlim(c.rho.min(), c.rho.max())
        lo, hi = c.t_lo.min(), c.t_hi.max()
        pad = 0.08 * (hi - lo)
        ax.set_ylim(lo - pad, hi + pad)
        ax.text(0.015, 0.97, "favours AE", transform=ax.transAxes, fontsize=6.5, color=MUTED, style="italic", va="top")
        ax.text(0.015, 0.03, "favours DAE", transform=ax.transAxes, fontsize=6.5, color=MUTED, style="italic", va="bottom")
        ax.set_xlabel(r"Cost ratio $\rho = C_{\mathrm{FP}}/C_{\mathrm{FN}}$ (log scale)")
        ax.set_ylabel(r"$(\rho\,\Delta\mathrm{FP} - \Delta\mathrm{TP})\,/\,(1+\rho)$")
        ax.set_title(dataset, fontsize=8.5, color=INK, loc="left")
        ax.grid(color=GRID, lw=0.4)
        ax.set_axisbelow(True)
    handles = [
        Line2D([], [], color=BLUE, lw=1.6, label="Five-seed mean"),
        Patch(facecolor=BLUE, alpha=0.18, label="Pointwise nominal 95% t interval (not simultaneous)"),
        Line2D([], [], color="#b8b8b8", lw=0.6, label="Individual seeds"),
        Line2D([], [], color=INK, lw=0.7, ls=":", label="Interval stops excluding zero"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=4, frameon=False, fontsize=6.8,
               bbox_to_anchor=(0.5, -0.05), handletextpad=0.4, columnspacing=1.2)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    _save(fig, out_dir, "fig3_loss_difference")


# --------------------------------------------------------------------------------------
# Figure 4: decision states of the 20 x 20 search-stage configuration pairs
# --------------------------------------------------------------------------------------

def _selected_rank(search: pd.DataFrame, dataset: str, model: str) -> int:
    g = search[(search.dataset == dataset) & (search.model_type == model)]
    hit = g[g.config_hash == CONFIG_HASHES[(dataset, model)]]
    if len(hit) != 1:
        raise ValueError(f"selected {model} configuration of {dataset} not found exactly once in the search files")
    return int(hit["rank"].iloc[0])


def figure_4(pairs: pd.DataFrame, search: pd.DataFrame, out_dir: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.75))
    for ax, dataset in zip(axes, DATASETS):
        p = pairs[pairs.dataset == dataset]
        n_ae, n_dae = int(p.AE_rank.max()), int(p.DAE_rank.max())
        for r in p.itertuples(index=False):
            x, y = r.DAE_rank - 1, r.AE_rank - 1
            hue = STATE_HUE[r.state]
            if STATE_SOLID[r.state]:
                ax.add_patch(Rectangle((x, y), 1, 1, facecolor=hue, edgecolor="white", lw=0.6))
            else:
                ax.add_patch(Rectangle((x, y), 1, 1, facecolor=TINT[hue], edgecolor="white", lw=0.6))
                ax.add_patch(Rectangle((x + 0.06, y + 0.06), 0.88, 0.88, facecolor="none", edgecolor=hue,
                                       hatch="////", lw=0))
        sa, sd = _selected_rank(search, dataset, "AE"), _selected_rank(search, dataset, "DAE")
        ax.add_patch(Rectangle((sd - 1, sa - 1), 1, 1, facecolor="none", edgecolor=INK, lw=1.4, zorder=5))
        ax.set_xlim(0, n_dae)
        ax.set_ylim(n_ae, 0)
        ticks = [1, 5, 10, 15, 20]
        ax.set_xticks([t - 0.5 for t in ticks])
        ax.set_xticklabels(ticks)
        ax.set_yticks([t - 0.5 for t in ticks])
        ax.set_yticklabels(ticks)
        ax.set_aspect("equal")
        ax.tick_params(length=2)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.set_xlabel("DAE configuration (development MCC rank)")
        ax.set_ylabel("AE configuration (development MCC rank)")
        ax.set_title(dataset, fontsize=8.5, color=INK, loc="left")
    handles = []
    for st in ("I", "II", "III", "IV"):
        hue = STATE_HUE[st]
        if STATE_SOLID[st]:
            handles.append(Patch(facecolor=hue, edgecolor=hue, label=STATE_LABEL[st]))
        else:
            handles.append(Patch(facecolor=TINT[hue], edgecolor=hue, hatch="////", lw=0.0, label=STATE_LABEL[st]))
    handles.append(Patch(facecolor="none", edgecolor=INK, lw=1.4, label="Selected AE–DAE pair"))
    fig.legend(handles=handles, loc="lower center", ncol=5, frameon=False, fontsize=6.5,
               bbox_to_anchor=(0.5, -0.04), handletextpad=0.4, columnspacing=1.0)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    _save(fig, out_dir, "fig4_configuration_states")


# --------------------------------------------------------------------------------------
# Figure S1: composition of the 3,125 enumerated paths (supplementary material)
# --------------------------------------------------------------------------------------

def figure_s1(t43: pd.DataFrame, out_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(3.5, 1.75))
    order = ["UNSW-NB15", "CICIDS2017"]
    total = None
    for yi, dataset in enumerate(order):
        r = t43.set_index("dataset").loc[dataset]
        total = int(r.total_paths)
        left = 0
        for st in ("I", "II", "III", "IV"):
            v = int(r[f"n_{st}"])
            if not v:
                continue
            hue = STATE_HUE[st]
            if STATE_SOLID[st]:
                ax.barh(yi, v, left=left, color=hue, height=0.55, edgecolor="white", linewidth=1.0)
                txt = "white"
            else:
                ax.barh(yi, v, left=left, color=TINT[hue], height=0.55, edgecolor="white", linewidth=1.0)
                ax.barh(yi, v, left=left, color="none", height=0.45, edgecolor=hue, hatch="////", linewidth=0)
                txt = INK
            label = f"State {st}: {v:,} ({100 * v / total:.2f}%)"
            if v > 900:
                ax.text(left + v / 2, yi, label, ha="center", va="center", fontsize=7, color=txt,
                        bbox=dict(facecolor="white", edgecolor="none", pad=0.6) if txt == INK else None)
            else:
                ax.text(left, yi - 0.36, label, ha="left", va="top", fontsize=7, color=INK)
            left += v
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels(order)
    ax.set_xlim(0, total)
    ax.set_xticks([0, 625, 1250, 1875, 2500, 3125])
    ax.set_xlabel(f"Enumerated ordered paths (of {total:,})")
    ax.set_ylim(-0.85, 1.45)
    fig.tight_layout()
    _save(fig, out_dir, "figS1_path_composition")
