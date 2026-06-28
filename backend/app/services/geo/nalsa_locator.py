"""
Nearest NALSA legal aid centers via Haversine distance on a bundled dataset.
The JSON is generated once and committed to the repo so no external API is needed.
"""
from __future__ import annotations
import json, math, logging
from pathlib import Path
from typing import List
from app.models.schemas import NearbyCenter

log = logging.getLogger(__name__)

# Minimal built-in dataset — covers state DLSA headquarters across India
_BUILT_IN_CENTERS = [
    {"name": "DLSA Mumbai", "address": "City Civil Court, Mumbai, Maharashtra", "phone": "022-22620956", "lat": 18.9322, "lon": 72.8264},
    {"name": "DLSA Delhi", "address": "Patiala House Courts, New Delhi", "phone": "011-23384573", "lat": 28.6139, "lon": 77.2090},
    {"name": "DLSA Bangalore", "address": "City Civil Court, Bangalore, Karnataka", "phone": "080-22868086", "lat": 12.9716, "lon": 77.5946},
    {"name": "DLSA Chennai", "address": "High Court Campus, Chennai, Tamil Nadu", "phone": "044-25340519", "lat": 13.0827, "lon": 80.2707},
    {"name": "DLSA Kolkata", "address": "City Civil Court, Kolkata, West Bengal", "phone": "033-22487900", "lat": 22.5726, "lon": 88.3639},
    {"name": "DLSA Hyderabad", "address": "District Courts, Hyderabad, Telangana", "phone": "040-23220533", "lat": 17.3850, "lon": 78.4867},
    {"name": "DLSA Pune", "address": "District Court, Pune, Maharashtra", "phone": "020-26056411", "lat": 18.5204, "lon": 73.8567},
    {"name": "DLSA Ahmedabad", "address": "City Civil Court, Ahmedabad, Gujarat", "phone": "079-25506636", "lat": 23.0225, "lon": 72.5714},
    {"name": "DLSA Jaipur", "address": "District Courts, Jaipur, Rajasthan", "phone": "0141-2700200", "lat": 26.9124, "lon": 75.7873},
    {"name": "DLSA Lucknow", "address": "District Courts, Lucknow, Uttar Pradesh", "phone": "0522-2239513", "lat": 26.8467, "lon": 80.9462},
    {"name": "DLSA Bhopal", "address": "District Court, Bhopal, Madhya Pradesh", "phone": "0755-2551052", "lat": 23.2599, "lon": 77.4126},
    {"name": "DLSA Patna", "address": "District Courts, Patna, Bihar", "phone": "0612-2215145", "lat": 25.5941, "lon": 85.1376},
    {"name": "DLSA Chandigarh", "address": "District Courts, Chandigarh", "phone": "0172-2700966", "lat": 30.7333, "lon": 76.7794},
    {"name": "DLSA Guwahati", "address": "District Courts, Guwahati, Assam", "phone": "0361-2543203", "lat": 26.1445, "lon": 91.7362},
    {"name": "DLSA Bhubaneswar", "address": "District Court, Bhubaneswar, Odisha", "phone": "0674-2391516", "lat": 20.2961, "lon": 85.8245},
]


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_lat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


def find_nearby_centers(lat: float, lon: float, max_results: int = 3) -> List[NearbyCenter]:
    """Return the `max_results` nearest NALSA centers sorted by distance."""
    # Try loading an extended dataset from disk first
    data_path = Path("data/processed/nalsa_centers.json")
    if data_path.exists():
        try:
            centers = json.loads(data_path.read_text())
        except Exception:
            centers = _BUILT_IN_CENTERS
    else:
        centers = _BUILT_IN_CENTERS

    results = [
        NearbyCenter(
            name=c["name"],
            address=c["address"],
            phone=c.get("phone", "1800-11-0031"),
            distance_km=round(_haversine(lat, lon, c["lat"], c["lon"]), 1),
        )
        for c in centers
    ]
    results.sort(key=lambda x: x.distance_km)
    return results[:max_results]
