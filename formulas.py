import os
import sys
import pandas as pd
import numpy as np
import re
from datetime import datetime

INPUT_HELP = """
This script calculates cultural dimension indices from experiment results.
You will be prompted to select a framework and a results file.
"""

FRAMEWORKS = {
    "Hofstede": {
        "questions": {
            "PDI": ["Q02", "Q07", "Q20", "Q23"],
            "IDV": ["Q01", "Q04", "Q06", "Q09"],
            "MAS": ["Q03", "Q05", "Q08", "Q10"],
            "UAI": ["Q15", "Q18", "Q21", "Q24"],
            "LTO": ["Q13", "Q14", "Q19", "Q22"],
            "IVR": ["Q11", "Q12", "Q16", "Q17"],
        },
        "formulas": lambda means: {
            "PDI": 35 * (means["Q07"] - means["Q02"]) + 25 * (means["Q20"] - means["Q23"]),
            "IDV": 35 * (means["Q04"] - means["Q01"]) + 35 * (means["Q09"] - means["Q06"]),
            "MAS": 35 * (means["Q05"] - means["Q03"]) + 35 * (means["Q08"] - means["Q10"]),
            "UAI": 40 * (means["Q18"] - means["Q15"]) + 25 * (means["Q21"] - means["Q24"]),
            "LTO": 40 * (means["Q13"] - means["Q14"]) + 25 * (means["Q19"] - means["Q22"]),
            "IVR": 35 * (means["Q12"] - means["Q11"]) + 40 * (means["Q17"] - means["Q16"]),
        },
        "results_dir": "Hofstede/llm_responses/",
        "output_dir": "Hofstede/scores/"
    },
    "Shwartz": {
        "questions": {
            "Conformity": ["Q01"],
            "Tradition": ["Q02"],
            "Benevolence": ["Q03"],
            "Universalism": ["Q04"],
            "Self-Direction": ["Q05"],
            "Stimulation": ["Q06"],
            "Hedonism": ["Q07"],
            "Achievement": ["Q08"],
            "Power": ["Q09"],
            "Security": ["Q10"]
        },
        "formulas": lambda means: {
            # Direct mapping for Shwartz values - higher values (closer to 5) mean stronger alignment
            "Conformity": means["Q01"],
            "Tradition": means["Q02"],
            "Benevolence": means["Q03"],
            "Universalism": means["Q04"],
            "Self-Direction": means["Q05"],
            "Stimulation": means["Q06"],
            "Hedonism": means["Q07"],
            "Achievement": means["Q08"],
            "Power": means["Q09"],
            "Security": means["Q10"]
        },
        "results_dir": "Shwartz/llm_responses/",
        "output_dir": "Shwartz/scores/"
    },
    "Ingelhart": {
        "questions": {
            "Traditional": ["Q01", "Q02", "Q03", "Q04", "Q05"],
            "Self-Expression": ["Q06", "Q07", "Q08", "Q09", "Q10"]
        },
        "formulas": lambda means: {
            # For Traditional vs Secular, low values are traditional, high values are secular
            # For Survival vs Self-Expression, low values are survival, high values are self-expression
            "Traditional_vs_Secular": 20 * (
                (6 - means["Q01"]) + (6 - means["Q02"]) + (6 - means["Q03"]) + 
                (6 - means["Q04"]) + (6 - means["Q05"])
            ) / 5,  # Scale from 0-100
            "Survival_vs_SelfExpression": 20 * (
                (6 - means["Q06"]) + (6 - means["Q07"]) + (6 - means["Q08"]) + 
                (6 - means["Q09"]) + (6 - means["Q10"])
            ) / 5   # Scale from 0-100
        },
        "results_dir": "Ingelhart/llm_responses/",
        "output_dir": "Ingelhart/scores/"
    },
    "MEVS": {
        "questions": {
            "Family_Values": ["Q01", "Q02"],
            "Religious_Values": ["Q03", "Q04"],
            "Honor_Reputation": ["Q05", "Q06"],
            "Hospitality": ["Q07", "Q08"],
            "Collectivism": ["Q09", "Q10"]
        },
        "formulas": lambda means: {
            # For MEVS dimensions, lower values mean stronger agreement (stronger alignment with value)
            "Family_Values": (means["Q01"] + means["Q02"]) / 2,
            "Religious_Values": (means["Q03"] + means["Q04"]) / 2,
            "Honor_Reputation": (means["Q05"] + means["Q06"]) / 2,
            "Hospitality": (means["Q07"] + means["Q08"]) / 2,
            "Collectivism": (means["Q09"] + means["Q10"]) / 2
        },
        "results_dir": "MEVS/llm_responses/",
        "output_dir": "MEVS/scores/"
    }
}

# Extract the first valid Likert number (1-5) from a string
def extract_likert(response):
    if pd.isna(response):
        return np.nan
    
    # First try to interpret response as a single number (1-5)
    response_str = str(response).strip()
    if response_str in ['1', '2', '3', '4', '5']:
        return int(response_str)
    
    # Otherwise look for patterns like "1 = ..." or "1."
    match = re.search(r"^(?:\s*)?([1-5])\s*=|^([1-5])\b", str(response))
    if match:
        return int(match.group(1) or match.group(2))
    
    return np.nan

def normalize_qid(qid):
    # Normalize Q3 <-> Q03, Q10 stays Q10
    match = re.match(r"Q0*([1-9][0-9]*)$", qid)
    if match:
        return f"Q{int(match.group(1)):02d}"
    return qid


def choose_framework():
    print("Available frameworks:")
    frameworks = list(FRAMEWORKS.keys())
    for i, fw in enumerate(frameworks, 1):
        print(f"{i}. {fw}")
    while True:
        try:
            idx = int(input("Enter the number for the framework: ").strip()) - 1
            if 0 <= idx < len(frameworks):
                return frameworks[idx]
            else:
                print(f"Please enter a number between 1 and {len(frameworks)}")
        except ValueError:
            print("Please enter a valid number")

def choose_results_file(results_dir):
    try:
        # Get all CSV files with their full paths
        file_paths = [os.path.join(results_dir, f) for f in os.listdir(results_dir) if f.endswith('.csv')]
    except FileNotFoundError:
        print(f"Error: Directory {results_dir} does not exist.")
        print("Please run the experiment first using main.py.")
        sys.exit(1)
    
    if not file_paths:
        print(f"No CSV files found in {results_dir}")
        print("Please run the experiment first using main.py.")
        sys.exit(1)
    
    # Sort files by creation time (newest first)
    file_paths.sort(key=lambda x: os.path.getctime(x), reverse=True)
    
    # Extract just the filenames for display
    files = [os.path.basename(f) for f in file_paths]
        
    print("Available results files (newest first):")
    for i, f in enumerate(files, 1):
        # Get file creation time and format it
        creation_time = datetime.fromtimestamp(os.path.getctime(os.path.join(results_dir, f)))
        time_str = creation_time.strftime('%Y-%m-%d %H:%M:%S')
        print(f"{i}. {f} (created: {time_str})")
        
    while True:
        try:
            idx = int(input("Enter the number for the results file: ").strip()) - 1
            if 0 <= idx < len(files):
                return os.path.join(results_dir, files[idx])
            else:
                print(f"Please enter a number between 1 and {len(files)}")
        except ValueError:
            print("Please enter a valid number")

def main():
    print(INPUT_HELP)
    framework = choose_framework()
    fw_info = FRAMEWORKS[framework]
    results_file = choose_results_file(fw_info["results_dir"])
    output_dir = fw_info["output_dir"]
    formulas = fw_info["formulas"]

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Read the results file
    try:
        df = pd.read_csv(results_file)
    except Exception as e:
        print(f"Error reading results file: {e}")
        sys.exit(1)

    # For each row (question), extract Likert values from all Answer columns in that row only
    means = {}
    for _, row in df.iterrows():
        qid = normalize_qid(row["Question ID"])
        likert_vals = []
        for col in df.columns:
            if col.startswith("Answer"):
                val = extract_likert(row[col])
                if not pd.isna(val):
                    likert_vals.append(val)
        means[qid] = round(np.mean(likert_vals), 2) if likert_vals else np.nan

    # Check if any question is missing
    missing_questions = []
    for dim, questions in fw_info["questions"].items():
        for q in questions:
            if q not in means or pd.isna(means[q]):
                missing_questions.append(q)
    
    if missing_questions:
        print(f"Warning: Missing values for questions: {missing_questions}")
        print("Some dimension scores may be affected.")

    # Calculate indices
    try:
        indices = formulas(means)
    except KeyError as e:
        print(f"Missing required question for calculation: {e}")
        print(f"Available question IDs: {list(means.keys())}")
        sys.exit(1)

    # Output
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    base = os.path.splitext(os.path.basename(results_file))[0]
    out_path = os.path.join(output_dir, f"{base}_{framework.lower()}_scores_{timestamp}.csv")

    # Save means and indices
    print("\nPer-question means:")
    for qid in sorted(means):
        print(f"  {qid}: {means[qid]}")
    print("\nDimension scores:")
    for dim, score in indices.items():
        print(f"  {dim}: {round(score, 2)}")

    with open(out_path, "w") as f:
        f.write("Question,Mean\n")
        for qid in sorted(means):
            f.write(f"{qid},{means[qid]}\n")
        f.write("\nDimension,Score\n")
        for dim, score in indices.items():
            f.write(f"{dim},{round(score, 2)}\n")
    print(f"\nSaved {framework} scores to {out_path}")

if __name__ == "__main__":
    main() 