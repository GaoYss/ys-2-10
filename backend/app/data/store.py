from copy import deepcopy
from datetime import date


class TrainingStore:
    def __init__(self):
        self.classes = [
            {
                "id": 1,
                "name": "Python Flask 周末班",
                "level": "入门",
                "teacher": "张老师",
                "room": "A-201",
                "status": "开课中",
                "capacity": 28,
                "students": [
                    {"id": 1, "name": "李明", "phone": "13800000001"},
                    {"id": 2, "name": "王雨", "phone": "13800000002"},
                    {"id": 3, "name": "陈晨", "phone": "13800000003"},
                ],
            },
            {
                "id": 2,
                "name": "React 全栈进阶班",
                "level": "进阶",
                "teacher": "刘老师",
                "room": "B-105",
                "status": "招生中",
                "capacity": 24,
                "students": [
                    {"id": 4, "name": "赵一", "phone": "13800000004"},
                    {"id": 5, "name": "周航", "phone": "13800000005"},
                ],
            },
        ]
        self.courses = [
            {"id": 1, "title": "Flask API 设计", "duration": 2, "category": "后端"},
            {"id": 2, "title": "React 组件化开发", "duration": 2, "category": "前端"},
            {"id": 3, "title": "数据库建模实践", "duration": 2, "category": "工程"},
            {"id": 4, "title": "项目联调与部署", "duration": 3, "category": "工程"},
        ]
        self.schedule = [
            {
                "id": 1,
                "class_id": 1,
                "course_id": 1,
                "date": str(date.today()),
                "time": "09:00-11:00",
                "room": "A-201",
                "teacher": "张老师",
            }
        ]
        self.attendance = [
            {"id": 1, "session_id": 1, "student_id": 1, "status": "present"},
            {"id": 2, "session_id": 1, "student_id": 2, "status": "late"},
            {"id": 3, "session_id": 1, "student_id": 3, "status": "absent"},
        ]
        self.holidays = [
            {"id": 1, "date": "2026-01-01", "name": "元旦", "type": "holiday"},
            {"id": 2, "date": "2026-02-16", "name": "春节", "type": "holiday"},
            {"id": 3, "date": "2026-02-17", "name": "春节", "type": "holiday"},
            {"id": 4, "date": "2026-04-06", "name": "清明节", "type": "holiday"},
            {"id": 5, "date": "2026-05-01", "name": "劳动节", "type": "holiday"},
            {"id": 6, "date": "2026-10-01", "name": "国庆节", "type": "holiday"},
            {"id": 7, "date": "2026-10-02", "name": "国庆节", "type": "holiday"},
            {"id": 8, "date": "2026-10-03", "name": "国庆节", "type": "holiday"},
        ]
        self.rest_days = [
            {"id": 1, "day_of_week": 6, "name": "周日"},
            {"id": 2, "day_of_week": 0, "name": "周一"},
        ]

    def next_id(self, collection):
        values = getattr(self, collection)
        return max([item["id"] for item in values], default=0) + 1

    def is_holiday(self, check_date):
        date_str = str(check_date)
        return any(h["date"] == date_str for h in self.holidays)

    def is_rest_day(self, check_date):
        day_of_week = check_date.weekday()
        return any(r["day_of_week"] == day_of_week for r in self.rest_days)

    def get_day_off_info(self, check_date):
        date_str = str(check_date)
        day_of_week = check_date.weekday()
        info = []
        for h in self.holidays:
            if h["date"] == date_str:
                info.append({"type": "holiday", "name": h["name"]})
        for r in self.rest_days:
            if r["day_of_week"] == day_of_week:
                info.append({"type": "rest_day", "name": r["name"]})
        return info

    def snapshot(self):
        return deepcopy(
            {
                "classes": self.classes,
                "courses": self.courses,
                "schedule": self.schedule,
                "attendance": self.attendance,
                "holidays": self.holidays,
                "rest_days": self.rest_days,
            }
        )


store = TrainingStore()
