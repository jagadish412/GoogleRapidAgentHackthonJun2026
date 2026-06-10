import config
import utils
from toolschemaGen import Tool, Parameter, generate_schema
import json

#For GUI code
import tkinter as tk
from tkinter import ttk
import threading
import time

# # Methods
# ## Using Tavily - Reccomended
# - You can use Tavily as a Tool that Gemini calls whenever it needs live price data.
# 
# ## Google search via Gemini
# - Use the "Grounding" Shortcut: If you don't want to code a scraper, simply enable the Google Search Tool in the Gemini API.
# 
# - Prompt: "Search Flipkart for the current price of [Product] and compare it with the last 3 reviews." Gemini will use Google to find the Flipkart page and read the info for you—no custom scraping required.
# 
# ## Webscarper
# ### Huge Risk!!!!
# - Avoid IP Bans: Flipkart has strict anti-bot measures. If your scraper fails after 5-10 tries, your IP is blocked.  
# 
# - Hackathon fix: Use a free-tier "Scraping API" like ScrapingDog or ZenRows. They handle the proxies and headers for you so you can focus on the AI.
# 

# # Create tools list
# 1. Get tool api access - Done in utils.py
# 2. Create tool function  - Done in utils.py
# 3. Create tool list for the AI agent


#Simple Prompt - for testing purpose only
#utils.get_response("phi4-mini:latest", prompt)

#list models - returns list based on the config.py
#list_available_models_from_vendor()

################################################### GUI CODE ####################################################

def log(message):
    """Append message to output box."""
    output_text.insert(tk.END, message + "\n")
    output_text.see(tk.END)


#Trigger Agent
def start_process():

    log("----------------------------------------")
    log(f"Chosen Model Vendor : {model_vendor_dropdown_var.get()}")
    log("----------------------------------------")


    model_vendor = model_vendor_dropdown_var.get()
    if use_custom_prompt.get():
        prompt = prompt_input.get("1.0", tk.END).strip()
    else:
        prompt = prompt_dropdown_var.get()
    
    log("----------------------------------------")
    log(f"Chosen Prompt : {prompt}")
    log("----------------------------------------")

    #output_text.delete(1.0, tk.END)

    tool_schema = create_tool_schema(model_vendor)

    #prompt to get information from e-commerce website using tavily
    if model_vendor == "Ollama":
        result = utils.tavily_access(config.OLLAMA_MODEL, prompt, tool_schema)
    elif model_vendor == "Openai":
        result = utils.tavily_access(config.OPEN_AI_MODEL, prompt, tool_schema)
    elif model_vendor == "Gemini":
        result = utils.tavily_access(config.GEMINI_MODEL, prompt, tool_schema)
    else:
        raise Exception(f"Unsupported model vendor: {model_vendor}")
    
    return result

def thread_worker():
    """Background thread worker."""

    try:
        result = start_process()

        root.after(
            0,
            lambda r=result: log("\n" + str(r))
        )

        root.after(
            0,
            lambda: log("\nProcess completed successfully.")
        )

    except Exception as e:

        error_msg = str(e)

        root.after(
            0,
            lambda msg=error_msg: log(f"\nERROR: {msg}")
        )

    finally:
        root.after(
            0,
            lambda: start_button.config(state="normal")
        )


def run():
    """Start button handler."""

    output_text.delete("1.0", tk.END)

    log("Starting process...")

    root.update_idletasks()
    start_button.config(state="disabled")

    threading.Thread(
        target=thread_worker,
        daemon=True
    ).start()

# ==========================================
# Close application
# ==========================================
def close_app():
    root.destroy()

########## tools list variable ###############################################
#Create tool schema from native format
def create_tool_schema (model):
    #Define tools in this format so that the lib file toolschemaGen can convert it to any format as per ollama, Gemini, openai.
    tools = [
        Tool(
            name="search_product_data_tavily_Flipkart",
            description="Search e-commerce website Flipkart for current product price, "
                        "specifications, and availability. Always search on flipkart.com only.",
            parameters=[
                Parameter(
                    name="product_name",
                    type="string",
                    description="The product name to search for on e-commerce sites like Flipkart",
                    required=True,
                )
            ],
        ),
        Tool(
            name="search_product_data_tavily_Amazon",
            description="Search e-commerce website Amazon for current product price, "
                        "specifications, and availability. Always search on Amazon.com only.",
            parameters=[
                Parameter(
                    name="product_name",
                    type="string",
                    description="The product name to search for on e-commerce sites like Amazon",
                    required=True,
                )
            ],
        )
        ]

    #generate tool schema as needed, model vendor argument can be "openai", "ollama", "anthropic", "gemini"

    tool_schema = generate_schema(config.MODEL_VENDOR_USED, tools) #Output: Type list
    return tool_schema



#Main window (Root)
root = tk.Tk()
root.title("Agentic Shopping Assistant")
root.geometry("1300x1000")

# Main container
frame = ttk.Frame(root, padding=10)
frame.pack(fill="both", expand=True)

################################################### Model selection dropdown ####################################################
############ Model label #############
ttk.Label(
    frame,
    text="Model:"
).pack(anchor="w")

############ Model dropdown box #############
model_vendor_dropdown_var = tk.StringVar()
model_vendor_dropdown = ttk.Combobox(
    frame,
    textvariable=model_vendor_dropdown_var,
    values=["Ollama", "Gemini", "OpenAI", "Anthropic"],
    state="readonly",
    width=40
)
model_vendor_dropdown.current(0)
model_vendor_dropdown.pack(anchor="w", pady=(0, 10))

################################################### Prompt Selection ####################################################
ttk.Label(
    frame,
    text="Prompt Selection:"
).pack(anchor="w")

############ prompt selection dropdown box #############
prompt_dropdown_var = tk.StringVar()
prompt_dropdown = ttk.Combobox(
    frame,
    textvariable=prompt_dropdown_var,
    values=[
                "Use the search tool to find the current price and discounts for any backpack on Flipkart and recommend the cheapest and best product for long treks on mountains. Only use results from flipkart.com.",
                "Use the search tool to find the current price and discounts for any backpack on Amazon and recommend the cheapest and best product for long treks on mountains. Only use results from amazon.in.",
                "Use the search tool to find the current price and discounts for any backpack on Amazon and Flipkart and recommend the cheapest and best product for long treks on mountains."
            ],
    state="readonly",
    width=180
)
prompt_dropdown.current(0)
prompt_dropdown.pack(anchor="w", pady=(0, 10))

####################### Custom prompt ####################
use_custom_prompt = tk.BooleanVar()

ttk.Checkbutton(
    frame,
    text="Use custom prompt",
    variable=use_custom_prompt
).pack(anchor="w")

ttk.Label(
    frame,
    text="Custom Prompt:"
).pack(anchor="w")

prompt_input = tk.Text(
    frame,
    height=2,
    width=100
)

prompt_input.pack(anchor="w", fill="x", pady=(0, 10))

####################################################  Buttons ######################################################## 

button_frame = ttk.Frame(frame)
button_frame.pack(anchor="w", pady=(0, 10))

############ Start button ##################
# Start button
start_button = ttk.Button(
    button_frame,
    text="Start",
    command=run
)
start_button.pack(side="left")

############ Close button ##################
close_button = ttk.Button(
    button_frame,
    text="Close",
    command=close_app
)

close_button.pack(
    side="left",
    padx=(10, 0)
)

############ Output box ##################
# Output label
ttk.Label(frame, text="Output:").pack(anchor="w")

# Output text box
output_text = tk.Text(
    frame,
    height=20,
    wrap="word"
)
output_text.pack(
    fill="both",
    expand=True
)

root.mainloop()


