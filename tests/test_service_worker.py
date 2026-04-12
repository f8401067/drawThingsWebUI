"""
测试 Service Worker 图片缓存功能
"""
import requests
import time

def test_service_worker_accessible():
    """测试 sw.js 文件是否可以访问"""
    print("测试 1: 检查 sw.js 是否可访问...")
    try:
        response = requests.get('http://127.0.0.1:5000/sw.js', timeout=5)
        if response.status_code == 200:
            print("✅ sw.js 可访问")
            print(f"   文件大小: {len(response.content)} bytes")
            print(f"   Content-Type: {response.headers.get('Content-Type')}")
            return True
        else:
            print(f"❌ sw.js 返回状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 访问 sw.js 失败: {e}")
        return False

def test_html_contains_sw_registration():
    """测试 HTML 页面是否包含 SW 注册代码"""
    print("\n测试 2: 检查 HTML 页面是否包含 SW 注册代码...")
    
    pages = ['index.html', 'history.html']
    all_passed = True
    
    for page in pages:
        try:
            response = requests.get(f'http://127.0.0.1:5000/{page}', timeout=5)
            if response.status_code == 200:
                content = response.text
                if 'serviceWorker' in content and 'register' in content:
                    print(f"✅ {page} 包含 SW 注册代码")
                else:
                    print(f"❌ {page} 缺少 SW 注册代码")
                    all_passed = False
            else:
                print(f"❌ 无法访问 {page}: {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"❌ 检查 {page} 失败: {e}")
            all_passed = False
    
    return all_passed

def test_cache_management_ui():
    """测试历史页面是否包含缓存管理UI"""
    print("\n测试 3: 检查历史页面是否包含缓存管理UI...")
    try:
        response = requests.get('http://127.0.0.1:5000/history.html', timeout=5)
        if response.status_code == 200:
            content = response.text
            if 'showCacheStats' in content and 'clearImageCache' in content:
                print("✅ 历史页面包含缓存管理UI")
                return True
            else:
                print("❌ 历史页面缺少缓存管理UI")
                return False
        else:
            print(f"❌ 无法访问 history.html: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        return False

def main():
    print("=" * 60)
    print("Service Worker 图片缓存功能测试")
    print("=" * 60)
    
    results = []
    
    # 运行测试
    results.append(("SW 可访问性", test_service_worker_accessible()))
    results.append(("HTML 注册代码", test_html_contains_sw_registration()))
    results.append(("缓存管理UI", test_cache_management_ui()))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总:")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！Service Worker 缓存功能已就绪。")
        print("\n下一步:")
        print("1. 在浏览器中打开 http://127.0.0.1:5000")
        print("2. 打开开发者工具 (F12)")
        print("3. 查看 Console 标签，应该看到 '[SW] Registered successfully'")
        print("4. 访问一些图片后，在历史页面点击'查看缓存'按钮")
    else:
        print("\n⚠️ 部分测试失败，请检查上述错误信息")

if __name__ == '__main__':
    main()
