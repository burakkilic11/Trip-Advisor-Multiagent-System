# AI Travel Planning Assistant

This Python project is an AI-powered travel planning assistant that helps users generate a basic travel plan based on their desired travel date and destination city. It leverages a local LLM (Ollama with Llama 3.2), external APIs for real-time data (weather, hotels, city info, exchange rates), and LangGraph to orchestrate the workflow between different specialized agents.

## Overview

The assistant guides the user through a short conversation:

1.  It asks for the planned travel date in natural language (e.g., "next Saturday").
2.  It asks for the destination city.
3.  It then fetches relevant information:
    *   Summarized city highlights (using web search).
    *   Hotel suggestions (using web search).
    *   5-day weather forecast (using OpenWeatherMap API).
    *   Currency exchange rates (using ExchangeRate-API).
4.  Finally, it uses the LLM to synthesize all this information into a coherent travel plan suggestion, including attractions, weather-based clothing advice, hotel ideas, and currency tips.

## Features

*   **Natural Language Date Processing:** Converts user input like "next Monday" into a specific `dd/mm/yyyy` format using an LLM.
*   **City Information Summarization:** Uses SerpAPI for web searches and an LLM to provide a concise summary of the destination city's highlights.
*   **Hotel Recommendations:** Uses Tavily Search API to find relevant hotel information and pricing.
*   **Weather Forecast:** Fetches a 5-day weather forecast (specifically for 18:00 each day) using the OpenWeatherMap API.
*   **Currency Exchange Rates:** Retrieves current exchange rates based on TRY using the ExchangeRate-API.
*   **Agent-Based Workflow:** Uses LangGraph to manage the sequence and state between different specialized agents.
*   **Local LLM:** Powered by Ollama and the Llama 3.2 model, allowing for local execution without relying on cloud LLM providers (if Ollama is running locally).

## Architecture & How it Works

The project employs an agent-based architecture orchestrated by **LangGraph**. LangGraph defines a state machine where different "nodes" (agents or functions) process information and update the shared state (`MessagesState`).

1.  **Initialization (`START`):** The graph execution begins.
2.  **`date_agent`:**
    *   Prompts the user for the travel date.
    *   Uses the Ollama LLM (`llama3.2`) with a specific prompt to parse the natural language date input (relative to the current date) and convert it into `dd/mm/yyyy` format.
    *   Updates the state with the formatted date.
3.  **`city_info_agent`:**
    *   Prompts the user for the destination city.
    *   Stores the city name (Note: currently uses a global variable `city_name`).
    *   Uses `SerpAPIWrapper` to search the web for travel information about the city.
    *   Uses the Ollama LLM to summarize the search results into key highlights.
    *   Updates the state with the city information summary.
4.  **Helper Functions (Data Fetching):** Before the final recommendation, several helper functions are called *within* the `recommendation_agent` to gather necessary real-time data:
    *   `get_hotels()`: Queries the Tavily Search API for hotel details in the specified city.
    *   `get_5_day_forecast()`: Calls the OpenWeatherMap API for the city's weather forecast.
    *   `get_exchange_rate()`: Calls the ExchangeRate-API for currency conversion rates (base TRY).
5.  **`recommendation_agent`:**
    *   Retrieves the date and city info from the current state.
    *   Calls the helper functions mentioned above to get weather, hotel, and exchange rate data.
    *   Constructs a comprehensive prompt containing all gathered information (date, city summary, weather, hotels, exchange rates).
    *   Uses the Ollama LLM to generate the final travel plan based on the comprehensive prompt.
    *   Outputs the final plan to the console and updates the state.
6.  **Termination (`END`):** The graph execution finishes after the recommendation agent runs.

**State Management:** LangGraph's `MessagesState` is intended to pass information between nodes. In this implementation, while state is passed, some information (like `city_name`) is handled via user input within nodes or global variables, and data fetching happens directly within the `recommendation_agent` rather than being passed solely through the state from previous dedicated nodes.

## Setup

1.  **Clone the Repository:**
    ```bash
    git clone <your-repository-url>
    cd <your-repository-directory>
    ```
2.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3.  **Install Dependencies:**
    Create a `requirements.txt` file with the following content (or generate it using `pip freeze > requirements.txt` after installing manually):
    ```txt
    requests
    langchain-ollama
    langchain-core
    langchain-community
    langgraph
    python-dotenv
    tavily-python
    google-search-results # For SerpAPIWrapper
    ```
    Then install:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Install and Run Ollama:**
    *   Download and install Ollama from [https://ollama.com/](https://ollama.com/).
    *   Pull the Llama 3.2 model:
        ```bash
        ollama pull llama3.2
        ```
    *   Ensure the Ollama server is running in the background.

5.  **API Key Configuration:**
    *   Create a file named `.env` in the project's root directory.
    *   Add your API keys to this file:
        ```env
        OPENWEATHER_API_KEY="YOUR_OPENWEATHERMAP_API_KEY"
        TAVILY_API_KEY="YOUR_TAVILY_API_KEY"
        SERPAPI_API_KEY="YOUR_SERPAPI_API_KEY"
        EXCHANGERATE_API_KEY="YOUR_EXCHANGERATE_API_KEY"
        ```
    *   Replace the placeholder values with your actual keys. You can obtain keys from:
        *   OpenWeatherMap: [https://openweathermap.org/api](https://openweathermap.org/api)
        *   Tavily AI: [https://tavily.com/](https://tavily.com/)
        *   SerpAPI: [https://serpapi.com/](https://serpapi.com/)
        *   ExchangeRate-API: [https://www.exchangerate-api.com/](https://www.exchangerate-api.com/)
    *   **Important:** Add `.env` to your `.gitignore` file to avoid committing your secret keys.

## Usage

Ensure your Ollama server is running and the `.env` file is configured correctly. Then, run the Python script:

```bash
python your_script_name.py

(Replace your_script_name.py with the actual name of your Python file.)
The script will prompt you to enter the travel date and destination city in the console. After gathering the necessary information, it will print the generated travel plan to the console.
