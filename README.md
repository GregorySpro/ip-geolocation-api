# IP Geolocation API

Open source REST API for IP geolocation using MaxMind GeoLite2. Self-hostable, privacy-first.

## Features

- Country, city, timezone, coordinates
- Auto-detect caller's IP via `/geolocate/me`
- Uses MaxMind GeoLite2 (free, offline database)

## Setup — GeoLite2 database

1. Create a free account at https://dev.maxmind.com/
2. Download **GeoLite2-City.mmdb**
3. Place it in the project root

For Render: upload the `.mmdb` as a persistent disk or use Render's environment variables + a startup script to download it.

## Endpoints

### `GET /geolocate/{ip}`

```json
// GET /geolocate/8.8.8.8
{
  "ip": "8.8.8.8",
  "country_code": "US",
  "country_name": "United States",
  "continent": "North America",
  "city": "Mountain View",
  "postal_code": "94043",
  "latitude": 37.386,
  "longitude": -122.0838,
  "timezone": "America/Los_Angeles",
  "accuracy_radius_km": 1000
}
```

### `GET /geolocate/me`

Uses the IP of the incoming request.

### `GET /health`

Returns `{ "status": "ok", "database": "available" }`.

## Run locally

```bash
pip install -r requirements.txt
# Place GeoLite2-City.mmdb in project root
uvicorn main:app --reload
```

API docs available at `http://localhost:8000/docs`

## Deploy on Render

1. Push this repo to GitHub
2. Create a new Web Service on [render.com](https://render.com)
3. Add a **Persistent Disk** mounted at `/opt/render/project/src/` and upload `GeoLite2-City.mmdb`

## License

MIT
