# 大模型调用耗时记录功能

## 概述

本次更新为所有大模型（LLM）调用添加了耗时记录功能，每次调用都会在日志文件中记录详细的耗时信息，便于性能监控和问题排查。

## 修改内容

### 1. NSFW检测模块 ([llm_client.py](file:///d:/work/project/my/drawThingsWebUI/llm_client.py))

在 `detect_nsfw_content()` 函数中添加了耗时记录：

- **开始时间记录**：在函数开始时记录 `start_time`
- **成功情况**：记录 "NSFW检测完成 - 图片ID: xxx, 耗时: x.xx秒"
- **失败情况**：在所有错误路径中都记录耗时信息
  - API响应格式异常
  - API请求失败
  - 网络异常或其他错误

### 2. 提示词润色模块 ([ai_refine.py](file:///d:/work/project/my/drawThingsWebUI/ai_refine.py))

在 `refine_prompt_with_llm()` 函数中添加了耗时记录：

- **开始时间记录**：在函数开始时记录 `start_time`
- **成功情况**：记录 "提示词润色成功 - 原始长度: xx, 润色后长度: xx, 耗时: x.xx秒"
- **失败情况**：在所有错误路径中都记录耗时信息
  - API请求失败
  - 网络异常或其他错误

## 日志输出示例

### 成功调用示例

```
2026-04-10 22:45:30,123 - INFO - 开始NSFW检测 - 图片ID: 20260410_224530, 提示词长度: 165
2026-04-10 22:45:35,456 - INFO - NSFW检测API响应 - 状态码: 200
2026-04-10 22:45:35,457 - INFO - NSFW检测完成 - 图片ID: 20260410_224530, 耗时: 5.33秒
2026-04-10 22:45:35,457 - INFO - NSFW检测结果 - 图片ID: 20260410_224530, 结果: 安全, 回答: NO
```

```
2026-04-10 22:46:10,789 - INFO - 开始润色提示词 - 原始长度: 28, 语言: zh
2026-04-10 22:46:15,234 - INFO - 提示词润色API响应 - 状态码: 200
2026-04-10 22:46:15,235 - INFO - 提示词润色成功 - 原始长度: 28, 润色后长度: 165, 耗时: 4.45秒
```

### 失败调用示例

```
2026-04-10 22:47:20,123 - INFO - 开始NSFW检测 - 图片ID: 20260410_224720, 提示词长度: 100
2026-04-10 22:47:50,456 - ERROR - LLM API请求失败，状态码: 500 - 耗时: 30.33秒
```

```
2026-04-10 22:48:05,789 - INFO - 开始润色提示词 - 原始长度: 50, 语言: en
2026-04-10 22:48:10,234 - ERROR - 网络请求错误: Connection timeout - 耗时: 4.45秒
```

## 技术实现

### 核心代码模式

```python
import time

def llm_function():
    start_time = time.time()  # 记录开始时间
    
    try:
        # ... LLM调用逻辑 ...
        
        # 成功时记录耗时
        elapsed_time = time.time() - start_time
        llm_logger.info(f"操作完成 - 耗时: {elapsed_time:.2f}秒")
        
    except Exception as e:
        # 失败时也记录耗时
        elapsed_time = time.time() - start_time
        llm_logger.error(f"操作失败: {str(e)} - 耗时: {elapsed_time:.2f}秒")
```

### 关键特点

1. **全面覆盖**：所有成功和失败路径都记录耗时
2. **精确计时**：使用 `time.time()` 获得高精度时间戳
3. **格式化输出**：保留两位小数，易于阅读
4. **无侵入性**：不影响现有功能，仅增加日志记录

## 使用场景

### 1. 性能监控

通过日志分析可以了解：
- 平均LLM调用耗时
- 不同操作的耗时分布
- 性能瓶颈识别

### 2. 问题排查

当出现超时时，可以通过耗时记录判断：
- 是网络问题还是模型处理慢
- 超时发生的具体阶段
- 是否需要调整timeout参数

### 3. 成本优化

通过耗时分析可以：
- 识别耗时的调用模式
- 优化prompt长度
- 选择合适的模型

## 日志文件位置

所有LLM调用日志都记录在：
```
logs/llm_calls.log
```

## 注意事项

1. **时间精度**：耗时记录精确到秒的小数点后两位
2. **异步调用**：NSFW检测是异步执行的，耗时记录在后台线程中完成
3. **日志级别**：
   - INFO级别：成功调用和正常流程
   - ERROR级别：失败调用和异常情况
   - WARNING级别：配置问题等非致命错误

## 相关文件

- [llm_client.py](file:///d:/work/project/my/drawThingsWebUI/llm_client.py) - NSFW检测模块
- [ai_refine.py](file:///d:/work/project/my/drawThingsWebUI/ai_refine.py) - 提示词润色模块
- [app.py](file:///d:/work/project/my/drawThingsWebUI/app.py) - 主应用（包含日志配置）
- [logs/llm_calls.log](file:///d:/work/project/my/drawThingsWebUI/logs/llm_calls.log) - LLM调用日志文件

## 测试验证

运行以下测试脚本验证功能：

```bash
python test_llm_timing.py
python test_timing_verification.py
```

## 总结

本次更新为所有大模型调用添加了完整的耗时记录功能，使得：
- ✅ 每次LLM调用都有明确的耗时记录
- ✅ 成功和失败情况都会记录耗时
- ✅ 便于性能监控和问题排查
- ✅ 不影响现有功能的正常运行
