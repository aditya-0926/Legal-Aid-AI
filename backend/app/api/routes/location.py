from fastapi import APIRouter, Query
from app.services.geo.nalsa_locator import find_nearby_centers

router = APIRouter(prefix="/location", tags=["location"])


@router.get("/centers")
def get_centers(lat: float = Query(..., ge=-90, le=90), lon: float = Query(..., ge=-180, le=180)):
    return find_nearby_centers(lat, lon)
