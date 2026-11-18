from google import genai
from app.core.config import settings
import json

client = genai.Client(api_key=settings.GEMINI_API_KEY)
prompt = (
    "Generate a 2-day travel itinerary for Paris as a JSON array of days. "
    "Each day must have day_number, title, theme, and 3 activities (morning, afternoon, evening). "
    "Each activity must have: time_slot, time_str, title, description, location_name, lat, lng, estimated_cost, duration_mins, travel_time_from_prev, transport_mode, category, is_indoor. "
    "Return ONLY raw JSON, no code fences."
)

r = client.models.generate_content(model='gemini-3.5-flash-lite', contents=prompt)
text = r.text.strip()
if text.startswith("```"):
    text = text.split("\n", 1)[1].rsplit("\n", 1)[0]
data = json.loads(text)
print("SUCCESSFULLY PARSED ITINERARY FOR:", len(data), "DAYS!")
for d in data:
    print(f"{d['title']} ({len(d['activities'])} activities):")
    for a in d['activities']:
        print(f"  - {a['time_str']}: {a['title']} at {a['location_name']} ({a['lat']}, {a['lng']})")
