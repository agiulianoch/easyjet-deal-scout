import os
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI(title="easyJet Deal Scout API", version="2.0.0")

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = "skyscanner-flights4.p.rapidapi.com"

class FlightSearchRequest(BaseModel):
    origin: str = Field(..., example="ZRH")
    destination: str = Field(..., example="PMI")
    date_from: str = Field(..., example="2026-06-01")
    date_to: str = Field(..., example="2026-06-07")
    passengers: int = Field(1, example=2)
    max_price: Optional[float] = Field(None, example=180)
    baggage: Optional[bool] = Field(False, example=False)


class FlightResult(BaseModel):
    airline: str
    origin: str
    destination: str
    departure_date: str
    return_date: str
    price: float
    currency: str
    booking_url: str
    deal_score: int
    notes: str


class FlightSearchResponse(BaseModel):
    results: List[FlightResult]


class AlertRequest(BaseModel):
    origin: str
    destination: str
    date_from: str
    date_to: str
    max_price: float
    notification_channel: str = "email"


@app.get("/")
def root():
    return {"status": "running", "service": "easyJet Deal Scout API", "version": "2.0.0"}


def extract_price(item):
    for key in ["price", "rawPrice", "minPrice", "amount"]:
        value = item.get(key)
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            cleaned = value.replace("CHF", "").replace("$", "").replace("€", "").replace(",", "").strip()
            try:
                return float(cleaned)
            except:
                pass
    return None


def extract_airline(item):
    for key in ["airline", "carrier", "airlineName", "name"]:
        value = item.get(key)
        if isinstance(value, str):
            return value
    return "Unknown"


@app.post("/search-flights", response_model=FlightSearchResponse)
def search_flights(data: FlightSearchRequest):
    if not RAPIDAPI_KEY:
        raise HTTPException(status_code=500, detail="RAPIDAPI_KEY is missing in Render environment variables.")

    url = f"https://{RAPIDAPI_HOST}/api/v1/roundtrip"

    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }

    params = {
        "origin": data.origin.upper(),
        "destination": data.destination.upper(),
        "departureDate": data.date_from,
        "returnDate": data.date_to,
        "adults": data.passengers,
        "currency": "CHF",
        "market": "CH",
        "locale": "de-CH",
        "cabin": "economy"
    }

    response = requests.get(url, headers=headers, params=params, timeout=25)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    payload = response.json()

    possible_lists = []
    if isinstance(payload, dict):
        for key in ["data", "results", "itineraries", "flights"]:
            if isinstance(payload.get(key), list):
                possible_lists = payload[key]
                break

    results = []

    for item in possible_lists[:10]:
        if not isinstance(item, dict):
            continue

        price = extract_price(item)
        if price is None:
            continue

        airline = extract_airline(item)

        score = 80
        if data.max_price:
            if price <= data.max_price:
                score = 95
            elif price <= data.max_price * 1.2:
                score = 75
            else:
                score = 45

        results.append({
            "airline": airline,
            "origin": data.origin.upper(),
            "destination": data.destination.upper(),
            "departure_date": data.date_from,
            "return_date": data.date_to,
            "price": price,
            "currency": "CHF",
            "booking_url": "https://www.skyscanner.ch/",
            "deal_score": score,
            "notes": "Live result from Skyscanner via RapidAPI. Please verify final price before booking."
        })

    if not results:
        return {
            "results": [{
                "airline": "No result",
                "origin": data.origin.upper(),
                "destination": data.destination.upper(),
                "departure_date": data.date_from,
                "return_date": data.date_to,
                "price": 0,
                "currency": "CHF",
                "booking_url": "https://www.skyscanner.ch/",
                "deal_score": 0,
                "notes": "No live flight result could be parsed. Check RapidAPI response format."
            }]
        }

    return {"results": results}


@app.post("/create-alert")
def create_alert(data: AlertRequest):
    return {
        "status": "created",
        "message": "Alert saved as demo. Database/Telegram notification can be added next.",
        "alert": data.model_dump()
    }
