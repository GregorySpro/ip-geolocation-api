import geoip2.database
import geoip2.errors
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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
BATCH_LIMIT = 10


class BatchRequest(BaseModel):
    ips: list[str]


def get_reader():
    if not DB_PATH.exists():
        raise HTTPException(
            status_code=503,
            detail="GeoLite2 database not found. Download it from https://dev.maxmind.com/geoip/geolite2-free-geolocation-data and place GeoLite2-City.mmdb in the project root.",
        )
    return geoip2.database.Reader(str(DB_PATH))


def lookup(reader, ip: str) -> dict:
    try:
        record = reader.city(ip)
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
    except geoip2.errors.AddressNotFoundError:
        return {"ip": ip, "error": "No data found for this IP address."}
    except Exception as e:
        return {"ip": ip, "error": f"Invalid IP address: {str(e)}"}


@app.get("/health")
def health():
    return {"status": "ok", "database": "available" if DB_PATH.exists() else "missing"}


@app.get("/geolocate/me")
def geolocate_me(request: Request):
    ip = request.headers.get("x-forwarded-for", request.client.host)
    ip = ip.split(",")[0].strip()
    with get_reader() as reader:
        result = lookup(reader, ip)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@app.get("/geolocate/{ip}")
def geolocate_ip(ip: str):
    with get_reader() as reader:
        result = lookup(reader, ip)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@app.post("/geolocate/batch")
def geolocate_batch(body: BatchRequest):
    if not body.ips:
        raise HTTPException(status_code=400, detail="IPs list cannot be empty.")
    if len(body.ips) > BATCH_LIMIT:
        raise HTTPException(status_code=400, detail=f"Maximum {BATCH_LIMIT} IPs per batch.")
    with get_reader() as reader:
        results = [lookup(reader, ip.strip()) for ip in body.ips]
    return {"count": len(results), "results": results}


@app.get("/country/{ip}")
def get_country(ip: str):
    with get_reader() as reader:
        try:
            record = reader.city(ip)
            return {
                "ip": ip,
                "country_code": record.country.iso_code,
                "country_name": record.country.name,
                "continent": record.continent.name,
            }
        except geoip2.errors.AddressNotFoundError:
            raise HTTPException(status_code=404, detail=f"No data found for IP: {ip}")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid IP: {str(e)}")


@app.get("/timezone/{ip}")
def get_timezone(ip: str):
    with get_reader() as reader:
        try:
            record = reader.city(ip)
            return {
                "ip": ip,
                "timezone": record.location.time_zone,
                "latitude": record.location.latitude,
                "longitude": record.location.longitude,
            }
        except geoip2.errors.AddressNotFoundError:
            raise HTTPException(status_code=404, detail=f"No data found for IP: {ip}")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid IP: {str(e)}")
