from datetime import date
from flask import Blueprint, jsonify, request

from app.data.store import store


calendar_bp = Blueprint("calendar", __name__)


@calendar_bp.get("/holidays")
def list_holidays():
    return jsonify(store.holidays)


@calendar_bp.post("/holidays")
def create_holiday():
    payload = request.get_json() or {}
    if not payload.get("date") or not payload.get("name"):
        return jsonify({"error": "日期和名称不能为空"}), 400

    existing = next((h for h in store.holidays if h["date"] == payload["date"]), None)
    if existing:
        return jsonify({
            "error": f"该日期 {payload['date']} 已有节假日安排：{existing['name']}",
            "existing": existing,
        }), 409

    holiday = {
        "id": store.next_id("holidays"),
        "date": payload["date"],
        "name": payload["name"],
        "type": payload.get("type", "holiday"),
    }
    store.holidays.append(holiday)
    return jsonify(holiday), 201


@calendar_bp.put("/holidays/<int:holiday_id>")
def update_holiday(holiday_id):
    payload = request.get_json() or {}
    holiday = next((h for h in store.holidays if h["id"] == holiday_id), None)
    if not holiday:
        return jsonify({"error": "节假日不存在"}), 404

    new_date = payload.get("date", holiday["date"])
    if new_date != holiday["date"]:
        existing = next((h for h in store.holidays if h["date"] == new_date), None)
        if existing:
            return jsonify({
                "error": f"该日期 {new_date} 已有节假日安排：{existing['name']}",
                "existing": existing,
            }), 409

    holiday["date"] = new_date
    holiday["name"] = payload.get("name", holiday["name"])
    holiday["type"] = payload.get("type", holiday.get("type", "holiday"))
    return jsonify(holiday)


@calendar_bp.delete("/holidays/<int:holiday_id>")
def delete_holiday(holiday_id):
    holiday = next((h for h in store.holidays if h["id"] == holiday_id), None)
    if not holiday:
        return jsonify({"error": "节假日不存在"}), 404

    store.holidays = [h for h in store.holidays if h["id"] != holiday_id]
    return jsonify({"message": "删除成功"})


@calendar_bp.get("/rest-days")
def list_rest_days():
    return jsonify(store.rest_days)


@calendar_bp.post("/rest-days")
def create_rest_day():
    payload = request.get_json() or {}
    if payload.get("day_of_week") is None or not payload.get("name"):
        return jsonify({"error": "星期和名称不能为空"}), 400

    day_of_week = int(payload["day_of_week"])
    if day_of_week < 0 or day_of_week > 6:
        return jsonify({"error": "星期值必须在0-6之间"}), 400

    existing = any(r["day_of_week"] == day_of_week for r in store.rest_days)
    if existing:
        return jsonify({"error": "该星期已设置为休息日"}), 400

    rest_day = {
        "id": store.next_id("rest_days"),
        "day_of_week": day_of_week,
        "name": payload["name"],
    }
    store.rest_days.append(rest_day)
    return jsonify(rest_day), 201


@calendar_bp.delete("/rest-days/<int:rest_day_id>")
def delete_rest_day(rest_day_id):
    rest_day = next((r for r in store.rest_days if r["id"] == rest_day_id), None)
    if not rest_day:
        return jsonify({"error": "休息日不存在"}), 404

    store.rest_days = [r for r in store.rest_days if r["id"] != rest_day_id]
    return jsonify({"message": "删除成功"})


@calendar_bp.get("/check/<check_date>")
def check_date(check_date):
    try:
        parsed = date.fromisoformat(check_date)
    except ValueError:
        return jsonify({"error": "日期格式无效，请使用 YYYY-MM-DD"}), 400

    is_day_off = store.is_holiday(parsed) or store.is_rest_day(parsed)
    day_off_info = store.get_day_off_info(parsed)

    return jsonify({
        "date": check_date,
        "is_day_off": is_day_off,
        "day_off_info": day_off_info,
    })
