# weather_client.py
import requests
from typing import Dict, Optional, List
from datetime import datetime
from config import Config

class WeatherClient:
    def __init__(self):
        self.api_key = Config.OPENWEATHER_API_KEY
        self.base_url = Config.BASE_URL
        self.session = requests.Session()
        
    def _make_request(self, endpoint: str, params: Dict) -> Dict:
        """Make HTTP request to weather API with error handling"""
        params['appid'] = self.api_key
        params['units'] = 'metric'  # Use 'imperial' for Fahrenheit
        
        try:
            response = self.session.get(f"{self.base_url}/{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise Exception("Invalid API key")
            elif response.status_code == 404:
                raise Exception("Location not found")
            else:
                raise Exception(f"HTTP error: {e}")
        except requests.exceptions.ConnectionError:
            raise Exception("Connection error - check your internet connection")
        except requests.exceptions.Timeout:
            raise Exception("Request timed out")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")
    
    def get_current_weather(self, city: str, country_code: Optional[str] = None) -> Dict:
        """Get current weather for a city"""
        location = f"{city},{country_code}" if country_code else city
        params = {'q': location}
        
        data = self._make_request('weather', params)
        
        return {
            'city': data['name'],
            'country': data['sys']['country'],
            'temperature': data['main']['temp'],
            'feels_like': data['main']['feels_like'],
            'humidity': data['main']['humidity'],
            'pressure': data['main']['pressure'],
            'description': data['weather'][0]['description'],
            'wind_speed': data['wind']['speed'],
            'visibility': data.get('visibility', 0),
            'timestamp': datetime.fromtimestamp(data['dt'])
        }
    
    def get_weather_by_coordinates(self, lat: float, lon: float) -> Dict:
        """Get current weather by coordinates"""
        params = {'lat': lat, 'lon': lon}
        
        data = self._make_request('weather', params)
        
        return {
            'city': data['name'],
            'country': data['sys']['country'],
            'temperature': data['main']['temp'],
            'feels_like': data['main']['feels_like'],
            'humidity': data['main']['humidity'],
            'pressure': data['main']['pressure'],
            'description': data['weather'][0]['description'],
            'wind_speed': data['wind']['speed'],
            'coordinates': {'lat': data['coord']['lat'], 'lon': data['coord']['lon']},
            'timestamp': datetime.fromtimestamp(data['dt'])
        }
    
    def get_forecast(self, city: str, days: int = 5) -> List[Dict]:
        """Get weather forecast for next 5 days"""
        params = {'q': city, 'cnt': days * 8}  # 8 forecasts per day (3-hour intervals)
        
        data = self._make_request('forecast', params)
        
        forecasts = []
        for item in data['list']:
            forecasts.append({
                'datetime': datetime.fromtimestamp(item['dt']),
                'temperature': item['main']['temp'],
                'feels_like': item['main']['feels_like'],
                'humidity': item['main']['humidity'],
                'description': item['weather'][0]['description'],
                'wind_speed': item['wind']['speed'],
                'pressure': item['main']['pressure']
            })
        
        return forecasts
    
    def search_cities(self, query: str, limit: int = 5) -> List[Dict]:
        """Search for cities by name"""
        params = {'q': query, 'limit': limit}
        
        try:
            response = self.session.get(
                f"http://api.openweathermap.org/geo/1.0/direct",
                params={**params, 'appid': self.api_key}
            )
            response.raise_for_status()
            data = response.json()
            
            return [
                {
                    'name': city['name'],
                    'country': city['country'],
                    'state': city.get('state'),
                    'lat': city['lat'],
                    'lon': city['lon']
                }
                for city in data
            ]
        except requests.exceptions.RequestException as e:
            raise Exception(f"City search failed: {e}")