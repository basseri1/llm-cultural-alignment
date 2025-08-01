# LLM Cultural Alignment Experiment 🌎🤖

[![Python](https://img.shields.io/badge/python-v3.6+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenAI](https://img.shields.io/badge/OpenAI-API-green.svg)](https://openai.com/blog/openai-api)
[![Anthropic](https://img.shields.io/badge/Claude-API-blueviolet.svg)](https://docs.anthropic.com/claude/reference/getting-started-with-the-api)
[![Gemini](https://img.shields.io/badge/Gemini-API-orange.svg)](https://ai.google.dev/tutorials/python_quickstart)

<p align="center">
  <img src="https://github.com/basseri1/llm-cultural-alignment/raw/main/assets/cultural_alignment_banner.png" alt="Project Banner" width="600">
  <br>
  <em>Banner image created by OpenAI's GPT-4o</em>
</p>

## 📖 Description

This research project investigates how Large Language Models (LLMs) like GPT-4, Claude, and Gemini align with the cultural values of different nations. By utilizing established cultural frameworks, we explore how these AI models represent and reproduce cultural perspectives.

**Key Research Questions:**
- How accurately do LLMs represent cultural perspectives of specific countries?
- Do different LLMs exhibit varying degrees of cultural alignment?
- Can we quantify cultural biases in LLM responses across different frameworks?

The experiment currently focuses on Saudi Arabia and the United States, with plans to expand to more countries and regions.

## 🧪 Cultural Frameworks

The project employs four established cultural analysis frameworks:

1. **Hofstede's Cultural Dimensions Theory** - Measures cultural tendencies across six dimensions: Power Distance (PDI), Individualism (IDV), Masculinity (MAS), Uncertainty Avoidance (UAI), Long Term Orientation (LTO), and Indulgence vs. Restraint (IVR).

2. **Shwartz's Theory of Basic Human Values** - Identifies ten core values including Conformity, Tradition, Benevolence, Universalism, Self-Direction, Stimulation, Hedonism, Achievement, Power, and Security.

3. **Inglehart's World Values Survey** - Analyzes values along two major dimensions: Traditional vs. Secular-Rational values and Survival vs. Self-Expression values.

4. **Middle Eastern Values Survey (MEVS)** - Focuses on values particularly relevant to Middle Eastern cultures such as Family Values, Religious Values, Honor & Reputation, Hospitality, and Collectivism.

## 🏗️ Project Structure

```
project/
│
├── Hofstede/             # Hofstede's Cultural Dimensions framework
│   ├── questions.csv     # Survey questions for Hofstede framework
│   ├── llm_responses/    # LLM responses to Hofstede questions
│   └── scores/           # Calculated Hofstede dimension scores
│
├── Shwartz/              # Shwartz's Theory of Basic Human Values
│   ├── questions.csv
│   ├── llm_responses/
│   └── scores/
│
├── Ingelhart/            # Inglehart's World Values Survey
│   ├── questions.csv
│   ├── llm_responses/
│   └── scores/
│
├── MEVS/                 # Middle Eastern Values Survey
│   ├── questions.csv
│   ├── llm_responses/
│   └── scores/
│
├── main.py               # Main experiment script
├── llm_apis.py           # OpenAI, Claude, and Gemini API integration
├── formulas.py           # Dimension score calculation logic
├── requirements.txt      # Project dependencies
├── .env.example          # Template for API keys configuration
└── README.md             # Project documentation
```

## 🚀 Getting Started

### Prerequisites

- Python 3.6+
- API keys for the LLMs you want to test:
  - OpenAI API key
  - Anthropic API key
  - Google API key

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/basseri1/llm-cultural-alignment.git
   cd llm-cultural-alignment
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API Keys**
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

## 📊 Running Experiments

### 1. Collect LLM Responses

```bash
python main.py [--intersect INTERSECT]
```

You will be prompted to enter:
- The LLM model to use (GPT-4o, Claude-3.5-Sonnet, Gemini-1.5-Pro, etc.)
- The cultural framework to test (Hofstede, Shwartz, Ingelhart, MEVS)
- The country perspective (Saudi Arabia, United States)
- Number of repetitions per question (for statistical validity)
- Generation parameters (temperature, top-p)

The optional `--intersect` argument allows for intersectional analysis:
```bash
python main.py --intersect female
```

This prompts the LLM to respond as a female citizen of the selected country.

### 2. Calculate Cultural Dimension Scores

After collecting responses, calculate the cultural dimension scores:

```bash
python formulas.py
```

You'll select:
- The framework to analyze
- The specific results file to process

Scores are saved to CSV files in the framework's `scores/` directory.

## 📋 Supported Models

### OpenAI Models
- gpt-4o
- gpt-4.1
- o4-mini
- gpt-3.5-turbo

### Anthropic Models
- claude-3.5-sonnet
- claude-3.5-haiku
- claude-3-opus

### Google Models
- gemini-1.5-pro
- gemini-1.5-flash
- gemini-1.0-pro

## 📈 Analyzing Results

Each framework produces different cultural dimension scores:

- **Hofstede**: PDI, IDV, MAS, UAI, LTO, IVR
- **Shwartz**: Conformity, Tradition, Benevolence, Universalism, Self-Direction, Stimulation, Hedonism, Achievement, Power, Security
- **Ingelhart**: Traditional_vs_Secular, Survival_vs_SelfExpression
- **MEVS**: Family_Values, Religious_Values, Honor_Reputation, Hospitality, Collectivism

Compare scores across different LLMs and countries to identify alignment patterns and potential biases.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- Cultural frameworks and theories by Geert Hofstede, Shalom Schwartz, and Ronald Inglehart
- OpenAI, Anthropic, and Google for providing API access to their language models
- Banner image created by OpenAI's GPT-4o

---

## 📧 Contact

For questions or collaborations, please [open an issue](https://github.com/basseri1/llm-cultural-alignment/issues) on this repository.