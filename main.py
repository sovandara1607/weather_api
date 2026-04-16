# main.py
import asyncio
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Static, DataTable, LoadingIndicator
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.binding import Binding
from textual.reactive import reactive
from datetime import datetime

from weather_client import WeatherClient
from config import Config

class CurrentWeatherCard(Static):
    """A stylish card for current weather"""
    
    DEFAULT_CSS = """
    CurrentWeatherCard {
        width: 100%;
        height: auto;
        background: $surface;
        border: solid $accent;
        padding: 1 2;
        margin-bottom: 1;
    }
    .temp-large {
        text-style: bold;
        color: $text;
        dock: left;
        width: 30%;
        content-align: center middle;
    }
    .details {
        width: 70%;
        padding-left: 1;
    }
    .city-name {
        text-style: bold italic;
        color: $primary;
    }
    .condition {
        color: $secondary;
        text-style: bold;
    }
    .stat-row {
        layout: horizontal;
        height: 1;
        margin-top: 1;
    }
    .stat-label {
        width: 12;
        color: $text-muted;
    }
    .stat-value {
        text-style: bold;
    }
    .error-msg {
        color: $error;
        text-style: bold;
        padding: 1;
    }
    """

    def __init__(self):
        super().__init__()
        self.data = None
        self.error = None

    def update_data(self, data: dict):
        self.data = data
        self.error = None
        self.refresh()

    def update_error(self, message: str):
        self.data = None
        self.error = message
        self.refresh()

    def compose(self) -> ComposeResult:
        if self.error:
            yield Static(f"⚠️  {self.error}", classes="error-msg")
            return
        if not self.data:
            yield Static("🔍 Search for a city to begin...", classes="placeholder")
            return

        w = self.data
        # Main Temperature Display
        yield Static(f"{w['temperature']}°C", classes="temp-large")
        
        with Vertical(classes="details"):
            yield Static(f"📍 {w['city']}, {w['country']}", classes="city-name")
            yield Static(f"☁️ {w['description'].title()}", classes="condition")
            
            with Horizontal(classes="stat-row"):
                yield Static("Feels Like:", classes="stat-label")
                yield Static(f"{w['feels_like']}°C", classes="stat-value")
            
            with Horizontal(classes="stat-row"):
                yield Static("Humidity:", classes="stat-label")
                yield Static(f"{w['humidity']}%", classes="stat-value")
                
            with Horizontal(classes="stat-row"):
                yield Static("Wind:", classes="stat-label")
                yield Static(f"{w['wind_speed']} m/s", classes="stat-value")

class ForecastTable(DataTable):
    """A clean table for forecast data"""
    
    DEFAULT_CSS = """
    ForecastTable {
        height: 1fr;
        border: solid $surface-lighten-1;
    }
    """

    def update_data(self, forecasts: list):
        self.clear()
        if not forecasts:
            return
            
        # Add columns
        if not self.columns:
            self.add_columns("Time", "Temp", "Condition", "Humidity", "Wind")

        for f in forecasts:
            time_str = f['datetime'].strftime("%a %H:%M")
            temp_str = f"{f['temperature']}°"
            desc_str = f['description'].title()
            hum_str = f"{f['humidity']}%"
            wind_str = f"{f['wind_speed']}m/s"
            
            self.add_row(time_str, temp_str, desc_str, hum_str, wind_str)

class WeatherApp(App):
    """A modern TUI Weather App"""
    
    CSS = """
    Screen {
        layout: grid;
        grid-size: 2;
        grid-columns: 1fr 2fr; /* Left panel smaller, right panel wider */
        grid-gutter: 1;
        padding: 1;
        background: $background;
    }
    
    #sidebar {
        width: 100%;
        height: 100%;
    }
    
    #main-content {
        width: 100%;
        height: 100%;
    }

    Input {
        dock: top;
        margin-bottom: 1;
        border: solid $primary;
    }
    
    .header-title {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }

    LoadingIndicator {
        width: 100%;
        height: 100%;
        display: none; /* Hidden by default */
    }
    
    LoadingIndicator.loading {
        display: block;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("ctrl+r", "refresh", "Refresh"),
    ]

    loading = reactive(False)

    def __init__(self):
        super().__init__()
        try:
            Config.validate()
            self.client = WeatherClient()
        except ValueError as e:
            self.exit(message=f"Config Error: {e}")

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        with Horizontal():
            # Left Sidebar: Search & Current Weather
            with Vertical(id="sidebar"):
                yield Input(placeholder="🔍 City Name...", id="search-input")
                yield CurrentWeatherCard()
            
            # Right Panel: Forecast
            with Vertical(id="main-content"):
                yield Static("📅 5-Day Forecast", classes="header-title")
                yield ForecastTable()
                yield LoadingIndicator(id="loader")

        yield Footer()

    def on_mount(self) -> None:
        self.query_one(Input).focus()

    async def watch_loading(self, loading: bool) -> None:
        """Show/hide loader based on reactive state"""
        loader = self.query_one("#loader", LoadingIndicator)
        if loading:
            loader.add_class("loading")
        else:
            loader.remove_class("loading")

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        city = event.value
        if not city:
            return
        
        self.loading = True
        
        try:
            # Run blocking IO in thread to keep UI responsive
            current = await asyncio.to_thread(self.client.get_current_weather, city)
            forecast = await asyncio.to_thread(self.client.get_forecast, city)
            
            # Update UI components
            self.query_one(CurrentWeatherCard).update_data(current)
            self.query_one(ForecastTable).update_data(forecast)
            
        except Exception as e:
            self.notify(f"Error: {str(e)}", severity="error", timeout=10)
            self.query_one(CurrentWeatherCard).update_error(str(e))
        finally:
            self.loading = False

    def action_refresh(self) -> None:
        input_widget = self.query_one(Input)
        if input_widget.value:
            # Simulate enter press
            self.post_message(Input.Submitted(input_widget, input_widget.value))

if __name__ == "__main__":
    app = WeatherApp()
    app.run()