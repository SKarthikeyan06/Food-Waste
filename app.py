"""
The Conscious Observer — Food Waste Management Platform
Flask Backend (app.py)

Tech Stack: Python Flask + Supabase (PostgreSQL) + Random Forest AI
Author: FoodWise AI Team
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import datetime
import random
import math

# ─── Optional: uncomment when Supabase + sklearn are installed ───
# from supabase import create_client, Client
# from sklearn.ensemble import RandomForestRegressor
# from sklearn.preprocessing import LabelEncoder
# import numpy as np
# import pandas as pd

app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)

# ─────────────────────────────────────────────
# CONFIG  (replace with real Supabase keys)
# ─────────────────────────────────────────────
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-public-key"

# supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# ─────────────────────────────────────────────
# IN-MEMORY MOCK DATA  (replace with Supabase)
# ─────────────────────────────────────────────
MOCK_USERS = [
    {"id": "u1", "name": "Arjun Kumar",  "email": "canteen@college.edu",  "role": "canteen",  "institution": "VIT Chennai"},
    {"id": "u2", "name": "Priya NGO",    "email": "ngo@hope.org",          "role": "ngo",      "institution": "Hope Foundation"},
    {"id": "u3", "name": "Dr. Rajan",    "email": "admin@college.edu",     "role": "admin",    "institution": "VIT Chennai"},
    {"id": "u4", "name": "Ms. Lakshmi", "email": "welfare@college.edu",   "role": "welfare",  "institution": "VIT Chennai"},
]

MOCK_FOOTFALL = [
    {"date": "2024-01-08", "actual": 820,  "predicted": 810, "attendance_pct": 92, "event_flag": False},
    {"date": "2024-01-09", "actual": 790,  "predicted": 805, "attendance_pct": 88, "event_flag": False},
    {"date": "2024-01-10", "actual": 860,  "predicted": 850, "attendance_pct": 95, "event_flag": True},
    {"date": "2024-01-11", "actual": 910,  "predicted": 895, "attendance_pct": 98, "event_flag": True},
    {"date": "2024-01-12", "actual": 780,  "predicted": 795, "attendance_pct": 86, "event_flag": False},
    {"date": "2024-01-13", "actual": 420,  "predicted": 440, "attendance_pct": 45, "event_flag": False},
    {"date": "2024-01-14", "actual": 380,  "predicted": 370, "attendance_pct": 40, "event_flag": False},
]

MOCK_FOOD_ITEMS = [
    {"id": "f1", "name": "Rice",       "qty_prepared": 80,  "qty_remaining": 75, "unit": "kg", "price": 30, "shelf_life_hrs": 6,  "status": "urgent"},
    {"id": "f2", "name": "Dal Tadka",  "qty_prepared": 40,  "qty_remaining": 28, "unit": "kg", "price": 25, "shelf_life_hrs": 5,  "status": "warning"},
    {"id": "f3", "name": "Mixed Sabzi","qty_prepared": 30,  "qty_remaining": 12, "unit": "kg", "price": 35, "shelf_life_hrs": 4,  "status": "safe"},
    {"id": "f4", "name": "Chapati",    "qty_prepared": 200, "qty_remaining": 40, "unit": "pcs","price": 5,  "shelf_life_hrs": 3,  "status": "urgent"},
    {"id": "f5", "name": "Curd",       "qty_prepared": 20,  "qty_remaining": 8,  "unit": "kg", "price": 15, "shelf_life_hrs": 8,  "status": "safe"},
]

MOCK_NGO_PARTNERS = [
    {"id": "n1", "name": "Hope Foundation",  "type": "NGO",        "capacity_kg": 120, "is_active": True,  "area": "Anna Nagar"},
    {"id": "n2", "name": "SwiftDeliver",     "type": "CRO",        "capacity_kg": 80,  "is_active": True,  "area": "T. Nagar"},
    {"id": "n3", "name": "Green Farm",       "type": "Farm",       "capacity_kg": 200, "is_active": False, "area": "Tambaram"},
    {"id": "n4", "name": "PetCare NGO",      "type": "Pet Keeper", "capacity_kg": 50,  "is_active": True,  "area": "Velachery"},
    {"id": "n5", "name": "Annadaata",        "type": "NGO",        "capacity_kg": 150, "is_active": True,  "area": "Adyar"},
]

MOCK_REDISTRIBUTION = [
    {"id": "r1", "food_item": "Rice 75kg",   "phase": 2, "status": "pending",   "urgency": "high",   "ngo": "Hope Foundation"},
    {"id": "r2", "food_item": "Dal 28kg",    "phase": 1, "status": "accepted",  "urgency": "medium", "ngo": "SwiftDeliver"},
    {"id": "r3", "food_item": "Chapati 40pc","phase": 2, "status": "redirected","urgency": "high",   "ngo": "PetCare NGO"},
]

MOCK_DELIVERIES = [
    {"id": "d1", "request_id": "r1", "driver": "Marcus Chen",    "status": "in_transit", "pickup": "A-Block Canteen", "destination": "Hope Foundation"},
    {"id": "d2", "request_id": "r2", "driver": "Sarah Jenkins",  "status": "delivered",  "pickup": "B-Block Canteen", "destination": "Welfare Centre"},
    {"id": "d3", "request_id": "r3", "driver": "Elena Rodriguez","status": "assigned",   "pickup": "Hostel Canteen",  "destination": "PetCare NGO"},
]

MOCK_CALENDAR_EVENTS = [
    {"id": "c1", "title": "Fall Finals Week",      "type": "Exam",     "start_date": "2023-12-12", "end_date": "2023-12-18", "impact_pct": 30},
    {"id": "c2", "title": "Global Biotech Expo",   "type": "Festival", "start_date": "2024-01-05", "end_date": "2024-01-06", "impact_pct": 15},
    {"id": "c3", "title": "Spring Orientation",    "type": "Semester", "start_date": "2024-01-18", "end_date": "2024-01-19", "impact_pct": 10},
    {"id": "c4", "title": "Tech Conf 2024",        "type": "Event",    "start_date": "2024-03-12", "end_date": "2024-03-12", "impact_pct": 25},
]

MOCK_IMPACT_LOGS = [
    {"month": "Oct", "kg_redistributed": 420, "kg_fertilizer": 60,  "kg_animal_feed": 30, "co2_saved": 110, "people_fed": 210},
    {"month": "Nov", "kg_redistributed": 510, "kg_fertilizer": 75,  "kg_animal_feed": 38, "co2_saved": 130, "people_fed": 255},
    {"month": "Dec", "kg_redistributed": 490, "kg_fertilizer": 70,  "kg_animal_feed": 35, "co2_saved": 125, "people_fed": 245},
    {"month": "Jan", "kg_redistributed": 580, "kg_fertilizer": 90,  "kg_animal_feed": 42, "co2_saved": 145, "people_fed": 290},
    {"month": "Feb", "kg_redistributed": 620, "kg_fertilizer": 100, "kg_animal_feed": 48, "co2_saved": 158, "people_fed": 310},
    {"month": "Mar", "kg_redistributed": 710, "kg_fertilizer": 115, "kg_animal_feed": 55, "co2_saved": 178, "people_fed": 355},
]


# ─────────────────────────────────────────────
# RANDOM FOREST AI  (mock implementation)
# Replace with real sklearn when pandas is installed
# ─────────────────────────────────────────────

def mock_random_forest_predict(
    attendance_pct: float,
    event_flag: bool,
    seasonal_factor: float,
    day_of_week: int,
    employee_count: int = 2400
) -> dict:
    """
    Mock Random Forest footfall prediction.
    Replace body with:
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        prediction = model.predict([[...]])[0]
    """
    base = employee_count * 0.35
    att_contribution  = attendance_pct * 4.2    # feature weight: 42%
    event_contribution = 50 if event_flag else 0 # feature weight: 28%
    seasonal_contribution = seasonal_factor * 30  # feature weight: 19%

    # Weekend penalty
    weekend_factor = 0.48 if day_of_week >= 5 else 1.0

    raw = (base + att_contribution + event_contribution + seasonal_contribution) * weekend_factor
    prediction = int(raw + random.gauss(0, 12))  # add noise

    return {
        "predicted_footfall": max(50, prediction),
        "confidence": round(random.uniform(0.88, 0.96), 3),
        "r2_score": 0.91,
        "mae": 42,
        "feature_importances": {
            "attendance": 0.42,
            "calendar":   0.28,
            "seasonal":   0.19,
            "behavioural":0.11
        },
        "algorithm": "Random Forest",
        "n_estimators": 100,
        "training_window_days": 7,
        "model_version": "v2.1"
    }


def calculate_waste_prediction(predicted_footfall: int, avg_kg_per_person: float = 0.28) -> dict:
    """Predict food waste based on footfall and prepare suggestions."""
    predicted_consumption = predicted_footfall * avg_kg_per_person
    safety_buffer = 1.08
    recommended_prep = predicted_consumption * safety_buffer
    
    return {
        "predicted_consumption_kg": round(predicted_consumption, 1),
        "recommended_preparation_kg": round(recommended_prep, 1),
        "expected_surplus_kg": round(recommended_prep * 0.08, 1),
        "waste_reduction_tip": "Prepare in 3 batches: 60% at open, 25% at noon, 15% top-up"
    }


def dual_phase_alert(food_item: dict) -> dict:
    """
    Dual-phase alert logic:
    Phase 1: Within expiry → reduce price
    Phase 2A: Small surplus + near expiry → NGO request
    Phase 2B: NGO declines → CRO to needy
    Phase 3: Expired → fertilizer or animal feed via NGO
    """
    hours_left = food_item.get("shelf_life_hrs", 0)
    qty = food_item.get("qty_remaining", 0)

    if hours_left > 4:
        return {"phase": 1, "action": "reduce_price", "discount_pct": 30,
                "message": f"Reduce price by 30% to clear {qty} {food_item['unit']} of {food_item['name']}"}
    elif hours_left > 2:
        return {"phase": 2, "sub_phase": "A", "action": "ngo_request",
                "priority": "medium", "message": f"Send {qty} {food_item['unit']} to NGO network"}
    elif hours_left > 0:
        return {"phase": 2, "sub_phase": "B", "action": "cro_delivery",
                "priority": "urgent", "message": f"URGENT: dispatch via CRO to nearest shelter"}
    else:
        path = "animal_feed" if qty < 30 else "fertilizer"
        return {"phase": 3, "action": path, "priority": "expired",
                "message": f"Expired: redirect {qty} {food_item['unit']} to {path.replace('_', ' ')}"}


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def ok(data, status=200):
    return jsonify({"success": True, "data": data}), status

def err(message, status=400):
    return jsonify({"success": False, "error": message}), status

def _now():
    return datetime.datetime.utcnow().isoformat() + "Z"


# ─────────────────────────────────────────────
# ROUTES — SERVE FRONTEND
# ─────────────────────────────────────────────

@app.route("/")
def index():
    """Serve the single-page frontend."""
    return send_from_directory(".", "index.html")


# ─────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────

@app.route("/api/auth/register", methods=["POST"])
def register():
    """
    POST /api/auth/register
    Body: { name, email, password, role, institution }
    Returns: { user, token }
    """
    body = request.get_json() or {}
    email = body.get("email", "").strip().lower()
    name  = body.get("name", "").strip()
    role  = body.get("role", "canteen")
    inst  = body.get("institution", "").strip()

    if not email or not name:
        return err("Name and email are required")

    # Single DB check — same list used by login
    if any(u["email"] == email for u in MOCK_USERS):
        return err("Email already registered. Please sign in instead.", 409)

    new_user = {
        "id":          f"u{len(MOCK_USERS) + 1}",
        "name":        name,
        "email":       email,
        "role":        role,
        "institution": inst,
    }
    MOCK_USERS.append(new_user)   # single source of truth

    token = f"demo_token_{new_user['id']}_{int(datetime.datetime.utcnow().timestamp())}"
    return ok({"user": new_user, "token": token, "expires_in": 3600}, 201)


@app.route("/api/auth/login", methods=["POST"])
def login():
    """
    POST /api/auth/login
    Body: { email, password, role }
    Returns: { user, token }
    """
    body = request.get_json() or {}
    email = body.get("email", "").lower()
    role  = body.get("role", "canteen")

    user = next((u for u in MOCK_USERS if u["email"] == email or u["role"] == role), None)
    if not user:
        user = MOCK_USERS[0]  # demo: allow any login

    # In production: supabase.auth.sign_in_with_password({"email": email, "password": password})
    token = f"demo_token_{user['id']}_{int(datetime.datetime.utcnow().timestamp())}"

    return ok({"user": user, "token": token, "expires_in": 3600})


@app.route("/api/auth/logout", methods=["POST"])
def logout():
    return ok({"message": "Logged out successfully"})


# ─────────────────────────────────────────────
# AI PREDICTION
# ─────────────────────────────────────────────

@app.route("/api/ai/predict-footfall", methods=["POST"])
def predict_footfall():
    """
    POST /api/ai/predict-footfall
    Body: { attendance_pct, event_flag, seasonal_factor, day_of_week, employee_count }
    Returns: AI prediction result
    """
    body = request.get_json() or {}
    attendance_pct   = float(body.get("attendance_pct", 88))
    event_flag       = bool(body.get("event_flag", False))
    seasonal_factor  = float(body.get("seasonal_factor", 1.0))
    day_of_week      = int(body.get("day_of_week", datetime.datetime.today().weekday()))
    employee_count   = int(body.get("employee_count", 2400))

    prediction = mock_random_forest_predict(
        attendance_pct, event_flag, seasonal_factor, day_of_week, employee_count
    )
    waste_info = calculate_waste_prediction(prediction["predicted_footfall"])

    return ok({
        "prediction": prediction,
        "waste_forecast": waste_info,
        "timestamp": _now()
    })


@app.route("/api/ai/weekly-forecast", methods=["GET"])
def weekly_forecast():
    """GET /api/ai/weekly-forecast — 7-day footfall forecast."""
    today = datetime.date.today()
    forecast = []
    for i in range(7):
        day = today + datetime.timedelta(days=i)
        dow = day.weekday()
        att = random.uniform(75, 98) if dow < 5 else random.uniform(35, 50)
        ev = random.random() < 0.15
        result = mock_random_forest_predict(att, ev, 1.0, dow)
        forecast.append({
            "date": str(day),
            "day": ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"][dow],
            "predicted_footfall": result["predicted_footfall"],
            "event_flag": ev,
            "confidence": result["confidence"]
        })
    return ok(forecast)


@app.route("/api/ai/anomalies", methods=["GET"])
def get_anomalies():
    """GET /api/ai/anomalies — Predictive anomalies detected today."""
    anomalies = [
        {"id": "a1", "type": "low_footfall",  "severity": "warning",
         "message": "Unusually low footfall detected at 10:30 AM",
         "suggestion": "Reduce preparation of 'Hot Plate 1' by 15% to avoid waste.",
         "time": "2 mins ago"},
        {"id": "a2", "type": "ngo_confirmed", "severity": "info",
         "message": "NGO Pickup confirmed for 6:00 PM",
         "suggestion": "Green Hearts Food Bank will collect 24kg of surplus proteins.",
         "time": "45 mins ago"},
    ]
    return ok(anomalies)


# ─────────────────────────────────────────────
# FOOTFALL RECORDS
# ─────────────────────────────────────────────

@app.route("/api/footfall", methods=["GET"])
def get_footfall():
    """GET /api/footfall?days=7 — historical footfall records."""
    days = int(request.args.get("days", 7))
    return ok(MOCK_FOOTFALL[-days:])


@app.route("/api/footfall", methods=["POST"])
def log_footfall():
    """POST /api/footfall — log today's actual footfall."""
    body = request.get_json() or {}
    record = {
        "date": body.get("date", str(datetime.date.today())),
        "actual": body.get("actual", 0),
        "predicted": body.get("predicted", 0),
        "attendance_pct": body.get("attendance_pct", 0),
        "event_flag": body.get("event_flag", False),
        "recorded_at": _now()
    }
    # In production: supabase.table("footfall").insert(record).execute()
    MOCK_FOOTFALL.append(record)
    return ok(record, 201)


# ─────────────────────────────────────────────
# FOOD ITEMS (SURPLUS)
# ─────────────────────────────────────────────

@app.route("/api/food-items", methods=["GET"])
def get_food_items():
    """GET /api/food-items?status=urgent — list food items with optional filter."""
    status = request.args.get("status")
    items = MOCK_FOOD_ITEMS
    if status:
        items = [i for i in items if i["status"] == status]

    # Attach dual-phase alert to each item
    enriched = []
    for item in items:
        enriched.append({**item, "alert": dual_phase_alert(item)})

    return ok(enriched)


@app.route("/api/food-items", methods=["POST"])
def add_food_item():
    """POST /api/food-items — log new surplus food item."""
    body = request.get_json() or {}
    required = ["name", "qty_prepared", "unit", "shelf_life_hrs"]
    for field in required:
        if field not in body:
            return err(f"Missing required field: {field}")

    item = {
        "id": f"f{len(MOCK_FOOD_ITEMS)+1}",
        "name": body["name"],
        "category": body.get("category", "Main Course"),
        "qty_prepared": float(body["qty_prepared"]),
        "qty_remaining": float(body.get("qty_remaining", body["qty_prepared"])),
        "unit": body["unit"],
        "price": float(body.get("price", 0)),
        "discounted_price": None,
        "shelf_life_hrs": int(body["shelf_life_hrs"]),
        "status": "safe",
        "created_at": _now()
    }
    item["alert"] = dual_phase_alert(item)

    # In production: supabase.table("food_items").insert(item).execute()
    MOCK_FOOD_ITEMS.append(item)
    return ok(item, 201)


@app.route("/api/food-items/<item_id>/reduce-price", methods=["POST"])
def reduce_price(item_id):
    """POST /api/food-items/<id>/reduce-price — apply discount to near-expiry item."""
    body = request.get_json() or {}
    discount = int(body.get("discount_pct", 40))
    item = next((i for i in MOCK_FOOD_ITEMS if i["id"] == item_id), None)
    if not item:
        return err("Food item not found", 404)
    item["discounted_price"] = round(item["price"] * (1 - discount / 100), 2)
    item["status"] = "discounted"
    return ok({"item_id": item_id, "new_price": item["discounted_price"], "discount_pct": discount})


# ─────────────────────────────────────────────
# REDISTRIBUTION REQUESTS
# ─────────────────────────────────────────────

@app.route("/api/redistribution", methods=["GET"])
def get_redistribution():
    """GET /api/redistribution — all redistribution requests."""
    return ok(MOCK_REDISTRIBUTION)


@app.route("/api/redistribution", methods=["POST"])
def create_redistribution():
    """POST /api/redistribution — create a new redistribution request."""
    body = request.get_json() or {}
    req = {
        "id": f"r{len(MOCK_REDISTRIBUTION)+1}",
        "food_item": body.get("food_item", "Unknown item"),
        "food_item_id": body.get("food_item_id"),
        "canteen_id": body.get("canteen_id"),
        "ngo_id": body.get("ngo_id"),
        "phase": body.get("phase", 1),
        "status": "pending",
        "urgency": body.get("urgency", "medium"),
        "created_at": _now()
    }
    MOCK_REDISTRIBUTION.append(req)
    return ok(req, 201)


@app.route("/api/redistribution/<req_id>/accept", methods=["POST"])
def accept_redistribution(req_id):
    """POST /api/redistribution/<id>/accept — NGO/CRO accepts request."""
    req = next((r for r in MOCK_REDISTRIBUTION if r["id"] == req_id), None)
    if not req:
        return err("Request not found", 404)
    req["status"] = "accepted"
    req["responded_at"] = _now()

    # Auto-create delivery
    delivery = {
        "id": f"d{len(MOCK_DELIVERIES)+1}",
        "request_id": req_id,
        "status": "assigned",
        "assigned_at": _now()
    }
    MOCK_DELIVERIES.append(delivery)
    return ok({"request": req, "delivery": delivery})


@app.route("/api/redistribution/<req_id>/decline", methods=["POST"])
def decline_redistribution(req_id):
    """POST /api/redistribution/<id>/decline — NGO declines, trigger Phase 2B."""
    req = next((r for r in MOCK_REDISTRIBUTION if r["id"] == req_id), None)
    if not req:
        return err("Request not found", 404)
    req["status"] = "declined"
    req["responded_at"] = _now()
    return ok({
        "request": req,
        "next_action": "cro_delivery",
        "message": "NGO declined. Redirecting to CRO delivery partner for needy/students."
    })


# ─────────────────────────────────────────────
# DELIVERIES
# ─────────────────────────────────────────────

@app.route("/api/deliveries", methods=["GET"])
def get_deliveries():
    """GET /api/deliveries?status=in_transit — list deliveries."""
    status = request.args.get("status")
    deliveries = MOCK_DELIVERIES
    if status:
        deliveries = [d for d in deliveries if d["status"] == status]
    return ok(deliveries)


@app.route("/api/deliveries/<delivery_id>/update-status", methods=["POST"])
def update_delivery(delivery_id):
    """POST /api/deliveries/<id>/update-status — update delivery step."""
    body = request.get_json() or {}
    delivery = next((d for d in MOCK_DELIVERIES if d["id"] == delivery_id), None)
    if not delivery:
        return err("Delivery not found", 404)
    new_status = body.get("status", delivery["status"])
    delivery["status"] = new_status
    if new_status == "delivered":
        delivery["delivered_at"] = _now()
    return ok(delivery)


# ─────────────────────────────────────────────
# NGO PARTNERS
# ─────────────────────────────────────────────

@app.route("/api/ngo-partners", methods=["GET"])
def get_ngo_partners():
    """GET /api/ngo-partners — list all NGO/CRO partners."""
    active_only = request.args.get("active") == "true"
    partners = [p for p in MOCK_NGO_PARTNERS if p["is_active"]] if active_only else MOCK_NGO_PARTNERS
    return ok(partners)


@app.route("/api/ngo-partners", methods=["POST"])
def register_ngo():
    """POST /api/ngo-partners — register a new NGO/CRO partner."""
    body = request.get_json() or {}
    partner = {
        "id": f"n{len(MOCK_NGO_PARTNERS)+1}",
        "name": body.get("name", "New Partner"),
        "type": body.get("type", "NGO"),
        "contact_person": body.get("contact_person", ""),
        "phone": body.get("phone", ""),
        "area": body.get("area", ""),
        "capacity_kg": float(body.get("capacity_kg", 50)),
        "accepts_animal_feed": bool(body.get("accepts_animal_feed", False)),
        "is_active": True,
        "created_at": _now()
    }
    MOCK_NGO_PARTNERS.append(partner)
    return ok(partner, 201)


# ─────────────────────────────────────────────
# CALENDAR EVENTS
# ─────────────────────────────────────────────

@app.route("/api/calendar-events", methods=["GET"])
def get_calendar_events():
    """GET /api/calendar-events — list all calendar events."""
    return ok(MOCK_CALENDAR_EVENTS)


@app.route("/api/calendar-events", methods=["POST"])
def add_calendar_event():
    """POST /api/calendar-events — add a new academic/institutional event."""
    body = request.get_json() or {}
    event = {
        "id": f"c{len(MOCK_CALENDAR_EVENTS)+1}",
        "title": body.get("title", "New Event"),
        "type": body.get("type", "Event"),
        "start_date": body.get("start_date", str(datetime.date.today())),
        "end_date": body.get("end_date", str(datetime.date.today())),
        "footfall_impact_pct": int(body.get("footfall_impact_pct", 10)),
        "institution_id": body.get("institution_id", "inst1"),
        "created_at": _now()
    }
    MOCK_CALENDAR_EVENTS.append(event)
    return ok(event, 201)


# ─────────────────────────────────────────────
# IMPACT / REPORTS
# ─────────────────────────────────────────────

@app.route("/api/impact", methods=["GET"])
def get_impact():
    """GET /api/impact — monthly impact summary."""
    total_redistributed = sum(m["kg_redistributed"] for m in MOCK_IMPACT_LOGS)
    total_fertilizer    = sum(m["kg_fertilizer"] for m in MOCK_IMPACT_LOGS)
    total_animal_feed   = sum(m["kg_animal_feed"] for m in MOCK_IMPACT_LOGS)
    total_co2_saved     = sum(m["co2_saved"] for m in MOCK_IMPACT_LOGS)
    total_people_fed    = sum(m["people_fed"] for m in MOCK_IMPACT_LOGS)

    return ok({
        "summary": {
            "total_redistributed_kg": total_redistributed,
            "total_fertilizer_kg":    total_fertilizer,
            "total_animal_feed_kg":   total_animal_feed,
            "total_co2_saved_kg":     total_co2_saved,
            "total_people_fed":       total_people_fed,
            "total_social_impact_units": total_people_fed * 3  # formula
        },
        "monthly": MOCK_IMPACT_LOGS
    })


@app.route("/api/impact/welfare", methods=["GET"])
def get_welfare_impact():
    """GET /api/impact/welfare — welfare-specific tracking."""
    return ok({
        "students_served_week": 320,
        "food_received_today_kg": 48,
        "pending_deliveries": 6,
        "cost_savings_month": 18420,
        "incoming_alerts": [
            {"type": "delivery", "message": "Dal + Rice — 48kg incoming",   "eta_min": 45, "severity": "success"},
            {"type": "offer",    "message": "Vegetable Curry — 20kg, -50%", "eta_min": 60, "severity": "info"},
            {"type": "urgent",   "message": "Bread — 60 units near expiry", "eta_min": 0,  "severity": "warning"},
        ]
    })


# ─────────────────────────────────────────────
# SYSTEM / ADMIN
# ─────────────────────────────────────────────

@app.route("/api/system/health", methods=["GET"])
def system_health():
    """GET /api/system/health — platform health check."""
    return ok({
        "status": "healthy",
        "database": "connected",
        "ai_model": "v2.1 — active",
        "total_food_diverted_kg": 14282,
        "biogas_generation_m3":  840,
        "ngo_network_count":     42,
        "timestamp": _now()
    })


@app.route("/api/system/diagnostic", methods=["POST"])
def run_diagnostic():
    """POST /api/system/diagnostic — run platform diagnostic."""
    report = {
        "run_at": _now(),
        "checks": {
            "database_connection": "OK",
            "ai_model_loaded":     "OK",
            "ngo_api_reachable":   "OK",
            "alert_queue":         f"{random.randint(0,5)} pending alerts",
            "delivery_tracking":   "OK",
            "supabase_realtime":   "connected"
        },
        "overall": "PASS",
        "recommendation": "All systems nominal. AI model accuracy at 93.2%."
    }
    return ok(report)


@app.route("/api/users", methods=["GET"])
def get_users():
    """GET /api/users — list all platform users (admin only)."""
    return ok(MOCK_USERS)


@app.route("/api/behavioral-factors", methods=["POST"])
def add_behavioral_factor():
    """POST /api/behavioral-factors — add AI training factor."""
    body = request.get_json() or {}
    factor = {
        "id": f"bf{random.randint(100,999)}",
        "name": body.get("name", "New Factor"),
        "impact_weight": body.get("impact_weight", "medium"),
        "frequency": body.get("frequency", "daily"),
        "created_at": _now()
    }
    return ok({"factor": factor, "message": "Factor added to AI training pipeline. Re-training in next cycle."})


# ─────────────────────────────────────────────
# SQL SCHEMA ENDPOINT
# ─────────────────────────────────────────────

@app.route("/api/schema", methods=["GET"])
def get_schema():
    """GET /api/schema — returns Supabase/PostgreSQL schema."""
    schema = """
-- ============================================================
-- THE CONSCIOUS OBSERVER — SUPABASE POSTGRESQL SCHEMA
-- ============================================================

-- Users
CREATE TABLE users (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name          TEXT NOT NULL,
  email         TEXT UNIQUE NOT NULL,
  role          TEXT CHECK(role IN ('canteen','ngo','admin','welfare')) NOT NULL,
  institution   TEXT,
  phone         TEXT,
  avatar_url    TEXT,
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  last_login    TIMESTAMPTZ
);

-- Food Items (Surplus Inventory)
CREATE TABLE food_items (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  canteen_id       UUID REFERENCES users(id),
  name             TEXT NOT NULL,
  category         TEXT,
  qty_prepared     NUMERIC(10,2) NOT NULL,
  qty_remaining    NUMERIC(10,2),
  unit             TEXT DEFAULT 'kg',
  price            NUMERIC(8,2),
  discounted_price NUMERIC(8,2),
  shelf_life_hrs   INT NOT NULL,
  prepared_at      TIMESTAMPTZ DEFAULT NOW(),
  expiry_at        TIMESTAMPTZ,
  status           TEXT DEFAULT 'available',
  created_at       TIMESTAMPTZ DEFAULT NOW()
);

-- Footfall Records
CREATE TABLE footfall (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  canteen_id       UUID REFERENCES users(id),
  recorded_at      DATE NOT NULL,
  actual_count     INT,
  predicted_count  INT,
  attendance_pct   NUMERIC(5,2),
  seasonal_factor  NUMERIC(4,2) DEFAULT 1.0,
  behavioural_score NUMERIC(5,2),
  event_flag       BOOLEAN DEFAULT FALSE,
  model_version    TEXT DEFAULT 'v2.1'
);

-- NGO / CRO Partners
CREATE TABLE ngo_partners (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name                TEXT NOT NULL,
  type                TEXT CHECK(type IN ('NGO','CRO','Farm','Pet Keeper')),
  contact_person      TEXT,
  phone               TEXT,
  area                TEXT,
  capacity_kg         NUMERIC(10,2) DEFAULT 50,
  accepts_animal_feed BOOLEAN DEFAULT FALSE,
  verified            BOOLEAN DEFAULT FALSE,
  is_active           BOOLEAN DEFAULT TRUE,
  created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- Redistribution Requests
CREATE TABLE redistribution_requests (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  food_item_id    UUID REFERENCES food_items(id),
  canteen_id      UUID REFERENCES users(id),
  ngo_id          UUID REFERENCES ngo_partners(id),
  phase           INT CHECK(phase IN (1,2,3)),
  sub_phase       TEXT CHECK(sub_phase IN ('A','B')),
  status          TEXT DEFAULT 'pending',
  urgency         TEXT DEFAULT 'medium',
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  responded_at    TIMESTAMPTZ
);

-- Deliveries
CREATE TABLE deliveries (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  request_id       UUID REFERENCES redistribution_requests(id),
  cro_partner_id   UUID REFERENCES ngo_partners(id),
  driver_name      TEXT,
  pickup_location  TEXT,
  destination      TEXT,
  status           TEXT DEFAULT 'assigned',
  assigned_at      TIMESTAMPTZ DEFAULT NOW(),
  delivered_at     TIMESTAMPTZ,
  co2_saved_kg     NUMERIC(8,3)
);

-- Calendar Events
CREATE TABLE calendar_events (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title               TEXT NOT NULL,
  type                TEXT,
  start_date          DATE NOT NULL,
  end_date            DATE,
  footfall_impact_pct INT DEFAULT 0,
  institution_id      UUID REFERENCES users(id),
  created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- Behavioral Factors (AI Training)
CREATE TABLE behavioral_factors (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name           TEXT NOT NULL,
  impact_weight  TEXT DEFAULT 'medium',
  frequency      TEXT DEFAULT 'daily',
  value          NUMERIC,
  recorded_at    TIMESTAMPTZ DEFAULT NOW()
);

-- Impact Logs
CREATE TABLE impact_logs (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  date                DATE NOT NULL,
  canteen_id          UUID REFERENCES users(id),
  kg_redistributed    NUMERIC(10,2) DEFAULT 0,
  kg_fertilizer       NUMERIC(10,2) DEFAULT 0,
  kg_animal_feed      NUMERIC(10,2) DEFAULT 0,
  kg_biogas_input     NUMERIC(10,2) DEFAULT 0,
  biogas_m3           NUMERIC(10,3) DEFAULT 0,
  co2_saved_kg        NUMERIC(10,2) DEFAULT 0,
  people_fed          INT DEFAULT 0,
  cost_saved          NUMERIC(10,2) DEFAULT 0
);
    """.strip()
    return jsonify({"schema": schema}), 200


# ─────────────────────────────────────────────
# ERROR HANDLERS
# ─────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return err("Endpoint not found", 404)

@app.errorhandler(405)
def method_not_allowed(e):
    return err("Method not allowed", 405)

@app.errorhandler(500)
def internal_error(e):
    return err(f"Internal server error: {str(e)}", 500)


# ─────────────────────────────────────────────
# RUN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("╔══════════════════════════════════════════╗")
    print("║   The Conscious Observer — API Server    ║")
    print("║   Food Waste Management Platform         ║")
    print("╠══════════════════════════════════════════╣")
    print("║  Frontend : http://localhost:5000        ║")
    print("║  API Base : http://localhost:5000/api    ║")
    print("╠══════════════════════════════════════════╣")
    print("║  Key Endpoints:                          ║")
    print("║   POST /api/auth/login                   ║")
    print("║   POST /api/ai/predict-footfall          ║")
    print("║   GET  /api/ai/weekly-forecast           ║")
    print("║   GET  /api/food-items                   ║")
    print("║   POST /api/food-items                   ║")
    print("║   GET  /api/redistribution               ║")
    print("║   POST /api/redistribution               ║")
    print("║   GET  /api/ngo-partners                 ║")
    print("║   GET  /api/impact                       ║")
    print("║   GET  /api/system/health                ║")
    print("║   GET  /api/schema                       ║")
    print("╚══════════════════════════════════════════╝")
    app.run(debug=True, host="0.0.0.0", port=5000)
