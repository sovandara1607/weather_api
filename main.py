# main.py
from weather_client import WeatherClient
from config import Config
import sys

def display_current_weather(weather_data: dict):
    """Display current weather information"""
    print("\n" + "="*50)
    print(f"Weather in {weather_data['city']}, {weather_data['country']}")
    print("="*50)
    print(f"Temperature: {weather_data['temperature']}°C")
    print(f"Feels like: {weather_data['feels_like']}°C")
    print(f"Condition: {weather_data['description'].title()}")
    print(f"Humidity: {weather_data['humidity']}%")
    print(f"Pressure: {weather_data['pressure']} hPa")
    print(f"Wind Speed: {weather_data['wind_speed']} m/s")
    print(f"Visibility: {weather_data['visibility']} meters")
    print(f"Last updated: {weather_data['timestamp']}")
    print("="*50)

def display_forecast(forecast_data: list):
    """Display weather forecast"""
    print("\n" + "="*50)
    print("5-Day Weather Forecast")
    print("="*50)
    
    for forecast in forecast_data:
        print(f"\n{forecast['datetime'].strftime('%Y-%m-%d %H:%M')}")
        print(f"  Temperature: {forecast['temperature']}°C")
        print(f"  Condition: {forecast['description'].title()}")
        print(f"  Humidity: {forecast['humidity']}%")
        print(f"  Wind: {forecast['wind_speed']} m/s")

def main():
    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)
    
    # Initialize weather client
    weather_client = WeatherClient()
    
    while True:
        print("\nWeather App Menu:")
        print("1. Get current weather by city")
        print("2. Get current weather by coordinates")
        print("3. Get 5-day forecast")
        print("4. Search for cities")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        try:
            if choice == '1':
                city = input("Enter city name: ").strip()
                country = input("Enter country code (optional, e.g., US): ").strip()
                
                weather_data = weather_client.get_current_weather(
                    city, 
                    country if country else None
                )
                display_current_weather(weather_data)
                
            elif choice == '2':
                lat = float(input("Enter latitude: "))
                lon = float(input("Enter longitude: "))
                
                weather_data = weather_client.get_weather_by_coordinates(lat, lon)
                display_current_weather(weather_data)
                
            elif choice == '3':
                city = input("Enter city name: ").strip()
                forecast_data = weather_client.get_forecast(city)
                display_forecast(forecast_data)
                
            elif choice == '4':
                query = input("Enter city name to search: ").strip()
                cities = weather_client.search_cities(query)
                
                if cities:
                    print("\nFound cities:")
                    for i, city in enumerate(cities, 1):
                        state_info = f", {city['state']}" if city.get('state') else ""
                        print(f"{i}. {city['name']}{state_info}, {city['country']}")
                else:
                    print("No cities found.")
                    
            elif choice == '5':
                print("Goodbye!")
                break
                
            else:
                print("Invalid choice. Please enter 1-5.")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()