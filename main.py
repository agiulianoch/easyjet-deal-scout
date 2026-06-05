from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI(
    title="easyJet Deal Scout API",
    version="1.0.0",
    description="Simple MVP backend for a Custom GPT that searches dummy easyJet flight deals and creates price alerts."
)


class FlightSearchRequest(BaseModel):
    origin: str = Field(..., example="ZRH")
    destination: str = Field(..., example="PMI")
    date_from: str = Field(..., example="2026-06-01")
    date_to: str = Field(..., example="2026-06-30")
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
    origin: str = Field(..., example="ZRH")
    destination: str = Field(..., example="PMI")
    date_from: str = Field(..., example="2026-06-01")
    date_to: str = Field(..., example="2026-06-30")
    max_price: float = Field(..., example=180)
    notification_channel: str = Field("email", example="email")


@app.get("/")
def root():
    return {
        "status": "running",
        "service": "easyJet Deal Scout API",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }


@app.post("/search-flights", response_model=FlightSearchResponse)
def search_flights(data: FlightSearchRequest):
    """
    MVP endpoint for Custom GPT Actions.
    Currently returns demo data so you can test the full GPT + Render setup.
    Replace this logic later with a real flight API such as Duffel, Amadeus, Kiwi or another provider.
    """
    base_price = 89.0
    if data.baggage:
        base_price += 35.0

    deal_score = 92
    if data.max_price and base_price > data.max_price:
        deal_score = 55

    return {
        "results": [
            {
                "airline": "easyJet",
                "origin": data.origin.upper(),
                "destination": data.destination.upper(),
                "departure_date": data.date_from,
                "return_date": data.date_to,
                "price": base_price,
                "currency": "CHF",
                "booking_url": "https://www.easyjet.com/",
                "deal_score": deal_score,
                "notes": "Demo result. Connect a real flight API for live prices."
            }
        ]
    }


@app.post("/create-alert")
def create_alert(data: AlertRequest):
    """
    MVP alert endpoint.
    Currently confirms creation only. Later this can store alerts in a database and notify via Telegram or email.
    """
    return {
        "status": "created",
        "message": "Demo alert created successfully.",
        "alert": data.model_dump()
    }
