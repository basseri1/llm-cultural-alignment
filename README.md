# LLM Cultural Alignment Experiment

This project is designed to experiment with how well large language models (LLMs) align with the cultural values of specific nations, focusing on Saudi Arabia and the United States. The experiment uses four cultural frameworks:

- Hofstede
- Shwartz
- Ingelhart
- Middle Eastern Values Survey (MEVS)

## Project Structure

- Each framework has its own folder containing:
  - `questions.csv`: Survey questions for that framework
  - `llm_responses/`: Folder where LLM responses are saved
  - `scores/`: Folder where calculated dimension scores are saved
- `main.py`: Main experiment script
- `llm_apis.py`: OpenAI, Claude, and Gemini API integration
- `formulas.py`: Script to calculate cultural dimension scores from responses
- `.env`: Your API keys (create from .env.example)

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API Keys**
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` and add your API keys:
     ```
     OPENAI_API_KEY=your-openai-api-key-here
     ANTHROPIC_API_KEY=your-anthropic-api-key-here
     GOOGLE_API_KEY=your-google-api-key-here
     ```
   - Your `.env` file is gitignored for security

3. **Survey Questions**
   - Each framework has pre-populated questions in the corresponding `questions.csv` file
   - Questions are formatted with Likert scale options (typically 1-5)
   - Each framework uses specific questions to measure different cultural dimensions

## How to Use

1. **Run the Experiment**
   - Execute the script:
     ```bash
     python main.py [--intersect INTERSECT]
     ```
   - You will be prompted to enter:
     - The LLM model (GPT-4, Claude-3, Gemini, etc.)
     - The cultural framework (Hofstede, Shwartz, Ingelhart, MEVS)
     - The country (Saudi Arabia, United States)
     - Number of repetitions for each question (for statistical validity)
     - Generation parameters (temperature, top-p)
   - The optional `--intersect` argument allows you to specify intersectional dimensions (e.g., `--intersect female`) so the LLM is prompted to respond as, for example, a female Saudi Arabian citizen

2. **LLM Responses**
   - The script will iterate over the questions, prompt the LLM, and save the responses in the appropriate `llm_responses` folder with the filename format:
     ```
     modelname_frameworkname_seeds{num}_temp{temperature}_topp{top_p}_timestamp.csv
     ```
   - Output format: CSV with question IDs and responses (one row per question, with multiple answer columns for repetitions)

3. **Calculate Dimension Scores**
   - After collecting responses, run:
     ```bash
     python formulas.py
     ```
   - You'll be prompted to select:
     - The framework to analyze
     - The results file to process (newest files listed first)
   - This will calculate cultural dimension scores for the selected framework
   - Scores are saved to the framework's `scores/` folder with the filename format:
     ```
     modelname_frameworkname_seeds{num}_temp{temperature}_topp{top_p}_timestamp_framework_scores_timestamp.csv
     ```

4. **Analyzing Results**
   - Each framework produces different cultural dimension scores:
     - **Hofstede**: PDI (Power Distance), IDV (Individualism), MAS (Masculinity), UAI (Uncertainty Avoidance), LTO (Long Term Orientation), IVR (Indulgence vs. Restraint)
     - **Shwartz**: Conformity, Tradition, Benevolence, Universalism, Self-Direction, Stimulation, Hedonism, Achievement, Power, Security
     - **Ingelhart**: Traditional_vs_Secular, Survival_vs_SelfExpression
     - **MEVS**: Family_Values, Religious_Values, Honor_Reputation, Hospitality, Collectivism
   - Compare scores across different LLMs and countries to identify alignment patterns

## Supported Models

- **OpenAI Models**:
  - gpt-4o
  - gpt-4.1
  - o4-mini
  - gpt-3.5-turbo

- **Anthropic Models**:
  - claude-3.5-sonnet
  - claude-3.5-haiku
  - claude-3-opus

- **Google Models**:
  - gemini-1.5-pro
  - gemini-1.5-flash
  - gemini-1.0-pro

## Environment Configuration

The project uses a `.env` file to store your API keys securely:
- Copy `.env.example` to `.env`
- Add your API keys to the corresponding variables
- The `.env` file is gitignored to prevent accidental commits

## Requirements
- Python 3.x
- OpenAI API key (for OpenAI models)
- Anthropic API key (for Claude models)
- Google API key (for Gemini models)
- Dependencies are listed in `requirements.txt`:
  - openai
  - python-dotenv
  - anthropic
  - pandas
  - numpy
  - google-generativeai

---

For any questions, please update the relevant `questions.csv` files and ensure your API keys are properly configured in the `.env` file. 