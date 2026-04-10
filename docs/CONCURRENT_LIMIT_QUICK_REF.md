# 并发限制功能 - 快速参考

## 🎯 核心功能
系统最多允许 **5个** 图片生成任务同时进行，超出的请求会被拒绝。

## 🔍 如何查看当前负载

### 方法1：状态面板
连接服务器后，状态面板会显示：
```
🔄 当前有 X 个任务正在生成中... (最多允许5个并发任务)
```

### 方法2：API 查询
```bash
curl http://127.0.0.1:5000/api/status/generating
```

响应：
```json
{
  "success": true,
  "generating_count": 3
}
```

## ⚠️ 达到限制时会发生什么

### 后端响应
- HTTP 状态码：`429 Too Many Requests`
- 错误信息：`"当前已有 5 个任务正在生成中，请稍后再试（最多允许5个并发任务）"`

### 前端表现
- 弹出警告对话框
- 显示错误信息和重试建议
- 生成按钮恢复正常状态

## 💡 用户操作建议

1. **等待片刻**：等待当前任务完成后再试
2. **查看状态**：通过状态面板了解当前负载
3. **错峰使用**：避免在高峰期集中提交任务

## 🧪 测试功能

运行自动化测试：
```bash
python test_concurrent_limit.py
```

## 📝 开发者注意

### 修改限制值
在 `app.py` 的 `generate_image()` 函数中：
```python
if current_count >= 5:  # 修改这个数字
```

### 线程安全
- 计数器使用 `threading.Lock()` 保护
- 在 `finally` 块中清理计数

## 🔗 相关文档
- [详细功能说明](CONCURRENT_LIMIT_FEATURE.md)
- [更新摘要](CONCURRENT_LIMIT_UPDATE.md)
- [API 文档](../README.md#api-接口)
