"""
验证重构后的应用是否正常工作
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def verify_imports():
    """验证所有模块能否正常导入"""
    print("=" * 60)
    print("验证模块导入...")
    print("=" * 60)
    
    try:
        from src.app import app
        print("✅ app.py 导入成功")
    except Exception as e:
        print(f"❌ app.py 导入失败: {e}")
        return False
    
    try:
        from src.history_routes import register_history_routes, get_user_uid
        print("✅ history_routes.py 导入成功")
    except Exception as e:
        print(f"❌ history_routes.py 导入失败: {e}")
        return False
    
    try:
        from src.database import (
            init_database,
            add_history_record,
            get_user_history,
            get_all_history,
            update_rating,
            delete_bad_images
        )
        print("✅ database.py 导入成功")
    except Exception as e:
        print(f"❌ database.py 导入失败: {e}")
        return False
    
    return True


def verify_routes():
    """验证所有路由是否正确注册"""
    print("\n" + "=" * 60)
    print("验证路由注册...")
    print("=" * 60)
    
    from src.app import app
    
    expected_routes = [
        ('/', 'GET'),
        ('/api/generate', 'POST'),
        ('/api/status', 'GET'),
        ('/api/config', 'GET'),
        ('/api/config', 'POST'),
        ('/api/history', 'GET'),
        ('/api/history', 'DELETE'),
        ('/api/rating', 'POST'),
        ('/api/history/bad', 'DELETE'),
        ('/api/status/generating', 'GET'),
    ]
    
    registered_rules = {
        (rule.rule, method) 
        for rule in app.url_map.iter_rules() 
        for method in rule.methods 
        if method not in ('OPTIONS', 'HEAD') and rule.endpoint != 'static'
    }
    
    all_found = True
    for route, method in expected_routes:
        if (route, method) in registered_rules:
            print(f"✅ {method:7} {route}")
        else:
            print(f"❌ {method:7} {route} - 未找到")
            all_found = False
    
    return all_found


def verify_database():
    """验证数据库功能"""
    print("\n" + "=" * 60)
    print("验证数据库功能...")
    print("=" * 60)
    
    try:
        from src.database import get_history_count
        
        # 测试基本查询
        count = get_history_count()
        print(f"✅ 数据库查询正常，当前记录数: {count}")
        
        return True
    except Exception as e:
        print(f"❌ 数据库功能异常: {e}")
        return False


def verify_code_quality():
    """验证代码质量"""
    print("\n" + "=" * 60)
    print("验证代码质量...")
    print("=" * 60)
    
    # 获取项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 检查文件行数
    files_to_check = [
        'app.py',
        'history_routes.py',
        'database.py'
    ]
    
    for filename in files_to_check:
        filepath = os.path.join(project_root, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = len(f.readlines())
            print(f"✅ {filename:25} {lines:4} 行")
        else:
            print(f"❌ {filename} 不存在")
            return False
    
    return True


def main():
    """主验证函数"""
    print("\n" + "=" * 60)
    print("DrawThings WebUI 重构验证")
    print("=" * 60 + "\n")
    
    results = []
    
    # 1. 验证导入
    results.append(("模块导入", verify_imports()))
    
    # 2. 验证路由
    results.append(("路由注册", verify_routes()))
    
    # 3. 验证数据库
    results.append(("数据库功能", verify_database()))
    
    # 4. 验证代码质量
    results.append(("代码质量", verify_code_quality()))
    
    # 总结
    print("\n" + "=" * 60)
    print("验证总结")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name:15} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n🎉 所有验证通过！重构成功！\n")
        return 0
    else:
        print("\n⚠️  部分验证失败，请检查上述错误\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
