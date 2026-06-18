import requests

base = 'http://127.0.0.1:5000/api'

print('=== 测试1: 风险检查包含 warnings_detail ===')
r = requests.post(f'{base}/schedule/check-risk', json={
    'class_id': 1, 'course_id': 1, 'date': '2026-01-01',
    'time': '09:00-11:00', 'room': 'A-201'
})
print(f'Status: {r.status_code}')
result = r.json()
print(f'has_risk: {result.get("has_risk")}')
print(f'warnings: {result.get("warnings")}')
print(f'warnings_detail: {result.get("warnings_detail")}')
print()

print('=== 测试2: 教室时间冲突风险检查 ===')
r = requests.post(f'{base}/schedule/check-risk', json={
    'class_id': 1, 'course_id': 1, 'date': '2026-06-19',
    'time': '09:00-11:00', 'room': 'A-201'
})
result = r.json()
print(f'Status: {r.status_code}')
print(f'warnings_detail: {result.get("warnings_detail")}')
print()

print('=== 测试3: 无风险日期 ===')
r = requests.post(f'{base}/schedule/check-risk', json={
    'class_id': 1, 'course_id': 1, 'date': '2026-06-23',
    'time': '14:00-16:00', 'room': 'B-105'
})
result = r.json()
print(f'Status: {r.status_code}')
print(f'has_risk: {result.get("has_risk")}')
print(f'warnings_detail: {result.get("warnings_detail")}')
print()

print('=== 所有测试完成 ===')
