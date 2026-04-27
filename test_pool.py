from fastapi.testclient import TestClient
from backend.main import app
import datetime

client = TestClient(app)

print("Creating pool...")
res = client.post("/api/pools/", json={
    "source": "A",
    "destination": "B",
    "departure_time": (datetime.datetime.utcnow() + datetime.timedelta(days=1)).isoformat() + "Z",
    "luggage": "None",
    "open_to_pool": True,
    "user": {
        "name": "Creator",
        "phone": "0000000000",
        "year": "1st Year",
        "department": "CS"
    }
})
print(res.status_code, res.text)
if res.status_code == 200:
    pool_id = res.json()["id"]
    print(f"Created pool {pool_id}, now joining...")
    join_res = client.post(f"/api/pools/{pool_id}/join", json={
        "user": {
            "name": "Joiner",
            "phone": "1111111111",
            "year": "2nd Year",
            "department": "CS"
        }
    })
    print(join_res.status_code, join_res.text)

