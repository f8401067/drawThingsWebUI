"""
测试数字用户ID功能
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_user_id_creation():
    """测试用户ID自动创建"""
    print("1. 测试用户ID创建...")
    
    # 调用新的用户创建接口
    response = requests.post(f"{BASE_URL}/api/user/create")
    
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            user_id = data.get('user_id')
            print(f"   ✓ 成功创建用户 ID: {user_id}")
            
            # 验证是整数
            if isinstance(user_id, int):
                print(f"   ✓ 用户 ID 是整数类型")
            else:
                print(f"   ✗ 用户 ID 不是整数类型: {type(user_id)}")
            
            return user_id
        else:
            print(f"   ✗ 请求失败: {data.get('error')}")
    else:
        print(f"   ✗ HTTP 错误: {response.status_code}")
    
    return None

def test_history_with_user_id(user_id):
    """测试使用用户ID获取历史记录"""
    print(f"\n2. 测试使用用户 ID ({user_id}) 获取历史记录...")
    
    response = requests.get(
        f"{BASE_URL}/api/history",
        headers={"X-User-ID": str(user_id)}
    )
    
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            print(f"   ✓ 成功获取历史记录")
            print(f"   - 记录数量: {data.get('count', 0)}")
            print(f"   - 返回的 user_id: {data.get('user_id')}")
            return True
        else:
            print(f"   ✗ 请求失败: {data.get('error')}")
    else:
        print(f"   ✗ HTTP 错误: {response.status_code}")
    
    return False

def test_all_users_history():
    """测试获取所有用户的历史记录"""
    print("\n3. 测试获取所有用户的历史记录...")
    
    response = requests.get(
        f"{BASE_URL}/api/history?all_users=true",
        headers={}
    )
    
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            print(f"   ✓ 成功获取所有用户历史记录")
            print(f"   - 记录数量: {data.get('count', 0)}")
            print(f"   - all_users: {data.get('all_users')}")
            return True
        else:
            print(f"   ✗ 请求失败: {data.get('error')}")
    else:
        print(f"   ✗ HTTP 错误: {response.status_code}")
    
    return False

def test_dates_query():
    """测试日期查询"""
    print("\n4. 测试日期查询...")
    
    response = requests.get(
        f"{BASE_URL}/api/history?query_dates=true",
        headers={}
    )
    
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            print(f"   ✓ 成功获取日期列表")
            print(f"   - 日期数量: {data.get('count', 0)}")
            print(f"   - 日期列表: {data.get('dates', [])}")
            return True
        else:
            print(f"   ✗ 请求失败: {data.get('error')}")
    else:
        print(f"   ✗ HTTP 错误: {response.status_code}")
    
    return False

if __name__ == "__main__":
    print("=" * 60)
    print("测试数字用户ID功能")
    print("=" * 60)
    
    # 测试1: 用户ID自动创建
    user_id = test_user_id_creation()
    
    if user_id:
        # 测试2: 使用用户ID获取历史
        test_history_with_user_id(user_id)
        
        # 测试3: 获取所有用户历史
        test_all_users_history()
        
        # 测试4: 日期查询
        test_dates_query()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
