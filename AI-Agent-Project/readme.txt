Travel Planning Assistant - README
This project is a multi-agent system designed to assist users in planning their travels by providing essential recommendations and information. It integrates multiple APIs to gather data on travel dates, city information, weather forecasts, hotels, and currency exchange rates.

Features
Date Agent: Converts natural language date inputs (e.g., "next Saturday") into an exact date.

City Info Agent: Retrieves and summarizes information about a city (e.g., tourist attractions, culture) using SerpAPI.

Hotel Recommendations: Provides a list of hotels in the selected city using the Tavily API.

Weather Forecast: Fetches a 5-day weather forecast for the city using the OpenWeatherMap API.

Currency Exchange Rates: Retrieves the latest exchange rates for Turkish Lira (TRY) to other currencies using the ExchangeRate API.

Travel Plan: Generates a detailed travel plan using the above data, including suggestions for places to visit, clothing recommendations based on weather, and hotel suggestions.

Requirements
Python 3.x

Required Python libraries:

requests

langchain_ollama

langchain_core

langgraph

tavily

serpapi

json

re

dotenv

Setup

Don't forget to pull the Llama 3.2 model from Ollama

Install the required dependencies:

bash
Copy
pip install requests langchain_ollama langchain_core langgraph tavily serpapi python-dotenv
Create a .env file in the project root directory with the following content:

OPENWEATHER_API_KEY=your_openweathermap_api_key
TAVILY_API_KEY=your_tavily_api_key
SERPAPI_API_KEY=your_serpapi_api_key
EXCHANGERATE_API_KEY=your_exchangerate_api_key
Get API keys from the following services:

OpenWeatherMap API

Tavily API

SerpAPI (i created it in the bash with venv)

ExchangeRate API

How to Run
After setting up the environment and API keys, run the script:

bash
Copy
python main.py
Interact with the Assistant:

The assistant will ask for your travel date and preferred city.

It will provide weather forecasts, hotel suggestions, and exchange rates.

Finally, the assistant will generate a complete travel plan.

Notes
API keys should be stored in the .env file and loaded using the dotenv library for security.

This project can be easily extended to add more features, such as activity recommendations, local events, etc.

Enjoy planning your trip!