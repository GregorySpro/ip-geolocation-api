#!/bin/bash
set -e

DB_FILE="GeoLite2-City.mmdb"

if [ ! -f "$DB_FILE" ]; then
  if [ -z "$MAXMIND_LICENSE_KEY" ]; then
    echo "ERROR: MAXMIND_LICENSE_KEY is not set and database is missing."
    exit 1
  fi
  echo "Downloading GeoLite2-City database..."
  curl -f -L \
    "https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-City&license_key=${MAXMIND_LICENSE_KEY}&suffix=tar.gz" \
    -o /tmp/geolite2.tar.gz
  tar -xzf /tmp/geolite2.tar.gz -C /tmp/
  find /tmp -name "GeoLite2-City.mmdb" -exec cp {} . \;
  rm -rf /tmp/geolite2.tar.gz /tmp/GeoLite2-City_*
  echo "Database ready: $(du -h $DB_FILE | cut -f1)"
else
  echo "Database already present: $(du -h $DB_FILE | cut -f1)"
fi

exec uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}" --proxy-headers --forwarded-allow-ips='*'
