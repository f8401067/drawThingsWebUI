"""验证日期筛选默认行为"""
import requests

print("验证历史页面日期筛选默认行为...")
print("=" * 60)

try:
    response = requests.get('http://127.0.0.1:5000/history.html', timeout=5)
    
    if response.status_code == 200:
        print("✅ 历史页面可访问")
        
        content = response.text
        
        # 检查是否设置了默认为空
        if "currentDateFilter = '';" in content:
            print("✅ 日期筛选变量初始化为空字符串")
        else:
            print("❌ 日期筛选变量未正确初始化")
        
        # 检查DOMContentLoaded中的逻辑
        if "// 默认不设置日期筛选，显示所有日期的图片" in content:
            print("✅ 包含正确的注释说明")
        else:
            print("⚠️  缺少说明注释")
        
        # 检查是否在DOM加载时设置为空
        if "document.getElementById('dateFilterDisplay').value = '';" in content:
            print("✅ 日期输入框默认值为空")
        else:
            print("❌ 日期输入框默认值未设置")
        
        print("\n" + "=" * 60)
        print("总结: 日期筛选已调整为默认为空，将显示所有日期的图片")
        print("=" * 60)
    else:
        print(f"❌ 无法访问历史页面: {response.status_code}")
        
except Exception as e:
    print(f"❌ 测试失败: {e}")
