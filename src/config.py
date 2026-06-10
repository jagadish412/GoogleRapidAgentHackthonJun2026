#API keys
"Below are the names used when environmental variables are created for respective model vendors"
ANTHROPIC_API_KEY = "dummy"
OPEN_AI_API_KEY = "OpenAIKey_Json55"
GEMINI_API_KEY = "GeminiAPIKey_Json55"
TAVILY_API_KEY      = "TavilyAPIKeyJson55" #Web search AI tool

#models from different vendors
ollama_models = [] #since tokens are free we check everytime which models are present and update the list using the script.
openai_models = [
    "gpt-5",
    "gpt-5-mini",
    "gpt-5-nano",
    "gpt-4.1",
    "gpt-4.1-mini",
    "gpt-4o",
    "gpt-4o-mini"
    ]
anthropic_models = ""

#gemini models - manually updated
gemini_models = [
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "gemini-2.0-flash",
        "gemini-2.0-flash-001",
        "gemini-2.0-flash-lite-001",
        "gemini-2.0-flash-lite",
        "gemini-2.5-flash-preview-tts",
        "gemini-2.5-pro-preview-tts",
        "gemma-4-26b-a4b-it",
        "gemma-4-31b-it",
        "gemini-flash-latest",
        "gemini-flash-lite-latest",
        "gemini-pro-latest",
        "gemini-2.5-flash-lite",
        "gemini-2.5-flash-image",
        "gemini-3-pro-preview",
        "gemini-3-flash-preview",
        "gemini-3.1-pro-preview",
        "gemini-3.1-pro-preview-customtools",
        "gemini-3.1-flash-lite-preview",
        "gemini-3.1-flash-lite",
        "gemini-3-pro-image-preview",
        "nano-banana-pro-preview",
        "gemini-3.1-flash-image-preview",
        "lyria-3-clip-preview",
        "lyria-3-pro-preview",
        "gemini-3.1-flash-tts-preview",
        "gemini-robotics-er-1.5-preview",
        "gemini-robotics-er-1.6-preview",
        "gemini-2.5-computer-use-preview-10-2025",
        "deep-research-max-preview-04-2026",
        "deep-research-preview-04-2026",
        "deep-research-pro-preview-12-2025",
        "aqa"
    ]

#model dictionary
MODEL_VENDOR_DICT = {
    "Ollama": "ollama",
    "Openai": "openai",
    "Gemini": "gemini",
    "Anthropic": "anthropic"
}
# CONFIGURATION = Specify which model is used
MODEL_VENDOR_USED = MODEL_VENDOR_DICT["Ollama"] #select from the list model_vendors

# Specific which model is used
OLLAMA_MODEL = "qwen2.5:7b"
GEMINI_MODEL = "gpt-4.1"
OPEN_AI_MODEL = "gemini-2.5-flash"