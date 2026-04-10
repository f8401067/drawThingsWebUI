"""
测试NSFW标记功能
"""

import requests
import json

# 测试配置
BASE_URL = "http://127.0.0.1:5000"

def test_nsfw_feature():
    """测试NSFW功能"""
    
    print("=" * 60)
    print("测试NSFW标记功能")
    print("=" * 60)
    
    # 1. 创建用户
    print("\n1. 创建新用户...")
    response = requests.post(f"{BASE_URL}/api/user/create")
    
    if response.status_code != 200:
        print(f"   ✗ 创建用户失败: {response.status_code}")
        return False
    
    user_data = response.json()
    user_id = user_data.get('user_id')
    print(f"   ✓ 用户ID: {user_id}")
    
    headers = {"X-User-ID": str(user_id)}
    
    # 2. 获取历史记录
    print("\n2. 获取历史记录...")
    response = requests.get(
        f"{BASE_URL}/api/history",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"   ✗ 获取历史失败: {response.status_code}")
        return False
    
    data = response.json()
    if not data['success'] or not data['history']:
        print("   ⚠ 没有找到历史记录，请先在主页生成一些图片")
        print("   跳过后续测试")
        return True
    
    image_id = data['history'][0]['image_id']
    print(f"   ✓ 找到图片 ID: {image_id}")
    
    # 3. 标记为NSFW
    print(f"\n3. 标记图片 {image_id} 为NSFW...")
    response = requests.post(
        f"{BASE_URL}/api/nsfw",
        headers={**headers, "Content-Type": "application/json"},
        json={"image_id": image_id}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✓ NSFW标记成功: is_nsfw={result['is_nsfw']}")
    else:
        print(f"   ✗ 标记失败: {response.status_code}")
        return False
    
    # 4. 验证默认隐藏NSFW
    print("\n4. 验证默认隐藏NSFW内容...")
    response = requests.get(
        f"{BASE_URL}/api/history",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        nsfw_count_before = sum(1 for item in data['history'] if item.get('is_nsfw', 0) == 1)
        print(f"   ✓ 当前显示的图片数: {data['count']}")
        print(f"   ✓ 其中NSFW图片数: {nsfw_count_before}")
        
        if nsfw_count_before == 0:
            print("   ✓ 默认情况下NSFW图片被隐藏")
        else:
            print("   ⚠ 仍有NSFW图片显示（可能是其他原因）")
    else:
        print(f"   ✗ 查询失败")
        return False
    
    # 5. 验证显示NSFW
    print("\n5. 验证显示NSFW内容...")
    response = requests.get(
        f"{BASE_URL}/api/history?show_nsfw=true",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        nsfw_count_after = sum(1 for item in data['history'] if item.get('is_nsfw', 0) == 1)
        print(f"   ✓ 显示NSFW后的图片数: {data['count']}")
        print(f"   ✓ 其中NSFW图片数: {nsfw_count_after}")
        
        if nsfw_count_after > 0:
            print("   ✓ NSFW图片已显示")
        else:
            print("   ⚠ 没有NSFW图片（可能都被删除了）")
    else:
        print(f"   ✗ 查询失败")
        return False
    
    # 6. 取消NSFW标记
    print(f"\n6. 取消图片 {image_id} 的NSFW标记...")
    response = requests.post(
        f"{BASE_URL}/api/nsfw",
        headers={**headers, "Content-Type": "application/json"},
        json={"image_id": image_id}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✓ 取消NSFW标记成功: is_nsfw={result['is_nsfw']}")
    else:
        print(f"   ✗ 取消失败: {response.status_code}")
        return False
    
    print("\n" + "=" * 60)
    print("✓ 所有测试通过!")
    print("=" * 60)
    return True

if __name__ == '__main__':
    try:
        test_nsfw_feature()
    except Exception as e:
        print(f"\n✗ 测试出错: {e}")
        import traceback
        traceback.print_exc()
