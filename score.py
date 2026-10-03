import re
from pathlib import Path

import pandas as pd

from vsm import DIMS, indices

HERE = Path(__file__).parent
ANSWERS = [f"answer_{i}" for i in range(1, 101)]
ARABIC_CENTRIC = ("ALLaM-7B", "Command R7B Arabic", "SILMA-9B")
COMPLEXITY = {"Age": "uni", "Country": "uni", "Gender": "uni",
              "Country_Age": "bi", "Country_Gender": "bi", "Gender_Age": "bi", "Country_Gender_Age": "tri"}


def load_responses(path=HERE / "data" / "responses.csv.gz"):
    return pd.read_csv(path)


def persona_info(persona):
    target = "KSA" if "Saudi" in persona else "USA" if "United States" in persona else "none"
    gender = "female" if "female" in persona else "male" if re.search(r"\bmale\b", persona) else "unspecified"
    age = ("young" if "young" in persona else "middle-aged" if "middle aged" in persona
           else "elder" if "elder" in persona else "unspecified")
    return target, gender, age, f"{age} / {gender}"


def cells(responses):
    r = responses.assign(item=responses.question_id.str[1:].astype(int),
                         item_mean=responses[ANSWERS].mean(axis=1),
                         valid=responses[ANSWERS].notna().sum(axis=1))
    keys = ["model", "persona_type", "persona", "language"]
    means = r.pivot_table(index=keys, columns="item", values="item_mean")
    out = pd.DataFrame([indices(row) for _, row in means.iterrows()], index=means.index).round(2)
    out = out.join(r.groupby(keys).valid.sum().rename("valid_responses"))
    out = out.join(means.rename(columns=lambda i: f"Q{i:02d}_mean")).reset_index()
    info = out.persona.map(persona_info)
    out.insert(1, "model_type", out.model.map(lambda m: "arabic-centric" if m in ARABIC_CENTRIC else "general"))
    out.insert(3, "complexity", out.persona_type.map(COMPLEXITY))
    for i, col in enumerate(("target", "gender", "age", "profile")):
        out.insert(5 + i, col, info.str[i])
    return out[["model", "model_type", "persona_type", "complexity", "persona", "target", "gender", "age", "profile",
                "language", "valid_responses", *DIMS, *[f"Q{i:02d}_mean" for i in range(1, 25)]]]


if __name__ == "__main__":
    out = cells(load_responses())
    out.to_csv(HERE / "data" / "cells.csv", index=False)
    print(f"wrote data/cells.csv: {len(out)} cells")
