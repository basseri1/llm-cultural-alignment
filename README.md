# The Arabic Alignment Paradox: analysis pipeline

Analysis code for *The Arabic Alignment Paradox: Prompting Language Effects on Cultural Alignment in Arabic-Centric
Large Language Models* (Bushra Asseri, Hend Alrasheed and Areej Al-Wabil).

Six models, three Arabic-centric (ALLaM-7B, Command R7B Arabic, SILMA-9B) and three general-purpose (GPT-4o,
Gemini 2.5 Pro, Mistral Small 3.2), answered the 24 items of Hofstede's Values Survey Module 2013 (VSM 2013) in Arabic
and English under 35 personas, 100 times each. The design gives 420 cells (6 models × 2 languages × 35 personas).
This code turns the item-level answers into VSM 2013 profiles and runs the statistical analyses reported in the paper.

## Files

| File | Contents |
|---|---|
| `vsm.py` | VSM 2013 index formulas and the reference profiles: Hofstede's Saudi Arabia and United States profiles, and the Saudi profile of AlMutairi, Heller and Yen (2021) for the sensitivity analysis |
| `score.py` | Item-level answers → one row per cell: the 24 item means and the six indices (C = 50) |
| `analysis.py` | The paper's analyses; prints a summary and writes `results.json` |

## Running

Python 3.10 or later.

```bash
pip install -r requirements.txt
python score.py
python analysis.py
```

## Input

`data/responses.csv.gz` has one row per model × language × persona × item (10,080 rows):

| Column | Values |
|---|---|
| `model` | model name; `ALLaM-7B`, `Command R7B Arabic` and `SILMA-9B` are Arabic-centric, all others general-purpose |
| `question_id` | `Q01` to `Q24` |
| `persona_type` | `Age`, `Gender`, `Country` (uni-dimensional); `Country_Age`, `Country_Gender`, `Gender_Age` (bi-dimensional); `Country_Gender_Age` (tri-dimensional) |
| `persona` | English persona text, such as `a young female from Saudi Arabia`; target country, gender and age group are read from it |
| `language` | `English` or `Arabic` |
| `answer_1` to `answer_100` | the answer in each iteration, 1 to 5; empty when the output was not an integer from 1 to 5 |

Other columns are ignored. Invalid answers are left out of the item means.

## License

MIT
