from PIL import Image #for handling image prompts
import config
from ollama import Client #for using ollama interfaces
from openai import OpenAI #for using open ai interfaces
from google import genai
from google.genai import types
from anthropic import Anthropic
import sys
import os 
from tavily import TavilyClient

###################################### Opening AI Tool Clients ##############################################
TAVILY_API_KEY      = "TavilyAPIKeyJson55" #Web search AI tool

# Ensure API key is set in your environment variables
tavily_api_key = os.getenv(TAVILY_API_KEY)
tavilyClient = TavilyClient(api_key=tavily_api_key)


def search_product_data_tavily_Flipkart (product_name: str) -> str:
    """
    Searches the e-commerce web for the product information using Tavily and returns consolidated raw text context.
    """
    print(f"🔍 Searching the web for: '{product_name}'...")
    
    # We construct a query targeted at e-commerce specifications and pricing
    search_query = f"site:flipkart.com {product_name} price"  

    response = tavilyClient.search(
        query=search_query,
        search_depth="advanced",
        max_results=3,
        include_raw_content=False,
        include_domains=["flipkart.com"]  
    )
    
    # Compile the snippets/content into a singular context block for Phi-4
    context_segments = []
    for result in response.get("results", []):
        context_segments.append(f"Source URL: {result['url']}\nTitle: {result['title']}\nContent: {result['content']}\n")
        
    return "\n---\n".join(context_segments)


def search_product_data_tavily_Amazon (product_name: str) -> str:
    """
    Searches the e-commerce web for the product information using Tavily and returns consolidated raw text context.
    """
    print(f"🔍 Searching the web for: '{product_name}'...")
    
    # We construct a query targeted at e-commerce specifications and pricing
    search_query = f"site:amazon.in {product_name} price"  

    response = tavilyClient.search(
        query=search_query,
        search_depth="advanced",
        max_results=3,
        include_raw_content=False,
        include_domains=["amazon.in"]  
    )
    
    # Compile the snippets/content into a singular context block for Phi-4
    context_segments = []
    for result in response.get("results", []):
        context_segments.append(f"Source URL: {result['url']}\nTitle: {result['title']}\nContent: {result['content']}\n")
        
    return "\n---\n".join(context_segments)

###################################### Opening AI Client ##############################################
ANTHROPIC_API_KEY = "dummy"
OPEN_AI_API_KEY = "OpenAIKey_Json55"
GEMINI_API_KEY = "GeminiAPIKey_Json55"

# Ensure API key is set in your environment variables
openai_api_key = os.getenv(OPEN_AI_API_KEY)
gemini_api_key = os.getenv(GEMINI_API_KEY)
anthropic_api_key = os.getenv(ANTHROPIC_API_KEY)

# Create client as per model configuration in Config.py
if config.MODEL_USED == config.MODEL_DICT["Openai"]:
    # Initialize the client
    client = OpenAI(api_key=openai_api_key)
    """
    # Code to get list of OpenAI models
    # OpenAI models are returned as a list in the 'data' attribute
    for m in client.models.list():
        # Typically we filter by 'gpt' or 'o1' to find generative models
        if "gpt" in m.id or "o1" in m.id:
            print(f"OpenAI Model: {m.id}")
    """            
    
elif config.MODEL_USED ==  config.MODEL_DICT["Gemini"]:
    # Initialize the client
    client = genai.Client(api_key=gemini_api_key)
    """
    # Code to get list of gemini models
    for m in client.models.list():
        # Check if ANY of the actions contain the word 'generate'
        if any('generate' in action for action in m.supported_actions):
            print(f" {m.display_name} ({m.name})")
    """

elif config.MODEL_USED ==  config.MODEL_DICT["Anthropic"]:
    # Initialize the client
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    """
    # Code to get list of anthropic models
    # Anthropic returns a 'data' list containing Model objects
    for m in client.models.list():
        # In 2026, we check the 'capabilities' object
        # This checks if the model supports standard message generation
        if getattr(m, 'capabilities', None) and m.capabilities.messages:
            print(f" Anthropic Model: {m.display_name} ({m.id})")
    """
    
elif config.MODEL_USED ==  config.MODEL_DICT["Ollama"]:
    # Initialize the client
    client = Client(host='http://localhost:11434')
    # List all installed models
    models = client.list()
    # get available model names
    for model in models['models']:
        config.ollama_models.append(model.model)

else:
    print(f"model configured {config.MODEL_USED} is not in list {config.MODEL_DICT}")    

###################################### Define functions for using AI CLient ##############################################

def list_available_models_from_vendor():
    if config.MODEL_USED == config.MODEL_DICT["Openai"]:
        # Code to get list of OpenAI models
        # OpenAI models are returned as a list in the 'data' attribute
        for m in client.models.list():
            # Typically we filter by 'gpt' or 'o1' to find generative models
            if "gpt" in m.id or "o1" in m.id:
                print(f" OpenAI Model: {m.id}")          
    
    elif config.MODEL_USED ==  config.MODEL_DICT["Gemini"]:
        # Code to get list of gemini models
        for m in client.models.list():
            # Check if ANY of the actions contain the word 'generate'
            if any('generate' in action for action in m.supported_actions):
                print(f" {m.display_name} ({m.name})")
    
    elif config.MODEL_USED ==  config.MODEL_DICT["Anthropic"]:
        # Code to get list of anthropic models
        # Anthropic returns a 'data' list containing Model objects
        for m in client.models.list():
            # In 2026, we check the 'capabilities' object
            # This checks if the model supports standard message generation
            if getattr(m, 'capabilities', None) and m.capabilities.messages:
                print(f" Anthropic Model: {m.display_name} ({m.id})")
        
    elif config.MODEL_USED ==  config.MODEL_DICT["Ollama"]:
            print("Internal list of ollama models populated")
            # print(config.ollama_models)
    
    else:
        print(f"model configured {config.MODEL_USED} is not in list {config.MODEL_DICT}")  


def allowed_model_use_check (model):
    if config.MODEL_USED == config.MODEL_DICT["Openai"]:
        for temp in config.openai_models:
            if temp == model:
                print(f"model {temp} usage is allowed")
                return "yes"
        print("model use not allowed, use a different model or update configuration python file")
        return "no"            
    
    elif config.MODEL_USED ==  config.MODEL_DICT["Gemini"]:
        for temp in config.gemini_models:
            if temp == model:
                print(f"model {temp} usage is allowed")
                return "yes"
        print("model use not allowed, use a different model or update configuration python file")
        return "no" 
    
    elif config.MODEL_USED ==  config.MODEL_DICT["Anthropic"]:
        for temp in config.anthropic_models:
            if temp == model:
                print(f"model {temp} usage is allowed")
                return "yes"
        print("model use not allowed, use a different model or update configuration python file")
        return "no"  
        
    elif config.MODEL_USED ==  config.MODEL_DICT["Ollama"]:
        for temp in config.ollama_models:
            if temp == model:
                print(f"model {temp} usage is allowed")
                return "yes"
        print("model use not allowed, use a different model or update configuration python file")
        return "no" 
    else:
        print(f"model configured {config.MODEL_USED} is not in list {config.MODEL_DICT}")  

#initialize prompt message buffer
def init_promptbuffer():
    messages = []
    messages.append({"role": "system", "content": ""})

# Function to test if the model can be accesed to get a response for a prompt
def get_response(model: str, prompt: str) -> str:
    #Check if the needed model is allowed for use
    allowed_model_use_check (model)
    #Get the response from the model 
    return get_response_format(model, prompt)
    
#Function for handling only text prompts
def get_response_format(model: str, prompt: str) -> str:

    if config.MODEL_USED == config.MODEL_DICT["Openai"]:
        # OpenAI response format
        response = client.responses.create(
            model=model,
            input=prompt,
        )
        return response.output_text

    elif config.MODEL_USED == config.MODEL_DICT["Gemini"]:
        # Gemini response format
        response = client.models.generate_content(
            model=model, 
            contents= prompt
            )
        return response.text
    
    elif config.MODEL_USED == config.MODEL_DICT["Ollama"]:
        # Ollama response format
        response = client.chat(
            model=model,
            messages=[
                {'role': 'user', 'content': prompt},
            ]
        )
        return response['message']['content']
    
    else:
        print(f"no call function implemented for the model {model} or its vendor")

'''
#Function for handling image prompts
def image_gemini_call (model: str, prompt: str, img) -> str:

    #example for image input argument
    #img = Image.open('circuit_board.jpg')

    response = client.models.generate_content(
        model=model,
        contents=["What is the main microcontroller in this image?", img]
        )
    return response.text
'''

def tavily_access(model: str, prompt: str, tools):
    #Check if the needed model is allowed for use
    allowed_model_use_check (model)

    #Message for LLM in stage 1: Obtaining infomration from the e-commerce website
    messageLLM = [{'role': 'system', 'content': "You are an expert shopping assistant, provide at least one product which is an optimal recommendation from the list based on the user request. \
                   Use all tools which can access any e-commerce website\
                   Also return the website from which the produt was recommended as part of the response"},
                {'role': 'user', 'content': prompt}]
    
    #Message for tavilysearchTool in stage 2: Obtaining infomration from the e-commerce website
    messages = [{'role': 'user', 'content': prompt}]

    #Ask LLM which tool to be used
    response = client.chat(model=model, messages=messageLLM, tools=tools)

    if response.message.tool_calls:
        messages.append(response.message)

        for tool in response.message.tool_calls:
            print("A tool call was provided from LLM")
            if tool.function.name == 'search_product_data_tavily_Flipkart':  # matches registered name
                product_name = tool.function.arguments['product_name']  # matches schema
                tool_result = search_product_data_tavily_Flipkart(product_name)

                messages.append({
                    'role': 'tool',
                    'content': str(tool_result),
                    'name': tool.function.name
                })
            elif tool.function.name == 'search_product_data_tavily_Amazon':  # matches registered name
                product_name = tool.function.arguments['product_name']  # matches schema
                tool_result = search_product_data_tavily_Amazon(product_name)

                messages.append({
                    'role': 'tool',
                    'content': str(tool_result),
                    'name': tool.function.name
                })

        #Pass the tool information back to LLM
        final_response = client.chat(model=model, messages=messages)
        return final_response.message.content
    else:
        print("LLM could not decide if a tool is needed for this request")
        return response.message.content




if __name__ == '__main__':
    tools1 = [{
        'type': 'function',
        'function': {
            'name': 'tavily_web_search',
            'description': 'Look up the infomration from e-commerce webites based on user prompt.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'query': {
                        'type': 'string',
                        'description': 'The search query to look up from e-commerce webites',
                    },
                },
                'required': ['query'],
            },
        },
     }
    ]
    # Code for testing purposes
    prompt = "what day is it today?"
    # Tool functions check 
    #tools_list = [tavily_web_search]
    #print(tavily_access("qwen2.5-coder:7b", "what is the price of raspberry pi 5 in flipkart?", tools1))
    #print(tavily_access("phi4-mini:latest", "what is the price of raspberry pi 5 in flipkart?", tools1))

    #output = get_response("qwen2.5vl:latest", prompt)
    #print(output)