import { useState } from "react";
import { CalendarPlus, Trash2 } from "lucide-react";
import { SectionHeader } from "../../components/SectionHeader";

const WEEKDAYS = [
  { value: 0, label: "周一" },
  { value: 1, label: "周二" },
  { value: 2, label: "周三" },
  { value: 3, label: "周四" },
  { value: 4, label: "周五" },
  { value: 5, label: "周六" },
  { value: 6, label: "周日" },
];

export function CalendarManager({
  holidays,
  restDays,
  onCreateHoliday,
  onDeleteHoliday,
  onCreateRestDay,
  onDeleteRestDay,
}) {
  const [holidayDate, setHolidayDate] = useState("");
  const [holidayName, setHolidayName] = useState("");
  const [restDayOfWeek, setRestDayOfWeek] = useState("");
  const [restDayName, setRestDayName] = useState("");

  async function handleAddHoliday(event) {
    event.preventDefault();
    if (!holidayDate || !holidayName) return;

    await onCreateHoliday({
      date: holidayDate,
      name: holidayName,
      type: "holiday",
    });

    setHolidayDate("");
    setHolidayName("");
  }

  async function handleAddRestDay(event) {
    event.preventDefault();
    if (restDayOfWeek === "" || !restDayName) return;

    await onCreateRestDay({
      day_of_week: parseInt(restDayOfWeek, 10),
      name: restDayName,
    });

    setRestDayOfWeek("");
    setRestDayName("");
  }

  const sortedHolidays = [...holidays].sort((a, b) => a.date.localeCompare(b.date));

  return (
    <section className="module">
      <div className="table-panel">
        <SectionHeader eyebrow="Holidays" title="法定节假日" />
        <form className="toolbar-panel" onSubmit={handleAddHoliday}>
          <label>
            日期
            <input
              type="date"
              value={holidayDate}
              onChange={(e) => setHolidayDate(e.target.value)}
            />
          </label>
          <label>
            节假日名称
            <input
              type="text"
              placeholder="如：元旦、春节"
              value={holidayName}
              onChange={(e) => setHolidayName(e.target.value)}
            />
          </label>
          <button className="primary-action" type="submit">
            <CalendarPlus size={18} />
            添加节假日
          </button>
        </form>

        <div className="schedule-grid">
          {sortedHolidays.length === 0 ? (
            <p className="notice">暂无节假日设置</p>
          ) : (
            sortedHolidays.map((holiday) => (
              <article className="schedule-card holiday" key={holiday.id}>
                <span>{holiday.date}</span>
                <h3>{holiday.name}</h3>
                <div className="card-actions">
                  <button
                    className="danger-action"
                    onClick={() => onDeleteHoliday(holiday.id)}
                    type="button"
                  >
                    <Trash2 size={14} />
                    删除
                  </button>
                </div>
              </article>
            ))
          )}
        </div>
      </div>

      <div className="table-panel">
        <SectionHeader eyebrow="Rest Days" title="校区每周休息日" />
        <form className="toolbar-panel" onSubmit={handleAddRestDay}>
          <label>
            星期
            <select
              value={restDayOfWeek}
              onChange={(e) => setRestDayOfWeek(e.target.value)}
            >
              <option value="">请选择星期</option>
              {WEEKDAYS.map((day) => (
                <option key={day.value} value={day.value}>
                  {day.label}
                </option>
              ))}
            </select>
          </label>
          <label>
            说明
            <input
              type="text"
              placeholder="如：周日休息"
              value={restDayName}
              onChange={(e) => setRestDayName(e.target.value)}
            />
          </label>
          <button className="primary-action" type="submit">
            <CalendarPlus size={18} />
            添加休息日
          </button>
        </form>

        <div className="schedule-grid">
          {restDays.length === 0 ? (
            <p className="notice">暂无休息日设置</p>
          ) : (
            restDays.map((restDay) => {
              const weekday = WEEKDAYS.find((d) => d.value === restDay.day_of_week);
              return (
                <article className="schedule-card rest-day" key={restDay.id}>
                  <span>{weekday?.label || `星期${restDay.day_of_week}`}</span>
                  <h3>{restDay.name}</h3>
                  <div className="card-actions">
                    <button
                      className="danger-action"
                      onClick={() => onDeleteRestDay(restDay.id)}
                      type="button"
                    >
                      <Trash2 size={14} />
                      删除
                    </button>
                  </div>
                </article>
              );
            })
          )}
        </div>
      </div>

      <div className="table-panel">
        <SectionHeader eyebrow="Legend" title="说明" />
        <div className="legend-info">
          <p>
            <strong>节假日：</strong>特殊日期的休假安排，如春节、国庆节等。自动排课时会自动跳过这些日期。
          </p>
          <p>
            <strong>校区休息日：</strong>每周固定的休息日，如周日、周一等。自动排课时会自动跳过这些星期。
          </p>
          <p>
            <strong>手动排课：</strong>在课程表页面可以手动添加课程。如果选择的日期是节假日或休息日，系统会提示风险，确认后仍可强制排课。
          </p>
        </div>
      </div>
    </section>
  );
}
