"""
测试跨用户评分功能
"""

import requests
import json

# 测试配置
BASE_URL = "http://127.0.0.1:5000"

def test_cross_user_rating():
    """测试跨用户评分功能"""
    
    # 获取所有用户的历史记录
    print("1. 获取所有用户的历史记录...")
    response = requests.get(
        f"{BASE_URL}/api/history?all_users=true",
        headers={"X-User-UID": "test-user"}
    )
    
    if response.status_code == 200:
        data = response.json()
        if data['success'] and data['history']:
            # 找到第一个有记录的图片
            for item in data['history']:
                if item.get('image_id'):
                    image_id = item['image_id']
                    owner_uid = item.get('uid', 'unknown')
                    print(f"   找到图片 ID: {image_id}")
                    print(f"   图片所有者 UID: {owner_uid}")
                    
                    # 使用不同的用户 UID 进行评分
                    different_uid = "different-user-" + owner_uid[:8]
                    print(f"\n2. 使用不同用户 ({different_uid}) 为图片评分...")
                    
                    response = requests.post(
                        f"{BASE_URL}/api/rating",
                        headers={
                            "X-User-UID": different_uid,
                            "Content-Type": "application/json"
                        },
                        json={
                            "image_id": image_id,
                            "rating": 4
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        print(f"   ✓ 评分成功: {result['message']}")
                        print(f"   评分值: {result['rating']}")
                        
                        # 验证评分已更新
                        print("\n3. 验证评分已更新...")
                        response = requests.get(
                            f"{BASE_URL}/api/history?all_users=true",
                            headers={"X-User-UID": "test-user"}
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            for item in data['history']:
                                if item.get('image_id') == image_id:
                                    print(f"   图片 {image_id} 的当前评分: {item['rating']}")
                                    break
                        
                        print("\n✓ 跨用户评分功能测试通过！")
                        return True
                    else:
                        print(f"   ✗ 评分失败: {response.json()}")
                        return False
            
            print("   没有找到合适的图片进行测试")
            return False
        else:
            print("   没有找到历史记录")
            return False
    else:
        print(f"   获取历史失败: {response.status_code}")
        return False

if __name__ == '__main__':
    test_cross_user_rating()
