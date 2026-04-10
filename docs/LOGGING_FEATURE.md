# 日志记录功能说明

## 概述

系统现已集成完整的日志记录功能，用于跟踪图片生成和大模型调用的详细过程。所有日志文件都保存在 `logs/` 目录下。

## 日志文件

### 1. image_generation.log - 图片生成日志

记录所有图片生成相关的操作，包括：
- 开始生成图片（包含参数信息）
- 生成成功（包含文件名、耗时、Seed等）
- 生成失败（包含错误信息和耗时）
- 连接超时或失败

**日志位置**: `logs/image_generation.log`

**记录内容示例**:
```
2026-04-10 22:30:15,123 - INFO - 开始生成图片 - 用户ID: 1, 尺寸: 512x512, 步数: 8, Seed: -1
2026-04-10 22:30:45,456 - INFO - 图片生成成功 - 文件名: generated_20260410_223015.png, 耗时: 30.33秒, Seed: 123456789
```

### 2. llm_calls.log - 大模型调用日志

记录所有大模型API调用，包括：
- NSFW检测调用
- 提示词润色调用
- API请求和响应状态
- 检测结果
- 错误信息

**日志位置**: `logs/llm_calls.log`

**记录内容示例**:
```
2026-04-10 22:30:46,789 - INFO - 开始NSFW检测 - 图片ID: 20260410_223015, 提示词长度: 45
2026-04-10 22:30:48,012 - INFO - NSFW检测API响应 - 状态码: 200
2026-04-10 22:30:48,013 - INFO - NSFW检测结果 - 图片ID: 20260410_223015, 结果: 安全, 回答: NO
```

## 实现细节

### 修改的文件

1. **app.py**
   - 添加了 `logging` 模块导入
   - 创建了日志目录和两个logger实例
   - 在 `generate_image()` 函数中添加了关键节点的日志记录
   - 记录了开始、成功、失败、超时等各种情况

2. **llm_client.py**
   - 添加了 `logging` 模块导入
   - 配置了LLM调用logger
   - 在 `detect_nsfw_content()` 函数中添加了详细的日志记录
   - 记录了检测开始、API响应、检测结果等信息

3. **ai_refine.py**
   - 添加了 `logging` 模块导入
   - 配置了LLM调用logger
   - 在 `refine_prompt_with_llm()` 函数中添加了日志记录
   - 记录了润色开始、API响应、润色结果等信息

### 日志格式

所有日志采用统一格式：
```
%(asctime)s - %(levelname)s - %(message)s
```

例如：
```
2026-04-10 22:30:15,123 - INFO - 开始生成图片 - 用户ID: 1, 尺寸: 512x512
```

### 日志级别

- **INFO**: 正常操作流程（开始、成功、结果等）
- **WARNING**: 警告信息（配置不完整等）
- **ERROR**: 错误信息（API失败、异常等）

## 使用方法

### 查看日志

**Windows PowerShell**:
```powershell
# 查看图片生成日志
Get-Content logs\image_generation.log -Tail 50

# 查看LLM调用日志
Get-Content logs\llm_calls.log -Tail 50

# 实时监控日志
Get-Content logs\image_generation.log -Wait
```

**Windows CMD**:
```cmd
# 查看图片生成日志
type logs\image_generation.log

# 查看LLM调用日志
type logs\llm_calls.log
```

**Linux/Mac**:
```bash
# 查看最后50行
tail -n 50 logs/image_generation.log
tail -n 50 logs/llm_calls.log

# 实时监控
tail -f logs/image_generation.log
tail -f logs/llm_calls.log
```

### 日志轮转

目前日志文件会持续增长。如果需要限制日志文件大小或进行轮转，可以使用Python的 `RotatingFileHandler` 或 `TimedRotatingFileHandler`。

## 测试

运行测试脚本验证日志功能：

```bash
python test_logging.py
```

测试脚本会：
1. 检查日志目录是否存在
2. 导入app模块触发日志配置
3. 检查日志文件是否创建
4. 写入测试日志并验证内容

## 注意事项

1. **编码**: 日志文件使用UTF-8编码，支持中文内容
2. **性能**: 日志写入是同步操作，但影响极小
3. **磁盘空间**: 长期运行需要定期清理或轮转日志文件
4. **隐私**: 日志中可能包含用户提示词，请妥善保管

## 未来改进

可能的改进方向：
- [ ] 添加日志轮转功能（按大小或时间）
- [ ] 添加更详细的调试日志（DEBUG级别）
- [ ] 支持日志分级输出到不同文件
- [ ] 添加日志分析工具
- [ ] 支持远程日志收集
