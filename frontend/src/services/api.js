const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:5000/api";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    const error = new Error(`API request failed: ${response.status}`);
    error.status = response.status;
    error.data = errorBody;
    throw error;
  }

  return response.json();
}

export const api = {
  getClasses: () => request("/classes"),
  createClass: (payload) =>
    request("/classes", { method: "POST", body: JSON.stringify(payload) }),
  addStudent: (classId, payload) =>
    request(`/classes/${classId}/students`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  getCourses: () => request("/courses"),
  getSchedule: () => request("/schedule"),
  generateSchedule: (payload) =>
    request("/schedule/generate", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  createSchedule: (payload) =>
    request("/schedule", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  updateSchedule: (sessionId, payload) =>
    request(`/schedule/${sessionId}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
  deleteSchedule: (sessionId) =>
    request(`/schedule/${sessionId}`, { method: "DELETE" }),
  checkScheduleRisk: (payload) =>
    request("/schedule/check-risk", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  getHolidays: () => request("/calendar/holidays"),
  createHoliday: (payload) =>
    request("/calendar/holidays", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  updateHoliday: (holidayId, payload) =>
    request(`/calendar/holidays/${holidayId}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
  deleteHoliday: (holidayId) =>
    request(`/calendar/holidays/${holidayId}`, { method: "DELETE" }),
  getRestDays: () => request("/calendar/rest-days"),
  createRestDay: (payload) =>
    request("/calendar/rest-days", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  deleteRestDay: (restDayId) =>
    request(`/calendar/rest-days/${restDayId}`, { method: "DELETE" }),
  checkDate: (dateStr) => request(`/calendar/check/${dateStr}`),
  getAttendance: () => request("/attendance"),
  recordAttendance: (payload) =>
    request("/attendance", { method: "POST", body: JSON.stringify(payload) }),
  getHourStats: () => request("/stats/hours"),
};
