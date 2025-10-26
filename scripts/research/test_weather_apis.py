"""
Weather API Research Script

Weather conditions have significant impact on NFL player props:
- Wind: Affects passing yards, kicking accuracy
- Rain/Snow: Reduces passing, increases rushing
- Temperature: Affects ball handling, player performance
- Indoor vs Outdoor: Dome games unaffected by weather

This script tests multiple weather APIs to find the best source for:
1. Current conditions at NFL stadiums
2. Forecasts for upcoming games
3. Historical weather data
4. Hourly forecasts (for game time predictions)

APIs Tested:
1. OpenWeatherMap (free tier: 1000 calls/day)
2. WeatherAPI.com (free tier: 1M calls/month)
3. NOAA/NWS (free government API, US only)

**IMPORTANT:** Weather APIs typically require API keys.
Get free keys at:
- OpenWeatherMap: https://openweathermap.org/api
- WeatherAPI.com: https://www.weatherapi.com/signup.aspx
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
import aiohttp


# NFL Stadium Locations for testing
NFL_STADIUMS = {
    "Arrowhead Stadium": {"city": "Kansas City", "state": "MO", "lat": 39.0489, "lon": -94.4839, "team": "KC", "outdoor": True},
    "Lambeau Field": {"city": "Green Bay", "state": "WI", "lat": 44.5013, "lon": -88.0622, "team": "GB", "outdoor": True},
    "Soldier Field": {"city": "Chicago", "state": "IL", "lat": 41.8623, "lon": -87.6167, "team": "CHI", "outdoor": True},
    "Gillette Stadium": {"city": "Foxborough", "state": "MA", "lat": 42.0909, "lon": -71.2643, "team": "NE", "outdoor": True},
    "AT&T Stadium": {"city": "Arlington", "state": "TX", "lat": 32.7473, "lon": -97.0945, "team": "DAL", "outdoor": False},  # Dome
    "Mercedes-Benz Stadium": {"city": "Atlanta", "state": "GA", "lat": 33.7553, "lon": -84.4006, "team": "ATL", "outdoor": False},  # Dome
}


class WeatherAPIResearcher:
    """Research multiple weather APIs and compare results."""

    def __init__(self):
        # API keys from environment
        self.openweather_key = os.getenv("OPENWEATHER_API_KEY")
        self.weatherapi_key = os.getenv("WEATHERAPI_KEY")

        self.results: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "apis_tested": [],
            "successful": [],
            "failed": [],
            "findings": {},
        }

        # Create directories for saving results
        self.samples_dir = Path("/Users/jace/dev/nfl-ai/samples/weather")
        self.samples_dir.mkdir(parents=True, exist_ok=True)

    async def test_openweathermap(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Test OpenWeatherMap API."""
        result = {
            "api": "OpenWeatherMap",
            "status": "pending",
            "tests": []
        }

        if not self.openweather_key:
            result["status"] = "skipped"
            result["error"] = "No API key found (OPENWEATHER_API_KEY)"
            print("\n⚠️  Skipping OpenWeatherMap - No API key")
            print("   Get free key at: https://openweathermap.org/api")
            return result

        print("\n" + "="*80)
        print("TESTING: OpenWeatherMap API")
        print("="*80)

        # Test current weather for Arrowhead Stadium
        stadium = NFL_STADIUMS["Arrowhead Stadium"]

        try:
            # Current weather
            url = "https://api.openweathermap.org/data/2.5/weather"
            params = {
                "lat": stadium["lat"],
                "lon": stadium["lon"],
                "appid": self.openweather_key,
                "units": "imperial"
            }

            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()

                    # Save sample
                    save_path = self.samples_dir / "openweather_current.json"
                    with open(save_path, 'w') as f:
                        json.dump(data, f, indent=2)

                    result["tests"].append({
                        "endpoint": "current",
                        "status": "success",
                        "data_keys": list(data.keys()),
                        "temp": data.get("main", {}).get("temp"),
                        "humidity": data.get("main", {}).get("humidity"),
                        "wind_speed": data.get("wind", {}).get("speed"),
                        "description": data.get("weather", [{}])[0].get("description"),
                    })

                    print(f"✅ Current Weather: {data.get('main', {}).get('temp')}°F, "
                          f"{data.get('weather', [{}])[0].get('description')}, "
                          f"Wind: {data.get('wind', {}).get('speed')} mph")

            # Forecast
            url_forecast = "https://api.openweathermap.org/data/2.5/forecast"
            async with session.get(url_forecast, params=params) as response:
                if response.status == 200:
                    data = await response.json()

                    save_path = self.samples_dir / "openweather_forecast.json"
                    with open(save_path, 'w') as f:
                        json.dump(data, f, indent=2)

                    result["tests"].append({
                        "endpoint": "forecast",
                        "status": "success",
                        "forecast_count": len(data.get("list", [])),
                    })

                    print(f"✅ Forecast: {len(data.get('list', []))} data points")

            result["status"] = "success"

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            print(f"❌ OpenWeatherMap failed: {e}")

        return result

    async def test_weatherapi_com(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Test WeatherAPI.com."""
        result = {
            "api": "WeatherAPI.com",
            "status": "pending",
            "tests": []
        }

        if not self.weatherapi_key:
            result["status"] = "skipped"
            result["error"] = "No API key found (WEATHERAPI_KEY)"
            print("\n⚠️  Skipping WeatherAPI.com - No API key")
            print("   Get free key at: https://www.weatherapi.com/signup.aspx")
            return result

        print("\n" + "="*80)
        print("TESTING: WeatherAPI.com")
        print("="*80)

        stadium = NFL_STADIUMS["Lambeau Field"]

        try:
            # Current weather
            url = "http://api.weatherapi.com/v1/current.json"
            params = {
                "key": self.weatherapi_key,
                "q": f"{stadium['lat']},{stadium['lon']}",
                "aqi": "no"
            }

            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()

                    save_path = self.samples_dir / "weatherapi_current.json"
                    with open(save_path, 'w') as f:
                        json.dump(data, f, indent=2)

                    current = data.get("current", {})
                    result["tests"].append({
                        "endpoint": "current",
                        "status": "success",
                        "temp_f": current.get("temp_f"),
                        "wind_mph": current.get("wind_mph"),
                        "precip_in": current.get("precip_in"),
                        "condition": current.get("condition", {}).get("text"),
                    })

                    print(f"✅ Current: {current.get('temp_f')}°F, "
                          f"{current.get('condition', {}).get('text')}, "
                          f"Wind: {current.get('wind_mph')} mph")

            # Forecast
            url_forecast = "http://api.weatherapi.com/v1/forecast.json"
            params_forecast = {
                "key": self.weatherapi_key,
                "q": f"{stadium['lat']},{stadium['lon']}",
                "days": 7,
                "aqi": "no",
                "alerts": "no"
            }

            async with session.get(url_forecast, params=params_forecast) as response:
                if response.status == 200:
                    data = await response.json()

                    save_path = self.samples_dir / "weatherapi_forecast.json"
                    with open(save_path, 'w') as f:
                        json.dump(data, f, indent=2)

                    forecast_days = data.get("forecast", {}).get("forecastday", [])
                    result["tests"].append({
                        "endpoint": "forecast",
                        "status": "success",
                        "days": len(forecast_days),
                    })

                    print(f"✅ Forecast: {len(forecast_days)} days")

            result["status"] = "success"

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            print(f"❌ WeatherAPI.com failed: {e}")

        return result

    async def test_noaa_nws(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Test NOAA National Weather Service API (Free, no key required)."""
        result = {
            "api": "NOAA/NWS",
            "status": "pending",
            "tests": []
        }

        print("\n" + "="*80)
        print("TESTING: NOAA National Weather Service (FREE)")
        print("="*80)

        stadium = NFL_STADIUMS["Soldier Field"]

        try:
            # NWS requires a point lookup first
            url_point = f"https://api.weather.gov/points/{stadium['lat']},{stadium['lon']}"

            headers = {
                'User-Agent': 'NFL-AI Research (contact@example.com)',
                'Accept': 'application/json'
            }

            async with session.get(url_point, headers=headers) as response:
                if response.status == 200:
                    point_data = await response.json()

                    save_path = self.samples_dir / "noaa_point.json"
                    with open(save_path, 'w') as f:
                        json.dump(point_data, f, indent=2)

                    # Get forecast URL
                    forecast_url = point_data.get("properties", {}).get("forecast")
                    forecast_hourly_url = point_data.get("properties", {}).get("forecastHourly")

                    print(f"✅ Point lookup successful")

                    # Get forecast
                    if forecast_url:
                        async with session.get(forecast_url, headers=headers) as resp:
                            if resp.status == 200:
                                forecast_data = await resp.json()

                                save_path = self.samples_dir / "noaa_forecast.json"
                                with open(save_path, 'w') as f:
                                    json.dump(forecast_data, f, indent=2)

                                periods = forecast_data.get("properties", {}).get("periods", [])
                                result["tests"].append({
                                    "endpoint": "forecast",
                                    "status": "success",
                                    "periods": len(periods),
                                })

                                if periods:
                                    print(f"✅ Forecast: {periods[0].get('name')} - "
                                          f"{periods[0].get('temperature')}°F, "
                                          f"{periods[0].get('shortForecast')}")

                    result["status"] = "success"

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            print(f"❌ NOAA/NWS failed: {e}")

        return result

    async def run_all_tests(self):
        """Run all weather API tests."""
        print("\n" + "="*80)
        print("WEATHER API RESEARCH - COMPREHENSIVE TESTING")
        print("="*80)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)

        async with aiohttp.ClientSession() as session:
            # Test all APIs
            openweather_result = await self.test_openweathermap(session)
            self.results["apis_tested"].append(openweather_result)

            weatherapi_result = await self.test_weatherapi_com(session)
            self.results["apis_tested"].append(weatherapi_result)

            noaa_result = await self.test_noaa_nws(session)
            self.results["apis_tested"].append(noaa_result)

        # Analyze results
        self._generate_summary()
        self._save_results()

    def _generate_summary(self):
        """Generate summary and recommendation."""
        print("\n" + "="*80)
        print("RESEARCH SUMMARY")
        print("="*80)

        for api_result in self.results["apis_tested"]:
            status_icon = {
                "success": "✅",
                "failed": "❌",
                "skipped": "⏭️"
            }.get(api_result["status"], "❓")

            print(f"\n{status_icon} {api_result['api']}: {api_result['status'].upper()}")

            if api_result["status"] == "success":
                self.results["successful"].append(api_result["api"])
                print(f"   Tests passed: {len([t for t in api_result.get('tests', []) if t['status'] == 'success'])}")
            elif api_result["status"] == "skipped":
                print(f"   Reason: {api_result.get('error', 'Unknown')}")
            else:
                self.results["failed"].append(api_result["api"])
                print(f"   Error: {api_result.get('error', 'Unknown')}")

        # Recommendation
        print("\n" + "="*80)
        print("RECOMMENDATION")
        print("="*80)

        successful = [api for api in self.results["apis_tested"] if api["status"] == "success"]

        if successful:
            # Rank APIs
            rankings = []
            for api in successful:
                if api["api"] == "NOAA/NWS":
                    rankings.append(("NOAA/NWS", "FREE (no key), US-focused, reliable"))
                elif api["api"] == "WeatherAPI.com":
                    rankings.append(("WeatherAPI.com", "1M free calls/month, detailed hourly"))
                elif api["api"] == "OpenWeatherMap":
                    rankings.append(("OpenWeatherMap", "1000 free calls/day, popular"))

            print(f"🟢 GO - Weather data available from {len(successful)} source(s)\n")
            print("Recommended priority:")
            for i, (api, reason) in enumerate(rankings, 1):
                print(f"  {i}. {api}")
                print(f"     → {reason}")

            self.results["recommendation"] = "GO"
            self.results["recommended_apis"] = [r[0] for r in rankings]
        else:
            print("🔴 NO-GO - No weather APIs accessible")
            print("   Action: Obtain API keys for testing")
            self.results["recommendation"] = "NO-GO"

        # Weather impact analysis
        print("\n" + "="*80)
        print("WEATHER IMPACT ON PROPS")
        print("="*80)
        print("""
Weather significantly affects player props:

🌬️  WIND (>15 mph):
   - ⬇️  Passing yards (harder for deep balls)
   - ⬇️  FG accuracy (kicking affected)
   - ⬆️  Rushing attempts (teams run more)

🌧️  RAIN/SNOW:
   - ⬇️  Passing yards (ball handling issues)
   - ⬇️  Receptions (drops increase)
   - ⬆️  Rushing attempts
   - ⬇️  Total points

❄️  COLD (<32°F):
   - ⬇️  Passing accuracy
   - ⬇️  Ball handling
   - Affects visiting warm-weather teams more

☀️  DOME/INDOOR:
   - ✅ No weather impact
   - Consistent conditions
   - Passing-friendly

Recommendation: Fetch weather 24 hours before game, then hourly updates
""")

    def _save_results(self):
        """Save research results."""
        results_path = self.samples_dir / "research_results.json"
        with open(results_path, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"\n💾 Results saved to: {results_path}")

        print("\n" + "="*80)
        print("NEXT STEPS")
        print("="*80)
        print("1. Review saved sample responses in samples/weather/")
        print("2. Get API keys for any skipped services (if needed)")
        print("3. Document findings in docs/sources/WEATHER_API.md")
        print("4. Build weather data accessor")
        print("5. Integrate weather data into prop analysis")
        print("="*80 + "\n")


async def main():
    """Main entry point."""
    researcher = WeatherAPIResearcher()
    await researcher.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
