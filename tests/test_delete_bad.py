"""
测试删除Bad图片功能
"""

import requests
import os

# 测试配置
BASE_URL = "http://127.0.0.1:5000"
USER_UID = "test-delete-user"
IMAGES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'generated_images')

def test_delete_bad_images():
    """测试删除Bad图片功能"""
    
    print("=" * 60)
    print("测试删除Bad图片功能")
    print("=" * 60)
    
    # 1. 先给一些图片标记为Bad
    print("\n1. 获取历史记录并标记一些图片为Bad...")
    response = requests.get(
        f"{BASE_URL}/api/history?all_users=true",
        headers={"X-User-UID": USER_UID}
    )
    
    if response.status_code != 200:
        print(f"   ✗ 获取历史失败: {response.status_code}")
        return False
    
    data = response.json()
    if not data['success'] or not data['history']:
        print("   ✗ 没有找到历史记录")
        return False
    
    # 标记前3张图片为Bad
    bad_image_ids = []
    for i, item in enumerate(data['history'][:3]):
        image_id = item.get('image_id')
        if image_id:
            response = requests.post(
                f"{BASE_URL}/api/rating",
                headers={
                    "X-User-UID": USER_UID,
                    "Content-Type": "application/json"
                },
                json={
                    "image_id": image_id,
                    "rating": -1
                }
            )
            if response.status_code == 200:
                bad_image_ids.append(image_id)
                print(f"   ✓ 标记图片 {image_id} 为 Bad")
            else:
                print(f"   ✗ 标记失败: {response.json()}")
    
    if not bad_image_ids:
        print("   ✗ 没有成功标记任何图片为Bad")
        return False
    
    print(f"\n   共标记 {len(bad_image_ids)} 张图片为 Bad")
    
    # 2. 验证Bad筛选能看到这些图片
    print("\n2. 验证Bad筛选条件...")
    response = requests.get(
        f"{BASE_URL}/api/history?all_users=true&rating=-1",
        headers={"X-User-UID": USER_UID}
    )
    
    if response.status_code == 200:
        data = response.json()
        bad_count = data.get('count', 0)
        print(f"   ✓ Bad筛选找到 {bad_count} 张图片")
    else:
        print(f"   ✗ Bad筛选失败")
        return False
    
    # 3. 尝试在不选择Bad筛选时删除（应该失败）
    print("\n3. 测试未选择Bad筛选时的删除（应该失败）...")
    response = requests.delete(
        f"{BASE_URL}/api/history/bad?rating=5",  # 使用rating=5而不是-1
        headers={"X-User-UID": USER_UID}
    )
    
    if response.status_code == 400:
        result = response.json()
        print(f"   ✓ 正确拒绝删除: {result['error']}")
    else:
        print(f"   ✗ 应该拒绝但未拒绝")
        return False
    
    # 4. 执行删除Bad图片
    print("\n4. 执行删除Bad图片...")
    response = requests.delete(
        f"{BASE_URL}/api/history/bad?rating=-1&all_users=true",
        headers={"X-User-UID": USER_UID}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✓ 删除成功!")
        print(f"     - 数据库记录删除: {result['deleted_count']} 条")
        print(f"     - 文件删除: {result['files_deleted']} 个")
        print(f"     - 文件删除失败: {result['files_failed']} 个")
    else:
        print(f"   ✗ 删除失败: {response.json()}")
        return False
    
    # 5. 验证删除后Bad图片数量为0
    print("\n5. 验证删除后Bad图片数量...")
    response = requests.get(
        f"{BASE_URL}/api/history?all_users=true&rating=-1",
        headers={"X-User-UID": USER_UID}
    )
    
    if response.status_code == 200:
        data = response.json()
        bad_count = data.get('count', 0)
        if bad_count == 0:
            print(f"   ✓ Bad图片已全部删除 (剩余: {bad_count})")
        else:
            print(f"   ✗ 仍有 {bad_count} 张Bad图片未删除")
            return False
    else:
        print(f"   ✗ 验证失败")
        return False
    
    # 6. 验证原文件是否已删除
    print("\n6. 验证原文件是否已删除...")
    files_exist = 0
    for image_id in bad_image_ids:
        # 从image_id推断文件名
        filename = f"generated_{image_id}.png"
        file_path = os.path.join(IMAGES_DIR, filename)
        if os.path.exists(file_path):
            print(f"   ✗ 文件仍存在: {filename}")
            files_exist += 1
        else:
            print(f"   ✓ 文件已删除: {filename}")
    
    if files_exist > 0:
        print(f"\n   ⚠ 警告: {files_exist} 个文件未被删除")
    else:
        print(f"\n   ✓ 所有文件已成功删除")
    
    print("\n" + "=" * 60)
    print("✓ 删除Bad图片功能测试通过！")
    print("=" * 60)
    return True

if __name__ == '__main__':
    test_delete_bad_images()

