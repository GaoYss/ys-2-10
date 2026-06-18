import requests

base = 'http://127.0.0.1:5000/api'

print('=== 测试节假日列表 ===')
r = requests.get(f'{base}/calendar/holidays')
print(f'Status: {r.status_code}')
print(f'节假日数量: {len(r.json())}')

print('\n=== 测试休息日列表 ===')
r = requests.get(f'{base}/calendar/rest-days')
print(f'Status: {r.status_code}')
print(f'休息日数量: {len(r.json())}')

print('\n=== 测试日期检查 2026-01-01 (元旦) ===')
r = requests.get(f'{base}/calendar/check/2026-01-01')
print(f'Status: {r.status_code}')
print(f'结果: {r.json()}')

print('\n=== 测试日期检查 2026-01-02 (工作日) ===')
r = requests.get(f'{base}/calendar/check/2026-01-02')
print(f'Status: {r.status_code}')
print(f'结果: {r.json()}')

print('\n=== 测试自动排课 ===')
r = requests.post(f'{base}/schedule/generate', json={'class_id': 1, 'days': 3})
print(f'Status: {r.status_code}')
result = r.json()
print(f'生成课程数: {len(result.get("generated", []))}')
print(f'跳过日期数: {len(result.get("skipped", []))}')
if result.get('skipped'):
    print('跳过的日期:')
    for s in result['skipped'][:3]:
        names = [i['name'] for i in s['day_off_info']]
        print(f'  {s["date"]}: {names}')

print('\n=== 测试排课风险检查 (节假日) ===')
r = requests.post(f'{base}/schedule/check-risk', json={
    'class_id': 1, 'course_id': 1, 'date': '2026-01-01',
    'time': '09:00-11:00', 'room': 'A-201'
})
print(f'Status: {r.status_code}')
print(f'风险检查结果: {r.json()}')

print('\n=== 测试手动排课 (节假日, 不强制) ===')
r = requests.post(f'{base}/schedule', json={
    'class_id': 1, 'course_id': 1, 'date': '2026-01-01',
    'time': '09:00-11:00', 'room': 'A-201', 'teacher': '张老师'
})
print(f'Status: {r.status_code}')
print(f'结果: {r.json()}')

print('\n=== 测试手动排课 (节假日, 强制) ===')
r = requests.post(f'{base}/schedule', json={
    'class_id': 1, 'course_id': 1, 'date': '2026-01-01',
    'time': '09:00-11:00', 'room': 'A-201', 'teacher': '张老师',
    'force': True
})
print(f'Status: {r.status_code}')
print(f'结果成功: {r.json().get("session") is not None}')

print('\n=== 测试添加节假日 ===')
r = requests.post(f'{base}/calendar/holidays', json={
    'date': '2026-06-01', 'name': '儿童节', 'type': 'holiday'
})
print(f'Status: {r.status_code}')
print(f'结果: {r.json()}')

print('\n=== 测试添加休息日 ===')
r = requests.post(f'{base}/calendar/rest-days', json={
    'day_of_week': 2, 'name': '周三休息'
})
print(f'Status: {r.status_code}')
print(f'结果: {r.json()}')

print('\n=== 所有测试完成 ===')
