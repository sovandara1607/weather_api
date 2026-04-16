# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
    BASE_URL = os.getenv('BASE_URL', 'https://api.openweathermap.org/data/2.5')
    
    @classmethod
    def validate(cls):
        if not cls.OPENWEATHER_API_KEY:
            raise ValueError("OPENWEATHER_API_KEY environment variable is not set")
        return True