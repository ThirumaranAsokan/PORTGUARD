import asyncio
import websockets
import json
import os
import requests
from datetime import datetime, timezone

AIS_API_KEY = os.getenv("AIS_API_KEY")
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME")

AIRTABLE_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    "Content-Type": "application/json"
}

async def process_position_report(message):
    try:
        report = message["Message"]["PositionReport"]
        data = {
            "fields": {
                "MMSI": report["UserID"],
                "Latitude": report["Latitude"],
                "Longitude": report["Longitude"],
                "Speed": report["SOG"],
                "Course": report["COG"],
                "Timestamp": datetime.now(timezone.utc).isoformat()
            }
        }
        requests.post(AIRTABLE_URL, headers=HEADERS, json=data)
    except Exception as e:
        print(f"Error: {e}")

async def connect():
    while True:
        try:
            async with websockets.connect("wss://stream.aisstream.io/v0/stream") as ws:
                print("Connected to AISstream")
                await ws.send(json.dumps({
                    "APIKey": AIS_API_KEY,
                    "BoundingBoxes": [[[-90, -180], [90, 180]]],
                    "FilterMessageTypes": ["PositionReport"]
                }))
                async for msg in ws:
                    await process_position_report(json.loads(msg))
        except Exception as e:
            print(f"Connection error: {e}. Reconnecting in 5s")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(connect())
