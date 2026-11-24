"""Corpus and model bias report: distributions + error rates per group.

    python src/bias_report.py

Reads data/metadata.csv and results/predictions.csv (run train_probe.py first).
Groups: epoch, medium, district (fill these columns in metadata.csv; empty = 'unbekannt').
Writes results/bias_*.png and results/bias_tables.md.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from common import METADATA_CSV, RESULTS

GROUPS = ["epoch", "medium", "district", "license", "category"]


def main():
    meta = pd.read_csv(METADATA_CSV)
    lines = ["# Bias-Report\n", f"Korpus: {len(meta)} Bilder\n"]

    for g in GROUPS:
        if g not in meta:
            continue
        counts = meta[g].fillna("unbekannt").replace("", "unbekannt").value_counts()
        lines += [f"\n## Verteilung nach `{g}`\n", counts.to_markdown(), "\n"]
        ax = counts.head(15).plot.barh(figsize=(7, 0.4 * min(len(counts), 15) + 1.5))
        ax.invert_yaxis()
        ax.set_xlabel("Anzahl Bilder")
        plt.tight_layout()
        plt.savefig(RESULTS / f"bias_dist_{g}.png", dpi=150)
        plt.close()

    pred_path = RESULTS / "predictions.csv"
    if pred_path.exists():
        p = pd.read_csv(pred_path)
        p["correct_probe"] = p["epoch"] == p["pred_probe"]
        p["correct_zero_shot"] = p["epoch"] == p["pred_zero_shot"]
        for g in ["epoch", "medium", "district"]:
            if g not in p:
                continue
            p[g] = p[g].fillna("unbekannt").replace("", "unbekannt")
            tab = p.groupby(g)[["correct_zero_shot", "correct_probe"]].agg(["mean", "count"]).round(2)
            lines += [f"\n## Accuracy nach `{g}` (Test-Split; n klein -> vorsichtig lesen)\n", tab.to_markdown(), "\n"]
        lines += ["\n## Konfusionsmatrix (Linear Probe)\n",
                  pd.crosstab(p["epoch"], p["pred_probe"]).to_markdown(), "\n"]
    else:
        lines.append("\n_predictions.csv fehlt: erst train_probe.py ausfuehren._\n")

    (RESULTS / "bias_tables.md").write_text("\n".join(lines))
    print("saved results/bias_tables.md and bias_dist_*.png")


if __name__ == "__main__":
    main()
