# 日志功能快速参考

## 📁 日志位置
```
logs/
├── image_generation.log  # 图片生成日志
└── llm_calls.log         # 大模型调用日志
```

## 🔍 查看日志

### Windows PowerShell
```powershell
# 查看最后50行
Get-Content logs\image_generation.log -Tail 50
Get-Content logs\llm_calls.log -Tail 50

# 实时监控
Get-Content logs\image_generation.log -Wait
```

### Linux/Mac
```bash
# 查看最后50行
tail -n 50 logs/image_generation.log
tail -n 50 logs/llm_calls.log

# 实时监控
tail -f logs/image_generation.log
tail -f logs/llm_calls.log
```

## 📝 日志内容

### image_generation.log
记录每次图片生成：
- ✅ 开始生成（参数信息）
- ✅ 生成成功（文件名、耗时、Seed）
- ❌ 生成失败（错误信息）
- ⏱️ 超时或连接失败

**示例**:
```
2026-04-10 22:30:15,123 - INFO - 开始生成图片 - 用户ID: 1, 尺寸: 512x512, 步数: 8, Seed: -1
2026-04-10 22:30:45,456 - INFO - 图片生成成功 - 文件名: generated_20260410_223015.png, 耗时: 30.33秒, Seed: 123456789
```

### llm_calls.log
记录所有LLM API调用：
- 🔒 NSFW检测
- ✨ 提示词润色
- 📊 API响应状态
- ✅ 检测结果
- ❌ 错误信息

**示例**:
```
2026-04-10 22:30:46,789 - INFO - 开始NSFW检测 - 图片ID: 20260410_223015, 提示词长度: 45
2026-04-10 22:30:48,012 - INFO - NSFW检测API响应 - 状态码: 200
2026-04-10 22:30:48,013 - INFO - NSFW检测结果 - 图片ID: 20260410_223015, 结果: 安全, 回答: NO
```

## 🧪 测试功能
```bash
python test_logging.py
```

## 📖 详细文档
- [docs/LOGGING_FEATURE.md](docs/LOGGING_FEATURE.md) - 完整功能说明
- [docs/LOGGING_IMPLEMENTATION_SUMMARY.md](docs/LOGGING_IMPLEMENTATION_SUMMARY.md) - 实现总结

## ⚠️ 注意事项
1. 日志使用UTF-8编码，支持中文
2. 长期运行需定期清理日志文件
3. 日志包含用户提示词，注意隐私保护
4. 日志写入是同步操作，性能影响极小
