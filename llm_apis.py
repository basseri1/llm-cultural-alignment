"""
OpenAI, Claude, and Gemini API integration for cultural alignment experiments
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def call_openai_api(prompt, model="gpt-4", system_prompt=None, temperature=0.7, top_p=1.0):
    """Call OpenAI API with optional system prompt and generation parameters"""
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        return "[Error: OPENAI_API_KEY not found in environment variables. Please check your .env file]"
    
    if api_key == "your-openai-api-key-here":
        return "[Error: Please replace the placeholder with your actual OpenAI API key in .env file]"
    
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=500,
            temperature=temperature,
            top_p=top_p
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[Error calling OpenAI API: {str(e)}]"


def call_claude_api(prompt, model="claude-3-5-sonnet-20241022", system_prompt=None, temperature=0.7, top_p=1.0):
    """Call Claude API with optional system prompt and generation parameters"""
    api_key = os.getenv('ANTHROPIC_API_KEY')
    
    if not api_key:
        return "[Error: ANTHROPIC_API_KEY not found in environment variables. Please check your .env file]"
    
    if api_key == "your-anthropic-api-key-here":
        return "[Error: Please replace the placeholder with your actual Anthropic API key in .env file]"
    
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        
        # For Claude, system prompt is a separate parameter
        kwargs = {
            "model": model,
            "max_tokens": 500,
            "temperature": temperature,
            "top_p": top_p,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        if system_prompt:
            kwargs["system"] = system_prompt
        
        response = client.messages.create(**kwargs)
        return response.content[0].text
    except Exception as e:
        return f"[Error calling Claude API: {str(e)}]"


def call_gemini_api(prompt, model="gemini-1.5-pro", system_prompt=None, temperature=0.7, top_p=1.0):
    """Call Google Gemini API with optional system prompt and generation parameters"""
    api_key = os.getenv('GOOGLE_API_KEY')
    
    if not api_key:
        return "[Error: GOOGLE_API_KEY not found in environment variables. Please check your .env file]"
    
    if api_key == "your-google-api-key-here":
        return "[Error: Please replace the placeholder with your actual Google API key in .env file]"
    
    try:
        import google.generativeai as genai
        
        # Configure the API
        genai.configure(api_key=api_key)
        
        # Create a model instance
        model_instance = genai.GenerativeModel(model_name=model)
        
        # Set generation parameters
        generation_config = {
            "temperature": temperature,
            "top_p": top_p,
            "max_output_tokens": 500,
        }
        
        # For Gemini, we need to include the system prompt in the user message
        # since it doesn't have separate system prompt handling like OpenAI or Claude
        if system_prompt:
            combined_prompt = f"System: {system_prompt}\n\nUser: {prompt}"
            response = model_instance.generate_content(combined_prompt, generation_config=generation_config)
        else:
            response = model_instance.generate_content(prompt, generation_config=generation_config)
        
        return response.text
    except Exception as e:
        return f"[Error calling Gemini API: {str(e)}]"


# Map LLM names to their API functions
LLM_FUNCTIONS = {
    # OpenAI models
    'gpt-4o-2024-08-06': lambda prompt, system_prompt=None, temperature=0.7, top_p=1.0: call_openai_api(prompt, "gpt-4o-2024-08-06", system_prompt, temperature, top_p),
    'gpt-4.1-2025-04-14': lambda prompt, system_prompt=None, temperature=0.7, top_p=1.0: call_openai_api(prompt, "gpt-4.1-2025-04-14", system_prompt, temperature, top_p),
    'o4-mini-2025-04-16': lambda prompt, system_prompt=None, temperature=0.7, top_p=1.0: call_openai_api(prompt, "o4-mini-2025-04-16", system_prompt, temperature, top_p),
    'gpt-3.5-turbo-0125': lambda prompt, system_prompt=None, temperature=0.7, top_p=1.0: call_openai_api(prompt, "gpt-3.5-turbo-0125", system_prompt, temperature, top_p),
    
    # Claude models
    'claude-3-5-sonnet-20241022': lambda prompt, system_prompt=None, temperature=0.7, top_p=1.0: call_claude_api(prompt, "claude-3-5-sonnet-20241022", system_prompt, temperature, top_p),
    'claude-3-5-haiku-20241022': lambda prompt, system_prompt=None, temperature=0.7, top_p=1.0: call_claude_api(prompt, "claude-3-5-haiku-20241022", system_prompt, temperature, top_p),
    'claude-3-opus-20240229': lambda prompt, system_prompt=None, temperature=0.7, top_p=1.0: call_claude_api(prompt, "claude-3-opus-20240229", system_prompt, temperature, top_p),
    
    # Gemini models
    'gemini-1.5-pro': lambda prompt, system_prompt=None, temperature=0.7, top_p=1.0: call_gemini_api(prompt, "gemini-1.5-pro", system_prompt, temperature, top_p),
    'gemini-1.5-flash': lambda prompt, system_prompt=None, temperature=0.7, top_p=1.0: call_gemini_api(prompt, "gemini-1.5-flash", system_prompt, temperature, top_p),
    'gemini-1.0-pro': lambda prompt, system_prompt=None, temperature=0.7, top_p=1.0: call_gemini_api(prompt, "gemini-1.0-pro", system_prompt, temperature, top_p),
}


def call_llm(llm_name, prompt, system_prompt=None, temperature=0.7, top_p=1.0):
    """
    Call the specified LLM (OpenAI, Claude, or Gemini) with the given prompt, system prompt, and generation parameters
    """
    if llm_name in LLM_FUNCTIONS:
        return LLM_FUNCTIONS[llm_name](prompt, system_prompt, temperature, top_p)
    else:
        return f"[Error: Unknown LLM '{llm_name}'. Available: {list(LLM_FUNCTIONS.keys())}]" 