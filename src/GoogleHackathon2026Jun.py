import config
import utils

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

########## tools list variable ###############################################
#function is define in utils.py library
tools = [{
    'type': 'function',
    'function': {
        'name': 'search_product_data_tavily_Flipkart',  # no namespace prefix
        'description': (
            'Search e-commerce website Flipkart for current product price, '
            'specifications, and availability. Always search on flipkart.com only.'
        ),
        'parameters': {
            'type': 'object',
            'properties': {
                'product_name': {          # matches actual function parameter
                    'type': 'string',
                    'description': 'The product name to search for on e-commerce sites like Flipkart',
                },
            },
            'required': ['product_name'],  # consistent
        },
    },
},
{
    'type': 'function',
    'function': {
        'name': 'search_product_data_tavily_Amazon',  # no namespace prefix
        'description': (
            'Search e-commerce website Amazon for current product price, '
            'specifications, and availability. Always search on Amazon.com only.'
        ),
        'parameters': {
            'type': 'object',
            'properties': {
                'product_name': {          # matches actual function parameter
                    'type': 'string',
                    'description': 'The product name to search for on e-commerce sites like Amazon',
                },
            },
            'required': ['product_name'],  # consistent
        },
    },
}
]




# # Getting responses from the AI client

#prompt = "Use the search tool to find the current price and discounts for any backpack on Flipkart and recommend the cheapest and best product for long treks on mountains. Only use results from flipkart.com."
#prompt = "Use the search tool to find the current price and discounts for any backpack on Amazon and recommend the cheapest and best product for long treks on mountains. Only use results from amazon.in."
#prompt = "Use the search tool to find the current price and discounts for any backpack on Amazon and Flipkart and recommend the cheapest and best product for long treks on mountains."
prompt = "Use the search tool to find the current price and discounts for a latest iphone on Amazon and Flipkart e-commerce websites and recommend the cheapest and best product."


#Simple Prompt
#utils.get_response("phi4-mini:latest", prompt)

#prompt to get information from e-commerce website using tavily
result = utils.tavily_access("qwen2.5:7b", prompt, tools)
print(result)


