from flask import Blueprint, jsonify, request

from app.data.store import store
from app.services.scheduler import (
    check_schedule_risk,
    create_manual_session,
    delete_session,
    enrich_session,
    generate_schedule,
    update_session,
)


schedule_bp = Blueprint("schedule", __name__)


@schedule_bp.get("")
def list_schedule():
    return jsonify([enrich_session(item) for item in store.schedule])


@schedule_bp.post("/generate")
def generate():
    payload = request.get_json() or {}
    result = generate_schedule(
        class_id=payload.get("class_id"),
        days=int(payload.get("days", 8)),
    )
    return jsonify({
        "generated": [enrich_session(item) for item in result["generated"]],
        "skipped": result["skipped"],
    }), 201


@schedule_bp.post("/check-risk")
def check_risk():
    payload = request.get_json() or {}
    risk = check_schedule_risk(payload)
    return jsonify(risk)


@schedule_bp.post("")
def create_schedule():
    payload = request.get_json() or {}
    force = payload.get("force", False)

    required = ["class_id", "course_id", "date", "time"]
    if not all(payload.get(field) for field in required):
        return jsonify({"error": "缺少必要字段"}), 400

    result = create_manual_session(payload, force=force)

    if not result["success"]:
        if result.get("risk"):
            return jsonify(result), 409
        return jsonify({"error": result.get("message", "创建失败")}), 400

    return jsonify({
        "session": enrich_session(result["session"]),
        "risk": result["risk"],
    }), 201


@schedule_bp.put("/<int:session_id>")
def update_schedule(session_id):
    payload = request.get_json() or {}
    force = payload.get("force", False)

    result = update_session(session_id, payload, force=force)

    if not result["success"]:
        if result.get("risk"):
            return jsonify(result), 409
        return jsonify({"error": result.get("message", "更新失败")}), 400

    return jsonify({
        "session": enrich_session(result["session"]),
        "risk": result["risk"],
    })


@schedule_bp.delete("/<int:session_id>")
def delete_schedule(session_id):
    result = delete_session(session_id)
    if not result["success"]:
        return jsonify({"error": result.get("message", "删除失败")}), 404
    return jsonify(result)
