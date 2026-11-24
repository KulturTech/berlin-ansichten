"""Temporal classification: zero-shot CLIP vs. linear probe on CLIP features.

Only images with an epoch label are used. Fixed stratified split (seed 0).
Outputs: results/metrics.json, results/predictions.csv (test split).

    python src/train_probe.py
"""
import json

import numpy as np
import pandas as pd
import torch
from PIL import Image
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, f1_score
from sklearn.model_selection import train_test_split
from transformers import CLIPModel, CLIPProcessor

from common import EPOCHS, IMAGES, METADATA_CSV, RESULTS, device

MODEL = "openai/clip-vit-base-patch32"
PROMPT_TEXT = {
    "vor_1900": "a historical depiction of Berlin before 1900",
    "1900_1945": "a photograph of Berlin between 1900 and 1945",
    "1946_1989": "a photograph of Berlin between 1946 and 1989",
    "ab_1990": "a recent photograph of Berlin after 1990",
}


def embed_images(paths, model, proc, dev, bs=16):
    feats = []
    for i in range(0, len(paths), bs):
        imgs = [Image.open(p).convert("RGB") for p in paths[i:i + bs]]
        x = proc(images=imgs, return_tensors="pt").to(dev)
        with torch.no_grad():
            f = model.get_image_features(**x)
        feats.append(torch.nn.functional.normalize(f, dim=-1).cpu().numpy())
    return np.concatenate(feats)


def main():
    dev = device()
    model = CLIPModel.from_pretrained(MODEL).to(dev).eval()
    proc = CLIPProcessor.from_pretrained(MODEL)

    df = pd.read_csv(METADATA_CSV).dropna(subset=["epoch"]).reset_index(drop=True)
    print(df["epoch"].value_counts())
    X = embed_images([IMAGES / f for f in df["local_file"]], model, proc, dev)
    y = df["epoch"].values
    idx_tr, idx_te = train_test_split(np.arange(len(df)), test_size=0.3, stratify=y, random_state=0)

    # zero-shot
    classes = [e[0] for e in EPOCHS]
    t = proc(text=[PROMPT_TEXT[c] for c in classes], return_tensors="pt", padding=True).to(dev)
    with torch.no_grad():
        T = torch.nn.functional.normalize(model.get_text_features(**t), dim=-1).cpu().numpy()
    zs_pred = np.array(classes)[(X[idx_te] @ T.T).argmax(1)]

    # linear probe
    clf = LogisticRegression(max_iter=2000, class_weight="balanced").fit(X[idx_tr], y[idx_tr])
    lp_pred = clf.predict(X[idx_te])

    metrics = {
        "n_train": int(len(idx_tr)), "n_test": int(len(idx_te)),
        "zero_shot_macro_f1": f1_score(y[idx_te], zs_pred, average="macro"),
        "linear_probe_macro_f1": f1_score(y[idx_te], lp_pred, average="macro"),
        "report_linear_probe": classification_report(y[idx_te], lp_pred, output_dict=True, zero_division=0),
    }
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "metrics.json").write_text(json.dumps(metrics, indent=2))

    out = df.iloc[idx_te].copy()
    out["pred_zero_shot"], out["pred_probe"] = zs_pred, lp_pred
    out.to_csv(RESULTS / "predictions.csv", index=False)
    print({k: v for k, v in metrics.items() if k != "report_linear_probe"})


if __name__ == "__main__":
    main()
