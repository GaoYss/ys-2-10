from datetime import date, timedelta

from app.data.store import store


TIME_SLOTS = ["09:00-11:00", "14:00-16:00", "19:00-21:00"]


def generate_schedule(class_id=None, days=10):
    classes = store.classes
    if class_id:
        classes = [item for item in classes if item["id"] == int(class_id)]

    if not classes:
        return {
            "generated": [],
            "skipped": [],
        }

    generated = []
    skipped = []
    cursor = date.today() + timedelta(days=1)
    course_index = 0

    while len(generated) < days:
        is_holiday = store.is_holiday(cursor)
        is_rest_day = store.is_rest_day(cursor)
        day_off_info = store.get_day_off_info(cursor)

        if is_holiday or is_rest_day:
            skipped.append({
                "date": cursor.isoformat(),
                "weekday": cursor.strftime("%A"),
                "day_off_info": day_off_info,
            })
        else:
            for training_class in classes:
                course = store.courses[course_index % len(store.courses)]
                session = {
                    "id": store.next_id("schedule"),
                    "class_id": training_class["id"],
                    "course_id": course["id"],
                    "date": cursor.isoformat(),
                    "time": TIME_SLOTS[course_index % len(TIME_SLOTS)],
                    "room": training_class["room"],
                    "teacher": training_class["teacher"],
                }
                store.schedule.append(session)
                generated.append(session)
                course_index += 1
                if len(generated) >= days:
                    break
        cursor += timedelta(days=1)

    return {
        "generated": generated,
        "skipped": skipped,
    }


def check_schedule_risk(session_data):
    check_date_str = session_data.get("date")
    if not check_date_str:
        return {"has_risk": False, "warnings": [], "warnings_detail": []}

    try:
        check_date_val = date.fromisoformat(check_date_str)
    except ValueError:
        return {
            "has_risk": True,
            "warnings": ["日期格式无效"],
            "warnings_detail": [{"type": "invalid_date", "message": "日期格式无效"}],
        }

    warnings = []
    warnings_detail = []
    day_off_info = store.get_day_off_info(check_date_val)

    for info in day_off_info:
        if info["type"] == "holiday":
            msg = f"该日期是节假日：{info['name']}"
            warnings.append(msg)
            warnings_detail.append({"type": "holiday", "message": msg, "name": info["name"]})
        elif info["type"] == "rest_day":
            msg = f"该日期是校区休息日：{info['name']}"
            warnings.append(msg)
            warnings_detail.append({"type": "rest_day", "message": msg, "name": info["name"]})

    existing = [
        s for s in store.schedule
        if s["date"] == check_date_str
        and s["time"] == session_data.get("time")
        and s["room"] == session_data.get("room")
        and s.get("id") != session_data.get("id")
    ]
    if existing:
        msg = "该时段该教室已有课程安排"
        warnings.append(msg)
        warnings_detail.append({"type": "conflict", "message": msg})

    return {
        "has_risk": len(warnings) > 0,
        "warnings": warnings,
        "warnings_detail": warnings_detail,
        "day_off_info": day_off_info,
    }


def create_manual_session(session_data, force=False):
    risk = check_schedule_risk(session_data)

    if risk["has_risk"] and not force:
        return {
            "success": False,
            "risk": risk,
            "message": "该日期存在排课风险，请确认是否强制排课",
        }

    training_class = next(
        (item for item in store.classes if item["id"] == int(session_data["class_id"])), None
    )
    if not training_class:
        return {"success": False, "message": "班级不存在"}

    course = next(
        (item for item in store.courses if item["id"] == int(session_data["course_id"])), None
    )
    if not course:
        return {"success": False, "message": "课程不存在"}

    session = {
        "id": store.next_id("schedule"),
        "class_id": training_class["id"],
        "course_id": course["id"],
        "date": session_data["date"],
        "time": session_data["time"],
        "room": session_data.get("room", training_class["room"]),
        "teacher": session_data.get("teacher", training_class["teacher"]),
    }

    store.schedule.append(session)

    return {
        "success": True,
        "session": session,
        "risk": risk,
    }


def update_session(session_id, session_data, force=False):
    existing = next((s for s in store.schedule if s["id"] == int(session_id)), None)
    if not existing:
        return {"success": False, "message": "课程不存在"}

    check_data = {
        **existing,
        **session_data,
        "id": int(session_id),
    }
    risk = check_schedule_risk(check_data)

    if risk["has_risk"] and not force:
        return {
            "success": False,
            "risk": risk,
            "message": "该日期存在排课风险，请确认是否强制排课",
        }

    existing["date"] = session_data.get("date", existing["date"])
    existing["time"] = session_data.get("time", existing["time"])
    existing["room"] = session_data.get("room", existing["room"])
    existing["teacher"] = session_data.get("teacher", existing["teacher"])
    existing["course_id"] = session_data.get("course_id", existing["course_id"])
    existing["class_id"] = session_data.get("class_id", existing["class_id"])

    return {
        "success": True,
        "session": existing,
        "risk": risk,
    }


def delete_session(session_id):
    existing = next((s for s in store.schedule if s["id"] == int(session_id)), None)
    if not existing:
        return {"success": False, "message": "课程不存在"}

    store.schedule = [s for s in store.schedule if s["id"] != int(session_id)]
    return {"success": True, "message": "删除成功"}


def enrich_session(session):
    training_class = next(
        (item for item in store.classes if item["id"] == session["class_id"]), None
    )
    course = next((item for item in store.courses if item["id"] == session["course_id"]), None)
    return {
        **session,
        "class_name": training_class["name"] if training_class else "未知班级",
        "course_title": course["title"] if course else "未知课程",
        "duration": course["duration"] if course else 0,
    }
