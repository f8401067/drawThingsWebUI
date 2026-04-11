"""
测试并发任务限制功能
"""
import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# API 基础 URL
API_BASE = "http://127.0.0.1:5000"

def generate_image(task_id):
    """生成图片的函数"""
    params = {
        "prompt": f"Test image {task_id}",
        "negative_prompt": "",
        "width": 512,
        "height": 512,
        "seed": -1,
        "steps": 8
    }
    
    try:
        response = requests.post(f"{API_BASE}/api/generate", json=params)
        result = response.json()
        
        return {
            "task_id": task_id,
            "status_code": response.status_code,
            "success": result.get("success", False),
            "message": result.get("error", "Success") if not result.get("success", False) else "Generated successfully"
        }
    except Exception as e:
        return {
            "task_id": task_id,
            "status_code": None,
            "success": False,
            "message": str(e)
        }

def test_concurrent_limit():
    """测试并发限制功能"""
    print("开始测试并发任务限制功能...")
    print("=" * 50)
    
    # 发送6个并发请求（超过5个的限制）
    tasks = list(range(1, 7))  # 6个任务
    
    with ThreadPoolExecutor(max_workers=6) as executor:
        future_to_task = {executor.submit(generate_image, task_id): task_id for task_id in tasks}
        
        results = []
        for future in as_completed(future_to_task):
            result = future.result()
            results.append(result)
            
            status_icon = "✓" if result["success"] else "✗"
            print(f"[{status_icon}] 任务 {result['task_id']}: {result['message']} (状态码: {result['status_code']})")
    
    print("\n" + "=" * 50)
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    rejected_count = sum(1 for r in results if not r["success"] and r["status_code"] == 429)
    error_count = sum(1 for r in results if not r["success"] and r["status_code"] != 429)
    
    print(f"成功生成: {success_count}")
    print(f"被拒绝(429): {rejected_count}")
    print(f"其他错误: {error_count}")
    
    if rejected_count > 0:
        print("\n✅ 并发限制功能正常工作!")
    else:
        print("\n❌ 并发限制功能可能未正常工作!")

if __name__ == "__main__":
    test_concurrent_limit()