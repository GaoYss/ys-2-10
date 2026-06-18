import { CalendarPlus, Edit3, Plus, Trash2, X, AlertTriangle } from "lucide-react";
import { useState, useEffect } from "react";
import { SectionHeader } from "../../components/SectionHeader";
import { api } from "../../services/api";

const TIME_SLOTS = ["09:00-11:00", "14:00-16:00", "19:00-21:00"];

export function ScheduleBoard({
  classes,
  courses,
  schedule,
  holidays,
  restDays,
  onGenerate,
  onCreateSchedule,
  onUpdateSchedule,
  onDeleteSchedule,
  onRefresh,
}) {
  const [classId, setClassId] = useState("");
  const [days, setDays] = useState(8);
  const [showForm, setShowForm] = useState(false);
  const [editingSession, setEditingSession] = useState(null);
  const [formData, setFormData] = useState({
    class_id: "",
    course_id: "",
    date: "",
    time: TIME_SLOTS[0],
    room: "",
    teacher: "",
  });
  const [riskCheck, setRiskCheck] = useState(null);
  const [showRiskDialog, setShowRiskDialog] = useState(false);
  const [pendingAction, setPendingAction] = useState(null);

  function getDateStatus(dateStr) {
    const isHoliday = holidays.some((h) => h.date === dateStr);
    const d = new Date(dateStr);
    const dayOfWeek = d.getDay() === 0 ? 6 : d.getDay() - 1;
    const isRestDay = restDays.some((r) => r.day_of_week === dayOfWeek);
    const holidayInfo = holidays.find((h) => h.date === dateStr);
    const restDayInfo = restDays.find((r) => r.day_of_week === dayOfWeek);
    return {
      isHoliday,
      isRestDay,
      isDayOff: isHoliday || isRestDay,
      holidayName: holidayInfo?.name,
      restDayName: restDayInfo?.name,
    };
  }

  useEffect(() => {
    async function checkRisk() {
      if (formData.date && formData.time && formData.room) {
        try {
          const risk = await api.checkScheduleRisk({
            ...formData,
            id: editingSession?.id,
          });
          setRiskCheck(risk);
        } catch (e) {
          setRiskCheck(null);
        }
      } else {
        setRiskCheck(null);
      }
    }
    checkRisk();
  }, [formData.date, formData.time, formData.room, formData.class_id, editingSession]);

  async function handleAutoGenerate(event) {
    event.preventDefault();
    await onGenerate({ class_id: classId || undefined, days });
  }

  function openCreateForm() {
    setEditingSession(null);
    const defaultClass = classes[0];
    setFormData({
      class_id: defaultClass?.id || "",
      course_id: courses[0]?.id || "",
      date: "",
      time: TIME_SLOTS[0],
      room: defaultClass?.room || "",
      teacher: defaultClass?.teacher || "",
    });
    setRiskCheck(null);
    setShowForm(true);
  }

  function openEditForm(session) {
    setEditingSession(session);
    setFormData({
      class_id: session.class_id,
      course_id: session.course_id,
      date: session.date,
      time: session.time,
      room: session.room,
      teacher: session.teacher,
    });
    setRiskCheck(null);
    setShowForm(true);
  }

  function handleClassChange(classIdVal) {
    const trainingClass = classes.find((c) => c.id === parseInt(classIdVal, 10));
    setFormData({
      ...formData,
      class_id: classIdVal,
      room: trainingClass?.room || formData.room,
      teacher: trainingClass?.teacher || formData.teacher,
    });
  }

  async function handleSubmit(event) {
    event.preventDefault();
    const payload = {
      ...formData,
      class_id: parseInt(formData.class_id, 10),
      course_id: parseInt(formData.course_id, 10),
    };

    if (riskCheck?.has_risk) {
      setPendingAction({ type: editingSession ? "update" : "create", payload });
      setShowRiskDialog(true);
      return;
    }

    await executeAction(payload, false);
  }

  async function executeAction(payload, force) {
    const data = { ...payload, force };
    if (editingSession) {
      await onUpdateSchedule(editingSession.id, data);
    } else {
      await onCreateSchedule(data);
    }
    setShowForm(false);
    setShowRiskDialog(false);
    setPendingAction(null);
    await onRefresh();
  }

  async function handleConfirmForce() {
    if (pendingAction) {
      await executeAction(pendingAction.payload, true);
    }
  }

  async function handleDelete(sessionId) {
    if (window.confirm("确定要删除这个课程安排吗？")) {
      await onDeleteSchedule(sessionId);
    }
  }

  const sortedSchedule = [...schedule].sort((a, b) => a.date.localeCompare(b.date));

  return (
    <section className="module">
      <form className="toolbar-panel" onSubmit={handleAutoGenerate}>
        <label>
          排课班级
          <select value={classId} onChange={(event) => setClassId(event.target.value)}>
            <option value="">全部班级</option>
            {classes.map((item) => (
              <option key={item.id} value={item.id}>
                {item.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          生成课次数
          <input
            min="1"
            max="30"
            type="number"
            value={days}
            onChange={(event) => setDays(Number(event.target.value))}
          />
        </label>
        <button className="primary-action" type="submit">
          <CalendarPlus size={18} />
          自动生成课程表
        </button>
        <button
          className="secondary-action"
          type="button"
          onClick={openCreateForm}
        >
          <Plus size={18} />
          手动添加课程
        </button>
      </form>

      {showForm && (
        <div className="modal-overlay" onClick={() => setShowForm(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{editingSession ? "编辑课程" : "手动添加课程"}</h3>
              <button
                className="icon-button"
                type="button"
                onClick={() => setShowForm(false)}
              >
                <X size={20} />
              </button>
            </div>

            {riskCheck?.has_risk && (
              <div className="risk-warning">
                <AlertTriangle size={20} />
                <div>
                  <strong>排课风险提示</strong>
                  <ul>
                    {riskCheck.warnings.map((w, i) => (
                      <li key={i}>{w}</li>
                    ))}
                  </ul>
                </div>
              </div>
            )}

            <form className="form-grid" onSubmit={handleSubmit}>
              <label>
                班级
                <select
                  value={formData.class_id}
                  onChange={(e) => handleClassChange(e.target.value)}
                  required
                >
                  <option value="">请选择班级</option>
                  {classes.map((item) => (
                    <option key={item.id} value={item.id}>
                      {item.name}
                    </option>
                  ))}
                </select>
              </label>

              <label>
                课程
                <select
                  value={formData.course_id}
                  onChange={(e) =>
                    setFormData({ ...formData, course_id: e.target.value })
                  }
                  required
                >
                  <option value="">请选择课程</option>
                  {courses.map((item) => (
                    <option key={item.id} value={item.id}>
                      {item.title}
                    </option>
                  ))}
                </select>
              </label>

              <label>
                日期
                <input
                  type="date"
                  value={formData.date}
                  onChange={(e) =>
                    setFormData({ ...formData, date: e.target.value })
                  }
                  required
                />
              </label>

              <label>
                时段
                <select
                  value={formData.time}
                  onChange={(e) =>
                    setFormData({ ...formData, time: e.target.value })
                  }
                  required
                >
                  {TIME_SLOTS.map((slot) => (
                    <option key={slot} value={slot}>
                      {slot}
                    </option>
                  ))}
                </select>
              </label>

              <label>
                教室
                <input
                  type="text"
                  value={formData.room}
                  onChange={(e) =>
                    setFormData({ ...formData, room: e.target.value })
                  }
                  required
                />
              </label>

              <label>
                讲师
                <input
                  type="text"
                  value={formData.teacher}
                  onChange={(e) =>
                    setFormData({ ...formData, teacher: e.target.value })
                  }
                  required
                />
              </label>

              <div className="form-actions">
                <button
                  type="button"
                  className="secondary-action"
                  onClick={() => setShowForm(false)}
                >
                  取消
                </button>
                <button
                  type="submit"
                  className={`primary-action ${riskCheck?.has_risk ? "risk" : ""}`}
                >
                  {editingSession ? "保存修改" : "添加课程"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showRiskDialog && (
        <div className="modal-overlay" onClick={() => setShowRiskDialog(false)}>
          <div className="modal-content risk-dialog" onClick={(e) => e.stopPropagation()}>
            <div className="risk-icon">
              <AlertTriangle size={40} />
            </div>
            <h3>排课风险确认</h3>
            <p>以下问题可能影响课程安排：</p>
            <ul className="risk-list">
              {pendingAction?.payload &&
                (() => {
                  const status = getDateStatus(pendingAction.payload.date);
                  const items = [];
                  if (status.isHoliday) {
                    items.push(
                      <li key="holiday" className="risk-holiday">
                        该日期是节假日：<strong>{status.holidayName}</strong>
                      </li>
                    );
                  }
                  if (status.isRestDay) {
                    items.push(
                      <li key="rest" className="risk-rest">
                        该日期是校区休息日：<strong>{status.restDayName}</strong>
                      </li>
                    );
                  }
                  return items;
                })()}
            </ul>
            <p className="risk-note">
              确认要在该日期排课吗？此操作将覆盖节假日和休息日设置。
            </p>
            <div className="form-actions">
              <button
                type="button"
                className="secondary-action"
                onClick={() => setShowRiskDialog(false)}
              >
                取消
              </button>
              <button
                type="button"
                className="primary-action danger"
                onClick={handleConfirmForce}
              >
                确认强制排课
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="table-panel">
        <SectionHeader eyebrow="Schedule" title="课程表" />
        <div className="schedule-grid">
          {sortedSchedule.length === 0 ? (
            <p className="notice">暂无课程安排</p>
          ) : (
            sortedSchedule.map((session) => {
              const status = getDateStatus(session.date);
              return (
                <article
                  className={`schedule-card ${status.isDayOff ? "day-off" : ""}`}
                  key={session.id}
                >
                  <span className="session-date">
                    {session.date}
                    {status.isDayOff && (
                      <span className="day-off-badge">
                        {status.isHoliday ? status.holidayName : status.restDayName}
                      </span>
                    )}
                  </span>
                  <h3>{session.course_title}</h3>
                  <p>{session.class_name}</p>
                  <div>
                    <small>{session.time}</small>
                    <small>{session.room}</small>
                    <small>{session.teacher}</small>
                  </div>
                  <div className="card-actions">
                    <button
                      className="secondary-action"
                      onClick={() => openEditForm(session)}
                      type="button"
                    >
                      <Edit3 size={14} />
                      编辑
                    </button>
                    <button
                      className="danger-action"
                      onClick={() => handleDelete(session.id)}
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
        <SectionHeader eyebrow="Courses" title="课程库" />
        <div className="course-tags">
          {courses.map((course) => (
            <span key={course.id}>
              {course.title} · {course.duration}课时 · {course.category}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}
