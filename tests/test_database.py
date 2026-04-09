"""
测试数据库迁移和API功能
"""

import requests
import json

base_url = "http://localhost:5000"

print("=" * 60)
print("测试1: 检查数据迁移")
print("=" * 60)

# 使用一个有记录的UID测试
test_uid = "66c018e0-32cd-4db4-8649-c77a1bea5956"

response = requests.get(
    f"{base_url}/api/history",
    headers={"X-User-UID": test_uid}
)

print(f"状态码: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"✓ 获取成功")
    print(f"  记录数: {data.get('count')}")
    print(f"  UID: {data.get('uid')}")
    if data.get('history'):
        print(f"  第一条记录:")
        first = data['history'][0]
        print(f"    - ID: {first.get('id')}")
        print(f"    - Prompt: {first.get('prompt', '')[:50]}...")
        print(f"    - Created: {first.get('created_at')}")
else:
    print(f"✗ 失败: {response.text}")

print("\n" + "=" * 60)
print("测试2: 获取可用日期")
print("=" * 60)

response = requests.get(
    f"{base_url}/api/history?query_dates=true",
    headers={"X-User-UID": test_uid}
)

print(f"状态码: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"✓ 获取成功")
    print(f"  可用日期数: {data.get('count')}")
    print(f"  日期列表: {data.get('dates')}")
else:
    print(f"✗ 失败: {response.text}")

print("\n" + "=" * 60)
print("测试3: 按日期筛选")
print("=" * 60)

if response.status_code == 200 and data.get('dates'):
    test_date = data['dates'][0]  # 使用第一个日期
    print(f"测试日期: {test_date}")
    
    response = requests.get(
        f"{base_url}/api/history?date={test_date}",
        headers={"X-User-UID": test_uid}
    )
    
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ 筛选成功")
        print(f"  记录数: {data.get('count')}")
        if data.get('history'):
            print(f"  示例记录:")
            for item in data['history'][:2]:
                print(f"    - {item.get('id')}: {item.get('prompt', '')[:30]}...")
    else:
        print(f"✗ 失败: {response.text}")
else:
    print("跳过：没有可用日期")

print("\n" + "=" * 60)
print("测试4: 查看所有用户")
print("=" * 60)

response = requests.get(
    f"{base_url}/api/history?all_users=true",
    headers={"X-User-UID": test_uid}
)

print(f"状态码: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"✓ 获取成功")
    print(f"  总记录数: {data.get('count')}")
    print(f"  All Users: {data.get('all_users')}")
else:
    print(f"✗ 失败: {response.text}")

print("\n" + "=" * 60)
print("测试完成!")
print("=" * 60)
