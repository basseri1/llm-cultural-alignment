import os
import csv
from datetime import datetime
import argparse
from llm_apis import call_llm

FRAMEWORKS = {
    'Hofstede': 'Hofstede/questions.csv',
    'Shwartz': 'Shwartz/questions.csv',
    'Ingelhart': 'Ingelhart/questions.csv',
    'MEVS': 'MEVS/questions.csv',
}

COUNTRIES = ['Saudi Arabia', 'United States']


def get_user_input(args):
    # Model selection - display names without version dates, but map to full API names
    model_display_names = [
        # OpenAI models
        'gpt-4o', 'gpt-4.1', 'o4-mini', 'gpt-3.5-turbo', 
        # Claude models
        'claude-3.5-sonnet', 'claude-3.5-haiku', 'claude-3-opus',
        # Gemini models
        'gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-1.0-pro'
    ]
    
    model_api_names = [
        # OpenAI models
        'gpt-4o-2024-08-06', 'gpt-4.1-2025-04-14', 'o4-mini-2025-04-16', 'gpt-3.5-turbo-0125', 
        # Claude models
        'claude-3-5-sonnet-20241022', 'claude-3-5-haiku-20241022', 'claude-3-opus-20240229',
        # Gemini models
        'gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-1.0-pro'
    ]
    
    print('Available LLM models:')
    print('OpenAI:')
    for i in range(4):
        print(f'{i+1}. {model_display_names[i]}')
    print('Claude:')
    for i in range(4, 7):
        print(f'{i+1}. {model_display_names[i]}')
    print('Gemini:')
    for i in range(7, 10):
        print(f'{i+1}. {model_display_names[i]}')
    
    while True:
        try:
            model_choice = input('Enter the number for LLM model: ').strip()
            model_idx = int(model_choice) - 1
            if 0 <= model_idx < len(model_display_names):
                llm_display_name = model_display_names[model_idx]
                llm_api_name = model_api_names[model_idx]
                break
            else:
                print(f"Please enter a number between 1 and {len(model_display_names)}")
        except ValueError:
            print("Please enter a valid number")
    
    # Framework selection
    frameworks = list(FRAMEWORKS.keys())
    print('\nAvailable frameworks:')
    for i, fw in enumerate(frameworks, 1):
        print(f'{i}. {fw}')
    
    while True:
        try:
            framework_choice = input('Enter the number for cultural framework: ').strip()
            framework_idx = int(framework_choice) - 1
            if 0 <= framework_idx < len(frameworks):
                framework = frameworks[framework_idx]
                break
            else:
                print(f"Please enter a number between 1 and {len(frameworks)}")
        except ValueError:
            print("Please enter a valid number")
    
    # Country selection
    print('\nAvailable countries:')
    for i, country in enumerate(COUNTRIES, 1):
        print(f'{i}. {country}')
    
    while True:
        try:
            country_choice = input('Enter the number for country: ').strip()
            country_idx = int(country_choice) - 1
            if 0 <= country_idx < len(COUNTRIES):
                country = COUNTRIES[country_idx]
                break
            else:
                print(f"Please enter a number between 1 and {len(COUNTRIES)}")
        except ValueError:
            print("Please enter a valid number")
    
    # Number of seeds (repetitions)
    print('\nNumber of repetitions for each question:')
    while True:
        try:
            num_seeds = int(input('Enter number of times each question should be answered (1-100): ').strip())
            if 1 <= num_seeds <= 100:
                break
            else:
                print("Please enter a number between 1 and 100")
        except ValueError:
            print("Please enter a valid number")
    
    # Temperature setting
    print('\nTemperature setting (controls randomness):')
    while True:
        try:
            temperature = float(input('Enter temperature value (0.0-1.0, recommended 0.7): ').strip())
            if 0.0 <= temperature <= 1.0:
                break
            else:
                print("Please enter a value between 0.0 and 1.0")
        except ValueError:
            print("Please enter a valid number")
    
    # Top-p setting
    print('\nTop-p setting (nucleus sampling):')
    while True:
        try:
            top_p = float(input('Enter top-p value (0.0-1.0, recommended 1.0): ').strip())
            if 0.0 <= top_p <= 1.0:
                break
            else:
                print("Please enter a value between 0.0 and 1.0")
        except ValueError:
            print("Please enter a valid number")
    
    intersect = args.intersect if args.intersect else None
    return llm_display_name, llm_api_name, framework, country, intersect, num_seeds, temperature, top_p


def load_questions(framework):
    path = FRAMEWORKS[framework]
    
    # Check if file exists
    if not os.path.exists(path):
        print(f"Error: Question file not found at {path}")
        print(f"Please create a questions.csv file for the {framework} framework.")
        return {}
    
    questions = {}
    with open(path, newline='', encoding='utf-8') as csvfile:
        # Check if file is empty
        if os.path.getsize(path) == 0:
            print(f"Error: Question file is empty: {path}")
            print(f"Please add questions to the {framework} framework's questions.csv file.")
            return {}
            
        reader = csv.DictReader(csvfile)
        question_num = 1
        for row in reader:
            if row:
                # Try different possible column names for the question text
                question_text = (row.get('Prompt Text') or 
                               row.get('Question') or 
                               row.get('question') or 
                               row.get('prompt') or
                               list(row.values())[-1])  # fallback to last column
                if question_text and question_text.strip():
                    questions[f"Q{question_num:02d}"] = question_text.strip()
                    question_num += 1
    
    if not questions:
        print(f"Warning: No valid questions found in {path}.")
        print("Please check the format of your questions.csv file.")
    
    return questions


def prompt_llm(llm_name, country, question, intersect=None, temperature=0.7, top_p=1.0):
    """Create the system prompt for role-playing and call the OpenAI API"""
    if intersect:
        system_prompt = f"You are a {intersect} citizen of {country}. You were born and raised in {country}. Answer survey questions from your perspective as a person from this cultural background. IMPORTANT: Respond with ONLY the Likert scale number (1-5) that best represents your answer. Do not add any explanation or additional text."
    else:
        system_prompt = f"You are a citizen of {country}. You were born and raised in {country}. Answer survey questions from your perspective as a person from this cultural background. IMPORTANT: Respond with ONLY the Likert scale number (1-5) that best represents your answer. Do not add any explanation or additional text."
    
    return call_llm(llm_name, question, system_prompt, temperature, top_p)


def save_responses(llm_name, framework, country, responses_data, temperature, top_p, num_seeds):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{llm_name}_{framework}_seeds{num_seeds}_temp{temperature}_topp{top_p}_{timestamp}.csv"
    folder = os.path.join(framework, 'llm_responses')
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, filename)
    
    with open(path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Create header with metadata columns and answer columns
        num_answers = len(responses_data[list(responses_data.keys())[0]]) if responses_data else 0
        header = ['Question ID', 'Country', 'Temperature', 'Top-p']
        header.extend([f'Answer {i+1}' for i in range(num_answers)])
        writer.writerow(header)
        
        # Write data rows
        for question_id, answers in responses_data.items():
            row = [question_id, country, temperature, top_p]
            row.extend(answers)
            writer.writerow(row)
    
    print(f"Responses saved to {path}")


def main():
    parser = argparse.ArgumentParser(description='LLM Cultural Alignment Experiment')
    parser.add_argument('--intersect', type=str, help='Intersectional dimension (e.g., "female", "male", "young", etc.)')
    args = parser.parse_args()

    llm_display_name, llm_api_name, framework, country, intersect, num_seeds, temperature, top_p = get_user_input(args)
    questions = load_questions(framework)
    
    if not questions:
        print("No questions found. Please check your questions.csv file and try again.")
        return
    
    print(f"\nLoaded {len(questions)} questions from {framework}")
    print(f"Will run {num_seeds} repetition(s) per question")
    print(f"Temperature: {temperature}, Top-p: {top_p}")
    print("Starting experiment...")
    
    responses_data = {}
    total_calls = len(questions) * num_seeds
    current_call = 0
    
    for question_id, question in questions.items():
        print(f"\nProcessing {question_id}...")
        answers = []
        
        for seed in range(num_seeds):
            current_call += 1
            print(f"  Repetition {seed + 1}/{num_seeds} (Overall: {current_call}/{total_calls})")
            response = prompt_llm(llm_api_name, country, question, intersect, temperature, top_p)
            answers.append(response)
        
        responses_data[question_id] = answers
    
    if responses_data:
        save_responses(llm_display_name, framework, country, responses_data, temperature, top_p, num_seeds)
        print(f"\nExperiment completed! Processed {len(questions)} questions with {num_seeds} repetition(s) each.")
        print(f"Total API calls made: {total_calls}")
    else:
        print("No responses were collected. Experiment failed.")


if __name__ == '__main__':
    main() 