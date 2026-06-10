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
import json

###################################### Opening AI Tool Clients ##############################################
# Ensure API key is set in your environment variables
tavily_api_key = os.getenv(config.TAVILY_API_KEY)
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


# Ensure API key is set in your environment variables
openai_api_key = os.getenv(config.OPEN_AI_API_KEY)
gemini_api_key = os.getenv(config.GEMINI_API_KEY)
anthropic_api_key = os.getenv(config.ANTHROPIC_API_KEY)

# Create client as per model configuration in Config.py
if config.MODEL_VENDOR_USED == config.MODEL_VENDOR_DICT["Openai"]:
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
    
elif config.MODEL_VENDOR_USED ==  config.MODEL_VENDOR_DICT["Gemini"]:
    # Initialize the client
    client = genai.Client(api_key=gemini_api_key)
    """
    # Code to get list of gemini models
    for m in client.models.list():
        # Check if ANY of the actions contain the word 'generate'
        if any('generate' in action for action in m.supported_actions):
            print(f" {m.display_name} ({m.name})")
    """

elif config.MODEL_VENDOR_USED ==  config.MODEL_VENDOR_DICT["Anthropic"]:
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
    
elif config.MODEL_VENDOR_USED ==  config.MODEL_VENDOR_DICT["Ollama"]:
    # Initialize the client
    client = Client(host='http://localhost:11434')
    # List all installed models
    models = client.list()
    # get available model names
    for model in models['models']:
        config.ollama_models.append(model.model)

else:
    print(f"model configured {config.MODEL_VENDOR_USED} is not in list {config.MODEL_VENDOR_DICT}")    

###################################### Define functions for using AI CLient ##############################################

def list_available_models_from_vendor():
    if config.MODEL_VENDOR_USED == config.MODEL_VENDOR_DICT["Openai"]:
        # Code to get list of OpenAI models
        # OpenAI models are returned as a list in the 'data' attribute
        for m in client.models.list():
            # Typically we filter by 'gpt' or 'o1' to find generative models
            if "gpt" in m.id or "o1" in m.id:
                print(f" OpenAI Model: {m.id}")          
    
    elif config.MODEL_VENDOR_USED ==  config.MODEL_VENDOR_DICT["Gemini"]:
        # Code to get list of gemini models
        for m in client.models.list():
            # Check if ANY of the actions contain the word 'generate'
            if any('generate' in action for action in m.supported_actions):
                print(f" {m.display_name} ({m.name})")
    
    elif config.MODEL_VENDOR_USED ==  config.MODEL_VENDOR_DICT["Anthropic"]:
        # Code to get list of anthropic models
        # Anthropic returns a 'data' list containing Model objects
        for m in client.models.list():
            # In 2026, we check the 'capabilities' object
            # This checks if the model supports standard message generation
            if getattr(m, 'capabilities', None) and m.capabilities.messages:
                print(f" Anthropic Model: {m.display_name} ({m.id})")
        
    elif config.MODEL_VENDOR_USED ==  config.MODEL_VENDOR_DICT["Ollama"]:
            print("Internal list of ollama models populated")
            # print(config.ollama_models)
    
    else:
        print(f"model configured {config.MODEL_VENDOR_USED} is not in list {config.MODEL_VENDOR_DICT}")  


def allowed_model_use_check (model):
    if config.MODEL_VENDOR_USED == config.MODEL_VENDOR_DICT["Openai"]:
        for temp in config.openai_models:
            if temp == model:
                print(f"model {temp} usage is allowed")
                return "yes"
        print("model use not allowed, use a different model or update configuration python file")
        return "no"            
    
    elif config.MODEL_VENDOR_USED ==  config.MODEL_VENDOR_DICT["Gemini"]:
        for temp in config.gemini_models:
            if temp == model:
                print(f"model {temp} usage is allowed")
                return "yes"
        print("model use not allowed, use a different model or update configuration python file")
        return "no" 
    
    elif config.MODEL_VENDOR_USED ==  config.MODEL_VENDOR_DICT["Anthropic"]:
        for temp in config.anthropic_models:
            if temp == model:
                print(f"model {temp} usage is allowed")
                return "yes"
        print("model use not allowed, use a different model or update configuration python file")
        return "no"  
        
    elif config.MODEL_VENDOR_USED ==  config.MODEL_VENDOR_DICT["Ollama"]:
        for temp in config.ollama_models:
            if temp == model:
                print(f"model {temp} usage is allowed")
                return "yes"
        print("model use not allowed, use a different model or update configuration python file")
        return "no" 
    else:
        print(f"model configured {config.MODEL_VENDOR_USED} is not in list {config.MODEL_VENDOR_DICT}")  

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
def get_response_format(model: str, messages, **prompts) -> str:

    # Frame the prompt
    if ((prompts.get("system_prompt")) and (prompts.get("user_prompt"))):
            #Message for LLM in stage 1: Obtaining infomration from the e-commerce website
            message = [{'role': 'system', 'content': prompts.get("system_prompt")},
                        {'role': 'user', 'content': prompts.get("user_prompt")}]
    elif (prompts.get("user_prompt")):
        message = [{'role': 'user', 'content': prompts.get("user_prompt")}]
    else:
        print("ERROR!: niether user nor system prompt were specified")
        return ""
    
    if config.MODEL_VENDOR_USED == config.MODEL_VENDOR_DICT["Openai"]:
        # OpenAI response format
        response = client.responses.create(
            model=model,
            input=messages,
        )
        return response.output_text

    elif config.MODEL_VENDOR_USED == config.MODEL_VENDOR_DICT["Gemini"]:
        # Gemini response format
        response = client.models.generate_content(
            model=model, 
            contents= messages
            )
        return response.text
    
    elif config.MODEL_VENDOR_USED == config.MODEL_VENDOR_DICT["Ollama"]:
        # Ollama response format
        response = client.chat(
            model=model,
            messages= messages
        )
        return response['message']['content']
    
    else:
        print(f"no call function implemented for the model {model} or its vendor")

class tool_class_generic:
    #Function for handling only text prompts
    def get_response_tools_format(model: str, tools, **prompts) -> str:

        if ((prompts.get("system_prompt")) and (prompts.get("user_prompt"))):
            #Message for LLM in stage 1: Obtaining infomration from the e-commerce website
            messages = [{'role': 'system', 'content': prompts.get("system_prompt")},
                        {'role': 'user', 'content': prompts.get("user_prompt")}]
        elif (prompts.get("user_prompt")):
            messages = [{'role': 'user', 'content': prompts.get("user_prompt")}]
        else:
            print("ERROR!: niether user nor system prompt were specified")
            return ""
        
        #Message for tavilysearchTool in stage 2: Obtaining infomration from the e-commerce website
        messages = [{'role': 'user', 'content': prompts.get("user_prompt")}]
        
        if config.MODEL_VENDOR_USED == config.MODEL_VENDOR_DICT["Openai"]:
            # OpenAI response format
            response = client.responses.create(
                model=model,
                input=messages,
                tools=tools
            )
            return response

        elif config.MODEL_VENDOR_USED == config.MODEL_VENDOR_DICT["Gemini"]:
            # Gemini response format
            response = client.models.generate_content(
                model=model, 
                contents=  prompts.get("user_prompt"),
                config=types.GenerateContentConfig(
                        system_instruction=prompts.get("system_prompt"),
                        tools=tools
                    )
                )
            return response
        
        elif config.MODEL_VENDOR_USED == config.MODEL_VENDOR_DICT["Ollama"]:
            # Ollama response format
            response = client.chat(
                model=model,
                messages=messages,
                tools=tools
            )
            return response
        
        else:
            print(f"no call function implemented for the model {model} or its vendor")

    def validtoolcall (response):
        if (config.MODEL_VENDOR_USED == config.MODEL_VENDOR_DICT["Ollama"]) and (response.message.tool_calls):
            valid_call = True
        elif (config.MODEL_VENDOR_USED == config.MODEL_VENDOR_DICT["Openai"]) and (response.tool_calls):
            valid_call = True
        else:
            valid_call = False
        return valid_call    
        
    def gettoollist (response):
        if (config.MODEL_VENDOR_USED == config.MODEL_VENDOR_DICT["Ollama"]):
            tool_list = response.message.tool_calls
        elif (config.MODEL_VENDOR_USED == config.MODEL_VENDOR_DICT["Openai"]):
            tool_list = response.tool_calls
        else:
            tool_list = False
        return tool_list  

    def gettoolname (tool):
        if (config.MODEL_VENDOR_USED == config.MODEL_VENDOR_DICT["Ollama"]):
            tool_name = tool.function.name
        elif (config.MODEL_VENDOR_USED == config.MODEL_VENDOR_DICT["Openai"]):
            tool_name = tool.function.name
        else:
            tool_name = False
        return tool_name  

    def gettoolargumentvalue (tool, argument):
        if (config.MODEL_VENDOR_USED == config.MODEL_VENDOR_DICT["Ollama"]):
            tool_name = tool.function.arguments[argument]
        elif (config.MODEL_VENDOR_USED == config.MODEL_VENDOR_DICT["Openai"]):
            tool_name = tool.function.name
        else:
            tool_name = False
        return tool_name  

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

    #To expose functions available for handling tools
    toolClass = tool_class_generic
    
    #System prompt to define role and use case
    system_Prompt = ("You are an expert shopping assistant, provide at least one product which is an optimal recommendation from the list based on the user request."
                   "Use all tools which can access any e-commerce website"
                   "Also return the website from which the produt was recommended as part of the response")
    
    # Prompt requested by the user
    user_prompt = prompt
    
    #Message for tavilysearchTool in stage 2: Obtaining infomration from the e-commerce website
    messages = [{'role': 'user', 'content': user_prompt}]

    print("Asking LLM which tool to be used")
    #Ask LLM which tool to be used
    response = toolClass.get_response_tools_format(model=model, tools=tools, system_Prompt = system_Prompt, user_prompt = user_prompt)

    if toolClass.validtoolcall(response):
        
        messages.append(response.message)
        print("A tool call was provided from LLM")

        for tool in toolClass.gettoollist(response):    
            if toolClass.gettoolname(tool) == 'search_product_data_tavily_Flipkart':  # matches registered name
                product_name = toolClass.gettoolargumentvalue(tool, 'product_name')  # matches schema
                tool_result = search_product_data_tavily_Flipkart(product_name)

                messages.append({
                    'role': 'tool',
                    'content': str(tool_result),
                    'name': toolClass.gettoolname(tool)
                })
            elif toolClass.gettoolname(tool) == 'search_product_data_tavily_Amazon':  # matches registered name
                product_name = toolClass.gettoolargumentvalue(tool, 'product_name')  # matches schema
                tool_result = search_product_data_tavily_Amazon(product_name)

                messages.append({
                    'role': 'tool',
                    'content': str(tool_result),
                    'name': toolClass.gettoolname(tool)
                })

        #Pass the tool information back to LLM
        print(f"Processing tool results with LLM with the message")
        final_response = client.chat(model=model, messages=messages)
        
        #final_response = get_response_format(model=model, messages=messages)
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