# easyJet Deal Scout

MVP backend for a Custom GPT that can search demo easyJet flight deals and create demo price alerts.

## What this project does

This is a small FastAPI backend for ChatGPT Actions.

It includes:

- `GET /` health check
- `POST /search-flights` demo flight search
- `POST /create-alert` demo alert creation
- `GET /openapi.json` automatic OpenAPI schema
- `GET /docs` interactive API documentation

Important: this MVP uses demo data only. To get real flight prices, connect a real flight API later, for example Duffel, Amadeus, Kiwi, Skyscanner partner access, or another approved flight data provider.

## Deploy on Render

1. Create a new GitHub repository.
2. Upload these files:
   - `main.py`
   - `requirements.txt`
   - `render.yaml`
   - `README.md`
3. Go to Render.
4. Click **New +** > **Web Service**.
5. Connect the GitHub repository.
6. Render should detect the settings from `render.yaml`.
7. Deploy.

After deployment, Render gives you a URL like:

```text
https://easyjet-deal-scout.onrender.com
```

Open that URL. You should see:

```json
{
  "status": "running",
  "service": "easyJet Deal Scout API",
  "docs": "/docs",
  "openapi": "/openapi.json"
}
```

## Custom GPT Action schema

In your Custom GPT action settings, use this OpenAPI schema and replace the server URL with your Render URL:

```yaml
openapi: 3.1.0
info:
  title: easyJet Deal Scout API
  version: 1.0.0
servers:
  - url: https://YOUR-RENDER-URL.onrender.com
paths:
  /search-flights:
    post:
      operationId: searchFlights
      summary: Search for cheap easyJet flights
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - origin
                - destination
                - date_from
                - date_to
                - passengers
              properties:
                origin:
                  type: string
                destination:
                  type: string
                date_from:
                  type: string
                  format: date
                date_to:
                  type: string
                  format: date
                passengers:
                  type: integer
                max_price:
                  type: number
                baggage:
                  type: boolean
      responses:
        "200":
          description: Flight search results

  /create-alert:
    post:
      operationId: createFlightAlert
      summary: Create a price alert
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - origin
                - destination
                - date_from
                - date_to
                - max_price
              properties:
                origin:
                  type: string
                destination:
                  type: string
                date_from:
                  type: string
                  format: date
                date_to:
                  type: string
                  format: date
                max_price:
                  type: number
                notification_channel:
                  type: string
                  enum: [email, telegram]
      responses:
        "200":
          description: Alert created
```

## Local test

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Then open:

```text
http://127.0.0.1:8000
```
