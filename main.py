import geoip2.database
import geoip2.errors
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="IP Geolocation API",
    description="Open source IP geolocation API using MaxMind GeoLite2 database.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = Path(__file__).parent / "GeoLite2-City.mmdb"


def get_reader():
    if not DB_PATH.exists():
        raise HTTPException(
            status_code=503,
            detail="GeoLite2 database not found. Download it from https://dev.maxmind.com/geoip/geolite2-free-geolocation-data and place GeoLite2-City.mmdb in the project root.",
        )
    return geoip2.database.Reader(str(DB_PATH))


def build_response(ip: str, record) -> dict:
    return {
        "ip": ip,
        "country_code": record.country.iso_code,
        "country_name": record.country.name,
        "continent": record.continent.name,
        "city": record.city.name,
        "postal_code": record.postal.code,
        "latitude": record.location.latitude,
        "longitude": record.location.longitude,
        "timezone": record.location.time_zone,
        "accuracy_radius_km": record.location.accuracy_radius,
    }


@app.get("/health")
def health():
    db_available = DB_PATH.exists()
    return {"status": "ok", "database": "available" if db_available else "missing"}


@app.get("/geolocate/me")
def geolocate_me(request: Request):
    ip = request.headers.get("x-forwarded-for", request.client.host)
    ip = ip.split(",")[0].strip()
    return geolocate_ip(ip)


@app.get("/geolocate/{ip}")
def geolocate_ip(ip: str):
    if not ip:
        raise HTTPException(status_code=400, detail="IP address is required.")

    with get_reader() as reader:
        try:
            record = reader.city(ip)
            return build_response(ip, record)
        except geoip2.errors.AddressNotFoundError:
            raise HTTPException(status_code=404, detail=f"No data found for IP: {ip}")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid IP address: {str(e)}")
