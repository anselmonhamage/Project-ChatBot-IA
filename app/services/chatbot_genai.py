import os

import google.generativeai as genai

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("API_KEY")

API_KEY = API_KEY
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")