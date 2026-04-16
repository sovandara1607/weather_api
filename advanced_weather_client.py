# advanced_weather_client.py
import asyncio
import aiohttp
from functools import lru_cache
from datetime import datetime, timedelta
import json
import os

class AsyncWeatherClient:
    def __init__(self):
        self.api_key = Config.OPENWEATHER_API_KEY
        self.base_url = Config.BASE_URL
        self.cache = {}
        self.cache_timeout = timedelta(minutes=10)
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            return datetime.now() - timestamp < self.cache_timeout
        return False
    
    async def get_current_weather_async(self, city: str) -> Dict:
        """Async version of current weather with caching"""
        cache_key = f"current_{city}"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key][0]
        
        async with aiohttp.ClientSession() as session:
            params = {'q': city, 'appid': self.api_key, 'units': 'metric'}
            
            async with session.get(f"{self.base_url}/weather", params=params) as response:
                if response.status != 200:
                    raise Exception(f"API error: {response.status}")
                
                data = await response.json()
                
                # Cache the result
                self.cache[cache_key] = (data, datetime.now())
                
                return {
                    'city': data['name'],
                    'temperature': data['main']['temp'],
                    'description': data['weather'][0]['description'],
                    'timestamp': datetime.now()
                }

# Usage example for async version
async def main_async():
    client = AsyncWeatherClient()
    
    # Get weather for multiple cities concurrently
    cities = ['London', 'Paris', 'Tokyo', 'New York']
    tasks = [client.get_current_weather_async(city) for city in cities]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for city, result in zip(cities, results):
        if isinstance(result, Exception):
            print(f"Error getting weather for {city}: {result}")
        else:
            print(f"{city}: {result['temperature']}°C, {result['description']}")

# Run async version
# asyncio.run(main_async())