from datetime import datetime, timezone
from typing import Optional
import os
import httpx
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="AgriShield AI API", version="1.0.0", description="Climate-aware crop intelligence and farming assistant for Bangladesh.")
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

LOCATIONS = {
    "Bogura": {"lat": 24.8465, "lon": 89.3770, "district": "Bogura"},
    "Rajshahi": {"lat": 24.3745, "lon": 88.6042, "district": "Rajshahi"},
    "Dhaka": {"lat": 23.8103, "lon": 90.4125, "district": "Dhaka"},
    "Rangpur": {"lat": 25.7439, "lon": 89.2752, "district": "Rangpur"},
    "Mymensingh": {"lat": 24.7471, "lon": 90.4203, "district": "Mymensingh"},
    "Khulna": {"lat": 22.8456, "lon": 89.5403, "district": "Khulna"},
    "Sylhet": {"lat": 24.8949, "lon": 91.8687, "district": "Sylhet"},
    "Cumilla": {"lat": 23.4607, "lon": 91.1809, "district": "Cumilla"},
}

class FarmInput(BaseModel):
    district: str = "Bogura"
    upazila: str = "Shibganj"
    crop: str = "Boro rice"
    land_bigha: float = Field(default=1, gt=0, le=500)
    land_type: str = "Medium land"
    irrigation: str = "Tube-well"
    season: str = "Rabi"
    budget_bdt: float = Field(default=35000, ge=0)

class ProduceInput(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    category: str = "Vegetables"
    variety: str = "Local"
    price_bdt: float = Field(gt=0)
    quantity_kg: float = Field(gt=0)
    district: str = "Bogura"
    organic: bool = False
    description: str = ""

class ChatInput(BaseModel):
    question: str = Field(min_length=2, max_length=1000)
    crop: Optional[str] = None
    district: str = "Bogura"

PRODUCE = [
    {"id": 1, "name": "Himsagar Mango", "category": "Fruits", "variety": "Himsagar", "price_bdt": 75, "quantity_kg": 120, "district": "Rajshahi", "organic": True, "description": "Fresh seasonal mangoes from Rajshahi growers.", "image": "https://images.unsplash.com/photo-1553279768-865429fa0078?w=900&q=85"},
    {"id": 2, "name": "Desi Red Tomato", "category": "Vegetables", "variety": "Desi", "price_bdt": 42, "quantity_kg": 85, "district": "Bogura", "organic": True, "description": "Firm, locally grown tomatoes, harvested this morning.", "image": "https://images.unsplash.com/photo-1546094096-0df4bcaaa337?w=900&q=85"},
    {"id": 3, "name": "Fresh White Garlic", "category": "Vegetables", "variety": "White garlic", "price_bdt": 160, "quantity_kg": 40, "district": "Bogura", "organic": False, "description": "Naturally cured garlic bulbs.", "image": "https://images.unsplash.com/photo-1615477550927-6ec8445fc2f3?w=900&q=85"},
    {"id": 4, "name": "Diamond Potato", "category": "Vegetables", "variety": "Diamond", "price_bdt": 32, "quantity_kg": 250, "district": "Rangpur", "organic": False, "description": "Sorted table potatoes from Rangpur.", "image": "https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=900&q=85"},
    {"id": 5, "name": "Green Spinach", "category": "Vegetables", "variety": "Palong shak", "price_bdt": 28, "quantity_kg": 35, "district": "Dhaka", "organic": True, "description": "Tender leafy greens, carefully packed.", "image": "https://images.unsplash.com/photo-1576045057995-568f588f82fb?w=900&q=85"},
    {"id": 6, "name": "Golden Mustard Seed", "category": "Grains", "variety": "Local mustard", "price_bdt": 95, "quantity_kg": 90, "district": "Mymensingh", "organic": False, "description": "Cleaned mustard seed from local farms.", "image": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=900&q=85"},
]

KNOWLEDGE = [
    {"topic": "rice_heat", "keywords": ["rice", "boro", "heat", "temperature", "ধান", "গরম"], "answer": "For Boro rice, keep irrigation management aligned with the crop stage. During flowering, avoid water stress and monitor local heat alerts. Do not apply excess nitrogen during extreme heat. Confirm field-specific actions with a local agriculture extension officer.", "source": "Bangladesh Rice Research Institute (BRRI) cultivation guidance; verify the current local advisory."},
    {"topic": "tomato_rain", "keywords": ["tomato", "rain", "blight", "টমেটো", "বৃষ্টি"], "answer": "In wet weather, avoid overhead irrigation, improve drainage, and inspect lower leaves for water-soaked or dark lesions. Remove severely affected plant material safely. A photo-based diagnosis should be confirmed before applying any pesticide.", "source": "General integrated pest management guidance; confirm with DAE/plant pathology support."},
    {"topic": "irrigation", "keywords": ["water", "irrigation", "moisture", "পানি", "সেচ"], "answer": "Check soil moisture near the active root zone before irrigating. Prefer early morning irrigation where practical, and avoid watering immediately before forecast heavy rain. The right schedule depends on crop, soil texture, growth stage, and local conditions.", "source": "General water-efficient irrigation guidance; crop-specific schedule required."},
    {"topic": "soil", "keywords": ["soil", "ph", "fertilizer", "মাটি", "সার"], "answer": "Use a recent soil test to guide pH correction and fertilizer rates. Do not infer nutrient deficiency from leaf colour alone. Apply fertilizer according to crop stage and locally approved recommendations.", "source": "Bangladesh Soil Resource Development Institute (SRDI) soil-test approach."},
    {"topic": "flood", "keywords": ["flood", "waterlogging", "জলাবদ্ধ", "বন্যা"], "answer": "For waterlogging risk, clear drainage channels, protect stored seed and fertilizer above expected water level, and avoid field operations when soil is saturated. After floodwater recedes, assess crop damage before deciding on replanting.", "source": "General climate-resilient farm management; seek local DAE advice for field decisions."},
]

@app.get("/")
def root():
    from fastapi.responses import FileResponse
    index_file = os.path.join(os.path.dirname(__file__), "static", "index.html")
    return FileResponse(index_file)

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "AgriShield AI", "timestamp": datetime.now(timezone.utc).isoformat()}

@app.get("/api/dashboard")
def dashboard(district: str = "Bogura"):
    return {
        "district": district,
        "farm": {"land_bigha": 4.2, "active_crops": 3, "next_task": "Inspect tomato leaves", "farm_status": "Demo farm"},
        "metrics": [{"label": "Soil moisture", "value": "68", "unit": "%", "status": "Within demo target"}, {"label": "Temperature", "value": "29", "unit": "°C", "status": "Monitor afternoon heat"}, {"label": "Humidity", "value": "72", "unit": "%", "status": "Check fungal symptoms"}, {"label": "Soil pH", "value": "6.8", "unit": "", "status": "Illustrative reading"}],
        "alerts": [{"level": "watch", "title": "Rainfall watch", "detail": "Check the 3-day forecast before irrigation."}, {"level": "info", "title": "Crop scouting", "detail": "Inspect tomato lower leaves for early disease symptoms."}],
        "revenue": [{"month": "Jun", "value": 38000}, {"month": "Jul", "value": 44000}, {"month": "Aug", "value": 41000}, {"month": "Sep", "value": 52000}, {"month": "Oct", "value": 48000}, {"month": "Nov", "value": 61000}],
        "demo_mode": True,
    }

@app.get("/api/weather")
async def weather(district: str = "Bogura"):
    place = LOCATIONS.get(district, LOCATIONS["Bogura"])
    url = "https://api.open-meteo.com/v1/forecast"
    params = {"latitude": place["lat"], "longitude": place["lon"], "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,precipitation_sum,weather_code", "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m", "timezone": "Asia/Dhaka", "forecast_days": 6}
    try:
        async with httpx.AsyncClient(timeout=12) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
        daily = data.get("daily", {})
        days = []
        for i, day in enumerate(daily.get("time", [])):
            days.append({"date": day, "max_c": daily["temperature_2m_max"][i], "min_c": daily["temperature_2m_min"][i], "rain_probability": daily["precipitation_probability_max"][i], "rain_mm": daily["precipitation_sum"][i], "weather_code": daily["weather_code"][i]})
        return {"district": district, "current": data.get("current", {}), "days": days, "source": "Open-Meteo forecast API", "demo_mode": False}
    except Exception:
        return {"district": district, "current": {"temperature_2m": 29, "relative_humidity_2m": 72, "precipitation": 0, "wind_speed_10m": 8}, "days": [{"date": "Today", "max_c": 31, "min_c": 24, "rain_probability": 20, "rain_mm": 0.2, "weather_code": 2}, {"date": "Tomorrow", "max_c": 32, "min_c": 25, "rain_probability": 35, "rain_mm": 1.4, "weather_code": 3}, {"date": "Day 3", "max_c": 29, "min_c": 24, "rain_probability": 75, "rain_mm": 12, "weather_code": 61}, {"date": "Day 4", "max_c": 28, "min_c": 23, "rain_probability": 65, "rain_mm": 8, "weather_code": 61}, {"date": "Day 5", "max_c": 30, "min_c": 24, "rain_probability": 15, "rain_mm": 0, "weather_code": 1}, {"date": "Day 6", "max_c": 31, "min_c": 25, "rain_probability": 10, "rain_mm": 0, "weather_code": 0}], "source": "Illustrative fallback data (live weather unavailable)", "demo_mode": True}

@app.post("/api/assess-risk")
def assess_risk(farm: FarmInput):
    crop = farm.crop.lower()
    risk = 22
    factors = []
    if farm.land_type.lower().startswith("low"):
        risk += 22; factors.append("Low-lying land can retain excess water.")
    if farm.irrigation.lower() == "rain-fed":
        risk += 8; factors.append("Rain-fed farming is more exposed to rainfall variability.")
    if "tomato" in crop:
        risk += 10; factors.append("Tomato foliage needs closer monitoring during humid, wet periods.")
    if farm.season.lower() in ["monsoon", "kharif"]:
        risk += 12; factors.append("Monsoon season increases waterlogging and disease pressure.")
    risk = min(risk, 85)
    level = "High" if risk >= 60 else "Moderate" if risk >= 38 else "Low"
    return {"district": farm.district, "crop": farm.crop, "risk_score": risk, "risk_level": level, "factors": factors or ["No major risk factor was selected in this basic screening."], "recommendations": ["Check the latest local forecast before irrigation or spraying.", "Inspect the field at least twice weekly during high humidity.", "Keep drainage channels clear where waterlogging is possible."], "method": "Transparent rule-based screening prototype, not a validated predictive ML model.", "demo_mode": True}

@app.post("/api/farm-plan")
def farm_plan(farm: FarmInput):
    # Illustrative planning coefficients only; users must replace with local quotations and extension guidance.
    crop = farm.crop.lower()
    coefficients = {"boro rice": (26000, 22, 32), "aman rice": (23000, 20, 29), "tomato": (42000, 35, 55), "potato": (38000, 55, 85), "mango": (18000, 18, 30), "maize": (24000, 25, 38)}
    cost_per_bigha, low_yield, high_yield = coefficients.get(crop, (25000, 20, 35))
    total_cost = round(cost_per_bigha * farm.land_bigha)
    expected_yield = [round(low_yield * farm.land_bigha, 1), round(high_yield * farm.land_bigha, 1)]
    return {"crop": farm.crop, "land_bigha": farm.land_bigha, "estimated_cost_bdt": total_cost, "budget_bdt": farm.budget_bdt, "budget_gap_bdt": max(0, total_cost - farm.budget_bdt), "illustrative_yield_ton_range": expected_yield, "steps": ["Prepare land and confirm seed/seedling quality.", "Use soil-test results to finalize fertilizer plan.", "Monitor weather and irrigate according to crop stage.", "Scout for pests and disease every week.", "Harvest at crop-specific maturity and record batch details."], "notice": "Planning estimates are illustrative, not a guaranteed yield, price, or profit forecast. Confirm locally before spending."}

@app.get("/api/produce")
def list_produce(category: Optional[str] = None, search: Optional[str] = None):
    items = PRODUCE
    if category and category != "All": items = [p for p in items if p["category"] == category]
    if search: items = [p for p in items if search.lower() in p["name"].lower() or search.lower() in p["district"].lower()]
    return {"items": items, "count": len(items), "demo_mode": True}

@app.post("/api/produce")
def add_produce(item: ProduceInput):
    new_item = {"id": max([p["id"] for p in PRODUCE], default=0) + 1, **item.model_dump(), "image": "https://images.unsplash.com/photo-1542838132-92c53300491e?w=900&q=85"}
    PRODUCE.append(new_item)
    return {"item": new_item, "message": "Produce listing added to this demo session."}

@app.post("/api/disease/scan")
async def disease_scan(file: UploadFile = File(...)):
    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(status_code=415, detail="Upload a JPG, PNG, or WEBP image.")
    content = await file.read()
    if len(content) > 8 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Image must be 8 MB or smaller.")
    # No trained classifier is bundled. Never present a guessed label as a diagnosis.
    return {"status": "image_received", "filename": file.filename, "size_bytes": len(content), "diagnosis": None, "message": "Image upload is working. A validated crop-disease model is not connected yet, so this prototype will not guess a disease or pesticide. Use the symptom guide and consult a local plant pathology/DAE officer.", "next_steps": ["Photograph both sides of the leaf in natural light.", "Record crop, variety, plant age, and when symptoms began.", "Check whether nearby plants show the same symptoms.", "Seek confirmation before applying any pesticide."], "demo_mode": True}

@app.post("/api/assistant")
def assistant(payload: ChatInput):
    q = payload.question.lower()
    scored = []
    for item in KNOWLEDGE:
        score = sum(1 for word in item["keywords"] if word.lower() in q)
        if score: scored.append((score, item))
    if not scored:
        return {"answer": "I can help with basic crop, soil, irrigation, heat, rainfall, and waterlogging guidance. Please mention your crop, district, and the problem you see. For pesticide dosage, disease diagnosis, or urgent field decisions, consult a qualified local agriculture officer.", "source": "AgriShield safe-response guidance", "matched": False}
    item = sorted(scored, key=lambda x: x[0], reverse=True)[0][1]
    return {"answer": item["answer"], "source": item["source"], "matched": True, "topic": item["topic"]}

@app.get("/api/locations")
def locations():
    return {"locations": list(LOCATIONS.keys())}


# Serve the built React/Vite frontend from this same web service.
from fastapi.staticfiles import StaticFiles
_static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/", StaticFiles(directory=_static_dir, html=True), name="frontend")
