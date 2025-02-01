import os
import webbrowser
import datetime
import requests
import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

class EDITH:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_active = False
        
        # Google Services
        self.google_service = build(
            "customsearch", "v1",
            developerKey=os.getenv("GOOGLE_API_KEY")
        )
        self.cse_id = os.getenv("GOOGLE_CSE_ID")
        
        # Website mappings
        self.website_map = {
            "google": "https://google.com",
            "facebook": "https://facebook.com",
            "instagram": "https://instagram.com",
            "youtube": "https://youtube.com",
            "spotify": "https://open.spotify.com"
        }

    def speak(self, text):
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save("response.mp3")
        playsound("response.mp3")
        os.remove("response.mp3")

    def listen(self):
        with self.microphone as source:
            print("Listening...")
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source, phrase_time_limit=5)
            
        try:
            return self.recognizer.recognize_google(audio).lower()
        except:
            return ""

    def activate(self):
        self.is_active = True
        self.speak("Yes sir, I am here. How can I assist you?")

    def google_search(self, query):
        try:
            res = self.google_service.cse().list(
                q=query,
                cx=self.cse_id,
                num=3
            ).execute()
            return [item['snippet'] for item in res['items']]
        except:
            return None

    def get_weather(self, location="New York"):
        try:
            # Get coordinates using Google Geocoding
            geo_response = requests.get(
                f"https://maps.googleapis.com/maps/api/geocode/json?address={location}&key={os.getenv('GOOGLE_API_KEY')}"
            )
            lat_lng = geo_response.json()['results'][0]['geometry']['location']
            
            # Get weather using OpenWeatherMap
            weather_response = requests.get(
                f"https://api.openweathermap.org/data/2.5/weather?lat={lat_lng['lat']}&lon={lat_lng['lng']}&appid={os.getenv('OPENWEATHER_API_KEY')}&units=metric"
            )
            weather_data = weather_response.json()
            return f"{weather_data['weather'][0]['description']}, {weather_data['main']['temp']}°C"
        except:
            return "Unable to retrieve weather data"

    def handle_command(self, command):
        if "open" in command:
            for site in self.website_map:
                if site in command:
                    webbrowser.open(self.website_map[site])
                    self.speak(f"Opening {site} sir")
                    return
            self.speak("Website not in my database sir")

        elif "time" in command:
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            self.speak(f"The current time is {current_time}")

        elif "date" in command:
            current_date = datetime.datetime.now().strftime("%B %d, %Y")
            self.speak(f"Today's date is {current_date}")

        elif "weather" in command:
            location = command.replace("weather", "").strip() or "New York"
            weather_report = self.get_weather(location)
            self.speak(f"Weather in {location}: {weather_report}")

        elif "search" in command:
            query = command.replace("search", "").strip()
            results = self.google_search(query)
            if results:
                self.speak(f"Top results for {query}: " + ". ".join(results[:2]))
            else:
                self.speak("No relevant information found sir")

        else:
            self.speak("I can perform web searches if you say 'search' before your query")

    def run(self):
        self.speak("EDITH initialization complete. Systems operational sir")
        while True:
            audio_input = self.listen()
            
            if "edith" in audio_input:
                self.activate()
                while self.is_active:
                    command = self.listen()
                    if not command:
                        continue
                    if "sleep" in command or "exit" in command:
                        self.speak("Going to standby mode sir")
                        self.is_active = False
                    else:
                        self.handle_command(command)

if __name__ == "__main__":
    assistant = EDITH()
    assistant.run()