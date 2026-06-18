import requests

base = 'http://127.0.0.1:5000/api'

print('=== 测试1: 添加重复节假日日期 (2026-01-01 已存在) ===')
r = requests.post(f'{base}/calendar/holidays', json={
    'date': '2026-01-01', 'name': '重复测试', 'type': 'holiday'
})
print(f'Status: {r.status_code}')
print(f'Response: {r.json()}')
print()

print('=== 测试2: 修改节假日日期为已存在的日期 ===')
r = requests.put(f'{base}/calendar/holidays/2', json={
    'date': '2026-01-01', 'name': '春节修改测试'
})
print(f'Status: {r.status_code}')
print(f'Response: {r.json()}')
print()

print('=== 测试3: 正常修改节假日 (修改春节名称) ===')
r = requests.put(f'{base}/calendar/holidays/2', json={
    'name': '春节（修改后）'
})
print(f'Status: {r.status_code}')
print(f'Response: {r.json()}')
print()

print('=== 测试4: 排课风险检查（教室时间冲突） ===')
r = requests.post(f'{base}/schedule', json={
    'class_id': 1, 'course_id': 1, 'date': '2026-06-19',
    'time': '09:00-11:00', 'room': 'A-201', 'teacher': '张老师'
})
print(f'Status: {r.status_code}')
result = r.json()
if 'risk' in result:
    print(f'风险检查 warnings: {result["risk"]["warnings"]}')
else:
    print(f'Response: {result}')
print()

print('=== 测试5: 排课风险检查（节假日 + 可能的冲突） ===')
r = requests.post(f'{base}/schedule/check-risk', json={
    'class_id': 1, 'course_id': 1, 'date': '2026-01-01',
    'time': '09:00-11:00', 'room': 'A-201'
})
print(f'Status: {r.status_code}')
print(f'风险检查结果: {r.json()}')
print()

print('=== 所有改进测试完成 ===')
