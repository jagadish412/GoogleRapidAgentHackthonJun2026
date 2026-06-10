"""
Tool Schema Generator
Generates tool/function call schemas for OpenAI, Ollama, Anthropic, and Gemini
from a unified input format.
"""

from typing import Any
import json


# ─────────────────────────────────────────────
# Data types
# ─────────────────────────────────────────────

VALID_TYPES = {"string", "integer", "number", "boolean", "array", "object"}


class Parameter:
    def __init__(
        self,
        name: str,
        type: str,
        description: str,
        required: bool = False,
        enum: list[str] | None = None,
        items: dict | None = None,          # for array type
        properties: dict | None = None,     # for object type
    ):
        if type not in VALID_TYPES:
            raise ValueError(f"Invalid type '{type}' for parameter '{name}'. Must be one of {VALID_TYPES}")
        self.name = name
        self.type = type
        self.description = description
        self.required = required
        self.enum = enum
        self.items = items
        self.properties = properties


class Tool:
    def __init__(self, name: str, description: str, parameters: list[Parameter]):
        self.name = name
        self.description = description
        self.parameters = parameters


# ─────────────────────────────────────────────
# Shared helper: build JSON Schema for params
# ─────────────────────────────────────────────

def _build_json_schema(parameters: list[Parameter]) -> dict:
    """Build the JSON Schema 'parameters' block used by OpenAI / Ollama / Anthropic."""
    properties: dict[str, Any] = {}
    required: list[str] = []

    for param in parameters:
        schema: dict[str, Any] = {
            "type": param.type,
            "description": param.description,
        }
        if param.enum:
            schema["enum"] = param.enum
        if param.type == "array" and param.items:
            schema["items"] = param.items
        if param.type == "object" and param.properties:
            schema["properties"] = param.properties

        properties[param.name] = schema
        if param.required:
            required.append(param.name)

    result: dict[str, Any] = {
        "type": "object",
        "properties": properties,
    }
    if required:
        result["required"] = required
    return result


# ─────────────────────────────────────────────
# Provider-specific generators
# ─────────────────────────────────────────────

def generate_openai_schema(tools: list[Tool]) -> list[dict]:
    """
    OpenAI Responses API schema (client.responses.create).
    Tools are flat objects — no nested 'function' wrapper.
    Docs: https://platform.openai.com/docs/guides/tools
    """
    result = []
    for tool in tools:
        result.append({
            "type": "function",
            "name": tool.name,
            "description": tool.description,
            "parameters": _build_json_schema(tool.parameters),
        })
    return result


def generate_openai_chat_schema(tools: list[Tool]) -> list[dict]:
    """
    OpenAI Chat Completions API schema (client.chat.completions.create).
    Tools are nested under a 'function' key.
    Docs: https://platform.openai.com/docs/guides/function-calling
    """
    result = []
    for tool in tools:
        result.append({
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": _build_json_schema(tool.parameters),
            },
        })
    return result


def generate_ollama_schema(tools: list[Tool]) -> list[dict]:
    """
    Ollama schema — identical structure to OpenAI Chat Completions (Ollama follows the OpenAI spec).
    Docs: https://ollama.com/blog/tool-support
    """
    return generate_openai_chat_schema(tools)


def generate_anthropic_schema(tools: list[Tool]) -> list[dict]:
    """
    Anthropic (Claude) tool schema.
    Docs: https://docs.anthropic.com/en/docs/tool-use
    """
    result = []
    for tool in tools:
        result.append({
            "name": tool.name,
            "description": tool.description,
            "input_schema": _build_json_schema(tool.parameters),
        })
    return result


def _to_gemini_type(json_type: str) -> str:
    """Map JSON Schema types to Gemini Type enum strings."""
    mapping = {
        "string": "STRING",
        "integer": "INTEGER",
        "number": "NUMBER",
        "boolean": "BOOLEAN",
        "array": "ARRAY",
        "object": "OBJECT",
    }
    return mapping.get(json_type, "STRING")


def _build_gemini_properties(parameters: list[Parameter]) -> dict:
    """Recursively build Gemini-style parameter schema."""
    properties: dict[str, Any] = {}
    required: list[str] = []

    for param in parameters:
        schema: dict[str, Any] = {
            "type": _to_gemini_type(param.type),
            "description": param.description,
        }
        if param.enum:
            schema["enum"] = param.enum
        if param.type == "array" and param.items:
            schema["items"] = {"type": _to_gemini_type(param.items.get("type", "string"))}
        if param.type == "object" and param.properties:
            schema["properties"] = param.properties

        properties[param.name] = schema
        if param.required:
            required.append(param.name)

    result: dict[str, Any] = {"properties": properties}
    if required:
        result["required"] = required
    return result


def generate_gemini_schema(tools: list[Tool]) -> list[dict]:
    """
    Google Gemini function declaration schema.
    Docs: https://ai.google.dev/gemini-api/docs/function-calling
    """
    declarations = []
    for tool in tools:
        declarations.append({
            "name": tool.name,
            "description": tool.description,
            "parameters": {
                "type": "OBJECT",
                **_build_gemini_properties(tool.parameters),
            },
        })
    return [{"function_declarations": declarations}]


# ─────────────────────────────────────────────
# Main dispatcher
# ─────────────────────────────────────────────

PROVIDERS = {
    # OpenAI Responses API  — client.responses.create  (flat, no inner function wrapper)
    "openai": generate_openai_schema,
    # OpenAI Chat Completions — client.chat.completions.create  (nested function key)
    "openai_chat": generate_openai_chat_schema,
    "ollama": generate_ollama_schema,
    "anthropic": generate_anthropic_schema,
    "gemini": generate_gemini_schema,
}


def generate_schema(provider: str, tools: list[Tool]) -> list[dict]:
    """
    Generate tool schema for the specified provider.

    Args:
        provider:  One of the following (case-insensitive):
                     'openai'      -> OpenAI Responses API  (client.responses.create)
                     'openai_chat' -> OpenAI Chat Completions (client.chat.completions.create)
                     'ollama'      -> Ollama (mirrors openai_chat format)
                     'anthropic'   -> Anthropic / Claude
                     'gemini'      -> Google Gemini
        tools:     List of Tool objects describing your functions.

    Returns:
        A list of dicts ready to be passed as the `tools` argument to the provider's SDK.

    Raises:
        ValueError: If the provider is not supported.
    """
    key = provider.strip().lower()
    if key not in PROVIDERS:
        raise ValueError(
            f"Unsupported provider '{provider}'. Choose from: {', '.join(PROVIDERS)}"
        )
    return PROVIDERS[key](tools)


# ─────────────────────────────────────────────
# Example / demo
# ─────────────────────────────────────────────

if __name__ == "__main__":
    #Only for testing purpose
    # Define some example tools
    tools = [
        Tool(
            name="get_weather",
            description="Get the current weather for a given location.",
            parameters=[
                Parameter(
                    name="location",
                    type="string",
                    description="City and country, e.g. 'London, UK'",
                    required=True,
                ),
                Parameter(
                    name="unit",
                    type="string",
                    description="Temperature unit",
                    required=False,
                    enum=["celsius", "fahrenheit"],
                ),
            ],
        ),
        Tool(
            name="search_web",
            description="Search the internet and return top results.",
            parameters=[
                Parameter(
                    name="query",
                    type="string",
                    description="The search query string",
                    required=True,
                ),
                Parameter(
                    name="max_results",
                    type="integer",
                    description="Maximum number of results to return (default 5)",
                    required=False,
                ),
                Parameter(
                    name="domains",
                    type="array",
                    description="Restrict search to these domains",
                    required=False,
                    items={"type": "string"},
                ),
            ],
        ),
        Tool(
            name="send_email",
            description="Send an email to one or more recipients.",
            parameters=[
                Parameter(
                    name="to",
                    type="array",
                    description="List of recipient email addresses",
                    required=True,
                    items={"type": "string"},
                ),
                Parameter(
                    name="subject",
                    type="string",
                    description="Email subject line",
                    required=True,
                ),
                Parameter(
                    name="body",
                    type="string",
                    description="Plain-text body of the email",
                    required=True,
                ),
                Parameter(
                    name="cc",
                    type="array",
                    description="Optional CC recipients",
                    required=False,
                    items={"type": "string"},
                ),
            ],
        ),
    ]

    providers = ["openai", "openai_chat", "ollama", "anthropic", "gemini"]

    for provider in providers:
        print(f"\n{'='*60}")
        print(f"  {provider.upper()} SCHEMA")
        print(f"{'='*60}")
        schema = generate_schema(provider, tools)
        print(json.dumps(schema, indent=2))