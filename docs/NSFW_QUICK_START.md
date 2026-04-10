# 自动NSFW标记功能 - 快速开始

## 前置条件

1. ✅ LLM服务已启动并可访问
2. ✅ config.json中已配置LLM相关参数
3. ✅ 数据库已初始化（包含is_nsfw字段）

## 快速测试

### 方法1: 运行自动化测试

```bash
cd d:\work\project\my\drawThingsWebUI
python tests/test_auto_nsfw.py
```

预期输出：
```
✓ LLM配置加载成功
⚠️ 检测到NSFW: nude woman, explicit content...
✅ 未检测到: beautiful landscape with mountains...
```

### 方法2: 通过Web界面测试

#### 步骤1: 启动应用
```bash
python app.py
```

#### 步骤2: 访问主页
打开浏览器访问: `http://localhost:5000`

#### 步骤3: 测试NSFW检测

**测试用例1 - NSFW内容：**
```
提示词: nude woman, explicit content, adult
点击"生成图片"
等待图片生成完成
10-30秒后应弹出NSFW警告窗口
```

**测试用例2 - 安全内容：**
```
提示词: beautiful landscape with mountains and lake
点击"生成图片"
等待图片生成完成
不应弹出警告
```

#### 步骤4: 验证数据库标记

使用SQLite工具查看：
```sql
-- 查看最近生成的图片及其NSFW状态
SELECT 
    image_id,
    prompt,
    is_nsfw,
    created_at
FROM generation_history 
ORDER BY created_at DESC 
LIMIT 10;
```

预期结果：
- NSFW提示词生成的图片：`is_nsfw = 1`
- 安全提示词生成的图片：`is_nsfw = 0`

#### 步骤5: 查看历史记录

访问: `http://localhost:5000/history.html`

1. 默认情况下，NSFW图片会被隐藏
2. 开启"🔞 NSFW: 显示"开关
3. 可以看到标记为NSFW的图片带有红色图标

## 配置检查清单

### config.json配置示例

```json
{
  "drawthings_url": "http://192.168.1.8:7888",
  "llm_api_url": "http://192.168.1.8:9111/v1/chat/completions",
  "llm_model": "Qwen3.5-4B-MLX-4bit",
  "llm_api_key": "your-api-key"
}
```

### 验证配置

```python
from llm_client import load_llm_config

config = load_llm_config()
print("API URL:", config['api_url'])
print("Model:", config['model'])
print("API Key:", "已配置" if config['api_key'] else "未配置")
```

## 常见问题

### Q1: 没有看到NSFW警告？

**检查步骤：**
1. 确认LLM配置正确
2. 查看后端控制台是否有错误信息
3. 打开浏览器开发者工具，查看Console和Network标签
4. 确认数据库中is_nsfw字段是否被更新

### Q2: 如何禁用NSFW检测？

**方法1:** 删除config.json中的LLM配置
```json
{
  "drawthings_url": "http://192.168.1.8:7888"
  // 删除llm_api_url、llm_model、llm_api_key
}
```

**方法2:** 注释掉app.py中的调用代码
```python
# 注释掉这几行
# from llm_client import async_detect_nsfw
# async_detect_nsfw(prompt, negative_prompt, timestamp)
```

### Q3: 如何提高检测准确性？

1. **优化System Prompt**: 修改`llm_client.py`中的system_message
2. **更换模型**: 使用更强大的LLM模型
3. **增加上下文**: 同时发送正向和负向提示词
4. **调整温度**: 降低temperature值（当前0.1）以获得更一致的输出

## 监控和日志

### 后端日志

正常运行时，控制台会输出：
```
✅ 内容安全检查通过
```

检测到NSFW时：
```
⚠️  检测到NSFW内容: nude woman, explicit content...
检测到NSFW内容，已标记图片 20260410_143022
```

出错时：
```
LLM API请求失败，状态码: 500
异步NSFW检测失败: Connection timeout
```

### 前端日志

打开浏览器开发者工具，可以看到：
```
NSFW检测超时  (如果30秒内未完成)
检查NSFW状态失败: Network error
```

## 性能指标

- **检测延迟**: 通常5-15秒（取决于LLM响应速度）
- **轮询间隔**: 1秒/次
- **最大轮询次数**: 30次（30秒超时）
- **并发支持**: 每个图片生成独立线程，互不影响

## 下一步

- 📖 阅读完整文档: `docs/AUTO_NSFW_DETECTION.md`
- 🧪 运行更多测试: `tests/test_auto_nsfw.py`
- 🔧 自定义检测规则: 修改`llm_client.py`中的prompt
- 📊 分析NSFW数据: 查询数据库中的is_nsfw字段

## 技术支持

如遇到问题，请检查：
1. LLM服务是否正常运行
2. 网络连接是否正常
3. config.json配置是否正确
4. 数据库结构是否最新

查看日志文件获取详细错误信息。
