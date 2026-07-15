"""
prompts.py
==========
MCP Prompt definitions for the Weather MCP Server.

Prompts are reusable, parameterized templates that an MCP client can surface
to a user (e.g. as slash-commands) to kick off a well-structured interaction
with the underlying LLM, informed by this server's tools and resources.

Prompts registered here:
    - weather_summary          -> a friendly, plain-language weather summary
    - travel_recommendation    -> travel-planning advice based on the forecast
    - clothing_recommendation  -> what to wear given current conditions
"""

from __future__ import annotations

from fastmcp import FastMCP
from fastmcp.prompts.prompt import PromptMessage, TextContent

from logging_config import get_logger

logger = get_logger(__name__)


def register_prompts(mcp: FastMCP) -> None:
    """Register all MCP prompt templates on the given FastMCP instance."""

    @mcp.prompt(
        name="weather_summary",
        description=(
            "Generate a friendly, plain-language summary of current weather "
            "conditions for a city, suitable for a quick daily briefing."
        ),
    )
    def weather_summary(city: str) -> PromptMessage:
        """
        Build a prompt asking for a concise, friendly weather summary.

        Args:
            city: The city to summarize weather for.
        """
        text = (
            f"You are a friendly weather assistant. Use the `get_current_weather` "
            f"tool to fetch the latest conditions for '{city}', then write a short, "
            f"conversational summary (3-5 sentences) covering: the current "
            f"temperature and how it feels, general conditions (sunny, rainy, "
            f"etc.), humidity, and wind. Keep the tone warm and easy to read, as "
            f"if giving a quick briefing to a friend before they start their day."
        )
        return PromptMessage(role="user", content=TextContent(type="text", text=text))

    @mcp.prompt(
        name="travel_recommendation",
        description=(
            "Generate travel planning advice for a trip to a city, based on the "
            "multi-day weather forecast (best days to go outdoors, what to plan "
            "around, etc.)."
        ),
    )
    def travel_recommendation(city: str, days: int = 3) -> PromptMessage:
        """
        Build a prompt asking for forecast-informed travel advice.

        Args:
            city: The destination city.
            days: Number of forecast days to consider (1-5).
        """
        text = (
            f"You are a helpful travel planning assistant. Use the "
            f"`get_weather_forecast` tool to fetch a {days}-day forecast for "
            f"'{city}', and use the `get_weather_alerts` tool to check for any "
            f"active weather warnings. Then provide travel recommendations "
            f"covering: which days look best for outdoor activities and "
            f"sightseeing, any days travelers should plan indoor alternatives "
            f"for, whether to pack rain gear or sun protection, and a call-out "
            f"of any active weather alerts travelers should be aware of. "
            f"Structure the answer with clear headings and keep it practical."
        )
        return PromptMessage(role="user", content=TextContent(type="text", text=text))

    @mcp.prompt(
        name="clothing_recommendation",
        description=(
            "Generate a practical clothing recommendation for a city based on "
            "current temperature, wind, and precipitation conditions."
        ),
    )
    def clothing_recommendation(city: str) -> PromptMessage:
        """
        Build a prompt asking for a clothing recommendation based on current
        conditions.

        Args:
            city: The city to base the clothing recommendation on.
        """
        text = (
            f"You are a practical style and weather assistant. Use the "
            f"`get_current_weather` tool to fetch current conditions for "
            f"'{city}', then recommend what to wear today. Consider "
            f"temperature and 'feels like' temperature, wind speed (does it "
            f"warrant a windbreaker?), precipitation or cloudiness (is an "
            f"umbrella or raincoat needed?), and humidity. Give a short, "
            f"numbered list of clothing items, and one sentence of overall "
            f"advice (e.g. 'layer up, it will warm up by afternoon')."
        )
        return PromptMessage(role="user", content=TextContent(type="text", text=text))

    logger.info(
        "Registered 3 MCP prompts: weather_summary, travel_recommendation, "
        "clothing_recommendation"
    )
