# 自动NSFW标记功能说明

## 功能概述

本功能实现了在生成图片时自动检测提示词是否包含NSFW（Not Safe For Work）内容，并在检测到敏感内容时：
1. 异步调用LLM大模型进行内容分析
2. 自动对图片进行NSFW打标（保存到数据库）
3. 在前端弹出警告窗口（不拦截生成流程）

## 架构设计

### 后端组件

#### 1. LLM客户端模块 (`llm_client.py`)

**主要功能：**
- `load_llm_config()`: 从config.json加载LLM配置
- `detect_nsfw_content(prompt, negative_prompt, image_id)`: 同步检测NSFW内容
- `async_detect_nsfw(prompt, negative_prompt, image_id)`: 异步检测NSFW内容

**工作流程：**
```
用户提交生成请求 
    ↓
图片生成完成
    ↓
保存到历史记录
    ↓
启动后台线程进行NSFW检测
    ↓
调用LLM API分析提示词
    ↓
如果检测到NSFW → 更新数据库is_nsfw字段
```

**LLM Prompt设计：**
```python
system_message = """你是一个内容安全检测助手。请分析用户提供的图像生成提示词，判断是否包含不适合工作场所(NSFW)的内容。

NSFW内容包括但不限于：
- 色情或性暗示内容
- 暴力或血腥内容  
- 裸露或半裸内容
- 成人主题内容

请只回答"YES"或"NO"，不要添加其他解释。"""
```

#### 2. 数据库扩展 (`database.py`)

**新增函数：**
```python
def update_nsfw_status(image_id, is_nsfw):
    """直接设置图片的NSFW状态
    
    Args:
        image_id (str): 图片 ID
        is_nsfw (bool): 是否标记为NSFW
    
    Returns:
        bool: 更新成功返回True，失败返回False
    """
```

**数据库字段：**
- `is_nsfw INTEGER DEFAULT 0`: NSFW标记字段（0=正常，1=NSFW）

#### 3. 图片生成流程修改 (`app.py`)

在`generate_image()`函数中添加：
```python
# 保存到历史记录后
if user_id:
    # ... 保存记录 ...
    
    # 异步进行NSFW检测（如果配置了LLM）
    try:
        from llm_client import async_detect_nsfw
        prompt = params.get("prompt", "")
        negative_prompt = params.get("negative_prompt", "")
        async_detect_nsfw(prompt, negative_prompt, timestamp)
    except Exception as e:
        print(f"启动NSFW检测失败: {e}")
```

### 前端组件

#### 1. NSFW警告弹窗 (`static/index.html`)

**HTML结构：**
```html
<div id="nsfwWarningModal" class="custom-modal-overlay" style="display: none;">
    <div class="custom-modal">
        <div class="custom-modal-icon">⚠️</div>
        <div class="custom-modal-title">NSFW内容警告</div>
        <div class="custom-modal-message">
            检测到生成的图片可能包含不适合工作场所(NSFW)的内容。
            <br><br>
            该图片已被自动标记，您可以在历史记录中查看和管理。
        </div>
        <div class="custom-modal-buttons">
            <button class="btn-config btn-config-primary" onclick="closeNsfwWarning()">我知道了</button>
        </div>
    </div>
</div>
```

#### 2. 轮询检测机制

由于NSFW检测是异步进行的，前端使用轮询方式检查结果：

```javascript
// 在showResult函数中启动轮询
checkNsfwStatus(result.image_filename, 0);

// 轮询函数
async function checkNsfwStatus(imageFilename, attempts) {
    // 最多尝试30次（30秒）
    if (attempts >= 30) {
        console.log('NSFW检测超时');
        return;
    }

    try {
        // 从历史记录中获取该图片的信息
        const response = await fetch(`${API_BASE}/api/history?limit=1`, getFetchOptions());
        if (response.ok) {
            const data = await response.json();
            if (data.success && data.history && data.history.length > 0) {
                // 查找匹配的图片
                const image = data.history.find(item => item.image_filename === imageFilename);
                if (image && image.is_nsfw === 1) {
                    // 检测到NSFW，显示警告
                    showNsfwWarning();
                    return;
                }
            }
        }
    } catch (error) {
        console.error('检查NSFW状态失败:', error);
    }

    // 1秒后再次检查
    setTimeout(() => checkNsfwStatus(imageFilename, attempts + 1), 1000);
}
```

## 配置说明

### config.json配置项

```json
{
  "drawthings_url": "http://192.168.1.8:7888",
  "llm_api_url": "http://192.168.1.8:9111/v1/chat/completions",
  "llm_model": "Qwen3.5-4B-MLX-4bit",
  "llm_api_key": "yangfan"
}
```

**必需配置：**
- `llm_api_url`: LLM服务的API地址
- `llm_model`: 使用的模型名称
- `llm_api_key`: API密钥（可选，根据LLM服务要求）

**注意：** 如果未配置LLM参数，NSFW检测将自动跳过，不影响正常的图片生成流程。

## 使用流程

### 1. 用户生成图片

```
用户在主页输入提示词 → 点击生成 → 等待图片生成完成
```

### 2. 后台NSFW检测

```
图片生成完成 → 保存到数据库 → 启动异步NSFW检测
    ↓
LLM分析提示词 → 判断是否包含NSFW内容
    ↓
如果是NSFW → 更新数据库is_nsfw=1
```

### 3. 前端警告显示

```
显示生成的图片 → 开始轮询检查NSFW状态（最多30秒）
    ↓
检测到is_nsfw=1 → 弹出警告窗口
    ↓
用户点击"我知道了" → 关闭警告
```

### 4. 历史记录管理

用户可以在历史记录页面：
- 查看NSFW标记的图片（默认隐藏，需开启"显示NSFW"开关）
- 手动切换NSFW标记状态
- 删除标记为Bad的图片

## 特性说明

### ✅ 优点

1. **非阻塞式设计**: NSFW检测在后台异步执行，不影响用户体验
2. **容错性强**: 即使LLM服务不可用，也不影响正常图片生成
3. **灵活配置**: 通过config.json轻松启用/禁用功能
4. **用户友好**: 温和的警告提示，不强制拦截
5. **数据持久化**: NSFW标记保存在数据库中，可长期追踪

### ⚠️ 注意事项

1. **检测时机**: NSFW检测基于提示词，而非实际生成的图片内容
2. **准确性依赖**: 检测结果依赖于LLM模型的判断能力
3. **网络延迟**: 异步检测可能需要几秒到十几秒时间
4. **轮询开销**: 前端每张图片会进行最多30次轮询请求

### 🔧 性能优化建议

1. **缓存LLM响应**: 对于相同的提示词可以缓存检测结果
2. **批量检测**: 可以考虑批量处理多个图片的NSFW检测
3. **WebSocket替代轮询**: 未来可以使用WebSocket实现实时通知
4. **降低轮询频率**: 可以调整为2秒一次，减少服务器压力

## 测试方法

### 运行测试脚本

```bash
python tests/test_auto_nsfw.py
```

**测试内容：**
1. LLM配置加载测试
2. NSFW内容检测测试（正样本和负样本）
3. 异步检测功能测试
4. 数据库状态更新测试

### 手动测试流程

1. **准备环境：**
   - 确保LLM服务正常运行
   - 配置config.json中的LLM参数

2. **测试NSFW检测：**
   ```
   输入提示词: "nude woman, explicit content"
   点击生成
   观察控制台输出和前端警告
   ```

3. **验证数据库标记：**
   ```sql
   SELECT image_id, prompt, is_nsfw FROM generation_history 
   ORDER BY created_at DESC LIMIT 5;
   ```

4. **测试前端警告：**
   - 生成包含NSFW内容的图片
   - 等待10-30秒
   - 应该看到NSFW警告弹窗

## 故障排查

### 问题1: NSFW检测未执行

**可能原因：**
- LLM配置不完整
- LLM服务不可达

**解决方法：**
```python
# 检查配置
from llm_client import load_llm_config
config = load_llm_config()
print(config)  # 确认配置正确
```

### 问题2: 前端警告不显示

**可能原因：**
- 轮询未启动
- 数据库更新失败

**解决方法：**
1. 打开浏览器开发者工具
2. 查看Console是否有错误
3. 检查Network标签中的/api/history请求
4. 确认数据库中is_nsfw字段已更新

### 问题3: 检测准确率不高

**可能原因：**
- LLM模型能力有限
- Prompt设计不够清晰

**解决方法：**
1. 调整system_message中的NSFW定义
2. 更换更强大的LLM模型
3. 增加few-shot示例提高准确性

## 未来改进方向

1. **图片内容检测**: 不仅检测提示词，还检测实际生成的图片
2. **多级分类**: 区分不同类型的NSFW内容（色情、暴力等）
3. **置信度评分**: 返回检测的置信度，而非简单的YES/NO
4. **用户反馈机制**: 允许用户纠正误判，持续优化模型
5. **本地模型部署**: 使用轻量级本地模型提高响应速度

## 相关文件清单

```
drawThingsWebUI/
├── llm_client.py                    # LLM客户端模块（新增）
├── database.py                      # 数据库操作（新增update_nsfw_status）
├── app.py                           # 主应用（修改generate_image）
├── static/index.html                # 主页（新增NSFW警告弹窗）
├── config.json                      # 配置文件（需配置LLM参数）
└── tests/
    └── test_auto_nsfw.py           # 测试脚本（新增）
```

## 总结

自动NSFW标记功能通过异步调用LLM大模型，实现了对生成图片提示词的智能分析。该功能具有以下特点：

- ✅ **无感知集成**: 不影响现有图片生成流程
- ✅ **智能检测**: 利用LLM的强大理解能力
- ✅ **友好提示**: 温和警告，尊重用户选择
- ✅ **数据追踪**: 完整的NSFW标记历史记录
- ✅ **高度可配**: 灵活的配置选项

此功能有效提升了平台的内容安全性，同时保持了良好的用户体验。
