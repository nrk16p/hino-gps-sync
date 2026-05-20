import requests
import pandas as pd
import time
import json
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
)
log = logging.getLogger(__name__)

VEHICLES = [
    {'plate': '73-3160', 'plate_type': 'H', 'gps_vendor': 'hino', 'vid': 80812},
    {'plate': '73-3161', 'plate_type': 'H', 'gps_vendor': 'hino', 'vid': 80811},
    {'plate': '73-3162', 'plate_type': 'H', 'gps_vendor': 'hino', 'vid': 80810},
    {'plate': '73-3346', 'plate_type': 'H', 'gps_vendor': 'hino', 'vid': 81140},
    {'plate': '73-3343', 'plate_type': 'H', 'gps_vendor': 'hino', 'vid': 81141},
    {'plate': '73-3316', 'plate_type': 'H', 'gps_vendor': 'hino', 'vid': 81139},
    {'plate': '73-3315', 'plate_type': 'H', 'gps_vendor': 'hino', 'vid': 81138},
]

HINO_API_URL  = 'https://hino-api.onelink-iot.com/prod/fleet/V2/Infomation'
BACKEND_URL   = 'https://backend-tdm-qa.onrender.com/gpsdata'
DELAY         = 0.3
TIMEOUT       = 10


def fetch_gps(vid: int) -> dict:
    try:
        r = requests.get(
            HINO_API_URL,
            params={'vid': vid},
            headers={'Content-Type': 'application/json'},
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        gps = r.json().get('gps', {})
        return {
            'lat'    : gps.get('lat'),
            'lng'    : gps.get('lng'),
            'speed'  : gps.get('speed'),
            'gpsdate': gps.get('gpsdate'),
            'status' : 'ok',
        }
    except Exception as e:
        log.warning(f'vid={vid} fetch failed: {e}')
        return {'lat': None, 'lng': None, 'speed': None, 'gpsdate': None, 'status': str(e)}


def build_payload(df: pd.DataFrame) -> list:
    payload = []
    for _, row in df.iterrows():
        payload.append({
            'gps_id'        : str(row['vid']),
            'plate_master'  : row['plate'],
            'plate_type'    : row['plate_type'],
            'gps_vendor'    : 'hino',
            'current_latlng': f"{row['lat']},{row['lng']}" if row['lat'] and row['lng'] else '',
            'gps_updated_at': str(row['gpsdate']),
            'status'        : 'หยุด' if row['speed'] == 0 else 'วิ่ง',
        })
    return payload


def post_to_backend(payload: list) -> None:
    resp = requests.post(
        BACKEND_URL,
        json=payload,
        headers={'Content-Type': 'application/json'},
        timeout=30,
    )
    resp.raise_for_status()
    result = resp.json() if resp.text else []
    updated = len([r for r in result if r.get('gps_updated_at')])
    log.info(f'POST {resp.status_code} — sent={len(payload)}, updated={updated}')


def main():
    log.info(f'=== Hino GPS sync started — {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} ===')

    rows = []
    for i, v in enumerate(VEHICLES, 1):
        gps = fetch_gps(v['vid'])
        rows.append({**v, **gps})
        log.info(f'[{i}/{len(VEHICLES)}] {v["plate"]}  lat={gps["lat"]}  lng={gps["lng"]}  speed={gps["speed"]}  {gps["status"]}')
        time.sleep(DELAY)

    df = pd.DataFrame(rows)
    ok = df[df['status'] == 'ok']
    log.info(f'Fetch complete: {len(ok)}/{len(VEHICLES)} OK')

    if ok.empty:
        log.error('No GPS data fetched — aborting POST')
        return

    payload = build_payload(ok)
    post_to_backend(payload)
    log.info('=== Done ===')


if __name__ == '__main__':
    main()
