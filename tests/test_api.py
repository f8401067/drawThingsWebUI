import requests
import json

# 测试历史API
base_url = "http://localhost:5000"

# 测试1: 获取历史记录
print("=" * 50)
print("测试1: 获取历史记录")
print("=" * 50)
try:
    response = requests.get(f"{base_url}/api/history", headers={"X-User-UID": "test-uid"})
    print(f"状态码: {response.status_code}")
    print(f"响应头 Content-Type: {response.headers.get('Content-Type')}")
    print(f"响应内容 (前500字符): {response.text[:500]}")
    
    # 尝试解析JSON
    try:
        data = response.json()
        print(f"JSON解析成功!")
        print(f"success: {data.get('success')}")
        print(f"count: {data.get('count')}")
    except Exception as e:
        print(f"JSON解析失败: {e}")
except Exception as e:
    print(f"请求失败: {e}")

print("\n" + "=" * 50)
print("测试2: 获取可用日期")
print("=" * 50)
try:
    response = requests.get(f"{base_url}/api/history?query_dates=true", headers={"X-User-UID": "test-uid"})
    print(f"状态码: {response.status_code}")
    print(f"响应头 Content-Type: {response.headers.get('Content-Type')}")
    print(f"响应内容: {response.text}")
    
    # 尝试解析JSON
    try:
        data = response.json()
        print(f"JSON解析成功!")
        print(f"success: {data.get('success')}")
        print(f"dates: {data.get('dates')}")
        print(f"count: {data.get('count')}")
    except Exception as e:
        print(f"JSON解析失败: {e}")
except Exception as e:
    print(f"请求失败: {e}")
