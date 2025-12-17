from fastapi import FastAPI, HTTPException, Header
#import hashlib
import requests

app = FastAPI()

NETWORK_API = "https://192.168.2.6/network/default/dashboard"
API_KEY = "vp0mZ7hUklZX/LFy9f4g/g"
MAKE_API_KEY = "make_network_health"

headers ={
    "Authorization": f"Bearer {API_KEY}"
}

def verify_make_key(x_api_key: str = Header(None)):
   if x_api_key  != MAKE_API_KEY:
      raise HTTPException(status_code=401, detail="Unauthorized")
   

@app.get("/device/config")
def get_config(device_id: str, x_api_key: str = Header(None)):
 verify_make_key(x_api_key)
 return{
  "message": "Endpoint is working",
  "device_id": device_id
 }
#from fastapi import HTTPException

@app.get("/device/health")
def get_health(device_id: str, x_api_key: str = Header(None)):
    verify_make_key(x_api_key)
    """
    Correct device health endpoint:
    - Pulls metrics from network API
    - Validates data
    - Calculates health score
    """

    try:
        # Call the network API to get device health/status
        response = requests.get(
            f"{NETWORK_API}/devices/{device_id}/status",
            headers=headers,
            verify=False  # local device HTTPS (temporary)
        )

        # If the device API fails
        if response.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail="Failed to fetch device health from network API"
            )

        # Convert JSON response to Python dictionary
        data = response.json()

        # Extract values safely (default to 0 if missing)
        cpu = float(data.get("cpu", 0))
        ram = float(data.get("ram", 0))
        temperature = float(data.get("temperature", 0))

        # Health score formula (simple and realistic)
        health_score = 100 - (
            cpu * 0.4 +
            ram * 0.3 +
            temperature * 0.3
        )

        return {
            "device_id": device_id,
            "cpu": cpu,
            "ram": ram,
            "temperature": temperature,
            "health_score": round(max(health_score, 0), 2),
            "status": "OK" if health_score >= 70 else "WARNING"
        }

    except Exception as e:
        # Catch unexpected errors
        raise HTTPException(status_code=500, detail=str(e)
        )

