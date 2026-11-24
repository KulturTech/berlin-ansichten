"""Zero-shot segmentation of urban elements with CLIPSeg.

For each image and each text prompt, CLIPSeg predicts a mask. We store the
area share per prompt (results/segmentation_coverage.csv) and a few overlays
for qualitative failure analysis (results/overlays/).

    python src/zero_shot_segment.py --n 60
"""
import argparse

import numpy as np
import pandas as pd
import torch
from PIL import Image
from transformers import CLIPSegForImageSegmentation, CLIPSegProcessor

from common import IMAGES, METADATA_CSV, RESULTS, device

PROMPTS = ["street", "building", "car", "tram", "person", "tree", "sky", "water", "bridge", "horse carriage"]
THRESH = 0.4


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=60)
    ap.add_argument("--overlays", type=int, default=12)
    a = ap.parse_args()

    dev = device()
    proc = CLIPSegProcessor.from_pretrained("CIDAS/clipseg-rd64-refined")
    model = CLIPSegForImageSegmentation.from_pretrained("CIDAS/clipseg-rd64-refined").to(dev).eval()

    meta = pd.read_csv(METADATA_CSV)
    meta = meta.sample(min(a.n, len(meta)), random_state=0)
    (RESULTS / "overlays").mkdir(parents=True, exist_ok=True)

    rows = []
    for i, r in enumerate(meta.itertuples()):
        img = Image.open(IMAGES / r.local_file).convert("RGB")
        inputs = proc(text=PROMPTS, images=[img] * len(PROMPTS), padding=True, return_tensors="pt").to(dev)
        with torch.no_grad():
            logits = model(**inputs).logits  # (n_prompts, 352, 352)
        probs = torch.sigmoid(logits).cpu().numpy()
        row = {"file_id": r.file_id, "epoch": r.epoch}
        for p, m in zip(PROMPTS, probs):
            row[f"cov_{p}"] = float((m > THRESH).mean())
            row[f"max_{p}"] = float(m.max())
        rows.append(row)

        if i < a.overlays:  # save strongest-prompt overlay for manual inspection
            best = int(np.argmax([probs[j].max() for j in range(len(PROMPTS))]))
            mask = Image.fromarray((probs[best] * 255).astype("uint8")).resize(img.size)
            overlay = Image.blend(img, Image.merge("RGB", (mask, mask.point(lambda _: 0), mask.point(lambda _: 0))), 0.4)
            overlay.save(RESULTS / "overlays" / f"{i:02d}_{PROMPTS[best]}.jpg")

    pd.DataFrame(rows).to_csv(RESULTS / "segmentation_coverage.csv", index=False)
    print("saved results/segmentation_coverage.csv")


if __name__ == "__main__":
    main()
