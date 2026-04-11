"""
测试重构后的历史记录路由功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app import app
from src.database import add_history_record, get_user_history
import json


def test_history_routes():
    """测试历史记录路由"""
    print("测试历史记录路由...")
    
    # 创建测试客户端
    client = app.test_client()
    
    # 测试添加历史记录
    print("1. 测试添加历史记录...")
    test_record = {
        "uid": "test_user_001",
        "id": "test_timestamp_001",
        "image_url": "/generated_images/test_image.png",
        "image_filename": "test_image.png",
        "prompt": "test prompt",
        "negative_prompt": "test negative prompt",
        "width": 512,
        "height": 512,
        "steps": 8,
        "seed": 12345,
        "elapsed_time": 5.5,
        "rating": 0,
        "created_at": "2026-04-09T10:00:00"
    }
    
    try:
        record_id = add_history_record(test_record)
        print(f"   ✓ 成功添加记录，ID: {record_id}")
    except Exception as e:
        print(f"   ✗ 添加记录失败: {e}")
        return False
    
    # 测试获取历史记录
    print("2. 测试获取历史记录...")
    response = client.get('/api/history', headers={"X-User-UID": "test_user_001"})
    if response.status_code == 200:
        data = json.loads(response.data)
        if data['success']:
            print(f"   ✓ 成功获取历史记录，共 {data['count']} 条")
        else:
            print(f"   ✗ 获取历史记录失败: {data.get('error')}")
            return False
    else:
        print(f"   ✗ 请求失败，状态码: {response.status_code}")
        print(f"   响应内容: {response.data.decode('utf-8')}")
        return False
    
    # 测试评分功能
    print("3. 测试评分功能...")
    rating_data = {
        "image_id": "test_timestamp_001",
        "rating": 5
    }
    response = client.post('/api/rating', 
                          headers={"X-User-UID": "test_user_001"},
                          data=json.dumps(rating_data),
                          content_type='application/json')
    if response.status_code == 200:
        data = json.loads(response.data)
        if data['success']:
            print(f"   ✓ 成功更新评分")
        else:
            print(f"   ✗ 评分更新失败: {data.get('error')}")
            return False
    else:
        print(f"   ✗ 请求失败，状态码: {response.status_code}")
        print(f"   响应内容: {response.data.decode('utf-8')}")
        return False
    
    # 测试日期查询
    print("4. 测试日期查询...")
    response = client.get('/api/history?query_dates=true', headers={"X-User-UID": "test_user_001"})
    if response.status_code == 200:
        data = json.loads(response.data)
        if data['success']:
            print(f"   ✓ 成功获取日期列表，共 {data['count']} 个日期")
        else:
            print(f"   ✗ 日期查询失败: {data.get('error')}")
            return False
    else:
        print(f"   ✗ 请求失败，状态码: {response.status_code}")
        print(f"   响应内容: {response.data.decode('utf-8')}")
        return False
    
    print("\n✅ 所有测试通过！")
    return True


if __name__ == "__main__":
    success = test_history_routes()
    if not success:
        sys.exit(1)
