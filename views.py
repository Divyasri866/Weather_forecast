import requests
from django.shortcuts import render, redirect
from .forms import WeatherForm
from dotenv import load_dotenv
import os
from datetime import datetime
from twilio.rest import Client
from .forms import DisasterForm
from .ml.predict_disaster import predict_disaster
from .forms import LatLonForm
load_dotenv()
TOMORROW_API_KEY = os.getenv("TOMORROW_API_KEY")

# Weather code to readable condition and Bootstrap Icon
WEATHER_CODE_MAP = {
    1000: ("Clear", "bi-brightness-high"),
    1100: ("Mostly Clear", "bi-cloud-sun"),
    1101: ("Partly Cloudy", "bi-cloud"),
    1102: ("Mostly Cloudy", "bi-clouds"),
    1001: ("Cloudy", "bi-cloud-fill"),
    2000: ("Fog", "bi-cloud-fog2"),
    2100: ("Light Fog", "bi-cloud-fog"),
    4000: ("Drizzle", "bi-cloud-drizzle"),
    4001: ("Rain", "bi-cloud-rain"),
    4200: ("Light Rain", "bi-cloud-drizzle"),
    4201: ("Heavy Rain", "bi-cloud-rain-heavy"),
    5000: ("Snow", "bi-snow"),
    5001: ("Flurries", "bi-cloud-snow"),
    5100: ("Light Snow", "bi-cloud-snow"),
    5101: ("Heavy Snow", "bi-snow"),
    6000: ("Freezing Drizzle", "bi-cloud-drizzle"),
    6001: ("Freezing Rain", "bi-cloud-hail"),
    6200: ("Light Freezing Rain", "bi-cloud-drizzle"),
    6201: ("Heavy Freezing Rain", "bi-cloud-hail"),
    7000: ("Ice Pellets", "bi-cloud-hail"),
    7101: ("Heavy Ice Pellets", "bi-cloud-hail"),
    7102: ("Light Ice Pellets", "bi-cloud-hail"),
    8000: ("Thunderstorm", "bi-cloud-lightning"),
}


def get_weather(location, date):
    url = "https://api.tomorrow.io/v4/weather/forecast"
    params = {
        "location": location,
        "apikey": TOMORROW_API_KEY,
        "units": "metric",
        "timesteps": "1d",
    }

    response = requests.get(url, params=params)
    data = response.json()

    try:
        for interval in data["timelines"]["daily"]:
            forecast_date = interval["time"][:10]
            if forecast_date == date:
                values = interval["values"]
                code = values.get("weatherCodeMax")
                condition, icon = WEATHER_CODE_MAP.get(code, ("Unknown", "bi-question-circle"))

                filtered = {
                    "date": forecast_date,
                    "temperature_avg": values.get("temperatureAvg"),
                    "temperature_min": values.get("temperatureMin"),
                    "temperature_max": values.get("temperatureMax"),
                    "humidity": values.get("humidityAvg"),
                    "rain_probability": values.get("precipitationProbabilityAvg"),
                    "wind_speed": values.get("windSpeedAvg"),
                    "uv_index": values.get("uvIndexMax"),
                    "sunrise": values.get("sunriseTime"),
                    "sunset": values.get("sunsetTime"),
                    "weather_condition": condition,
                    "weather_icon": icon,
                }
                return filtered
    except Exception as e:
        print("Error in get_weather():", e)

    return None


def get_three_day_forecast(location):
    url = "https://api.tomorrow.io/v4/weather/forecast"
    params = {
        "location": location,
        "apikey": TOMORROW_API_KEY,
        "units": "metric",
        "timesteps": "1d",
    }

    response = requests.get(url, params=params)
    data = response.json()
    today = datetime.utcnow().date()
    forecast = {}

    try:
        for interval in data["timelines"]["daily"]:
            forecast_date = datetime.fromisoformat(interval["time"][:10]).date()
            delta = (forecast_date - today).days

            if 0 <= delta <= 2:
                day_label = ["today", "tomorrow", "day_after"][delta]
                code = interval["values"]["weatherCodeMax"]
                condition, icon = WEATHER_CODE_MAP.get(code, ("Unknown", "bi-question-circle"))

                forecast[day_label] = {
                    "date": forecast_date.isoformat(),
                    "max_temp": interval["values"]["temperatureMax"],
                    "condition": condition,
                    "icon": icon,
                }

    except Exception as e:
        print("Error in get_three_day_forecast():", e)

    return forecast

def index(request):
    context = {'message_sent': False, 'error': None}

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        print (f"Received: Name={name}, Email={email}, Message={message}")
        if name and email and message:
            try:
                # Twilio setup (use your actual credentials here)
                account_sid = 'ACf536987d330cff91a5958988c8abb088'
                auth_token = 'fe06224c03571372c7e6ac0ed75776de'
                twilio_number = '+17244428989'  # Your Twilio number
                your_number = '+918247089250'  # Your number

                client = Client(account_sid, auth_token)

                sms_body = f"Contact Form Submission:\nName: {name}\nEmail: {email}\nMessage: {message}"

                client.messages.create(
                    body=sms_body,
                    from_=twilio_number,
                    to=your_number
                )

                context['message_sent'] = True

            except Exception as e:
                context['error'] = f"SMS sending failed: {str(e)}"
        else:
            context['error'] = "Missing form fields."
    return render(request, 'index.html', context)
def weather_view(request):
    weather_data = None
    if request.method == 'POST':
        form = WeatherForm(request.POST)
        if form.is_valid():
            location = form.cleaned_data['location']
            date = form.cleaned_data['date'].isoformat()
            weather_data = get_weather(location, date)
    else:
        form = WeatherForm()

    return render(request, 'weather.html', {'form': form, 'weather_data': weather_data})

def blog2(request):
    return render(request, 'blog2.html')
def blog(request):
    return render(request,'blog.html')
def visionmission(request):
    return render(request, 'visionmission.html')
def feedback(request):
    return render(request, 'feedback.html') 
def otherservices(request):
    return render(request, 'other_service.html')

def careerGuidence(request):
    return render(request, 'careerGuidence.html')

def advancedCareer(request):
    return render(request, 'AdvancedCareer.html')

def weather_options(request):
    return render(request, 'weather_options.html')


def disaster_prediction_view(request):
    form = DisasterForm ()
    context = {"form": form}

    if request.method == "POST":
        form = DisasterForm (request.POST)
        if form.is_valid ():
            location = form.cleaned_data['location']
            date = form.cleaned_data['date'].isoformat ()

            # Step 1: Get weather data for this location and date
            weather_data = get_weather (location, date)

            if weather_data:
                # Step 2: Predict disaster using the ML model
                disaster_result = predict_disaster (weather_data)  # assuming it accepts a dict

                # Step 3: Render results page
                context.update ({
                    'location': location,
                    'date': date,
                    'weather_data': weather_data,
                    'disaster_result': disaster_result,
                })
                return render (request, 'disaster_results.html', context)
            else:
                context['error'] = "Weather data not available for the selected location or date."

    return render (request, 'disaster_form.html', context)

def disaster_form_view(request):
    return render(request, 'disaster_form.html')

def disaster_results_view(request):
    if request.method == 'POST':
        location = request.POST.get('location')
        try:
            result = predict_disaster(location)
        except Exception as e:
            result = f"Error: {str(e)}"
        return render(request, 'disaster_results.html', {'location': location, 'result': result})
    return redirect('disaster-form')


def weather_by_coordinates(request):
    weather_data = None
    latitude = None
    longitude = None
    selected_date = None
    if request.method == 'GET' and 'latitude' in request.GET and 'longitude' in request.GET and 'date' in request.GET:
        form = LatLonForm (request.GET)
        if form.is_valid():
            lat = form.cleaned_data['latitude']
            lon = form.cleaned_data['longitude']
            date = form.cleaned_data['date'].isoformat()
            latitude = lat
            longitude = lon
            selected_date = date
            url = "https://api.tomorrow.io/v4/weather/forecast"
            params = {
                "location": f"{lat},{lon}",
                "apikey": TOMORROW_API_KEY,
                "units": "metric",
                "timesteps": "1d",
            }

            try:
                response = requests.get(url, params=params)
                data = response.json()
                for interval in data["timelines"]["daily"]:
                    forecast_date = interval["time"][:10]
                    if forecast_date == date:
                        values = interval["values"]
                        code = values.get("weatherCodeMax")
                        condition, icon = WEATHER_CODE_MAP.get(code, ("Unknown", "bi-question-circle"))

                        weather_data = {
                            "date": forecast_date,
                            "temperature_avg": values.get("temperatureAvg"),
                            "temperature_min": values.get("temperatureMin"),
                            "temperature_max": values.get("temperatureMax"),
                            "humidity": values.get("humidityAvg"),
                            "rain_probability": values.get("precipitationProbabilityAvg"),
                            "wind_speed": values.get("windSpeedAvg"),
                            "uv_index": values.get("uvIndexMax"),
                            "sunrise": values.get("sunriseTime"),
                            "sunset": values.get("sunsetTime"),
                            "weather_condition": condition,
                            "weather_icon": icon,
                        }
                        break
            except Exception as e:
                print("Error fetching forecast by coordinates:", e)
    else:
        form = LatLonForm()

    return render(request, 'weather_by_coordinates.html', {'form': form, 'weather_data': weather_data, 'latitude': latitude,
        'longitude': longitude,
        'selected_date': selected_date,})
