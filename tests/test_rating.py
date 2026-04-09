"""
测试评分功能
"""

import requests
import json

# 测试配置
BASE_URL = "http://127.0.0.1:5000"
USER_UID = "0b74c836-2d8e-4b0f-b986-ccc3bc71817b"

def test_rating_api():
    """测试评分 API"""
    
    # 1. 获取历史记录
    print("1. 获取历史记录...")
    response = requests.get(
        f"{BASE_URL}/api/history",
        headers={"X-User-UID": USER_UID}
    )
    
    if response.status_code == 200:
        data = response.json()
        if data['success'] and data['history']:
            image_id = data['history'][0]['image_id']
            print(f"   找到图片 ID: {image_id}")
            
            # 2. 给图片评5星
            print(f"\n2. 给图片 {image_id} 评5星...")
            response = requests.post(
                f"{BASE_URL}/api/rating",
                headers={
                    "X-User-UID": USER_UID,
                    "Content-Type": "application/json"
                },
                json={
                    "image_id": image_id,
                    "rating": 5
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   评分成功: {result['message']}")
                
                # 3. 验证评分已更新
                print("\n3. 验证评分已更新...")
                response = requests.get(
                    f"{BASE_URL}/api/history",
                    headers={"X-User-UID": USER_UID}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    for item in data['history']:
                        if item['id'] == image_id:
                            print(f"   图片 {image_id} 的评分: {item['rating']}")
                            break
                
                # 4. 测试评分筛选
                print("\n4. 测试5星筛选...")
                response = requests.get(
                    f"{BASE_URL}/api/history?rating=5",
                    headers={"X-User-UID": USER_UID}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   5星图片数量: {data['count']}")
                    
            else:
                print(f"   评分失败: {response.json()}")
        
        else:
            print("   没有找到历史记录")
    else:
        print(f"   获取历史失败: {response.status_code}")

if __name__ == '__main__':
    test_rating_api()
