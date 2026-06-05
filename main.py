import os
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI(
    title="easyJet Deal Scout API",
    version="2.1.0"
)

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = "skyscanner-flights4.p.rapidapi.com"


class FlightSearchRequest(BaseModel):
    origin: str = Field(..., example="BSL")
    destination: str = Field(..., example="PMI")
    date_from: str = Field(..., example="2026-10-01")
    date_to: str = Field(..., example="2026-10-08")
    passengers: int = Field(1)
    max_price: Optional[float] = None
    baggage: Optional[bool] = False


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
    return {
        "status": "running",
        "service": "easyJet Deal Scout API",
        "version": "2.1.0"
    }


def extract_price(item):

    for key in [
        "price_raw",
        "price",
        "rawPrice",
        "minPrice",
        "amount"
    ]:

        value = item.get(key)

        if isinstance(value, (int, float)):
            return float(value)

        if isinstance(value, str):
            try:
                cleaned = (
                    value.replace("CHF", "")
                    .replace("EUR", "")
                    .replace("USD", "")
                    .replace("$", "")
                    .replace("€", "")
                    .replace(",", "")
                    .strip()
                )
                return float(cleaned)
            except:
                pass

    return None


def extract_airline(item):

    carriers = item.get("carriers")

    if isinstance(carriers, list) and len(carriers) > 0:
        return str(carriers[0])

    for key in [
        "airline",
        "carrier",
        "airlineName",
        "name"
    ]:
        value = item.get(key)

        if isinstance(value, str):
            return value

    return "Unknown"


@app.post("/search-flights", response_model=FlightSearchResponse)
def search_flights(data: FlightSearchRequest):

    if not RAPIDAPI_KEY:
        raise HTTPException(
            status_code=500,
            detail="RAPIDAPI_KEY missing in Render."
        )

    url = f"https://{RAPIDAPI_HOST}/api/v1/roundtrip"

    headers = {
        "x-rapidapi-host": RAPIDAPI_HOST,
        "x-rapidapi-key": RAPIDAPI_KEY,
        "Content-Type": "application/json"
    }
    
params = {
    "origin": data.origin.upper(),
    "destination": data.destination.upper(),
    "date": data.date_from,
    "return_date": data.date_to,
    "adults": data.passengers,
    "cabin": "economy",
    "currency": "CHF",
    "locale": "de-CH",
    "market": "CH",
    "limit": 20
}

response = requests.get(
    url,
    headers=headers,
    params=params,
    timeout=30
)

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    payload = response.json()

    print("========== RAPIDAPI RESPONSE ==========")
    print(payload)
    print("=======================================")

    results_raw = []

    if isinstance(payload, dict):
        results_raw = payload.get("results", [])

    results = []

    for item in results_raw[:10]:

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
            "notes": "Live result via RapidAPI Skyscanner."
        })

    if not results:

        return {
            "results": [
                {
                    "airline": "No result",
                    "origin": data.origin.upper(),
                    "destination": data.destination.upper(),
                    "departure_date": data.date_from,
                    "return_date": data.date_to,
                    "price": 0,
                    "currency": "CHF",
                    "booking_url": "https://www.skyscanner.ch/",
                    "deal_score": 0,
                    "notes": "No live flight result could be parsed. Check Render logs."
                }
            ]
        }

    return {
        "results": results
    }


@app.post("/create-alert")
def create_alert(data: AlertRequest):

    return {
        "status": "created",
        "message": "Demo alert created.",
        "alert": data.model_dump()
    }
