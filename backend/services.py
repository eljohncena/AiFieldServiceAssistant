import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from models import RouteCache

# Read the .env file so os.getenv can see google api key
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
ROUTES_URL = "https://routes.googleapis.com/directions/v2:computeRoutes"

def get_route_leg(origin_lat, origin_lang, destination_lat, destination_lang, db: Session) -> dict:

    # cache keys will be lat, lang string
    origin = f"{origin_lat},{origin_lang}"
    destination = f"{destination_lat},{destination_lang}"

    #checks db is origin AND destination match
    cached = db.query(RouteCache).filter(RouteCache.origin == origin, RouteCache.destination == destination).first()

    # return early if already cached
    if cached:
        return{"miles": cached.driving_miles, "duration_minutes": cached.driving_minutes}

    # if not cached, calculate and cache

    # sets up headers and body for google maps api
    #https://developers.google.com/maps/documentation/routes/choose_fields-rm#field-ref
    headers = {
        "Content-type": "application/json",
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        "X-Goog-FieldMask": "routes.distanceMeters,routes.duration",
    }

    body = {
        "origin": {"location": {"latitude": origin_lat, "longitude": origin_lang}},
        "destination": {"location": {"latLng": destination_lat, "longitude": destination_lang}},
        "travelMode": "DRIVE",
    }

    # call api and get response
    response = requests.post(ROUTES_URL, headers=headers, json=body)
    response.raise_for_status()
    date = response.json()

    # filter infor for miles and duration
    route = date["routes"][0]
    meters = route["distanceMeters"]
    duration_str = route["duration"]

    # convert meters to miles
    miles = meters / 1609.344
    seconds = int(duration_str.replace("s",""))
    minutes = seconds / 60

    # save to cache so we don't have to pay for this leg again
    new_cache = RouteCache(origin=origin, destination=destination, driving_miles=round(miles,2), driving_minutes=round(minutes,2), cached_at=datetime.now().isoformat())
    db.add(new_cache)
    db.commit()


    return {"miles": round(miles,2), "duration_minutes": round(minutes,2)}

