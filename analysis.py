import json
import warnings
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.stats as st
import statsmodels.formula.api as smf

from score import ANSWERS, ARABIC_CENTRIC, load_responses
from vsm import DIMS, REFERENCE, indices

warnings.filterwarnings("ignore")
HERE = Path(__file__).parent
TYPES = ("general", "arabic-centric")
LEVEL = {"uni": 1, "bi": 2, "tri": 3}
DESIGNATED_HIGH = {15, 17, 20}


def distance(cells, ref, c_shift=0.0, metric="euclidean"):
    diff = cells[DIMS].values + c_shift - ref
    return np.abs(diff).sum(axis=1) if metric == "manhattan" else np.sqrt((diff ** 2).sum(axis=1))


def crossover(cells, ref, c_shift=0.0, metric="euclidean"):
    d = cells.assign(dist=distance(cells, ref, c_shift, metric))
    fit = smf.mixedlm("dist ~ C(model_type, Treatment('general')) * C(language, Treatment('English'))",
                      d, groups=d["profile"]).fit(reml=True)
    term = next(t for t in fit.params.index if ":" in t)
    b, se = float(fit.params[term]), float(fit.bse[term])
    lo, hi = fit.conf_int().loc[term]
    m = d.groupby(["model_type", "language"]).dist.mean()
    return {"delta_delta": b, "se": se, "z": b / se, "p": float(fit.pvalues[term]), "ci": [float(lo), float(hi)],
            "d": b / float(np.sqrt(fit.scale)),
            "means": {f"{t} / {lang}": float(m[(t, lang)]) for t in TYPES for lang in ("Arabic", "English")},
            "change": {t: float(m[(t, "Arabic")] - m[(t, "English")]) for t in TYPES}}


def by_model(cells, ref):
    d = cells.assign(dist=distance(cells, ref)).groupby(["model", "language"]).dist.mean().unstack()
    return {m: {"Arabic": float(r.Arabic), "English": float(r.English), "change": float(r.Arabic - r.English)}
            for m, r in d.iterrows()}


def complexity_lmm(cells, ref, c_shift=0.0):
    d = cells.assign(dist=distance(cells, ref, c_shift), level=cells.complexity.map(LEVEL))
    fit = smf.mixedlm("dist ~ level", d, groups=d["profile"]).fit(reml=True)
    return {"beta": float(fit.params["level"]), "se": float(fit.bse["level"]), "p": float(fit.pvalues["level"])}


def rank_measures(cells, ref):
    rows = []
    for _, c in cells.iterrows():
        x = c[DIMS].values.astype(float)
        mis = np.mean([np.sign(x[i] - x[j]) != np.sign(ref[i] - ref[j]) for i, j in combinations(range(6), 2)])
        rows.append({"model_type": c.model_type, "language": c.language, "kendall": st.kendalltau(x, ref)[0],
                     "pearson": st.pearsonr(x, ref)[0], "misranking": mis})
    m = pd.DataFrame(rows).groupby(["model_type", "language"]).mean()
    return {k: {t: float(m.loc[(t, "Arabic"), k] - m.loc[(t, "English"), k]) for t in TYPES}
            for k in ("kendall", "pearson", "misranking")}


def reliability(responses):
    keys = ["model", "persona", "language"]
    r = responses.assign(item=responses.question_id.str[1:].astype(int))
    a = r[ANSWERS].apply(lambda col: col.fillna(r[ANSWERS].mean(axis=1)))
    arr = {}
    for (key, g), (_, ga) in zip(r.groupby(keys), a.groupby([r[k] for k in keys])):
        arr[key] = ga.set_axis(g.item.values).sort_index().values
    profiles = [indices({i + 1: v[i] for i in range(24)}) for v in arr.values()]
    out = {}
    for dim in DIMS:
        x = np.array([prof[dim] for prof in profiles])
        n, k = x.shape
        msb = k * ((x.mean(axis=1) - x.mean()) ** 2).sum() / (n - 1)
        msw = ((x - x.mean(axis=1, keepdims=True)) ** 2).sum() / (n * (k - 1))
        icc1 = (msb - msw) / (msb + (k - 1) * msw)
        out[dim] = float(k * icc1 / (1 + (k - 1) * icc1))
    return out


def response_patterns(responses):
    r = responses.assign(item=responses.question_id.str[1:].astype(int))
    long = r.melt(id_vars=["model", "language", "item"], value_vars=ANSWERS, value_name="answer").dropna()
    high = long.item.isin(DESIGNATED_HIGH)
    long["category"] = np.where(long.answer == 3, "midpoint",
                                np.where(high & (long.answer >= 4) | ~high & (long.answer <= 2), "designated", "complementary"))
    long["model_type"] = np.where(long.model.isin(ARABIC_CENTRIC), "arabic-centric", "general")
    share = lambda g: (100 * g.category.value_counts(normalize=True)).round(10).to_dict()
    sd = r[ANSWERS].std(axis=1, ddof=1)
    sd_type = np.where(r.model.isin(ARABIC_CENTRIC), "arabic-centric", "general")
    a, g = sd[sd_type == "arabic-centric"], sd[sd_type == "general"]
    pooled = np.sqrt(((len(a) - 1) * a.var() + (len(g) - 1) * g.var()) / (len(a) + len(g) - 2))
    return {"by_type": {t: share(x) for t, x in long.groupby("model_type")},
            "by_type_language": {f"{t} / {lang}": share(x) for (t, lang), x in long.groupby(["model_type", "language"])},
            "by_model_language": {f"{m} / {lang}": share(x) for (m, lang), x in long.groupby(["model", "language"])},
            "by_model": {m: share(x) for m, x in long.groupby("model")},
            "sd_by_type": {"general": float(g.mean()), "arabic-centric": float(a.mean())},
            "sd_ratio": float(a.mean() / g.mean()), "sd_cohens_d": float((a.mean() - g.mean()) / pooled),
            "sd_by_model": {m: float(x.mean()) for m, x in sd.groupby(r.model)}}


def dispersion(cells):
    d = cells.assign(sd=cells[DIMS].std(axis=1, ddof=1))
    out = {}
    for t, g in d.groupby("model_type"):
        uni, tri = g[g.complexity == "uni"].sd, g[g.complexity == "tri"].sd
        out[t] = {"uni": float(uni.mean()), "tri": float(tri.mean()), "increase_pct": float(100 * (tri.mean() / uni.mean() - 1)),
                  "welch_p": float(st.ttest_ind(tri, uni, equal_var=False).pvalue)}
    out["fold_by_model"] = {m: float(g[g.complexity == "tri"].sd.mean() / g[g.complexity == "uni"].sd.mean())
                            for m, g in d.groupby("model")}
    return out


def complexity_summary(cells, target, ref):
    d = cells[cells.target == target].assign(dist=lambda x: distance(x, ref))
    return {"overall": d.groupby("complexity").dist.mean().reindex(["uni", "bi", "tri"]).round(10).to_dict(),
            "by_type": {t: g.groupby("complexity").dist.mean().reindex(["uni", "bi", "tri"]).round(10).to_dict()
                        for t, g in d.groupby("model_type")},
            "dimension_means": {dim: d.groupby("complexity")[dim].mean().reindex(["uni", "bi", "tri"]).round(10).to_dict()
                                for dim in DIMS}}


def compute():
    cells = pd.read_csv(HERE / "data" / "cells.csv")
    responses = load_responses()
    ksa, usa, alt = REFERENCE["KSA"], REFERENCE["USA"], REFERENCE["KSA_almutairi"]
    sa, us, neutral = cells[cells.target == "KSA"], cells[cells.target == "USA"], cells[cells.target == "none"]
    matched = pd.concat([sa.assign(dist=distance(sa, ksa), mae=np.abs(sa[DIMS].values - ksa).mean(axis=1)),
                         us.assign(dist=distance(us, usa), mae=np.abs(us[DIMS].values - usa).mean(axis=1))])
    cat = {}
    for label, shift in (("C=50", 0.0), ("C=0", -50.0)):
        m = matched.assign(dist=np.concatenate([distance(sa, ksa, shift), distance(us, usa, shift)]))
        fit = smf.mixedlm("dist ~ C(model_type, Treatment('general'))", m, groups=m["model"]).fit(reml=True)
        term = next(t for t in fit.params.index if "model_type" in t)
        lo, hi = fit.conf_int().loc[term]
        cat[label] = {"beta": float(fit.params[term]), "se": float(fit.bse[term]), "z": float(fit.params[term] / fit.bse[term]),
                      "p": float(fit.pvalues[term]), "ci": [float(lo), float(hi)]}
    valid = responses[ANSWERS].notna()
    return {
        "data": {"rows": int(len(responses)), "answers": int(valid.size), "valid": int(valid.values.sum()),
                 "invalid": int((~valid).values.sum()), "cells": int(len(cells))},
        "reliability_spearman_brown": reliability(responses),
        "reference_distance_ksa_usa": float(np.linalg.norm(ksa - usa)),
        "reference_distance_ksa_almutairi": float(np.linalg.norm(ksa - alt)),
        "midpoint_responder": {"KSA": float(np.linalg.norm(50 - ksa)), "USA": float(np.linalg.norm(50 - usa))},
        "mae_by_type": matched.groupby("model_type").mae.mean().to_dict(),
        "category_lmm": cat,
        "crossover_saudi": crossover(sa, ksa),
        "crossover_us": crossover(us, usa),
        "per_model_saudi": by_model(sa, ksa),
        "per_model_us": by_model(us, usa),
        "sensitivity": {
            "almutairi_profile": crossover(sa, alt),
            "almutairi_per_model": by_model(sa, alt),
            "c0_saudi": crossover(sa, ksa, c_shift=-50.0),
            "c0_us": crossover(us, usa, c_shift=-50.0),
            "manhattan_saudi": crossover(sa, ksa, metric="manhattan"),
            "country_neutral_vs_saudi": crossover(neutral, ksa),
            "rank_measures_saudi": rank_measures(sa, ksa)},
        "complexity": {
            "saudi": complexity_summary(cells, "KSA", ksa), "us": complexity_summary(cells, "USA", usa),
            "lmm_saudi": complexity_lmm(sa, ksa), "lmm_us": complexity_lmm(us, usa),
            "lmm_us_general": complexity_lmm(us[us.model_type == "general"], usa),
            "lmm_us_arabic_centric": complexity_lmm(us[us.model_type == "arabic-centric"], usa),
            "lmm_saudi_c0": complexity_lmm(sa, ksa, c_shift=-50.0), "lmm_us_c0": complexity_lmm(us, usa, c_shift=-50.0),
            "lmm_saudi_almutairi": complexity_lmm(sa, alt)},
        "dispersion": dispersion(cells),
        "response_patterns": response_patterns(responses),
    }


def report(r):
    x, u = r["crossover_saudi"], r["crossover_us"]
    print(f"Answers: {r['data']['valid']:,} valid of {r['data']['answers']:,} ({r['data']['invalid']} invalid)")
    print("Saudi crossover: DeltaDelta = {delta_delta:.1f}, SE = {se:.2f}, z = {z:.2f}, p = {p:.2g}, 95% CI [{ci[0]:.1f}, {ci[1]:.1f}], d = {d:.2f}".format(**x))
    print("  cell means:", {k: round(v, 1) for k, v in x["means"].items()})
    print("US crossover:    DeltaDelta = {delta_delta:.1f}, SE = {se:.2f}, z = {z:.2f}, p = {p:.3f}, 95% CI [{ci[0]:.1f}, {ci[1]:.1f}], d = {d:.2f}".format(**u))
    s = r["sensitivity"]
    print(f"Sensitivity: AlMutairi profile {s['almutairi_profile']['delta_delta']:.1f} (d {s['almutairi_profile']['d']:.2f}); "
          f"C = 0 Saudi {s['c0_saudi']['delta_delta']:.1f} (d {s['c0_saudi']['d']:.2f}), US {s['c0_us']['delta_delta']:.1f} (d {s['c0_us']['d']:.2f}); "
          f"Manhattan {s['manhattan_saudi']['delta_delta']:.1f}; country-neutral {s['country_neutral_vs_saudi']['delta_delta']:.1f} "
          f"(d {s['country_neutral_vs_saudi']['d']:.2f})")
    print("Per model (Saudi, Arabic - English):", {m: round(v["change"], 1) for m, v in r["per_model_saudi"].items()})


if __name__ == "__main__":
    results = compute()
    (HERE / "results.json").write_text(json.dumps(results, indent=1))
    report(results)
    print("wrote results.json")
