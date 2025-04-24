import requests
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatMessagePromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities import SerpAPIWrapper
from langgraph.graph import StateGraph, MessagesState, START, END
from datetime import datetime
from tavily import TavilyClient
import json
import re
import os

from dotenv import load_dotenv

# .env dosyasındaki çevresel değişkenleri yükle
load_dotenv()

# API anahtarlarını environment variables'dan al
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
EXCHANGERATE_API_KEY = os.getenv("EXCHANGERATE_API_KEY")

# =======================
# 1. Environment & Models
# =======================
model = OllamaLLM(model="llama3.2")

# =======================
# 2. DATE AGENT
# =======================


def date_agent(state: MessagesState):
    user_input_date = input("📅 When are you planning to travel? (e.g., next Saturday): ")
    current_dt = datetime.now()
    today_str = current_dt.strftime("%d/%m/%Y")
    today_weekday = current_dt.strftime("%A")

    date_template = """
    You are an expert assistant that converts natural language date inputs into a concrete date format (dd/mm/yyyy).

    ----------------------------------------
    Here are some examples:

    user: Next saturday
    system: 05/04/2025

    user: Next monday
    system: 07/04/2025

    user: Next wednesday
    system: 09/04/2025
    ---------------------------------------

    Today is {today_str}, and it is a {today_weekday}.

    Given this information, convert the following date expression to its actual date:

    Natural language input: "{user_input_date}"

    Output format: "dd/mm/yyyy"
    """
    date_prompt = ChatPromptTemplate.from_template(date_template)
    date_chain = date_prompt | model

    # Invoke the date chain
    result = date_chain.invoke({
        "user_input_date": user_input_date,
        "today_str": today_str,
        "today_weekday": today_weekday,
    })

    # Look for the date in the result
    date_pattern = r'\b\d{2}/\d{2}/\d{4}\b'
    last_found_date = None

    for match in re.finditer(date_pattern, result):
        last_found_date = match.group(0)

    print(last_found_date)

    if last_found_date:
        # Update the message with the found date
        print(f"Updated travel date to: {last_found_date}")  # Debugging line
        return {"messages": HumanMessage(content=last_found_date)}
    
    else:
        # If no date is found, return the original message
        return {"messages": [state["messages"][0].content]}

# =======================
# 3. CITY INFO AGENT (SerpAPI)
# =======================
search = SerpAPIWrapper()

city_template = """
You are a travel assistant. Based on the following search results, summarize the main highlights of the city "{city_name}".

Include historical places, cultural attractions, and popular locations. Limit it to 4-5 sentences.

Search Results:
{search_results}
"""
city_prompt = ChatPromptTemplate.from_template(city_template)
city_chain = city_prompt | model

def city_info_agent(state: MessagesState):
    user_input_city = input("🌍 Which city would you like to visit?: ")
    # Şehir ismini dışarıda bir değişkende tutuyoruz
    global city_name
    city_name = user_input_city  # Şehir ismini global değişkene atıyoruz
    search_results = search.run(f"{user_input_city} travel guide tourist attractions")
    result = city_chain.invoke({
        "city_name": user_input_city,
        "search_results": search_results
    })

    updated_messages = [
        state["messages"][0],
        HumanMessage(content=str(result))  # model çıktısını HumanMessage olarak ekliyoruz
    ]

    return {"messages": updated_messages}

# =======================
# 4. Fetch Hotel Data Using Tavily API
# =======================
from tavily import TavilyClient

tavily_tool = TavilyClient(api_key= TAVILY_API_KEY)

def get_hotels(city_name):
    try:
        tavily_results = tavily_tool.search(f"{city_name} best hotels and prices")
        
        hotel_info = json.dumps(tavily_results.get('results', []), indent=4)
        
        hotel_string = ""
        for hotel in tavily_results.get('results', []):
            title = hotel.get('title', 'No title available')
            url = hotel.get('url', 'No URL available')
            content = hotel.get('content', 'No description available')
            score = hotel.get('score', 'No score available')

            hotel_string += f"Title: {title}\nURL: {url}\nDescription: {content}\nScore: {score}\n\n"
        
        return hotel_string

    except Exception as e:
        return f"Error: {str(e)}"

# =======================
# 5. Fetch Weather Forecast Using OpenWeatherMap API (Updated)
# =======================
def get_weather(city_name):
    # OpenWeatherMap API URL
    base_url = "http://api.openweathermap.org/data/2.5/forecast"
    
    # Şehir ismi ile API URL'yi oluştur
    url = f"{base_url}?q={city_name}&appid={OPENWEATHER_API_KEY}&units=metric"

    # API'ye istek gönder
    response = requests.get(url)
    data = response.json()

    return data

def get_5_day_forecast(city_name):
    weather_data = get_weather(city_name)
    
    # Hava durumu verisi kontrolü
    if 'list' in weather_data:
        forecast_data = []
        
        # Saat 18:00'deki tahmin verilerini al
        for forecast in weather_data['list']:
            dt_txt = forecast['dt_txt']  # Tarih ve saat
            if "18:00:00" in dt_txt:  # Yalnızca saat 18:00 verisini al
                temp = forecast['main']['temp']  # Sıcaklık
                description = forecast['weather'][0]['description']  # Hava durumu açıklaması
                forecast_data.append(f"{dt_txt}: {temp}°C, {description}")
                
                if len(forecast_data) >= 5:  # İlk 5 günün verisi
                    break

        # Veriyi string formatına dönüştürme
        return "\n".join(forecast_data)  # Listeden string'e dönüşüm
    else:
        return "Couldn't fetch weather data."


# =======================
# 6. ExchangeRate API 
# =======================
def get_exchange_rate(base_currency="TRY"):
    # API URL (ExchangeRate-API)
    api_key = EXCHANGERATE_API_KEY 
  # Buraya kendi API anahtarınızı girin
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{base_currency}"

    try:
        # API'ye istek gönder
        response = requests.get(url)
        data = response.json()

        # Döviz kuru verilerini al
        if data["result"] == "success":
            # Veriyi JSON formatında string'e dönüştürme
            return json.dumps(data["conversion_rates"], indent=4)
        else:
            return "Error: Unable to fetch exchange rates."
    except Exception as e:
        return f"Error: {str(e)}"
    
# =======================
# 7. TRAVEL PLAN AGENT (Recommendation Agent)
# =======================
# =======================
# 7. TRAVEL PLAN AGENT (Recommendation Agent)
# =======================
def recommendation_agent(state: MessagesState):
    # Get user inputs from the messages
    travel_date = state["messages"][0].content  # Travel date from date agent
    city_info = state["messages"][1].content

    # Get the other required data (weather, hotel, exchange rates) inside the function
    weather_forecast = get_5_day_forecast(city_name)  # Get the weather forecast for the city
    hotel_info = get_hotels(city_name)  # Get hotel recommendations for the city
    exchange_rates = get_exchange_rate()  # Get exchange rates (assuming base currency is TRY)

    # Seyahat planı oluşturuluyor
    recommendation_template = """
    You are a travel assistant that helps users create a complete travel plan.
    
    The user has provided the following information:
    
    - Travel Date: {travel_date}
    - City: {city_name}, {city_info}
    - Weather Forecast (18:00) for the next days: {weather_forecast}
    - Hotels in the city: {hotel_info}
    - Currency Exchange Rates (TRY to other currencies): {exchange_rates}
    
    Using this information, create a detailed travel plan for the user. Include:
    - A general overview of the city, including top attractions and culture.
    - Suggestions for places to visit and clothing reccomendation based on the given weather forecast.
    - Hotel suggestions based on budget and location.
    - Currency exchange tips to help with budgeting for the trip.(GBP)"""
    
    recommendation_prompt = ChatPromptTemplate.from_template(recommendation_template)
    recommendation_chain = recommendation_prompt | model

    # Seyahat planını oluşturmak için Llama 3.2 modelini çağır
    prompt_data = {
        "travel_date": travel_date,
        "city_name": city_name,
        "city_info": city_info,
        "weather_forecast": weather_forecast,
        "hotel_info": hotel_info,
        "exchange_rates": exchange_rates
    }

    result = recommendation_chain.invoke(prompt_data)
    # Burada sonucu ekrana yazdırıyoruz
    print(f"Generated Travel Plan:\n{result}")
    return {"messages": [result]}

# =======================
# 8. LangGraph Workflow
# =======================
builder = StateGraph(MessagesState)

builder.add_node("date_agent", date_agent)
builder.add_node("city_info_agent", city_info_agent)
builder.add_node("recommendation_agent", recommendation_agent)  # Add recommendation agent

# Start both agents
# İlk adımlar: tarih ve şehir bilgisi alınsın
builder.add_edge(START, "date_agent")
builder.add_edge("date_agent", "city_info_agent")  # date'ten sonra city

# City'den sonra recommendation gelsin
builder.add_edge("city_info_agent", "recommendation_agent")

# Son
builder.add_edge("recommendation_agent", END)

graph = builder.compile()

# =======================
# 9. Get User Input and Fetch Travel Plan Data
# =======================
# Get user inputs for travel date and city
if __name__ == "__main__":
    # Başlangıç mesajlarını ayarlıyoruz. Bu boş olabilir çünkü inputları fonksiyonlar içinde alıyorsun.
    initial_state = {"messages": []}
    
    graph.invoke(initial_state)

    
